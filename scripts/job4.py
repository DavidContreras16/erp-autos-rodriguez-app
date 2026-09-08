"""Job 4 - Logistica y Aduana.
Ejecutar: cat scripts/job4.py | bench --site development.localhost console

Crea:
- Almacenes canonicos (7) del negocio (prerrequisito para movimientos).
- DocType Movimiento Vehiculo (bitacora de traslados, reemplaza Stock Entry).
- DocType Factura Aduana (reemplaza factura de tramites + Landed Cost Voucher).
- Campos costo_importacion, costo_total, almacen_actual en Vehiculo.
- Transiciones de workflow para logistica (Comprado -> En transito, y rol
  Logistica en las transiciones de traslado; Job 9 hara la matriz fina).
- 3 Server Scripts:
    * Factura Aduana - Calcular Total (Before Save): monto_total = flete + aduana.
    * Factura Aduana - Costo Importacion (After Save): recalcula (idempotente)
      costo_importacion = suma de facturas del vehiculo; costo_total = OC + importacion.
    * Movimiento - Estado y Almacen (After Save): almacen_actual + avance de estado
      con guarda de transicion valida (NO usa apply_workflow).

Plano (sin funciones) porque el console IPython al pipear no respeta closures.
"""
import frappe

MODULE = "AutosRodriguez"

SM_PERMS = {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1,
            "email": 1, "print": 1, "report": 1, "share": 1, "export": 1}
LOG_RWC = {"role": "Logistica", "read": 1, "write": 1, "create": 1, "delete": 0,
           "email": 1, "print": 1, "report": 1, "share": 1, "export": 1}

# ---- 1) Almacenes canonicos (autoname Prompt -> name = nombre) ----
ALMACENES = [
    ("Subasta USA", "Origen"),
    ("En Transito", "Transito"),
    ("Puerto", "Transito"),
    ("Bodega SPS", "Bodega"),
    ("Taller", "Taller"),
    ("Sala de Venta", "Exhibicion"),
    ("En ruta a cliente", "Transito"),
]
for nombre, tipo in ALMACENES:
    if not frappe.db.exists("Almacen", nombre):
        frappe.get_doc({
            "doctype": "Almacen",
            "name": nombre,
            "nombre": nombre,
            "tipo": tipo,
        }).insert(ignore_permissions=True)
        print("CREATED Almacen", nombre)
    else:
        print("SKIP_EXISTS Almacen", nombre)

# ---- 2) DocType Movimiento Vehiculo ----
if not frappe.db.exists("DocType", "Movimiento Vehiculo"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Movimiento Vehiculo",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "MOV-.#####",
        "naming_rule": "Expression",
        "field_order": ["vehiculo", "almacen_origen", "almacen_destino", "fecha",
                        "responsable", "notas"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "vehiculo", "label": "Vehiculo", "fieldtype": "Link",
             "options": "Vehiculo", "reqd": 1, "in_list_view": 1},
            {"fieldname": "almacen_origen", "label": "Almacen Origen", "fieldtype": "Link",
             "options": "Almacen"},
            {"fieldname": "almacen_destino", "label": "Almacen Destino", "fieldtype": "Link",
             "options": "Almacen", "reqd": 1, "in_list_view": 1},
            {"fieldname": "fecha", "label": "Fecha", "fieldtype": "Datetime",
             "default": "now", "reqd": 1, "in_list_view": 1},
            {"fieldname": "responsable", "label": "Responsable", "fieldtype": "Link",
             "options": "User"},
            {"fieldname": "notas", "label": "Notas", "fieldtype": "Small Text"},
        ],
        "permissions": [SM_PERMS, LOG_RWC],
    }).insert()
    print("CREATED Movimiento Vehiculo")
else:
    print("SKIP_EXISTS Movimiento Vehiculo")

# ---- 3) DocType Factura Aduana ----
if not frappe.db.exists("DocType", "Factura Aduana"):
    frappe.get_doc({
        "doctype": "DocType",
        "name": "Factura Aduana",
        "module": MODULE,
        "custom": 0,
        "istable": 0,
        "engine": "InnoDB",
        "autoname": "FA-.#####",
        "naming_rule": "Expression",
        "field_order": ["vehiculo", "proveedor", "numero_factura", "fecha",
                        "monto_flete", "monto_aduana", "monto_total", "documento_adjunto"],
        "sort_field": "creation",
        "sort_order": "DESC",
        "grid_page_length": 50,
        "rows_threshold_for_grid_search": 20,
        "fields": [
            {"fieldname": "vehiculo", "label": "Vehiculo", "fieldtype": "Link",
             "options": "Vehiculo", "reqd": 1, "in_list_view": 1},
            {"fieldname": "proveedor", "label": "Proveedor", "fieldtype": "Link",
             "options": "Proveedor", "in_list_view": 1,
             "link_filters": "[[\"Proveedor\", \"tipo\", \"=\", \"Tramitador Aduanal\"]]"},
            {"fieldname": "numero_factura", "label": "Numero de Factura", "fieldtype": "Data"},
            {"fieldname": "fecha", "label": "Fecha", "fieldtype": "Date", "reqd": 1,
             "in_list_view": 1},
            {"fieldname": "monto_flete", "label": "Monto Flete", "fieldtype": "Currency"},
            {"fieldname": "monto_aduana", "label": "Monto Aduana", "fieldtype": "Currency"},
            {"fieldname": "monto_total", "label": "Monto Total", "fieldtype": "Currency",
             "read_only": 1, "in_list_view": 1},
            {"fieldname": "documento_adjunto", "label": "Documento Adjunto", "fieldtype": "Attach"},
        ],
        "permissions": [SM_PERMS, LOG_RWC],
    }).insert()
    print("CREATED Factura Aduana")
else:
    print("SKIP_EXISTS Factura Aduana")

# ---- 4) Vehiculo: campos costo_importacion, costo_total, almacen_actual ----
veh = frappe.get_doc("DocType", "Vehiculo")
existing_fields = {f.fieldname for f in veh.fields}
NEW_VEH_FIELDS = [
    ("costo_importacion", {"fieldname": "costo_importacion", "label": "Costo Importacion",
                           "fieldtype": "Currency", "read_only": 1, "insert_after": "orden_compra"}),
    ("costo_total", {"fieldname": "costo_total", "label": "Costo Total",
                     "fieldtype": "Currency", "read_only": 1, "insert_after": "costo_importacion"}),
    ("almacen_actual", {"fieldname": "almacen_actual", "label": "Almacen Actual",
                        "fieldtype": "Link", "options": "Almacen", "read_only": 1,
                        "insert_after": "costo_total"}),
]
added_any = False
for fname, fdef in NEW_VEH_FIELDS:
    if fname not in existing_fields:
        veh.append("fields", fdef)
        added_any = True
if added_any:
    veh.save(ignore_permissions=True)
    print("VEHICULO_UPDATED added:", [f for f, _ in NEW_VEH_FIELDS if f not in existing_fields])
else:
    print("VEHICULO_OK (campos ya existen)")

# ---- 5) Workflow: transiciones de logistica ----
if not frappe.db.exists("Workflow Action Master", "Enviar a Transito"):
    frappe.get_doc({
        "doctype": "Workflow Action Master",
        "workflow_action_name": "Enviar a Transito",
    }).insert(ignore_permissions=True)
    print("CREATED Action Master Enviar a Transito")
else:
    print("SKIP_EXISTS Action Master Enviar a Transito")

wf = frappe.get_doc("Workflow", "Flujo Vehiculo")
existing_tr = {(t.state, t.action, t.next_state, t.allowed) for t in wf.transitions}
WF_TRANSITIONS = [
    # Comprado -> En transito: transicion nueva (accion distinta para no chocar con "Continuar")
    ("Comprado", "Enviar a Transito", "En transito", "System Manager"),
    ("Comprado", "Enviar a Transito", "En transito", "Logistica"),
    # Rol Logistica en las transiciones de traslado ya existentes (solo tenian System Manager)
    ("En transito", "Continuar", "En aduana", "Logistica"),
    ("En aduana", "Continuar", "En bodega SPS", "Logistica"),
]
added_tr = 0
for state, action, next_state, allowed in WF_TRANSITIONS:
    if (state, action, next_state, allowed) in existing_tr:
        continue
    wf.append("transitions", {
        "state": state, "action": action, "next_state": next_state,
        "allowed": allowed, "allow_self_approval": 1,
    })
    added_tr += 1
if added_tr:
    wf.save(ignore_permissions=True)
    print("WF_TRANSITIONS_ADDED:", added_tr)
else:
    print("WF_TRANSITIONS_EXISTS")

# ---- 6) Server Script A: Factura Aduana - Calcular Total (Before Save) ----
SS_A = "Factura Aduana - Calcular Total"
SS_A_SCRIPT = (
    "doc.monto_total = (doc.monto_flete or 0) + (doc.monto_aduana or 0)\n"
)
if frappe.db.exists("Server Script", SS_A):
    ss = frappe.get_doc("Server Script", SS_A)
    if ss.script != SS_A_SCRIPT:
        ss.script = SS_A_SCRIPT
        ss.save(ignore_permissions=True)
        print("UPDATED Server Script", SS_A)
    else:
        print("UNCHANGED Server Script", SS_A)
else:
    frappe.get_doc({
        "doctype": "Server Script", "name": SS_A, "module": MODULE, "disabled": 0,
        "script_type": "DocType Event", "reference_doctype": "Factura Aduana",
        "doctype_event": "Before Save", "script": SS_A_SCRIPT,
    }).insert()
    print("CREATED Server Script", SS_A)

# ---- 7) Server Script B: Factura Aduana - Costo Importacion (After Save) ----
SS_B = "Factura Aduana - Costo Importacion"
SS_B_SCRIPT = (
    "facturas = frappe.get_all(\"Factura Aduana\", filters={\"vehiculo\": doc.vehiculo}, fields=[\"monto_total\"])\n"
    "total_aduana = 0\n"
    "for f in facturas:\n"
    "    total_aduana += (f.monto_total or 0)\n"
    "vehiculo = frappe.get_doc(\"Vehiculo\", doc.vehiculo)\n"
    "monto_oc = 0\n"
    "if vehiculo.orden_compra:\n"
    "    monto_oc = frappe.db.get_value(\"Orden de Compra\", vehiculo.orden_compra, \"monto_ofertado\") or 0\n"
    "vehiculo.db_set(\"costo_importacion\", total_aduana)\n"
    "vehiculo.db_set(\"costo_total\", monto_oc + total_aduana)\n"
)
if frappe.db.exists("Server Script", SS_B):
    ss = frappe.get_doc("Server Script", SS_B)
    if ss.script != SS_B_SCRIPT:
        ss.script = SS_B_SCRIPT
        ss.save(ignore_permissions=True)
        print("UPDATED Server Script", SS_B)
    else:
        print("UNCHANGED Server Script", SS_B)
else:
    frappe.get_doc({
        "doctype": "Server Script", "name": SS_B, "module": MODULE, "disabled": 0,
        "script_type": "DocType Event", "reference_doctype": "Factura Aduana",
        "doctype_event": "After Save", "script": SS_B_SCRIPT,
    }).insert()
    print("CREATED Server Script", SS_B)

# ---- 8) Server Script C: Movimiento - Estado y Almacen (After Save) ----
SS_C = "Movimiento - Estado y Almacen"
SS_C_SCRIPT = (
    "desde = None\n"
    "hacia = None\n"
    "if doc.almacen_destino == \"En Transito\":\n"
    "    desde = \"Comprado\"\n"
    "    hacia = \"En transito\"\n"
    "elif doc.almacen_destino == \"Puerto\":\n"
    "    desde = \"En transito\"\n"
    "    hacia = \"En aduana\"\n"
    "elif doc.almacen_destino == \"Bodega SPS\":\n"
    "    desde = \"En aduana\"\n"
    "    hacia = \"En bodega SPS\"\n"
    "if hacia:\n"
    "    vehiculo = frappe.get_doc(\"Vehiculo\", doc.vehiculo)\n"
    "    if vehiculo.estado == desde:\n"
    "        try:\n"
    "            vehiculo.estado = hacia\n"
    "            vehiculo.save()\n"
    "        except Exception as e:\n"
    "            frappe.log_error(str(e), \"Movimiento Estado\")\n"
    "frappe.db.set_value(\"Vehiculo\", doc.vehiculo, \"almacen_actual\", doc.almacen_destino)\n"
)
if frappe.db.exists("Server Script", SS_C):
    ss = frappe.get_doc("Server Script", SS_C)
    if ss.script != SS_C_SCRIPT:
        ss.script = SS_C_SCRIPT
        ss.save(ignore_permissions=True)
        print("UPDATED Server Script", SS_C)
    else:
        print("UNCHANGED Server Script", SS_C)
else:
    frappe.get_doc({
        "doctype": "Server Script", "name": SS_C, "module": MODULE, "disabled": 0,
        "script_type": "DocType Event", "reference_doctype": "Movimiento Vehiculo",
        "doctype_event": "After Save", "script": SS_C_SCRIPT,
    }).insert()
    print("CREATED Server Script", SS_C)

frappe.db.commit()
print("JOB4_DONE")
