"""UI del modelo contenido: Print Format, vista Kanban por defecto,
Number Cards / Charts y pagina de inicio (Workspace).

Ejecutar:
  bench --site development.localhost execute erp_autos_rodriguez.provision.setup_ui.all
"""
import json
import frappe

HTML = """
<div style="text-align:center; margin-bottom:12px;">
  <h2 style="margin:0;">Autos Rodriguez</h2>
  <div style="font-size:14px; letter-spacing:2px;">COMPROBANTE DE VENTA</div>
</div>
<hr>
<table class="table" style="width:100%; margin-bottom:10px;">
  <tr><td style="width:35%;"><b>Vehiculo</b></td>
      <td>{{ doc.marca or "" }} {{ doc.modelo or "" }} {{ doc.anio or "" }}</td></tr>
  <tr><td><b>VIN</b></td><td>{{ doc.vin or "" }}</td></tr>
  <tr><td><b>Estado</b></td><td>{{ doc.estado or "" }}</td></tr>
</table>
<table class="table table-bordered" style="width:100%;">
  <tr><td style="width:35%;"><b>Cliente</b></td><td>{{ doc.cliente or "" }}</td></tr>
  <tr><td><b>Precio de Venta</b></td>
      <td>L {{ "%.2f"|format(doc.precio_venta or 0) }}</td></tr>
  <tr><td><b>Forma de Pago</b></td><td>{{ doc.forma_pago or "" }}</td></tr>
  {% if doc.forma_pago == "Financiado" %}
  <tr><td><b>Financiera</b></td><td>{{ doc.financiera or "" }}</td></tr>
  <tr><td><b>Estado del Credito</b></td><td>{{ doc.estado_credito or "" }}</td></tr>
  {% endif %}
  <tr><td><b>Pagado</b></td><td>{{ "Si" if doc.pagado else "No" }}</td></tr>
  <tr><td><b>Fecha de Entrega</b></td><td>{{ doc.fecha_entrega or "" }}</td></tr>
  <tr><td><b>Recibido por</b></td><td>{{ doc.recibido_por or "" }}</td></tr>
</table>
<br><br>
<table style="width:100%;"><tr>
  <td style="text-align:center; border-top:1px solid #000; width:45%;">Entrega</td>
  <td style="width:10%;"></td>
  <td style="text-align:center; border-top:1px solid #000; width:45%;">Recibe</td>
</tr></table>
"""


def print_format():
    name = "Comprobante de Venta"
    if frappe.db.exists("Print Format", name):
        pf = frappe.get_doc("Print Format", name)
        pf.html = HTML
        pf.save(ignore_permissions=True)
    else:
        frappe.get_doc({
            "doctype": "Print Format", "name": name, "doc_type": "Vehiculo",
            "module": "AutosRodriguez", "standard": "Yes", "print_format_type": "Jinja",
            "disabled": 0, "html": HTML,
        }).insert(ignore_permissions=True)
    print("PRINT_FORMAT ok")


def kanban_default():
    # vista por defecto del doctype (via doc.save para exportar a disco en dev mode)
    d = frappe.get_doc("DocType", "Vehiculo")
    if d.default_view != "Kanban":
        d.default_view = "Kanban"
        d.save(ignore_permissions=True)
    print("KANBAN_DEFAULT set")


def _upsert_number_card(name, function, filters, based_on=None, label=None):
    data = {
        "doctype": "Number Card", "name": name, "label": label or name,
        "type": "Document Type", "document_type": "Vehiculo", "function": function,
        "aggregate_function_based_on": based_on, "is_public": 1, "currency": "HNL",
        "filters_json": json.dumps(filters),
    }
    if frappe.db.exists("Number Card", name):
        doc = frappe.get_doc("Number Card", name)
        doc.update(data)
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc(data).insert(ignore_permissions=True)


def _upsert_chart_sales():
    name = "Ventas por Mes"
    data = {
        "doctype": "Dashboard Chart", "name": name, "chart_name": name,
        "chart_type": "Sum", "document_type": "Vehiculo", "based_on": "fecha_entrega",
        "value_based_on": "precio_venta", "timeseries": 1, "time_interval": "Monthly",
        "timespan": "Last Year", "type": "Bar", "is_public": 1, "currency": "HNL",
        "filters_json": json.dumps([["Vehiculo", "estado", "=", "Vendido"]]),
    }
    if frappe.db.exists("Dashboard Chart", name):
        doc = frappe.get_doc("Dashboard Chart", name)
        doc.update(data)
        doc.save(ignore_permissions=True)
    else:
        frappe.get_doc(data).insert(ignore_permissions=True)


def stats():
    _upsert_number_card("Vehiculos en Inventario", "Count",
                        [["Vehiculo", "estado", "not in", "Vendido,Cancelado"]])
    _upsert_number_card("Vehiculos Vendidos", "Count",
                        [["Vehiculo", "estado", "=", "Vendido"]])
    _upsert_number_card("Inversion en Inventario", "Sum",
                        [["Vehiculo", "estado", "not in", "Vendido,Cancelado"]],
                        based_on="costo_total")
    _upsert_number_card("Valor de Ventas", "Sum",
                        [["Vehiculo", "estado", "=", "Vendido"]], based_on="precio_venta")
    _upsert_chart_sales()
    print("STATS ok")


def home():
    stats()
    ws = frappe.get_doc("Workspace", "Autos Rodriguez")
    ws.number_cards = []
    for nc in ("Vehiculos en Inventario", "Vehiculos Vendidos", "Inversion en Inventario",
               "Valor de Ventas", "Total Vehiculos"):
        ws.append("number_cards", {"number_card_name": nc, "label": nc})
    ws.charts = []
    for ch in ("Vehiculos por Estado", "Ventas por Mes"):
        ws.append("charts", {"chart_name": ch, "label": ch})
    # shortcut Vehiculos abre el Kanban
    ws.shortcuts = []
    ws.append("shortcuts", {"type": "DocType", "link_to": "Vehiculo", "label": "Vehiculos",
                            "icon": "truck", "doc_view": "Kanban", "kanban_board": "Vehiculos - Flujo",
                            "color": "Blue"})
    for label, link_to, icon in (("Proveedores", "Proveedor", "briefcase"),
                                 ("Clientes", "Cliente", "users"),
                                 ("Almacenes", "Almacen", "box"),
                                 ("Repuestos", "Repuesto", "wrench")):
        ws.append("shortcuts", {"type": "DocType", "link_to": link_to, "label": label,
                                "icon": icon, "doc_view": ""})

    def blk(t, d):
        return {"id": t + "_" + str(d.get("_i", "")), "type": t.split("#")[0], "data": d}

    content = [
        {"id": "hd1", "type": "header", "data": {"text": "<span class=\"h4\"><b>Panel Autos Rodriguez</b></span>", "col": 12}},
        {"id": "ncA", "type": "number_card", "data": {"number_card_name": "Vehiculos en Inventario", "col": 3}},
        {"id": "ncB", "type": "number_card", "data": {"number_card_name": "Vehiculos Vendidos", "col": 3}},
        {"id": "ncC", "type": "number_card", "data": {"number_card_name": "Inversion en Inventario", "col": 3}},
        {"id": "ncD", "type": "number_card", "data": {"number_card_name": "Valor de Ventas", "col": 3}},
        {"id": "chA", "type": "chart", "data": {"chart_name": "Vehiculos por Estado", "col": 6}},
        {"id": "chB", "type": "chart", "data": {"chart_name": "Ventas por Mes", "col": 6}},
        {"id": "hd2", "type": "header", "data": {"text": "<span class=\"h5\"><b>Accesos rapidos</b></span>", "col": 12}},
        {"id": "scA", "type": "shortcut", "data": {"shortcut_name": "Vehiculos", "col": 3}},
        {"id": "scB", "type": "shortcut", "data": {"shortcut_name": "Proveedores", "col": 3}},
        {"id": "scC", "type": "shortcut", "data": {"shortcut_name": "Clientes", "col": 3}},
        {"id": "scD", "type": "shortcut", "data": {"shortcut_name": "Almacenes", "col": 3}},
    ]
    ws.content = json.dumps(content)
    ws.save(ignore_permissions=True)
    print("HOME ok cards=", len(ws.number_cards), "charts=", len(ws.charts), "shortcuts=", len(ws.shortcuts))


def all():
    print_format()
    kanban_default()
    home()
    frappe.db.commit()
    print("SETUP_UI_DONE")
