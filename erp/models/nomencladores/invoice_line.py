# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


# class InvoiceLineTemplate(models.Model):
#     _inherit = 'invoice.line'
#
#     codigo_descripcion = fields.Char(string="Descripción", compute='_compute_codigo_descripcion')
#
#     @api.depends('product_id')
#     def _compute_codigo_descripcion(self):
#         self.name