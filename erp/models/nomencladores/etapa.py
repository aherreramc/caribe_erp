# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning

class Etapa(models.Model):
    _name = 'erp.nomencladores.etapa'

    name = fields.Char(required=True, string="Etapa")
    name_english = fields.Char(string="Traducción al inglés")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                            default=lambda self: self.env['res.company']._company_default_get())