# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

from openerp.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderLineTemplate(models.Model):
    _inherit = 'sale.order.line'

    discount_total = fields.Monetary(string='Discount', readonly=True, store=True)

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLineTemplate, self).product_id_change()
        self.name = self.product_id.descripcion_cliente

        return result
