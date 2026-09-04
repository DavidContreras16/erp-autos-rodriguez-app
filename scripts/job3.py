"""Job 3 - Modulo de Compras.
Ejecutar: cat scripts/job3.py | bench --site development.localhost console
Crea: Action Masters de subasta, 4 transiciones en workflow, DocTypes
Orden de Compra + Pago Compra, campo orden_compra en Vehiculo (y elimina el
campo project huerfano cuyo doctype ya no existe), Server Script para
estado_subasta (Ganada -> Comprado, Perdida -> Cancelado).
Plano (sin funciones) porque el console IPython al pipear no respeta closures.
"""
import frappe

MODULE = "AutosRodriguez"

SM_PERMS = {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1,
            "email": 1, "print": 1, "report": 1, "share": 1, "export": 1}
RW_PERMS = {"role": "Compras", "read": 1, "write": 1, "create": 1, "delete": 0,
            "email": 1, "print": 1, "report": 1, "share": 1, "export": 1}
R_PERMS = {"role": "Logistica", "read": 1, "write": 0, "create": 0, "delete": 0,
           "email": 1, "print": 1, "report": 1, "share": 1, "export": 1}

# ---- 1) Workflow Action Masters para las nuevas acciones ----
for am_name in ("Subasta Ganada", "Subasta Perdida"):
    if not frappe.db.exists("Workflow Action Master", am_name):
        frappe.get_doc({
            "doctype": "Workflow Action Master",
            "workflow_action_name": am_name,
        }).insert(ignore_permissions=True)
        print("CREATED Action Master", am_name)
    else:
        print("SKIP_EXISTS Action Master", am_name)

# ---- 2) Transiciones de subasta en el workflow ----
wf = frappe.get_doc("Workflow", "Flujo Vehiculo")
WF_TRANSITIONS = [
    ("Solicitado", "Subasta Ganada", "Comprado"),
    ("En subasta", "Subasta Ganada", "Comprado"),
    ("Solicitado", "Subasta Perdida", "Cancelado"),
    ("En subasta", "Subasta Perdida", "Cancelado"),
]
existing = {(t.state, t.action, t.next_state) for t in wf.transitions}
added = 0
for state, action, next_state in WF_TRANSITIONS:
    if (state, action, next_state) in existing:
        continue
    for allowed in ("System Manager", "Compras"):
        wf.append("transitions", {
            "state": state,
            "action": action,
            "next_state": next_state,
            "allowed": allowed,
            "allow_self_approval": 1,
        })
        added += 1
if added:
    wf.save(ignore_permissions=True)
    print("WF_TRANSITIONS_ADDED:", added)
else:
    print("WF_TRANSITIONS_EXISTS")

# ---- 3) DocType Orden de Compra ----
if not frappe.db.exists("DocType", "Orden de Compra"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Orden de Compra",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "OC-.#####",
        "naming_rule": "Expression",
        "field_order": ["vehiculo", "proveedor", "fecha", "monto_ofertado", "moneda",
                        "estado_subasta", "notas"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "vehiculo", "label": "Vehiculo", "fieldtype": "Link",
             "options": "Vehiculo", "reqd": 1, "in_list_view": 1},
            {"fieldname": "proveedor", "label": "Proveedor", "fieldtype": "Link",
             "options": "Proveedor", "reqd": 1, "in_list_view": 1,
             "link_filters": "[[\"Proveedor\", \"tipo\", \"=\", \"Casa de Subasta\"]]"},
            {"fieldname": "fecha", "label": "Fecha", "fieldtype": "Date", "reqd": 1,
             "in_list_view": 1},
            {"fieldname": "monto_ofertado", "label": "Monto Ofertado", "fieldtype": "Currency",
             "reqd": 1},
            {"fieldname": "moneda", "label": "Moneda", "fieldtype": "Select",
             "options": "USD\nHNL", "default": "USD"},
            {"fieldname": "estado_subasta", "label": "Estado Subasta", "fieldtype": "Select",
             "options": "Pendiente\nGanada\nPerdida", "default": "Pendiente", "in_list_view": 1},
            {"fieldname": "notas", "label": "Notas", "fieldtype": "Small Text"},
        ],
        "permissions": [SM_PERMS, RW_PERMS, R_PERMS],
    }).insert()
    print("CREATED Orden de Compra")
else:
    print("SKIP_EXISTS Orden de Compra")

# ---- 4) DocType Pago Compra ----
if not frappe.db.exists("DocType", "Pago Compra"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Pago Compra",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "PC-.#####",
        "naming_rule": "Expression",
        "field_order": ["orden_compra", "fecha_pago", "monto", "metodo_pago", "referencia",
                        "comprobante"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "orden_compra", "label": "Orden de Compra", "fieldtype": "Link",
             "options": "Orden de Compra", "reqd": 1, "in_list_view": 1},
            {"fieldname": "fecha_pago", "label": "Fecha de Pago", "fieldtype": "Date", "reqd": 1,
             "in_list_view": 1},
            {"fieldname": "monto", "label": "Monto", "fieldtype": "Currency", "reqd": 1},
            {"fieldname": "metodo_pago", "label": "Metodo de Pago", "fieldtype": "Select",
             "options": "Transferencia\nTarjeta\nCheque"},
            {"fieldname": "referencia", "label": "Referencia", "fieldtype": "Data"},
            {"fieldname": "comprobante", "label": "Comprobante", "fieldtype": "Attach"},
        ],
        "permissions": [SM_PERMS, RW_PERMS],
    }).insert()
    print("CREATED Pago Compra")
else:
    print("SKIP_EXISTS Pago Compra")

# ---- 5) Vehiculo: quitar project huerfano + agregar orden_compra ----
veh = frappe.get_doc("DocType", "Vehiculo")
removed_project = False
for f in list(veh.fields):
    if f.fieldname == "project":
        veh.remove(f)
        removed_project = True
added_oc = False
if not any(f.fieldname == "orden_compra" for f in veh.fields):
    veh.append("fields", {
        "fieldname": "orden_compra",
        "label": "Orden de Compra",
        "fieldtype": "Link",
        "options": "Orden de Compra",
        "insert_after": "estado",
    })
    added_oc = True
if removed_project or added_oc:
    veh.save(ignore_permissions=True)
    print("VEHICULO_UPDATED removed_project:", removed_project,
          "added_orden_compra:", added_oc)
else:
    print("VEHICULO_OK")

# ---- 6) Server Script: estado subasta -> estado de Vehiculo ----
SS_NAME = "OC - Estado Subasta a Vehiculo"
SS_SCRIPT = (
    "if doc.estado_subasta in (\"Ganada\", \"Perdida\"):\n"
    "    vehiculo = frappe.get_doc(\"Vehiculo\", doc.vehiculo)\n"
    "    if doc.estado_subasta == \"Ganada\":\n"
    "        if vehiculo.estado != \"Comprado\":\n"
    "            vehiculo.estado = \"Comprado\"\n"
    "            vehiculo.save()\n"
    "        if vehiculo.orden_compra != doc.name:\n"
    "            vehiculo.db_set(\"orden_compra\", doc.name)\n"
    "    elif doc.estado_subasta == \"Perdida\":\n"
    "        if vehiculo.estado != \"Cancelado\":\n"
    "            vehiculo.estado = \"Cancelado\"\n"
    "            vehiculo.save()\n"
)
if frappe.db.exists("Server Script", SS_NAME):
    ss = frappe.get_doc("Server Script", SS_NAME)
    if ss.script != SS_SCRIPT:
        ss.script = SS_SCRIPT
        ss.save(ignore_permissions=True)
        print("UPDATED Server Script", SS_NAME)
    else:
        print("UNCHANGED Server Script", SS_NAME)
else:
    frappe.get_doc({
        "doctype": "Server Script",
        "name": SS_NAME,
        "module": MODULE,
        "disabled": 0,
        "script_type": "DocType Event",
        "reference_doctype": "Orden de Compra",
        "doctype_event": "After Save",
        "script": SS_SCRIPT,
    }).insert()
    print("CREATED Server Script", SS_NAME)

frappe.db.commit()
print("JOB3_DONE")