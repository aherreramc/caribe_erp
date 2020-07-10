# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Material(models.Model):
    _name = 'erp.nomencladores.material'

    name = fields.Char(required=True, string="Material:")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                            default=lambda self: self.env['res.company']._company_default_get())