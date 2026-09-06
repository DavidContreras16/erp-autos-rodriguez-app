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


def _ensure_oc(vin, fecha, notas):
    """Crea la Orden de Compra 'Ganada' del vehiculo si no existe y enlaza."""
    oc_name = frappe.db.sql(
        "SELECT name FROM `tabOrden de Compra` WHERE vehiculo=%s LIMIT 1", vin
    )
    if oc_name:
        return frappe.get_doc("Orden de Compra", oc_name[0][0])
    copart = frappe.db.get_value("Proveedor", {"nombre": "Copart Central America"}, "name")
    oc = frappe.new_doc("Orden de Compra")
    oc.update({
        "vehiculo": vin,
        "proveedor": copart,
        "fecha": fecha,
        "monto_ofertado": 0,
        "moneda": "USD",
        "estado_subasta": "Ganada",
        "notas": notas,
    })
    oc.insert(ignore_permissions=True)
    frappe.db.set_value("Vehiculo", vin, "orden_compra", oc.name, update_modified=False)
    frappe.db.set_value("Vehiculo", vin, "fecha_compra", oc.fecha, update_modified=False)
    return oc


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
        {"vin": "2C3CDXBG9MH123456", "marca": "Toyota", "modelo": "Corolla", "anio": 2021, "titulo": "Toyota Corolla 2021", "estado": "En subasta", "casa_subasta": "Copart Central America"},
        {"vin": "1HGCV1F34LA012345", "marca": "Honda", "modelo": "Civic", "anio": 2020, "titulo": "Honda Civic 2020", "estado": "En aduana", "eta_llegada": "2026-09-12"},
        {"vin": "WDDPK4HA4KF765432", "marca": "Mercedes-Benz", "modelo": "C300", "anio": 2019, "titulo": "Mercedes-Benz C300 2019", "estado": "En transito", "numero_contenedor": "MSKU 8812345"},
        {"vin": "3VWD17AJ8KM654321", "marca": "Volkswagen", "modelo": "Jetta", "anio": 2022, "titulo": "Volkswagen Jetta 2022", "estado": "Listo para venta"},
        {"vin": "5N1AT2MV2JC098765", "marca": "Nissan", "modelo": "Rogue", "anio": 2018, "titulo": "Nissan Rogue 2018", "estado": "En taller"},
        {"vin": "4T1B11HK5KU987654", "marca": "Toyota", "modelo": "RAV4", "anio": 2019, "titulo": "Toyota RAV4 2019", "estado": "Solicitado"},
    ]
    for v in vehiculos:
        vdata = dict(v)
        target = vdata.pop("estado", None)
        doc = ensure_key("Vehiculo", "vin", vdata)
        if target and doc.estado != target:
            advance_vehicle(doc.name, target)

    honda_vin = "1HGCV1F34LA012345"
    copart = frappe.db.get_value("Proveedor", {"nombre": "Copart Central America"}, "name")

    honda_oc = _ensure_oc(
        honda_vin,
        "2026-01-20",
        "Oferta ganada en subasta por Honda Civic 2020.",
    )
    honda = frappe.get_doc("Vehiculo", honda_vin)
    frappe.db.set_value("Vehiculo", honda_vin, "orden_compra", honda_oc.name, update_modified=False)
    honda_oc.reload()
    frappe.db.set_value("Vehiculo", honda_vin, "fecha_compra", honda_oc.fecha, update_modified=False)

    if not frappe.db.exists("Pago Compra", {"orden_compra": honda_oc.name, "monto": 6500}):
        pc = frappe.new_doc("Pago Compra")
        pc.update({
            "orden_compra": honda_oc.name,
            "fecha_pago": "2026-01-22",
            "monto": 6500,
            "metodo_pago": "Transferencia",
            "referencia": "SWIFT HSBC-88231",
        })
        pc.insert(ignore_permissions=True)

    _ensure_oc("1N4AL3AP8JC123465", "2026-01-15", "Compra registrada de Nissan 200 (demo historica).")
    _ensure_oc("2T1BURHE0JC123457", "2026-07-29", "Compra registrada de Honda Civic (demo historica).")

    casa_fixed = _normalize_casa_subasta()
    typo_fixed = _fix_demo_typos()

    frappe.db.commit()

    print("CASA_FIXED:", casa_fixed)
    print("TYPO_FIXED:", typo_fixed)
    print("SEED_COUNTS:", {dt: len(frappe.get_all(dt)) for dt in ["Proveedor", "Almacen", "Repuesto", "Cliente", "Vehiculo", "Orden de Compra", "Pago Compra"]})

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