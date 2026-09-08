"""Replanteo: Vehiculo como contenedor unico (pestanas Compra/Aduana/Taller/Venta),
Kanban libre (sin Workflow). Elimina los doctypes por-etapa y sus scripts.

Ejecutar: bench --site development.localhost execute erp_autos_rodriguez.provision.reshape.run
Idempotente.
"""
import frappe

MODULE = "AutosRodriguez"
ESTADOS = ("Solicitado\nComprado\nEn subasta\nCancelado\nEn transito\nEn aduana\n"
           "En bodega SPS\nEn taller\nEn reparacion\nEsperando repuestos\n"
           "Listo para venta\nEn negociacion\nEn tramite de credito\nVendido")


def _child(name, fields):
    if frappe.db.exists("DocType", name):
        print("SKIP_EXISTS child", name)
        return
    frappe.get_doc({
        "doctype": "DocType", "name": name, "module": MODULE, "custom": 0,
        "istable": 1, "editable_grid": 1, "engine": "InnoDB", "fields": fields,
    }).insert()
    print("CREATED child", name)


def _fields():
    return [
        # General
        {"fieldname": "tab_general", "fieldtype": "Tab Break", "label": "General"},
        {"fieldname": "sb_datos", "fieldtype": "Section Break"},
        {"fieldname": "vin", "label": "VIN", "fieldtype": "Data", "reqd": 1, "unique": 1, "in_list_view": 1},
        {"fieldname": "marca", "label": "Marca", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
        {"fieldname": "modelo", "label": "Modelo", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
        {"fieldname": "cb_g1", "fieldtype": "Column Break"},
        {"fieldname": "anio", "label": "Anio", "fieldtype": "Int"},
        {"fieldname": "casa_subasta", "label": "Casa de Subasta", "fieldtype": "Data"},
        {"fieldname": "estado", "label": "Estado", "fieldtype": "Select", "options": ESTADOS,
         "default": "Solicitado", "in_list_view": 1, "in_standard_filter": 1},
        {"fieldname": "cb_g2", "fieldtype": "Column Break"},
        {"fieldname": "imagen", "label": "Imagen", "fieldtype": "Attach Image"},
        {"fieldname": "titulo", "label": "Titulo", "fieldtype": "Data", "read_only": 1, "hidden": 1},
        # Compra
        {"fieldname": "tab_compra", "fieldtype": "Tab Break", "label": "Compra"},
        {"fieldname": "sb_compra", "fieldtype": "Section Break", "label": "Datos de Compra"},
        {"fieldname": "proveedor_compra", "label": "Casa de Subasta (Proveedor)", "fieldtype": "Link",
         "options": "Proveedor", "link_filters": "[[\"Proveedor\",\"tipo\",\"=\",\"Casa de Subasta\"]]"},
        {"fieldname": "fecha_compra", "label": "Fecha de Compra", "fieldtype": "Date"},
        {"fieldname": "cb_compra", "fieldtype": "Column Break"},
        {"fieldname": "monto_ofertado", "label": "Monto Ofertado", "fieldtype": "Currency"},
        {"fieldname": "moneda", "label": "Moneda", "fieldtype": "Select", "options": "USD\nHNL", "default": "USD"},
        {"fieldname": "estado_subasta", "label": "Estado Subasta", "fieldtype": "Select",
         "options": "Pendiente\nGanada\nPerdida", "default": "Pendiente"},
        {"fieldname": "sb_pagos", "fieldtype": "Section Break", "label": "Pagos"},
        {"fieldname": "pagos", "label": "Pagos", "fieldtype": "Table", "options": "Vehiculo Pago"},
        # Aduana
        {"fieldname": "tab_aduana", "fieldtype": "Tab Break", "label": "Aduana"},
        {"fieldname": "sb_logistica", "fieldtype": "Section Break", "label": "Logistica"},
        {"fieldname": "eta_llegada", "label": "ETA Llegada", "fieldtype": "Date"},
        {"fieldname": "numero_contenedor", "label": "Numero de Contenedor", "fieldtype": "Data"},
        {"fieldname": "cb_ad1", "fieldtype": "Column Break"},
        {"fieldname": "almacen_actual", "label": "Ubicacion Actual", "fieldtype": "Link", "options": "Almacen"},
        {"fieldname": "sb_aduana", "fieldtype": "Section Break", "label": "Factura de Aduana"},
        {"fieldname": "tramitador", "label": "Tramitador Aduanal", "fieldtype": "Link", "options": "Proveedor",
         "link_filters": "[[\"Proveedor\",\"tipo\",\"=\",\"Tramitador Aduanal\"]]"},
        {"fieldname": "numero_factura_aduana", "label": "Numero de Factura", "fieldtype": "Data"},
        {"fieldname": "fecha_aduana", "label": "Fecha", "fieldtype": "Date"},
        {"fieldname": "cb_ad2", "fieldtype": "Column Break"},
        {"fieldname": "monto_flete", "label": "Monto Flete", "fieldtype": "Currency"},
        {"fieldname": "monto_aduana", "label": "Monto Aduana", "fieldtype": "Currency"},
        {"fieldname": "monto_total_aduana", "label": "Total Aduana", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "documento_aduana", "label": "Documento Adjunto", "fieldtype": "Attach"},
        {"fieldname": "sb_costos", "fieldtype": "Section Break", "label": "Costos"},
        {"fieldname": "costo_importacion", "label": "Costo Importacion", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "cb_costos", "fieldtype": "Column Break"},
        {"fieldname": "costo_total", "label": "Costo Total", "fieldtype": "Currency", "read_only": 1, "bold": 1},
        # Taller
        {"fieldname": "tab_taller", "fieldtype": "Tab Break", "label": "Taller"},
        {"fieldname": "sb_taller", "fieldtype": "Section Break", "label": "Orden de Trabajo"},
        {"fieldname": "fecha_ingreso_taller", "label": "Fecha de Ingreso", "fieldtype": "Date"},
        {"fieldname": "tipo_reparacion", "label": "Tipo de Reparacion", "fieldtype": "Select",
         "options": "\nMecanica\nElectrica\nCarroceria\nVarias"},
        {"fieldname": "estado_taller", "label": "Estado Taller", "fieldtype": "Select",
         "options": "\nAbierta\nEn proceso\nEsperando repuestos\nFinalizada"},
        {"fieldname": "cb_taller", "fieldtype": "Column Break"},
        {"fieldname": "descripcion_problema", "label": "Descripcion del Problema", "fieldtype": "Small Text"},
        {"fieldname": "sb_repuestos", "fieldtype": "Section Break", "label": "Repuestos Usados"},
        {"fieldname": "repuestos", "label": "Repuestos", "fieldtype": "Table", "options": "Vehiculo Repuesto"},
        {"fieldname": "sb_calidad", "fieldtype": "Section Break", "label": "Inspeccion de Calidad"},
        {"fieldname": "resultado_inspeccion", "label": "Resultado", "fieldtype": "Select",
         "options": "\nPendiente\nAprobado\nRechazado"},
        {"fieldname": "observaciones_calidad", "label": "Observaciones", "fieldtype": "Small Text"},
        {"fieldname": "checklist", "label": "Checklist", "fieldtype": "Table", "options": "Vehiculo Checklist"},
        # Venta
        {"fieldname": "tab_venta", "fieldtype": "Tab Break", "label": "Venta"},
        {"fieldname": "sb_venta", "fieldtype": "Section Break", "label": "Datos de Venta"},
        {"fieldname": "cliente", "label": "Cliente", "fieldtype": "Link", "options": "Cliente"},
        {"fieldname": "precio_venta", "label": "Precio de Venta", "fieldtype": "Currency"},
        {"fieldname": "forma_pago", "label": "Forma de Pago", "fieldtype": "Select", "options": "\nContado\nFinanciado"},
        {"fieldname": "cb_venta", "fieldtype": "Column Break"},
        {"fieldname": "financiera", "label": "Financiera", "fieldtype": "Link", "options": "Proveedor",
         "link_filters": "[[\"Proveedor\",\"tipo\",\"=\",\"Financiera\"]]"},
        {"fieldname": "estado_credito", "label": "Estado del Credito", "fieldtype": "Select",
         "options": "\nEnviado\nEn revision\nAprobado\nRechazado"},
        {"fieldname": "sb_cotizaciones", "fieldtype": "Section Break", "label": "Cotizaciones"},
        {"fieldname": "cotizaciones", "label": "Cotizaciones", "fieldtype": "Table", "options": "Vehiculo Cotizacion"},
        {"fieldname": "sb_entrega", "fieldtype": "Section Break", "label": "Entrega"},
        {"fieldname": "pagado", "label": "Pagado", "fieldtype": "Check"},
        {"fieldname": "fecha_entrega", "label": "Fecha de Entrega", "fieldtype": "Date"},
        {"fieldname": "cb_entrega", "fieldtype": "Column Break"},
        {"fieldname": "recibido_por", "label": "Recibido Por", "fieldtype": "Data"},
        {"fieldname": "firma_entrega", "label": "Firma / Comprobante", "fieldtype": "Attach"},
    ]


def run():
    # 1) Child DocTypes
    _child("Vehiculo Pago", [
        {"fieldname": "fecha_pago", "label": "Fecha", "fieldtype": "Date", "in_list_view": 1, "columns": 2},
        {"fieldname": "monto", "label": "Monto", "fieldtype": "Currency", "in_list_view": 1, "columns": 2},
        {"fieldname": "metodo_pago", "label": "Metodo", "fieldtype": "Select",
         "options": "Transferencia\nTarjeta\nCheque", "in_list_view": 1, "columns": 2},
        {"fieldname": "referencia", "label": "Referencia", "fieldtype": "Data", "in_list_view": 1},
        {"fieldname": "comprobante", "label": "Comprobante", "fieldtype": "Attach"},
    ])
    _child("Vehiculo Repuesto", [
        {"fieldname": "repuesto", "label": "Repuesto", "fieldtype": "Link", "options": "Repuesto",
         "in_list_view": 1, "columns": 4},
        {"fieldname": "cantidad", "label": "Cantidad", "fieldtype": "Int", "in_list_view": 1, "columns": 2},
        {"fieldname": "costo", "label": "Costo Unit.", "fieldtype": "Currency", "in_list_view": 1, "columns": 2},
    ])
    _child("Vehiculo Checklist", [
        {"fieldname": "item", "label": "Item", "fieldtype": "Data", "in_list_view": 1, "columns": 8},
        {"fieldname": "cumple", "label": "Cumple", "fieldtype": "Check", "in_list_view": 1},
    ])
    _child("Vehiculo Cotizacion", [
        {"fieldname": "cliente", "label": "Cliente", "fieldtype": "Link", "options": "Cliente",
         "in_list_view": 1, "columns": 3},
        {"fieldname": "fecha", "label": "Fecha", "fieldtype": "Date", "in_list_view": 1, "columns": 2},
        {"fieldname": "precio_ofertado", "label": "Precio", "fieldtype": "Currency", "in_list_view": 1, "columns": 2},
        {"fieldname": "forma_pago", "label": "Forma Pago", "fieldtype": "Select",
         "options": "Contado\nFinanciado", "in_list_view": 1, "columns": 2},
        {"fieldname": "estado", "label": "Estado", "fieldtype": "Select",
         "options": "Abierta\nAceptada\nRechazada", "in_list_view": 1},
    ])

    # 2) Reshape Vehiculo (fields wholesale)
    veh = frappe.get_doc("DocType", "Vehiculo")
    veh.set("fields", [])
    for f in _fields():
        veh.append("fields", f)
    veh.title_field = "titulo"
    veh.save(ignore_permissions=True)
    print("VEHICULO_RESHAPED fields=", len(veh.fields))

    # 3) Eliminar Workflow
    if frappe.db.exists("Workflow", "Flujo Vehiculo"):
        frappe.delete_doc("Workflow", "Flujo Vehiculo", force=1, ignore_permissions=True)
        print("DELETED Workflow Flujo Vehiculo")

    # 4) Eliminar Server Scripts obsoletos
    for ss in ("OC - Estado Subasta a Vehiculo", "Factura Aduana - Calcular Total",
               "Factura Aduana - Costo Importacion", "Movimiento - Estado y Almacen",
               "Vehiculo - Generar Titulo"):
        if frappe.db.exists("Server Script", ss):
            frappe.delete_doc("Server Script", ss, force=1, ignore_permissions=True)
            print("DELETED Server Script", ss)

    # 5) Purgar datos de doctypes viejos
    for dt in ("Movimiento Vehiculo", "Factura Aduana", "Pago Compra", "Orden de Compra"):
        if frappe.db.exists("DocType", dt):
            for r in frappe.get_all(dt):
                frappe.delete_doc(dt, r.name, force=1, ignore_permissions=True)
            print("PURGED data", dt)

    # 6) Eliminar DocTypes viejos
    for dt in ("Movimiento Vehiculo", "Factura Aduana", "Pago Compra", "Orden de Compra"):
        if frappe.db.exists("DocType", dt):
            frappe.delete_doc("DocType", dt, force=1, ignore_permissions=True)
            print("DELETED DocType", dt)

    frappe.db.commit()
    print("RESHAPE_DONE")
