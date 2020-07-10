# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class Marca(models.Model):
    _name = "erp.nomencladores.marca"

    name = fields.Char(required=True, string="Marca:")
    productos = fields.One2many('product.product', 'marca'
                                , domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
                                , change_default=True, ondelete='restrict', check_company=True)

    orden = fields.Integer(string='Orden')

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                                default=lambda self: self.env['res.company']._company_default_get())
