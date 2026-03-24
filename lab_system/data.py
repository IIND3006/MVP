"""
data.py - Base de datos en memoria con datos de ejemplo realistas
para el sistema de gestión de laboratorios universitarios (ACAFOXX).
"""

from models import InventoryItem, Course, Reservation

# ---------------------------------------------------------------------------
# INVENTARIO
# ---------------------------------------------------------------------------
inventory = [
    InventoryItem("I001", "Ácido Clorhídrico (HCl) 37%",   "Ácidos",      45,  20,  "mL"),
    InventoryItem("I002", "Hidróxido de Sodio (NaOH)",      "Bases",       80,  30,  "g"),
    InventoryItem("I003", "Etanol 96%",                     "Solventes",   12,  15,  "mL"),   # bajo stock
    InventoryItem("I004", "Agua destilada",                 "Solventes",  200,  50,  "mL"),
    InventoryItem("I005", "Glucosa anhidra",                "Reactivos",   60,  25,  "g"),
    InventoryItem("I006", "Azul de Metileno",               "Colorantes",   8,  10,  "mL"),   # bajo stock
    InventoryItem("I007", "Tubos de ensayo (13x100 mm)",    "Materiales",  90,  40,  "unid"),
    InventoryItem("I008", "Pipetas Pasteur",                "Materiales",  35,  20,  "unid"),
    InventoryItem("I009", "Guantes de nitrilo M",           "EPP",         18,  20,  "pares"), # bajo stock
    InventoryItem("I010", "Papel indicador pH",             "Materiales",  50,  15,  "tiras"),
    InventoryItem("I011", "Acetona",                        "Solventes",   30,  15,  "mL"),
    InventoryItem("I012", "Cloruro de Sodio (NaCl)",        "Reactivos",  150,  40,  "g"),
]

# ---------------------------------------------------------------------------
# CURSOS
# ---------------------------------------------------------------------------
courses = [
    Course(
        "C001", "QUIM-101", "Química General",
        "Dr. Ramírez",  28,
        [{"item_id": "I001", "quantity": 5},
         {"item_id": "I007", "quantity": 6},
         {"item_id": "I009", "quantity": 2}]
    ),
    Course(
        "C002", "BIOL-201", "Biología Celular",
        "Dra. Herrera", 22,
        [{"item_id": "I006", "quantity": 2},
         {"item_id": "I008", "quantity": 4},
         {"item_id": "I004", "quantity": 30}]
    ),
    Course(
        "C003", "QUIM-305", "Química Orgánica",
        "Dr. Ospina",   18,
        [{"item_id": "I003", "quantity": 8},
         {"item_id": "I011", "quantity": 5},
         {"item_id": "I010", "quantity": 10}]
    ),
    Course(
        "C004", "BIOL-102", "Microbiología Básica",
        "Dra. Torres",  25,
        [{"item_id": "I005", "quantity": 15},
         {"item_id": "I012", "quantity": 20},
         {"item_id": "I007", "quantity": 8}]
    ),
    Course(
        "C005", "BIOC-401", "Bioquímica Aplicada",
        "Dr. Morales",  16,
        [{"item_id": "I002", "quantity": 10},
         {"item_id": "I004", "quantity": 50},
         {"item_id": "I005", "quantity": 12}]
    ),
]

# ---------------------------------------------------------------------------
# RESERVAS
# ---------------------------------------------------------------------------
reservations = [
    Reservation("R001", "C001", "Lab A", "2026-03-25", "08:00"),
    Reservation("R002", "C002", "Lab B", "2026-03-25", "10:00"),
    Reservation("R003", "C003", "Lab A", "2026-03-26", "14:00"),
    Reservation("R004", "C004", "Lab C", "2026-03-27", "08:00"),
]

reservations[0].confirm()
reservations[1].confirm()

# ---------------------------------------------------------------------------
# Helpers de acceso rápido
# ---------------------------------------------------------------------------

def get_inventory_dict():
    """Retorna el inventario indexado por item_id."""
    return {item.item_id: item for item in inventory}

def get_courses_dict():
    """Retorna los cursos indexados por course_id."""
    return {c.course_id: c for c in courses}

def next_reservation_id():
    """Genera el siguiente ID de reserva."""
    if not reservations:
        return "R001"
    last = max(int(r.reservation_id[1:]) for r in reservations)
    return f"R{last + 1:03d}"
