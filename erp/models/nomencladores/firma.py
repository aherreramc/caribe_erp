# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Firma(models.Model):
    _name = 'erp.nomencladores.firma'

    name = fields.Char(required = True)

    firma = fields.Binary("Variant Image", attachment=True, required = True)

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                            default=lambda self: self.env['res.company']._company_default_get())
