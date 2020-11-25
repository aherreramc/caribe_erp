# -*- coding: utf-8 -*-

from odoo import models, fields, api

import odoo.addons.decimal_precision as dp


class Puerto(models.Model):
    _name = "erp.nomencladores.puerto"

    name = fields.Char(required=True, string="Nombre:")
    pais = fields.Many2one('erp.nomencladores.pais', string='País')

    tipo = fields.Selection([ ('puerto', 'Puerto'),('aereopuerto', 'Aereopuerto'), ('almacen', 'Almacén')
                                , ('bodega', 'Bodega')], string='Tipo', default='puerto')