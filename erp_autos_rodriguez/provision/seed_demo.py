import frappe


def ensure_prompt(dt, name, data):
    """Crea el doctytpe con autoname Prompt o sincroniza los campos si ya existe."""
    data = dict(data)
    data["name"] = name
    if frappe.db.exists(dt, name):
        doc = frappe.get_doc(dt, name)
        _sync_fields(doc, data)
        return frappe.get_doc(dt, name)
    doc = frappe.new_doc(dt)
    for k, v in data.items():
        doc.set(k, v)
    doc.insert(ignore_permissions=True)
    return doc


def ensure_key(dt, key_field, data):
    """Crea doc por campo unico o sincroniza los campos si ya existe."""
    exists = frappe.db.exists(dt, {key_field: data[key_field]})
    if exists:
        doc = frappe.get_doc(dt, exists)
        _sync_fields(doc, data)
        return frappe.get_doc(dt, exists)
    doc = frappe.new_doc(dt)
    for k, v in data.items():
        doc.set(k, v)
    doc.insert(ignore_permissions=True)
    return doc


def _sync_fields(doc, data):
    """db_set de los campos que difieren (sin disparar validaciones/workflow)."""
    for k, v in data.items():
        if k in ("name",) or not hasattr(doc, k):
            continue
        if doc.get(k) != v:
            doc.db_set(k, v, update_modified=False)


def _workflow_graph():
    wf = frappe.get_cached_doc("Workflow", "Flujo Vehiculo")
    graph = {}
    for t in wf.transitions:
        graph.setdefault(t.state, set()).add(t.next_state)
    return graph


def advance_vehicle(vin, target_state):
    """Camina el grafo real de transiciones del workflow hasta target_state."""
    doc = frappe.get_doc("Vehiculo", vin)
    if doc.estado == target_state:
        return doc
    graph = _workflow_graph()
    from collections import deque

    queue = deque([[doc.estado]])
    seen = set()
    path = None
    while queue:
        p = queue.popleft()
        node = p[-1]
        if node == target_state:
            path = p
            break
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph.get(node, []):
            queue.append(p + [nxt])
    if not path:
        frappe.log_error(
            f"Vehiculo {vin}: no hay ruta en el workflow de '{doc.estado}' a '{target_state}'",
            "SeedDemo",
        )
        print(f"WARN advance_vehicle {vin} -> {target_state}: sin ruta")
        return doc
    for st in path[1:]:
        doc = frappe.get_doc("Vehiculo", vin)
        doc.estado = st
        doc.save(ignore_permissions=True)
    return frappe.get_doc("Vehiculo", vin)


CASA_MAP = {
    "Copart": "Copart Central America",
    "Manheim": "Manheim Honduras",
    "IAAI": "Copart Central America",
    "Amazon Warehouse": "Copart Central America",
}


def _normalize_casa_subasta():
    """Unifica casa_subasta (texto libre) con los proveedores sembrados."""
    fixed = []
    for name in frappe.get_all("Vehiculo", pluck="name"):
        doc = frappe.get_doc("Vehiculo", name)
        value = (doc.casa_subasta or "").strip()
        new = CASA_MAP.get(value, value)
        if not new:
            new = "Copart Central America"
        if new != value:
            doc.db_set("casa_subasta", new, update_modified=False)
            fixed.append(f"{name}: '{value}' -> '{new}'")
    return fixed


def _fix_demo_typos():
    fixed = []
    nissan = frappe.db.get_value("Vehiculo", {"vin": "1N4AL3AP8JC123465"})
    if nissan:
        doc = frappe.get_doc("Vehiculo", nissan)
        if doc.modelo == "Nisan 200":
            doc.db_set("modelo", "Nissan 200", update_modified=False)
            fixed.append(f"{doc.name}: modelo 'Nisan 200' -> 'Nissan 200'")
    return fixed


def _ensure_oc(vin, data):
    """Crea la Orden de Compra 'Ganada' del vehiculo si no existe y enlaza."""
    copart = frappe.db.get_value("Proveedor", {"nombre": "Copart Central America"}, "name")
    oc_name = frappe.db.sql(
        "SELECT name FROM `tabOrden de Compra` WHERE vehiculo=%s LIMIT 1", vin
    )
    if oc_name:
        oc = frappe.get_doc("Orden de Compra", oc_name[0][0])
        if oc.monto_ofertado != data["monto"]:
            oc.db_set("monto_ofertado", data["monto"], update_modified=False)
        return oc
    oc = frappe.new_doc("Orden de Compra")
    oc.update({
        "vehiculo": vin,
        "proveedor": copart,
        "fecha": data["fecha"],
        "monto_ofertado": data["monto"],
        "moneda": "USD",
        "estado_subasta": "Ganada",
        "notas": data["notas"],
    })
    oc.insert(ignore_permissions=True)
    frappe.db.set_value("Vehiculo", vin, "orden_compra", oc.name, update_modified=False)
    frappe.db.set_value("Vehiculo", vin, "fecha_compra", oc.fecha, update_modified=False)
    return oc


def _ensure_pago(oc, data):
    """Crea el Pago Compra de la OC (un pago por compra) si no existe."""
    pago_name = frappe.db.exists("Pago Compra", {"orden_compra": oc.name, "monto": data["monto"]})
    if pago_name:
        return frappe.get_doc("Pago Compra", pago_name)
    pc = frappe.new_doc("Pago Compra")
    pc.update({
        "orden_compra": oc.name,
        "fecha_pago": data["pago_fecha"],
        "monto": data["monto"],
        "metodo_pago": data["pago_metodo"],
        "referencia": data["pago_ref"],
    })
    pc.insert(ignore_permissions=True)
    return pc


def seed():
    proveedores = [
        {"nombre": "Copart Central America", "tipo": "Casa de Subasta", "contacto": "Roberto Diaz", "telefono": "+1 305-555-0148", "email": "ventas@copart.com", "notas": "Subastas principales de autos accidentados."},
        {"nombre": "Manheim Honduras", "tipo": "Casa de Subasta", "contacto": "Luis Andrade", "telefono": "+504 2558-7788", "email": "l.andrade@manheim.hn", "notas": "Subastas de autos usados y danados."},
        {"nombre": "Aduanera del Norte", "tipo": "Tramitador Aduanal", "contacto": "Sandra Castro", "telefono": "+504 2557-1234", "email": "scastro@aduaneranorte.hn", "notas": "Tramites aduanales y desaduanaje."},
        {"nombre": "Taller Marbella", "tipo": "Taller Externo", "contacto": "Hector Reyes", "telefono": "+504 2552-3456", "email": "hreyes@tallermarbella.hn", "notas": "Trabajos de enderezado y pintura."},
    ]
    for p in proveedores:
        ensure_prompt("Proveedor", p["nombre"], p)

    almacenes = [
        {"nombre": "Origen Miami", "tipo": "Origen", "direccion": "Bodega portuaria, Miami, FL, USA"},
        {"nombre": "Bodega Central SPS", "tipo": "Bodega", "direccion": "Zona Industrial, San Pedro Sula"},
    ]
    for a in almacenes:
        ensure_prompt("Almacen", a["nombre"], a)

    repuestos = [
        {"codigo": "R-001", "nombre": "Filtro de aceite", "categoria": "Mecanica", "unidad_medida": "Unidad", "costo_referencia": 15.5, "stock_actual": 40},
        {"codigo": "R-002", "nombre": "Pastillas de freno", "categoria": "Mecanica", "unidad_medida": "Juego", "costo_referencia": 28.0, "stock_actual": 25},
        {"codigo": "R-003", "nombre": "Bujia", "categoria": "Electrica", "unidad_medida": "Unidad", "costo_referencia": 4.75, "stock_actual": 120},
        {"codigo": "R-004", "nombre": "Alternador", "categoria": "Electrica", "unidad_medida": "Unidad", "costo_referencia": 95.0, "stock_actual": 8},
        {"codigo": "R-005", "nombre": "Parabrisas delantero", "categoria": "Carroceria", "unidad_medida": "Unidad", "costo_referencia": 120.0, "stock_actual": 5},
        {"codigo": "R-006", "nombre": "Bomba de agua", "categoria": "Mecanica", "unidad_medida": "Unidad", "costo_referencia": 45.0, "stock_actual": 12},
        {"codigo": "R-007", "nombre": "Kit de embrague", "categoria": "Mecanica", "unidad_medida": "Juego", "costo_referencia": 210.0, "stock_actual": 4},
        {"codigo": "R-008", "nombre": "Faro izquierdo", "categoria": "Electrica", "unidad_medida": "Unidad", "costo_referencia": 60.0, "stock_actual": 18},
    ]
    for r in repuestos:
        ensure_key("Repuesto", "codigo", r)

    clientes = [
        {"nombre_completo": "Marco Antonio Lopez", "tipo_identificacion": "DNI", "numero_identificacion": "0801-1995-04567", "telefono": "+504 9945-1122", "email": "marco.lopez@gmail.com", "direccion": "Col. Trejo, SPS", "departamento": "Cortes"},
        {"nombre_completo": "Karla Patricia Mejia", "tipo_identificacion": "DNI", "numero_identificacion": "0801-1990-11234", "telefono": "+504 8888-7744", "email": "karla.mejia@yahoo.com", "direccion": "Col. Prado Alto, Tegucigalpa", "departamento": "Francisco Morazan"},
        {"nombre_completo": "Jorge Luis Castillo", "tipo_identificacion": "DNI", "numero_identificacion": "0501-1988-33221", "telefono": "+504 9777-8899", "email": "jlcastillo@hotmail.com", "direccion": "Barrio Solares, La Ceiba", "departamento": "Atlantida"},
        {"nombre_completo": "Maria Fernanda Reyes", "tipo_identificacion": "Pasaporte", "numero_identificacion": "H234567", "telefono": "+504 9955-0001", "email": "mfereyes@outlook.com", "direccion": "Col. La Libertad, Choluteca", "departamento": "Choluteca"},
        {"nombre_completo": "Pedro David Nunez", "tipo_identificacion": "RTN", "numero_identificacion": "08019008456712", "telefono": "+504 9900-1212", "email": "", "direccion": "Boulevard Morazan, Tegucigalpa", "departamento": "Francisco Morazan"},
        {"nombre_completo": "Ana Cristina Gomez", "tipo_identificacion": "DNI", "numero_identificacion": "0701-1998-77890", "telefono": "+504 9833-4567", "email": "ana.gomez@gmail.com", "direccion": "Col. Satelite, SPS", "departamento": "Cortes"},
    ]
    for c in clientes:
        ensure_prompt("Cliente", c["nombre_completo"], c)

    vehiculos = [
        {"vin": "2C3CDXBG9MH123456", "marca": "Toyota", "modelo": "Corolla", "anio": 2021, "estado": "En subasta", "casa_subasta": "Copart Central America"},
        {"vin": "1HGCV1F34LA012345", "marca": "Honda", "modelo": "Civic", "anio": 2020, "estado": "En aduana", "casa_subasta": "Copart Central America", "eta_llegada": "2026-09-12"},
        {"vin": "WDDPK4HA4KF765432", "marca": "Mercedes-Benz", "modelo": "C300", "anio": 2019, "estado": "En transito", "casa_subasta": "Copart Central America", "numero_contenedor": "MSKU 8812345", "eta_llegada": "2026-09-25"},
        {"vin": "1FTFW1ET5DFC12345", "marca": "Ford", "modelo": "F-150", "anio": 2021, "estado": "En transito", "casa_subasta": "Manheim Honduras", "numero_contenedor": "MSCU1234567", "eta_llegada": "2026-09-02"},
        {"vin": "5NPE24AF4FH123459", "marca": "Hyundai", "modelo": "Sonata", "anio": 2019, "estado": "En bodega SPS", "casa_subasta": "Copart Central America", "numero_contenedor": "TCLU7654321"},
        {"vin": "3VWD07AJ5EM123460", "marca": "Volkswagen", "modelo": "Jetta", "anio": 2020, "estado": "En taller", "casa_subasta": "Copart Central America"},
        {"vin": "5N1AT2MV2JC098765", "marca": "Nissan", "modelo": "Rogue", "anio": 2018, "estado": "En reparacion", "casa_subasta": "Copart Central America"},
        {"vin": "1G1ZE5ST8HF123461", "marca": "Chevrolet", "modelo": "Malibu", "anio": 2017, "estado": "En reparacion", "casa_subasta": "Copart Central America"},
        {"vin": "JTDKN3DU0E1123462", "marca": "Toyota", "modelo": "Prius", "anio": 2018, "estado": "Esperando repuestos", "casa_subasta": "Manheim Honduras"},
        {"vin": "3VWD17AJ8KM654321", "marca": "Volkswagen", "modelo": "Jetta", "anio": 2022, "estado": "Listo para venta", "casa_subasta": "Manheim Honduras"},
        {"vin": "5YFBURHE1FP123463", "marca": "Toyota", "modelo": "Corolla", "anio": 2021, "estado": "En negociacion", "casa_subasta": "Copart Central America"},
        {"vin": "1N4AL3AP8JC123464", "marca": "Nissan", "modelo": "Altima", "anio": 2019, "estado": "Vendido", "casa_subasta": "Copart Central America"},
        {"vin": "1N4AL3AP8JC123465", "marca": "Nissan", "modelo": "Nissan 200", "anio": 2004, "estado": "Comprado", "casa_subasta": "Copart Central America"},
        {"vin": "2T1BURHE0JC123457", "marca": "Honda", "modelo": "Civic", "anio": 2020, "estado": "Comprado", "casa_subasta": "Copart Central America"},
        {"vin": "1HGCM82633A123456", "marca": "Toyota", "modelo": "Corolla", "anio": 2019, "estado": "En subasta", "casa_subasta": "Copart Central America"},
        {"vin": "3FADP4EJ5DM123458", "marca": "Ford", "modelo": "Fusion", "anio": 2018, "estado": "En subasta", "casa_subasta": "Copart Central America"},
        {"vin": "4T1B11HK5KU987654", "marca": "Toyota", "modelo": "RAV4", "anio": 2019, "estado": "Solicitado", "casa_subasta": "Copart Central America"},
    ]
    for v in vehiculos:
        vdata = dict(v)
        target = vdata.pop("estado", None)
        doc = ensure_key("Vehiculo", "vin", vdata)
        if target and doc.estado != target:
            advance_vehicle(doc.name, target)

    oc_pagos = {
        "1HGCV1F34LA012345": {"fecha": "2026-01-20", "monto": 6500, "notas": "Oferta ganada en subasta por Honda Civic 2020.", "pago_fecha": "2026-01-22", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88231"},
        "1N4AL3AP8JC123465": {"fecha": "2026-01-15", "monto": 4200, "notas": "Compra registrada de Nissan 200 (demo historica).", "pago_fecha": "2026-01-18", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88232"},
        "2T1BURHE0JC123457": {"fecha": "2026-07-29", "monto": 5400, "notas": "Compra registrada de Honda Civic (demo historica).", "pago_fecha": "2026-08-01", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88233"},
        "1FTFW1ET5DFC12345": {"fecha": "2026-07-14", "monto": 14800, "notas": "Subasta ganada Ford F-150 2021.", "pago_fecha": "2026-07-17", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88234"},
        "WDDPK4HA4KF765432": {"fecha": "2026-03-20", "monto": 13200, "notas": "Subasta ganada Mercedes-Benz C300 2019.", "pago_fecha": "2026-03-23", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88235"},
        "3VWD07AJ5EM123460": {"fecha": "2026-06-14", "monto": 4300, "notas": "Subasta ganada Volkswagen Jetta 2020.", "pago_fecha": "2026-06-17", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88236"},
        "1G1ZE5ST8HF123461": {"fecha": "2026-06-09", "monto": 5200, "notas": "Subasta ganada Chevrolet Malibu 2017.", "pago_fecha": "2026-06-12", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88237"},
        "5N1AT2MV2JC098765": {"fecha": "2026-05-30", "monto": 8600, "notas": "Subasta ganada Nissan Rogue 2018.", "pago_fecha": "2026-06-02", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88238"},
        "5NPE24AF4FH123459": {"fecha": "2026-06-29", "monto": 4800, "notas": "Subasta ganada Hyundai Sonata 2019.", "pago_fecha": "2026-07-02", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88239"},
        "JTDKN3DU0E1123462": {"fecha": "2026-06-04", "monto": 8900, "notas": "Subasta ganada Toyota Prius 2018.", "pago_fecha": "2026-06-07", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88240"},
        "3VWD17AJ8KM654321": {"fecha": "2026-02-10", "monto": 5900, "notas": "Subasta ganada Volkswagen Jetta 2022.", "pago_fecha": "2026-02-13", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88241"},
        "5YFBURHE1FP123463": {"fecha": "2026-05-25", "monto": 5500, "notas": "Subasta ganada Toyota Corolla 2021.", "pago_fecha": "2026-05-28", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88242"},
        "1N4AL3AP8JC123464": {"fecha": "2026-04-25", "monto": 6200, "notas": "Subasta ganada Nissan Altima 2019.", "pago_fecha": "2026-04-28", "pago_metodo": "Transferencia", "pago_ref": "SWIFT HSBC-88243"},
    }
    ocs_created = 0
    pagos_created = 0
    for vin, od in oc_pagos.items():
        existing_oc = frappe.db.sql(
            "SELECT name FROM `tabOrden de Compra` WHERE vehiculo=%s LIMIT 1", vin
        )
        oc = _ensure_oc(vin, od)
        if not existing_oc:
            ocs_created += 1
        if not frappe.db.exists("Pago Compra", {"orden_compra": oc.name, "monto": od["monto"]}):
            pagos_created += 1
            _ensure_pago(oc, od)
    print("OCS_NUEVAS:", ocs_created, "| PAGOS_NUEVOS:", pagos_created)

    casa_fixed = _normalize_casa_subasta()
    typo_fixed = _fix_demo_typos()

    frappe.db.commit()

    print("CASA_FIXED:", casa_fixed)
    print("TYPO_FIXED:", typo_fixed)
    print("SEED_COUNTS:", {dt: len(frappe.get_all(dt)) for dt in ["Proveedor", "Almacen", "Repuesto", "Cliente", "Vehiculo", "Orden de Compra", "Pago Compra"]})

    # Job 4: logistica y aduana (si los doctypes ya existen)
    if frappe.db.exists("DocType", "Movimiento Vehiculo") and frappe.db.exists("DocType", "Factura Aduana"):
        from erp_autos_rodriguez.provision.seed_job4 import seed as seed_job4
        seed_job4()

    for v in frappe.get_all("Vehiculo", fields=["name", "marca", "modelo", "anio", "estado", "casa_subasta", "orden_compra", "fecha_compra"], order_by="name"):
        print("VEH:", v.name, "|", v.marca, v.modelo, "|", v.estado, "| casa:", v.casa_subasta, "| OC:", v.orden_compra, "| fecha:", v.fecha_compra)
    return {
        "counts": {dt: len(frappe.get_all(dt)) for dt in ["Proveedor", "Almacen", "Repuesto", "Cliente", "Vehiculo", "Orden de Compra", "Pago Compra"]},
        "casa_fixed": casa_fixed,
        "typo_fixed": typo_fixed,
    }


if __name__ == "__main__":
    result = seed()
    print("SEED_RESULT:", result)