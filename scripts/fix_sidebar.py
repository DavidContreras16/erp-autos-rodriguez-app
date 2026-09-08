"""Restaura el Workspace Sidebar del modulo (borrado por migrate) con el name
EXACTO 'AutosRodriguez' (== Module Def) para que el fork NO autogenere el
sidebar recortado de 3 doctypes (Vehiculo/Proveedor/Cliente). Incluye los 7
modulos de antes + los 2 nuevos del Job 4, agrega shortcuts al Workspace e
invalida caches.

autoname del doctype = field:title  => name = title. Por eso se crea con
title='AutosRodriguez' (name resultante='AutosRodriguez') y luego se ajusta el
title visible a 'Autos Rodriguez' con db_set (el name no cambia).

Ejecutar: echo "exec(open('.../scripts/fix_sidebar.py').read())" | bench console
"""
import frappe

SIDEBAR_ITEMS = [
    ("Autos Rodriguez", "Autos Rodriguez", "Workspace", "car"),
    ("Vehiculos", "Vehiculo", "DocType", "truck"),
    ("Ordenes de Compra", "Orden de Compra", "DocType", "shopping-cart"),
    ("Pagos de Compra", "Pago Compra", "DocType", "credit-card"),
    ("Proveedores", "Proveedor", "DocType", "briefcase"),
    ("Clientes", "Cliente", "DocType", "users"),
    ("Almacenes", "Almacen", "DocType", "box"),
    ("Repuestos", "Repuesto", "DocType", "wrench"),
    ("Movimientos", "Movimiento Vehiculo", "DocType", "map-pin"),
    ("Facturas de Aduana", "Factura Aduana", "DocType", "file-text"),
]

items = []
for label, link_to, link_type, icon in SIDEBAR_ITEMS:
    items.append({
        "child": 0, "collapsible": 1, "icon": icon, "indent": 0,
        "keep_closed": 0, "label": label, "link_to": link_to,
        "link_type": link_type, "show_arrow": 0, "type": "Link",
    })

# limpiar registros previos (el mio mal nombrado y cualquier resto)
for nm in ("Autos Rodriguez", "AutosRodriguez"):
    if frappe.db.exists("Workspace Sidebar", nm):
        frappe.delete_doc("Workspace Sidebar", nm, force=1, ignore_permissions=True)
        print("DELETED", nm)

sb = frappe.get_doc({
    "doctype": "Workspace Sidebar",
    "title": "AutosRodriguez",   # -> name = 'AutosRodriguez'
    "app": "erp_autos_rodriguez",
    "module": "AutosRodriguez",
    "header_icon": "hammer",
    "standard": 1,
    "items": items,
})
sb.insert(ignore_permissions=True)
print("CREATED sidebar name=", sb.name, "items=", len(sb.items))

# titulo visible con espacio (name se mantiene 'AutosRodriguez')
frappe.db.set_value("Workspace Sidebar", "AutosRodriguez", "title", "Autos Rodriguez")

# shortcuts nuevos en el Workspace
ws = frappe.get_doc("Workspace", "Autos Rodriguez")
existing_sc = {s.link_to for s in ws.shortcuts}
added = 0
for label, link_to, icon in (("Movimientos", "Movimiento Vehiculo", "map-pin"),
                              ("Facturas de Aduana", "Factura Aduana", "file-text")):
    if link_to not in existing_sc:
        ws.append("shortcuts", {"doc_view": "", "icon": icon, "label": label,
                                "link_to": link_to, "type": "DocType"})
        added += 1
if added:
    ws.save(ignore_permissions=True)
print("WORKSPACE_SHORTCUTS_ADDED:", added)

# invalidar caches (auto_generate usa site_cache; el sidebar usa cache por-usuario)
for key in ("desktop_icons", "bootinfo", "user_perm_can_read", "user_allowed_modules"):
    frappe.cache.delete_keys(key)
frappe.clear_cache()
print("CACHE_CLEARED")

frappe.db.commit()
print("FIX_SIDEBAR_DONE")
