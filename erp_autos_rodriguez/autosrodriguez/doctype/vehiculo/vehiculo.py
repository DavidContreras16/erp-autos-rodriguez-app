# Copyright (c) 2026, Autos Rodriguez and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Vehiculo(Document):
    def before_save(self):
        self._set_titulo()
        self._calcular_costos()
        self._auto_estado_subasta()

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
