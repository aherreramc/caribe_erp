# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class EstadoOferta(models.Model):
    _name = 'erp.nomencladores.estado_oferta'
    _order = 'name asc'

    name = fields.Char(required=True, string="Estado de oferta:")
