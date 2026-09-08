"""Seed demo idempotente para los modulos de Job 4 (Logistica y Aduana):
Movimiento Vehiculo y Factura Aduana.

Ejecutar:
    bench --site development.localhost execute erp_autos_rodriguez.provision.seed_job4.seed

- Camina 1 vehiculo Comprado por toda la cadena (En Transito -> Puerto ->
  Bodega SPS) para ilustrar el avance de estado automatico.
- Deja otro Comprado movido solo a En Transito (flujo en curso).
- Agrega Movimientos de bitacora a los que ya venian en transito/aduana/bodega.
- Agrega Facturas de Aduana con costos realistas a la flota que ya paso aduana,
  para poblar costo_importacion / costo_total.

Idempotente:
- Movimiento: clave (vehiculo, almacen_destino).
- Factura Aduana: clave numero_factura.
"""
import frappe

TRAMITADOR = "Aduanera del Norte"  # Proveedor tipo Tramitador Aduanal

# Almacenes canonicos requeridos por los movimientos (autoname Prompt: name=nombre)
ALMACENES = [
    ("Subasta USA", "Origen"),
    ("En Transito", "Transito"),
    ("Puerto", "Transito"),
    ("Bodega SPS", "Bodega"),
    ("Taller", "Taller"),
    ("Sala de Venta", "Exhibicion"),
    ("En ruta a cliente", "Transito"),
]


def _ensure_prereqs():
    """Almacenes canonicos + proveedor tramitador (idempotente), para que el
    seed no dependa de haber corrido scripts/job4.py a mano."""
    for nombre, tipo in ALMACENES:
        if not frappe.db.exists("Almacen", nombre):
            frappe.get_doc({"doctype": "Almacen", "name": nombre,
                            "nombre": nombre, "tipo": tipo}).insert(ignore_permissions=True)
    if not frappe.db.exists("Proveedor", TRAMITADOR):
        frappe.get_doc({"doctype": "Proveedor", "nombre": TRAMITADOR,
                        "tipo": "Tramitador Aduanal"}).insert(ignore_permissions=True)


def _ensure_movimiento(vin, origen, destino, fecha):
    exists = frappe.get_all(
        "Movimiento Vehiculo",
        filters={"vehiculo": vin, "almacen_destino": destino},
        limit=1,
    )
    if exists:
        return False
    doc = frappe.get_doc({
        "doctype": "Movimiento Vehiculo",
        "vehiculo": vin,
        "almacen_origen": origen,
        "almacen_destino": destino,
        "fecha": fecha,
        "notas": f"Traslado demo a {destino}",
    })
    doc.insert(ignore_permissions=True)
    return True


def _ensure_factura(vin, numero, fecha, flete, aduana):
    if frappe.db.exists("Factura Aduana", {"numero_factura": numero}):
        return False
    doc = frappe.get_doc({
        "doctype": "Factura Aduana",
        "vehiculo": vin,
        "proveedor": TRAMITADOR,
        "numero_factura": numero,
        "fecha": fecha,
        "monto_flete": flete,
        "monto_aduana": aduana,
    })
    doc.insert(ignore_permissions=True)
    return True


def seed():
    _ensure_prereqs()
    movs = 0
    fas = 0

    # 1) Cadena completa: Honda Civic Comprado -> En bodega SPS (avanza estado)
    full = "2T1BURHE0JC123457"
    movs += _ensure_movimiento(full, "Subasta USA", "En Transito", "2026-02-01 09:00:00")
    movs += _ensure_movimiento(full, "En Transito", "Puerto", "2026-02-18 10:00:00")
    movs += _ensure_movimiento(full, "Puerto", "Bodega SPS", "2026-02-25 14:00:00")

    # 2) Comprado movido solo a En Transito (flujo en curso)
    movs += _ensure_movimiento("1N4AL3AP8JC123465", "Subasta USA", "En Transito", "2026-02-20 09:00:00")

    # 3) Bitacora para los que ya venian en transito/aduana/bodega
    #    (la guarda del script no cambia el estado si no corresponde;
    #     solo actualiza almacen_actual)
    movs += _ensure_movimiento("1FTFW1ET5DFC12345", "Subasta USA", "En Transito", "2026-02-05 09:00:00")
    movs += _ensure_movimiento("WDDPK4HA4KF765432", "Subasta USA", "En Transito", "2026-02-08 09:00:00")
    movs += _ensure_movimiento("1HGCV1F34LA012345", "En Transito", "Puerto", "2026-02-10 11:00:00")
    movs += _ensure_movimiento("5NPE24AF4FH123459", "Puerto", "Bodega SPS", "2026-02-12 15:00:00")

    # 4) Facturas de Aduana (vehiculos que ya pasaron aduana)
    #    Los que siguen "En transito" (F-150, Mercedes) NO llevan factura aun.
    FACTURAS = [
        # (vin, numero, fecha, flete, aduana)
        ("2T1BURHE0JC123457", "FA-DEMO-3457", "2026-02-26", 450, 1100),
        ("1HGCV1F34LA012345", "FA-DEMO-2345", "2026-02-11", 500, 1250),
        ("5NPE24AF4FH123459", "FA-DEMO-3459", "2026-02-13", 600, 1400),
        ("3VWD07AJ5EM123460", "FA-DEMO-3460", "2026-01-15", 550, 1300),
        ("1G1ZE5ST8HF123461", "FA-DEMO-3461", "2026-01-18", 520, 1280),
        ("JTDKN3DU0E1123462", "FA-DEMO-3462", "2026-01-20", 480, 1150),
        ("5YFBURHE1FP123463", "FA-DEMO-3463", "2026-01-22", 500, 1350),
        ("3VWD17AJ8KM654321", "FA-DEMO-4321", "2026-01-25", 530, 1320),
        ("5N1AT2MV2JC098765", "FA-DEMO-8765", "2026-01-28", 610, 1450),
        ("1N4AL3AP8JC123464", "FA-DEMO-3464", "2026-01-30", 500, 1200),
    ]
    for vin, numero, fecha, flete, aduana in FACTURAS:
        fas += _ensure_factura(vin, numero, fecha, flete, aduana)

    frappe.db.commit()

    total_mov = frappe.db.count("Movimiento Vehiculo")
    total_fa = frappe.db.count("Factura Aduana")
    print(f"SEED_JOB4: nuevos movimientos={movs}, nuevas facturas={fas}")
    print(f"SEED_JOB4_TOTALES: Movimiento Vehiculo={total_mov}, Factura Aduana={total_fa}")
    print("SEED_JOB4_DONE")
