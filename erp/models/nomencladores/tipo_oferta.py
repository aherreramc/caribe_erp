# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class TipoOferta(models.Model):
    _name = 'erp.nomencladores.tipo_oferta'
    _order = 'name asc'

    name = fields.Char(required=True, string="Tipo:")
