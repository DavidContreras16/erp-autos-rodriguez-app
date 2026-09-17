"""Seed demo idempotente para el modelo contenido (Vehiculo como unico doctype).

Ejecutar: bench --site development.localhost execute erp_autos_rodriguez.provision.seed_demo.seed

Siembra catalogos (Proveedor, Almacen, Cliente) y una flota de vehiculos con sus
apartados llenos segun el estado (Compra / Aduana / Taller / Venta). Los repuestos
se registran como texto libre en la tabla del apartado Taller (sin catalogo).
Idempotente: upsert por VIN y por clave de catalogo.
"""
import frappe

# ---------- catalogos ----------
PROVEEDORES = [
    ("Copart Central America", "Casa de Subasta"),
    ("Manheim Honduras", "Casa de Subasta"),
    ("Aduanera del Norte", "Tramitador Aduanal"),
    ("Taller Marbella", "Taller Externo"),
    ("Banco Atlantida", "Financiera"),
]
ALMACENES = [
    ("Subasta USA", "Origen"), ("En Transito", "Transito"), ("Puerto", "Transito"),
    ("Bodega SPS", "Bodega"), ("Taller", "Taller"), ("Sala de Venta", "Exhibicion"),
]
CLIENTES = [
    ("Juan Perez", "DNI", "0801199012345", "9988-7766", "Tegucigalpa", "Francisco Morazan"),
    ("Maria Lopez", "RTN", "08011990123450", "9911-2233", "San Pedro Sula", "Cortes"),
    ("Carlos Mejia", "DNI", "0501198854321", "9955-4433", "La Ceiba", "Atlantida"),
]

# ---------- flota ----------
# cada vehiculo: dict con basicos + campos de etapa segun avance
VEHICULOS = [
    {"vin": "1HGCM82633A123456", "marca": "Toyota", "modelo": "Corolla", "anio": 2019,
     "casa_subasta": "Copart Central America", "estado": "En subasta",
     "proveedor_compra": "Copart Central America", "monto_ofertado": 6500, "estado_subasta": "Pendiente"},

    {"vin": "4T1B11HK5KU987654", "marca": "Toyota", "modelo": "RAV4", "anio": 2020,
     "casa_subasta": "Manheim Honduras", "estado": "Solicitado"},

    {"vin": "2T1BURHE0JC123457", "marca": "Honda", "modelo": "Civic", "anio": 2020,
     "casa_subasta": "Copart Central America", "estado": "Comprado",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2026-01-10",
     "monto_ofertado": 5400, "estado_subasta": "Ganada",
     "pagos": [{"fecha_pago": "2026-01-11", "monto": 5400, "metodo_pago": "Transferencia", "referencia": "SWIFT-88231"}]},

    {"vin": "1FTFW1ET5DFC12345", "marca": "Ford", "modelo": "F-150", "anio": 2018,
     "casa_subasta": "Manheim Honduras", "estado": "En transito",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2026-01-15", "eta_llegada": "2026-09-02",
     "numero_contenedor": "MSKU7788990", "almacen_actual": "En Transito",
     "monto_ofertado": 14800, "estado_subasta": "Ganada",
     "pagos": [{"fecha_pago": "2026-01-16", "monto": 14800, "metodo_pago": "Transferencia", "referencia": "SWIFT-88232"}]},

    {"vin": "1HGCV1F34LA012345", "marca": "Honda", "modelo": "Accord", "anio": 2021,
     "casa_subasta": "Copart Central America", "estado": "En aduana",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2026-01-05", "almacen_actual": "Puerto",
     "monto_ofertado": 9000, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-2345", "fecha_aduana": "2026-02-11",
     "monto_flete": 500, "monto_aduana": 1250,
     "pagos": [{"fecha_pago": "2026-01-06", "monto": 9000, "metodo_pago": "Transferencia", "referencia": "SWIFT-88233"}]},

    {"vin": "5NPE24AF4FH123459", "marca": "Hyundai", "modelo": "Sonata", "anio": 2019,
     "casa_subasta": "Manheim Honduras", "estado": "En bodega SPS",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2026-01-08", "almacen_actual": "Bodega SPS",
     "monto_ofertado": 6800, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3459", "fecha_aduana": "2026-02-13",
     "monto_flete": 600, "monto_aduana": 1400,
     "pagos": [{"fecha_pago": "2026-01-09", "monto": 6800, "metodo_pago": "Cheque", "referencia": "CHQ-101"}]},

    {"vin": "1G1ZE5ST8HF123461", "marca": "Chevrolet", "modelo": "Malibu", "anio": 2017,
     "casa_subasta": "Copart Central America", "estado": "En reparacion",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2025-12-20", "almacen_actual": "Taller",
     "monto_ofertado": 5200, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3461", "fecha_aduana": "2026-01-18",
     "monto_flete": 520, "monto_aduana": 1280,
     "fecha_ingreso_taller": "2026-02-01", "tipo_reparacion": "Mecanica", "estado_taller": "En proceso",
     "descripcion_problema": "Cambio de frenos y bateria",
     "repuestos": [{"repuesto": "Pastillas de freno", "cantidad": 1, "costo": 45},
                   {"repuesto": "Bateria 12V", "cantidad": 1, "costo": 120}],
     "pagos": [{"fecha_pago": "2025-12-21", "monto": 5200, "metodo_pago": "Transferencia", "referencia": "SWIFT-88234"}]},

    {"vin": "3VWD17AJ8KM654321", "marca": "Volkswagen", "modelo": "Jetta", "anio": 2019,
     "casa_subasta": "Manheim Honduras", "estado": "Vendido",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2025-12-10", "almacen_actual": "Sala de Venta",
     "monto_ofertado": 7000, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-4321", "fecha_aduana": "2026-01-25",
     "monto_flete": 530, "monto_aduana": 1320,
     "fecha_ingreso_taller": "2026-01-05", "estado_taller": "Finalizada", "resultado_inspeccion": "Aprobado",
     "observaciones_calidad": "Vehiculo en excelente estado",
     "checklist": [{"item": "Frenos", "cumple": 1}, {"item": "Luces", "cumple": 1}, {"item": "Motor", "cumple": 1}],
     "cliente": "Carlos Mejia", "precio_venta": 12500, "forma_pago": "Contado",
     "pagado": 1, "fecha_entrega": "2026-03-05", "recibido_por": "Carlos Mejia",
     "cotizaciones": [{"cliente": "Carlos Mejia", "fecha": "2026-02-20", "precio_ofertado": 12500,
                       "forma_pago": "Contado", "estado": "Aceptada"}],
     "pagos": [{"fecha_pago": "2025-12-11", "monto": 7000, "metodo_pago": "Transferencia", "referencia": "SWIFT-88235"}]},

    {"vin": "5YFBURHE1FP123463", "marca": "Toyota", "modelo": "Corolla", "anio": 2018,
     "casa_subasta": "Copart Central America", "estado": "Vendido",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2025-11-15", "almacen_actual": "Sala de Venta",
     "monto_ofertado": 6000, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3463", "fecha_aduana": "2026-01-22",
     "monto_flete": 500, "monto_aduana": 1350, "resultado_inspeccion": "Aprobado",
     "cliente": "Juan Perez", "precio_venta": 11500, "forma_pago": "Financiado",
     "financiera": "Banco Atlantida", "estado_credito": "Aprobado",
     "pagado": 1, "fecha_entrega": "2026-03-10", "recibido_por": "Juan Perez",
     "cotizaciones": [{"cliente": "Juan Perez", "fecha": "2026-03-01", "precio_ofertado": 11500,
                       "forma_pago": "Financiado", "estado": "Aceptada"}],
     "pagos": [{"fecha_pago": "2025-11-16", "monto": 6000, "metodo_pago": "Transferencia", "referencia": "SWIFT-88236"}]},

    {"vin": "1N4AL3AP8JC123464", "marca": "Nissan", "modelo": "Altima", "anio": 2019,
     "casa_subasta": "Manheim Honduras", "estado": "Vendido",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2025-10-10", "almacen_actual": "Sala de Venta",
     "monto_ofertado": 7200, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3464", "fecha_aduana": "2025-12-30",
     "monto_flete": 500, "monto_aduana": 1200, "resultado_inspeccion": "Aprobado",
     "cliente": "Maria Lopez", "precio_venta": 12800, "forma_pago": "Financiado",
     "financiera": "Banco Atlantida", "estado_credito": "Aprobado", "pagado": 1,
     "fecha_entrega": "2026-02-15", "recibido_por": "Maria Lopez",
     "cotizaciones": [{"cliente": "Maria Lopez", "fecha": "2026-01-20", "precio_ofertado": 12800,
                       "forma_pago": "Financiado", "estado": "Aceptada"}],
     "pagos": [{"fecha_pago": "2025-10-11", "monto": 7200, "metodo_pago": "Transferencia", "referencia": "SWIFT-88237"}]},

    # ---- resto de la flota (datos completos segun etapa) ----
    {"vin": "3FADP4EJ5DM123458", "marca": "Ford", "modelo": "Fusion", "anio": 2013,
     "casa_subasta": "Copart Central America", "estado": "En subasta",
     "proveedor_compra": "Copart Central America", "monto_ofertado": 4800, "estado_subasta": "Pendiente"},

    {"vin": "2C3CDXBG9MH123456", "marca": "Dodge", "modelo": "Charger", "anio": 2021,
     "casa_subasta": "Manheim Honduras", "estado": "En subasta",
     "proveedor_compra": "Manheim Honduras", "monto_ofertado": 9200, "estado_subasta": "Pendiente"},

    {"vin": "WDDPK4HA4KF765432", "marca": "Mercedes-Benz", "modelo": "C300", "anio": 2019,
     "casa_subasta": "Copart Central America", "estado": "En transito",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2026-01-18", "eta_llegada": "2026-09-25",
     "numero_contenedor": "TCLU5566778", "almacen_actual": "En Transito",
     "monto_ofertado": 13200, "estado_subasta": "Ganada",
     "pagos": [{"fecha_pago": "2026-01-19", "monto": 13200, "metodo_pago": "Transferencia", "referencia": "SWIFT-88238"}]},

    {"vin": "3VWD07AJ5EM123460", "marca": "Volkswagen", "modelo": "Jetta", "anio": 2014,
     "casa_subasta": "Manheim Honduras", "estado": "En taller",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2025-12-15", "almacen_actual": "Taller",
     "monto_ofertado": 5000, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3460", "fecha_aduana": "2026-01-15",
     "monto_flete": 540, "monto_aduana": 1290,
     "fecha_ingreso_taller": "2026-02-05", "tipo_reparacion": "Carroceria", "estado_taller": "Abierta",
     "descripcion_problema": "Reparacion de carroceria lado derecho",
     "pagos": [{"fecha_pago": "2025-12-16", "monto": 5000, "metodo_pago": "Cheque", "referencia": "CHQ-102"}]},

    {"vin": "JTDKN3DU0E1123462", "marca": "Toyota", "modelo": "Prius", "anio": 2014,
     "casa_subasta": "Copart Central America", "estado": "Esperando repuestos",
     "proveedor_compra": "Copart Central America", "fecha_compra": "2025-12-01", "almacen_actual": "Taller",
     "monto_ofertado": 5600, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-3462", "fecha_aduana": "2026-01-10",
     "monto_flete": 490, "monto_aduana": 1180,
     "fecha_ingreso_taller": "2026-01-25", "tipo_reparacion": "Electrica", "estado_taller": "Esperando repuestos",
     "descripcion_problema": "Bateria hibrida y sistema electrico",
     "repuestos": [{"repuesto": "Bateria 12V", "cantidad": 1, "costo": 120}],
     "pagos": [{"fecha_pago": "2025-12-02", "monto": 5600, "metodo_pago": "Transferencia", "referencia": "SWIFT-88239"}]},

    {"vin": "5N1AT2MV2JC098765", "marca": "Nissan", "modelo": "Rogue", "anio": 2018,
     "casa_subasta": "Manheim Honduras", "estado": "En reparacion",
     "proveedor_compra": "Manheim Honduras", "fecha_compra": "2025-12-18", "almacen_actual": "Taller",
     "monto_ofertado": 8600, "estado_subasta": "Ganada",
     "tramitador": "Aduanera del Norte", "numero_factura_aduana": "FA-8765", "fecha_aduana": "2026-01-28",
     "monto_flete": 610, "monto_aduana": 1450,
     "fecha_ingreso_taller": "2026-02-08", "tipo_reparacion": "Mecanica", "estado_taller": "En proceso",
     "descripcion_problema": "Cambio de frenos y filtro de aceite",
     "repuestos": [{"repuesto": "Pastillas de freno", "cantidad": 1, "costo": 45},
                   {"repuesto": "Filtro de aceite", "cantidad": 2, "costo": 12}],
     "pagos": [{"fecha_pago": "2025-12-19", "monto": 8600, "metodo_pago": "Transferencia", "referencia": "SWIFT-88240"}]},
]


def _ensure_catalogo():
    for nombre, tipo in PROVEEDORES:
        if not frappe.db.exists("Proveedor", {"nombre": nombre}):
            frappe.get_doc({"doctype": "Proveedor", "name": nombre, "nombre": nombre, "tipo": tipo}).insert(ignore_permissions=True)
    for nombre, tipo in ALMACENES:
        if not frappe.db.exists("Almacen", nombre):
            frappe.get_doc({"doctype": "Almacen", "name": nombre, "nombre": nombre, "tipo": tipo}).insert(ignore_permissions=True)
    for nombre, tid, num, tel, dir_, dep in CLIENTES:
        if not frappe.db.exists("Cliente", {"nombre_completo": nombre}):
            frappe.get_doc({"doctype": "Cliente", "name": nombre, "nombre_completo": nombre, "tipo_identificacion": tid,
                            "numero_identificacion": num, "telefono": tel, "direccion": dir_,
                            "departamento": dep}).insert(ignore_permissions=True)


def _apply(doc, data):
    tables = ("pagos", "repuestos", "checklist", "cotizaciones")
    for k, v in data.items():
        if k in tables:
            doc.set(k, [])
            for row in v:
                doc.append(k, row)
        else:
            doc.set(k, v)


def seed():
    _ensure_catalogo()
    seed_vins = {d["vin"] for d in VEHICULOS}
    # Prune: dejar la flota exactamente como el seed (coherencia total)
    pruned = 0
    for v in frappe.get_all("Vehiculo", pluck="name"):
        if v not in seed_vins:
            frappe.delete_doc("Vehiculo", v, force=1, ignore_permissions=True)
            pruned += 1
    created = 0
    for data in VEHICULOS:
        vin = data["vin"]
        if frappe.db.exists("Vehiculo", vin):
            doc = frappe.get_doc("Vehiculo", vin)
        else:
            doc = frappe.new_doc("Vehiculo")
            created += 1
        _apply(doc, data)
        doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("SEED: vehiculos nuevos=", created, "| eliminados=", pruned)
    total = frappe.db.count("Vehiculo")
    print("SEED: vehiculos nuevos=", created, "| total=", total)
    print("SEED_COUNTS:", {dt: frappe.db.count(dt) for dt in
                           ["Proveedor", "Almacen", "Cliente", "Vehiculo"]})
    print("SEED_DONE")


if __name__ == "__main__":
    seed()
