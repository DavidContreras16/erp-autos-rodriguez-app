"""Job 2 - Catalogo de doctypes maestros.
Ejecutar: cat scripts/job2.py | bench --site development.localhost console
Crea: Proveedor, Cliente, Almacen, Repuesto (modulo AutosRodriguez).
Plano (sin funciones) porque el console IPython al pipear no respeta closures.
"""
import frappe

MODULE = "AutosRodriguez"
READ_ROLES = ["Compras", "Logistica", "Taller", "Control de Calidad", "Ventas"]
FULL_PERMS = {
    "role": "System Manager",
    "read": 1, "write": 1, "create": 1, "delete": 1,
    "submit": 0, "cancel": 0, "amend": 0,
    "email": 1, "print": 1, "report": 1, "share": 1, "export": 1,
}

# ---- Proveedor ----
if not frappe.db.exists("DocType", "Proveedor"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Proveedor",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "Prompt",
        "naming_rule": "",
        "title_field": "nombre",
        "field_order": ["nombre", "tipo", "cb_contacto", "contacto", "telefono", "email", "sb_notas", "notas"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "nombre", "label": "Nombre", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "tipo", "label": "Tipo", "fieldtype": "Select",
             "options": "Casa de Subasta\nTramitador Aduanal\nTaller Externo\nRepuestos\nFinanciera\nOtro",
             "in_list_view": 1},
            {"fieldname": "cb_contacto", "fieldtype": "Column Break"},
            {"fieldname": "contacto", "label": "Contacto", "fieldtype": "Data"},
            {"fieldname": "telefono", "label": "Telefono", "fieldtype": "Data"},
            {"fieldname": "email", "label": "Email", "fieldtype": "Data"},
            {"fieldname": "sb_notas", "fieldtype": "Section Break", "collapsible": 1, "label": "Notas"},
            {"fieldname": "notas", "label": "Notas", "fieldtype": "Small Text"},
        ],
        "permissions": [FULL_PERMS] + [{"role": r, "read": 1} for r in READ_ROLES],
    }).insert()
    print("CREATED Proveedor")
else:
    print("SKIP_EXISTS Proveedor")

# ---- Cliente ----
if not frappe.db.exists("DocType", "Cliente"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Cliente",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "Prompt",
        "naming_rule": "",
        "title_field": "nombre_completo",
        "field_order": ["nombre_completo", "tipo_identificacion", "numero_identificacion", "cb_contacto", "telefono", "email", "sb_direccion", "direccion", "departamento"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "nombre_completo", "label": "Nombre Completo", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "tipo_identificacion", "label": "Tipo de Identificacion", "fieldtype": "Select", "options": "DNI\nPasaporte\nRTN"},
            {"fieldname": "numero_identificacion", "label": "Numero de Identificacion", "fieldtype": "Data"},
            {"fieldname": "cb_contacto", "fieldtype": "Column Break"},
            {"fieldname": "telefono", "label": "Telefono", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "email", "label": "Email", "fieldtype": "Data"},
            {"fieldname": "sb_direccion", "fieldtype": "Section Break", "label": "Direccion"},
            {"fieldname": "direccion", "label": "Direccion", "fieldtype": "Small Text"},
            {"fieldname": "departamento", "label": "Departamento", "fieldtype": "Data"},
        ],
        "permissions": [FULL_PERMS] + [{"role": r, "read": 1} for r in READ_ROLES],
    }).insert()
    print("CREATED Cliente")
else:
    print("SKIP_EXISTS Cliente")

# ---- Almacen ----
if not frappe.db.exists("DocType", "Almacen"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Almacen",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "Prompt",
        "naming_rule": "",
        "title_field": "nombre",
        "field_order": ["nombre", "tipo", "sb_direccion", "direccion"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "nombre", "label": "Nombre", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "tipo", "label": "Tipo", "fieldtype": "Select",
             "options": "Origen\nTransito\nBodega\nTaller\nExhibicion",
             "in_list_view": 1},
            {"fieldname": "sb_direccion", "fieldtype": "Section Break", "label": "Direccion"},
            {"fieldname": "direccion", "label": "Direccion", "fieldtype": "Small Text"},
        ],
        "permissions": [FULL_PERMS] + [{"role": r, "read": 1} for r in READ_ROLES],
    }).insert()
    print("CREATED Almacen")
else:
    print("SKIP_EXISTS Almacen")

# ---- Repuesto ----
if not frappe.db.exists("DocType", "Repuesto"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Repuesto",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "field:codigo",
        "naming_rule": "By fieldname",
        "title_field": "nombre",
        "field_order": ["codigo", "nombre", "categoria", "unidad_medida", "cb_costos", "costo_referencia", "stock_actual"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "codigo", "label": "Codigo", "fieldtype": "Data", "reqd": 1, "in_list_view": 1, "unique": 1},
            {"fieldname": "nombre", "label": "Nombre", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "categoria", "label": "Categoria", "fieldtype": "Select", "options": "Mecanica\nElectrica\nCarroceria\nOtro"},
            {"fieldname": "unidad_medida", "label": "Unidad de Medida", "fieldtype": "Select", "options": "Unidad\nPar\nJuego"},
            {"fieldname": "cb_costos", "fieldtype": "Column Break"},
            {"fieldname": "costo_referencia", "label": "Costo de Referencia", "fieldtype": "Currency"},
            {"fieldname": "stock_actual", "label": "Stock Actual", "fieldtype": "Int", "read_only": 1},
        ],
        "permissions": [FULL_PERMS] + [{"role": r, "read": 1} for r in READ_ROLES],
    }).insert()
    print("CREATED Repuesto")
else:
    print("SKIP_EXISTS Repuesto")

frappe.db.commit()
print("JOB2_DONE")