# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class DiasParaCobrosYPagos(models.Model):
    _name = 'erp.nomencladores.dias_para_cobros_y_pagos'
    _order = 'name asc'

    name = fields.Integer(required=True, string="Días:")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                            default=lambda self: self.env['res.company']._company_default_get())
