# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Material(models.Model):
    _name = 'erp.nomencladores.material'

    name = fields.Char(required=True, string="Material:")