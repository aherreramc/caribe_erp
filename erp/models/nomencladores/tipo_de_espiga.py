# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class TipoDeEspiga(models.Model):
    _name = 'erp.nomencladores.tipo_de_espiga'

    name = fields.Char(required=True, string="Nombre:")
    active = fields.Boolean('Activo', default=True,help="Si se encuentra marcado, el instrumento no será visualizado pero tampoco eliminado.")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                        default=lambda self: self.env['res.company']._company_default_get())