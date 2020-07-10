# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class Puerto(models.Model):
    _name = "erp.nomencladores.puerto"

    name = fields.Char(required=True, string="Nombre:")
    pais = fields.Many2one('res.country', string='País')

    tipo = fields.Selection([('puerto', 'Puerto'), ('aereopuerto', 'Aereopuerto'), ('almacen', 'Almacén')
                                , ('bodega', 'Bodega')], string='Tipo', default='puerto')

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                                default=lambda self: self.env['res.company']._company_default_get())
