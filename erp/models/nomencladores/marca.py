# -*- coding: utf-8 -*-

from odoo import models, fields, api

import odoo.addons.decimal_precision as dp


class Marca(models.Model):
    _name = "erp.nomencladores.marca"

    name = fields.Char(required=True, string="Marca:")
    productos = fields.One2many('erp.product.product', 'marca')

    orden = fields.Integer(string='Orden')