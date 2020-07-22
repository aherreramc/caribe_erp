# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning

import os

class DegradationType(models.Model):
    _name = 'erp.nomencladores.degradation_type'

    name = fields.Char(required=True, string="Nombre:")

    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                default=lambda self: self.env['res.company']._company_default_get())

