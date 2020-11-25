# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

from openerp.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderLineTemplate(models.Model):
    _inherit = 'sale.order.line'

    discount_total = fields.Monetary(string='Discount', readonly=True, store=True)

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    item_currency_id = fields.Many2one('res.currency', 'Currency', related='order_id.currency_id')

    sale_percent = fields.Float('Sale comision%', default=0, digits=(16, 2), compute='_compute_sale_comision')
    sale = fields.Monetary(string='Sale Comision', currency_field='item_currency_id', compute='_compute_sale_comision', store=True)

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLineTemplate, self).product_id_change()
        self.name = self.product_id.descripcion_cliente

        return result


    @api.onchange('discount')
    def _compute_sale_comision_on_change(self):
        for order_line in self:
            order_line.sale_percent += 1
            order_line.sale_percent += 1
