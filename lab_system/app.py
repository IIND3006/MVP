"""
app.py - Aplicación Flask principal para el sistema de gestión
de laboratorios universitarios ACAFOXX.

Rutas:
  GET  /                    → Dashboard
  GET  /classes             → Lista de cursos
  GET  /inventory           → Inventario
  GET  /reservations        → Lista de reservas
  GET  /reservations/add    → Formulario nueva reserva
  POST /reservations/add    → Guardar nueva reserva
  POST /reservations/<id>/complete → Completar práctica y descontar inventario
  POST /reservations/<id>/cancel   → Cancelar reserva
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import data
from models import Reservation

app = Flask(__name__)
app.secret_key = "acafoxx_secret_2026"   # necesario para flash messages

LABS = ["Lab A", "Lab B", "Lab C", "Lab D"]


# ────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ────────────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    low_stock_items = [item for item in data.inventory if item.is_low_stock()]
    pending_count = sum(
        1 for r in data.reservations
        if r.status in (Reservation.STATUS_PENDING, Reservation.STATUS_CONFIRMED)
    )
    return render_template(
        "dashboard.html",
        total_courses=len(data.courses),
        total_inventory=len(data.inventory),
        total_reservations=len(data.reservations),
        pending_reservations=pending_count,
        low_stock_items=low_stock_items,
    )


# ────────────────────────────────────────────────────────────────────────────
# CURSOS
# ────────────────────────────────────────────────────────────────────────────

@app.route("/classes")
def classes():
    inv_dict = data.get_inventory_dict()
    courses_with_materials = []
    for course in data.courses:
        materials_detail = []
        for mat in course.materials:
            item = inv_dict.get(mat["item_id"])
            if item:
                materials_detail.append({
                    "name": item.name,
                    "quantity": mat["quantity"],
                    "unit": item.unit,
                })
        courses_with_materials.append({
            "course": course,
            "materials_detail": materials_detail,
        })
    return render_template("classes.html", courses_with_materials=courses_with_materials)


# ────────────────────────────────────────────────────────────────────────────
# INVENTARIO
# ────────────────────────────────────────────────────────────────────────────

@app.route("/inventory")
def inventory():
    categories = sorted(set(item.category for item in data.inventory))
    return render_template(
        "inventory.html",
        items=data.inventory,
        categories=categories,
    )


# ────────────────────────────────────────────────────────────────────────────
# RESERVAS — lista
# ────────────────────────────────────────────────────────────────────────────

@app.route("/reservations")
def reservations():
    courses_dict = data.get_courses_dict()
    inv_dict = data.get_inventory_dict()

    enriched = []
    for r in data.reservations:
        course = courses_dict.get(r.course_id)
        inv_used_detail = []
        for entry in r.inventory_used:
            inv_used_detail.append(entry)   # ya viene con name incluido
        enriched.append({
            "reservation": r,
            "course": course,
            "inv_used_detail": inv_used_detail,
        })

    # Ordenar por fecha y hora
    enriched.sort(key=lambda x: (x["reservation"].date_str, x["reservation"].time_str))
    return render_template("reservations.html", enriched=enriched)


# ────────────────────────────────────────────────────────────────────────────
# RESERVAS — agregar
# ────────────────────────────────────────────────────────────────────────────

@app.route("/reservations/add", methods=["GET", "POST"])
def add_reservation():
    if request.method == "POST":
        course_id = request.form.get("course_id")
        lab = request.form.get("lab")
        date_str = request.form.get("date_str")
        time_str = request.form.get("time_str")

        # Validar campos requeridos
        if not all([course_id, lab, date_str, time_str]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("add_reservation"))

        # Validar que el curso existe
        courses_dict = data.get_courses_dict()
        if course_id not in courses_dict:
            flash("Curso inválido.", "error")
            return redirect(url_for("add_reservation"))

        # Verificar colisión: mismo lab, misma fecha y hora
        new_key = f"{lab}_{date_str}_{time_str}"
        for existing in data.reservations:
            if (existing.datetime_key == new_key
                    and existing.status != Reservation.STATUS_CANCELLED):
                flash(
                    f"Ya existe una reserva en {lab} el {date_str} a las {time_str}. "
                    "Por favor elige otro horario o laboratorio.",
                    "error"
                )
                return redirect(url_for("add_reservation"))

        # Crear reserva
        new_id = data.next_reservation_id()
        reservation = Reservation(new_id, course_id, lab, date_str, time_str)
        reservation.confirm()
        data.reservations.append(reservation)
        flash(f"Reserva {new_id} creada exitosamente.", "success")
        return redirect(url_for("reservations"))

    return render_template("add_reservation.html", courses=data.courses, labs=LABS)


# ────────────────────────────────────────────────────────────────────────────
# RESERVAS — completar práctica
# ────────────────────────────────────────────────────────────────────────────

@app.route("/reservations/<reservation_id>/complete", methods=["POST"])
def complete_reservation(reservation_id):
    # Buscar reserva
    reservation = next((r for r in data.reservations if r.reservation_id == reservation_id), None)
    if not reservation:
        flash("Reserva no encontrada.", "error")
        return redirect(url_for("reservations"))

    if reservation.status == Reservation.STATUS_COMPLETED:
        flash("Esta reserva ya fue completada.", "warning")
        return redirect(url_for("reservations"))

    if reservation.status == Reservation.STATUS_CANCELLED:
        flash("No se puede completar una reserva cancelada.", "error")
        return redirect(url_for("reservations"))

    # Obtener curso y materiales requeridos
    courses_dict = data.get_courses_dict()
    inv_dict = data.get_inventory_dict()
    course = courses_dict.get(reservation.course_id)

    if not course:
        flash("Curso asociado no encontrado.", "error")
        return redirect(url_for("reservations"))

    # Intentar descontar inventario
    insufficient = []
    for mat in course.materials:
        item = inv_dict.get(mat["item_id"])
        if item and item.stock < mat["quantity"]:
            insufficient.append(f"{item.name} (necesario: {mat['quantity']} {item.unit}, disponible: {item.stock})")

    if insufficient:
        flash(
            "Stock insuficiente para completar la práctica: " + "; ".join(insufficient),
            "error"
        )
        return redirect(url_for("reservations"))

    # Descontar y registrar
    inventory_used = []
    for mat in course.materials:
        item = inv_dict.get(mat["item_id"])
        if item:
            item.deduct(mat["quantity"])
            inventory_used.append({
                "item_id": item.item_id,
                "name": item.name,
                "quantity": mat["quantity"],
                "unit": item.unit,
            })

    reservation.complete(inventory_used)
    flash(f"Práctica completada. Inventario actualizado ({len(inventory_used)} ítems descontados).", "success")
    return redirect(url_for("reservations"))


# ────────────────────────────────────────────────────────────────────────────
# RESERVAS — cancelar
# ────────────────────────────────────────────────────────────────────────────

@app.route("/reservations/<reservation_id>/cancel", methods=["POST"])
def cancel_reservation(reservation_id):
    reservation = next((r for r in data.reservations if r.reservation_id == reservation_id), None)
    if not reservation:
        flash("Reserva no encontrada.", "error")
    elif reservation.status == Reservation.STATUS_COMPLETED:
        flash("No se puede cancelar una reserva ya completada.", "error")
    else:
        reservation.cancel()
        flash(f"Reserva {reservation_id} cancelada.", "warning")
    return redirect(url_for("reservations"))


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
