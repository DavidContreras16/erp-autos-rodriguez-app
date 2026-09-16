# Copyright (c) 2026, Autos Rodriguez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Vehiculo(Document):
    def validate(self):
        self._validar_flujo()

    def before_save(self):
        # auto-estado primero para que el titulo refleje el estado final
        self._auto_estado_subasta()
        self._set_titulo()
        self._calcular_costos()

    def _validar_flujo(self):
        # Bloquea: no se puede marcar Vendido sin cliente y precio de venta.
        if self.estado == "Vendido" and (not self.cliente or not self.precio_venta):
            frappe.throw("No se puede marcar como <b>Vendido</b> sin Cliente y Precio de Venta "
                         "(pestana Venta).")
        # Avisa: pasar a Listo para venta sin inspeccion aprobada.
        if self.estado == "Listo para venta" and self.resultado_inspeccion != "Aprobado":
            frappe.msgprint("Este vehiculo esta en <b>Listo para venta</b> pero su inspeccion "
                            "de calidad no esta <b>Aprobada</b> (pestana Taller).", alert=True)
        # Avisa: negociacion/credito sin cliente asignado.
        if self.estado in ("En negociacion", "En tramite de credito") and not self.cliente:
            frappe.msgprint("Falta asignar el <b>Cliente</b> (pestana Venta) para esta etapa.",
                            alert=True)

    def _set_titulo(self):
        partes = [self.marca, self.modelo, self.anio]
        base = " ".join(str(p) for p in partes if p)
        self.titulo = f"{base} - {self.estado}" if self.estado else base

    def _calcular_costos(self):
        self.monto_total_aduana = (self.monto_flete or 0) + (self.monto_aduana or 0)
        self.costo_importacion = self.monto_total_aduana
        repuestos_total = 0
        for r in (self.repuestos or []):
            repuestos_total += (r.costo or 0) * (r.cantidad or 0)
        self.costo_total = (self.monto_ofertado or 0) + (self.costo_importacion or 0) + repuestos_total

    def _auto_estado_subasta(self):
        # Al ganar la subasta, si sigue en etapas previas, pasa a Comprado.
        if self.estado_subasta == "Ganada" and self.estado in ("Solicitado", "En subasta"):
            self.estado = "Comprado"
        elif self.estado_subasta == "Perdida" and self.estado in ("Solicitado", "En subasta"):
            self.estado = "Cancelado"
