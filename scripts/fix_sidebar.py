"""Sidebar/Workspace del modelo contenido: solo Vehiculos + catalogos.
Recrea el Workspace Sidebar 'AutosRodriguez' (name == modulo, para que el fork
no autogenere el recortado) e invalida caches.
Ejecutar: echo "exec(open('.../scripts/fix_sidebar.py').read())" | bench console
"""
import frappe

SIDEBAR_ITEMS = [
    ("Autos Rodriguez", "Autos Rodriguez", "Workspace", "car"),
    ("Vehiculos", "Vehiculo", "DocType", "truck"),
    ("Proveedores", "Proveedor", "DocType", "briefcase"),
    ("Clientes", "Cliente", "DocType", "users"),
    ("Almacenes", "Almacen", "DocType", "box"),
    ("Repuestos", "Repuesto", "DocType", "wrench"),
]
SHORTCUTS = [
    ("Vehiculos", "Vehiculo", "truck"),
    ("Proveedores", "Proveedor", "briefcase"),
    ("Clientes", "Cliente", "users"),
    ("Almacenes", "Almacen", "box"),
    ("Repuestos", "Repuesto", "wrench"),
]

items = []
for label, link_to, link_type, icon in SIDEBAR_ITEMS:
    items.append({"child": 0, "collapsible": 1, "icon": icon, "indent": 0, "keep_closed": 0,
                  "label": label, "link_to": link_to, "link_type": link_type,
                  "show_arrow": 0, "type": "Link"})

for nm in ("Autos Rodriguez", "AutosRodriguez"):
    if frappe.db.exists("Workspace Sidebar", nm):
        frappe.delete_doc("Workspace Sidebar", nm, force=1, ignore_permissions=True)

sb = frappe.get_doc({"doctype": "Workspace Sidebar", "title": "AutosRodriguez",
                     "app": "erp_autos_rodriguez", "module": "AutosRodriguez",
                     "header_icon": "hammer", "standard": 1, "items": items})
sb.insert(ignore_permissions=True)
frappe.db.set_value("Workspace Sidebar", "AutosRodriguez", "title", "Autos Rodriguez")
print("SIDEBAR ok items=", len(sb.items))

ws = frappe.get_doc("Workspace", "Autos Rodriguez")
ws.set("shortcuts", [])
for label, link_to, icon in SHORTCUTS:
    ws.append("shortcuts", {"doc_view": "", "icon": icon, "label": label,
                            "link_to": link_to, "type": "DocType"})
ws.save(ignore_permissions=True)
print("WORKSPACE shortcuts=", len(ws.shortcuts))

for key in ("desktop_icons", "bootinfo", "user_perm_can_read", "user_allowed_modules"):
    frappe.cache.delete_keys(key)
frappe.clear_cache()
frappe.db.commit()
print("FIX_SIDEBAR_DONE")
