# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class Pontencia(models.Model):
    _name = 'erp.nomencladores.potencia'

    name = fields.Char(required=True, string="Nombre:")