# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


class AccountInvoiceLineTemplate(models.Model):
    _inherit = 'account.move.line'

    codigo_descripcion = fields.Char(string="Descripción", compute='_compute_codigo_descripcion')

    @api.depends('product_id')
    def _compute_codigo_descripcion(self):

        for line in self:
            line.codigo_descripcion = "Producto: "

            if line.product_id.name is not False:
                line.codigo_descripcion += "Producto: " + line.product_id.name

            if line.name is not False:
                line.codigo_descripcion += ". " + line.name