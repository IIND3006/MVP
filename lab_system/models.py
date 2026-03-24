"""
models.py - Clases del dominio del sistema de gestión de laboratorios
"""

from datetime import datetime


class InventoryItem:
    """Representa un ítem del inventario del laboratorio."""

    def __init__(self, item_id, name, category, stock, min_stock, unit):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.stock = stock
        self.min_stock = min_stock
        self.unit = unit

    def is_low_stock(self):
        """Retorna True si el stock está por debajo del mínimo."""
        return self.stock <= self.min_stock

    def status(self):
        """Retorna 'Bajo Stock' o 'OK' según el nivel actual."""
        return "Bajo Stock" if self.is_low_stock() else "OK"

    def deduct(self, amount):
        """
        Descuenta una cantidad del stock.
        Retorna True si la operación fue exitosa, False si no hay suficiente stock.
        """
        if self.stock >= amount:
            self.stock -= amount
            return True
        return False

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "stock": self.stock,
            "min_stock": self.min_stock,
            "unit": self.unit,
            "status": self.status(),
            "low_stock": self.is_low_stock(),
        }


class Course:
    """Representa un curso o asignatura que usa el laboratorio."""

    def __init__(self, course_id, code, name, professor, students, materials):
        """
        materials: lista de dicts con {item_id, quantity}
        """
        self.course_id = course_id
        self.code = code
        self.name = name
        self.professor = professor
        self.students = students
        self.materials = materials  # [{"item_id": "I001", "quantity": 10}, ...]

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "code": self.code,
            "name": self.name,
            "professor": self.professor,
            "students": self.students,
            "materials": self.materials,
        }


class Reservation:
    """Representa una reserva de laboratorio para una sesión de práctica."""

    STATUS_PENDING = "Pendiente"
    STATUS_CONFIRMED = "Confirmada"
    STATUS_COMPLETED = "Completada"
    STATUS_CANCELLED = "Cancelada"

    def __init__(self, reservation_id, course_id, lab, date_str, time_str):
        self.reservation_id = reservation_id
        self.course_id = course_id
        self.lab = lab
        self.date_str = date_str      # "YYYY-MM-DD"
        self.time_str = time_str      # "HH:MM"
        self.status = self.STATUS_PENDING
        self.inventory_used = []      # registra lo descontado al completar

    def complete(self, inventory_used_list):
        """
        Marca la reserva como completada y registra el inventario usado.
        inventory_used_list: [{"item_id": ..., "name": ..., "quantity": ...}, ...]
        """
        self.status = self.STATUS_COMPLETED
        self.inventory_used = inventory_used_list

    def cancel(self):
        self.status = self.STATUS_CANCELLED

    def confirm(self):
        self.status = self.STATUS_CONFIRMED

    @property
    def datetime_key(self):
        """Clave única para detectar colisiones en mismo lab y mismo horario."""
        return f"{self.lab}_{self.date_str}_{self.time_str}"

    def to_dict(self):
        return {
            "reservation_id": self.reservation_id,
            "course_id": self.course_id,
            "lab": self.lab,
            "date_str": self.date_str,
            "time_str": self.time_str,
            "status": self.status,
            "inventory_used": self.inventory_used,
        }
