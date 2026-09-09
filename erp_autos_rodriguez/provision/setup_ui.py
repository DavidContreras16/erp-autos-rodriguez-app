"""Crea el Print Format 'Comprobante de Venta' sobre Vehiculo (idempotente).
Ejecutar: bench --site development.localhost execute erp_autos_rodriguez.provision.setup_ui.print_format
"""
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
      <td>{{ frappe.utils.fmt_money(doc.precio_venta or 0, currency="HNL") }}</td></tr>
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
        print("UPDATED Print Format", name)
    else:
        frappe.get_doc({
            "doctype": "Print Format", "name": name, "doc_type": "Vehiculo",
            "module": "AutosRodriguez", "standard": "Yes", "print_format_type": "Jinja",
            "disabled": 0, "html": HTML,
        }).insert(ignore_permissions=True)
        print("CREATED Print Format", name)
    frappe.db.commit()
    print("SETUP_UI_DONE")
