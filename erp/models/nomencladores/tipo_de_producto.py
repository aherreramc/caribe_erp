# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class TipoDeProducto(models.Model):
    _name = "erp.nomencladores.tipo_de_producto"

    name = fields.Char(required=True)
