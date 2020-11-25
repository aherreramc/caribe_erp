# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Embalaje(models.Model):
    _name = 'erp.nomencladores.embalaje'
    _order = 'name asc'

    name = fields.Char(required=True, string="Embalaje:")
