# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class RepresentanteCliente(models.Model):
    _name = 'erp.nomencladores.representante_cliente'

    name = fields.Char(required=True, string="Nombre:")
    empresa = fields.Many2one('res.partner')
    cargo = fields.Char(string="Cargo:")

    tratamiento = fields.Selection([ ('Sr.', 'Sr.'),('Sra.', 'Sra.')], string='Tratamiento')
