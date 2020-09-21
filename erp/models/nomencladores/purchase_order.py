# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderTemplate(models.Model):
    _inherit = 'purchase.order'

    sale_orders = fields.Many2one('res.company', string='Compañía', required=True,
                            default=lambda self: self.env['res.company']._company_default_get())

    sale_orders = fields.Many2many('sale.order', 'erp_sale_order_purchase_orders', 'sale_id', 'purchase_id', 'Órdenes de venta:')

    @api.onchange('sale_orders')
    def sale_orders_change(self):


        for purchase_order in self:
            for sale_order in purchase_order.sale_orders:
                raise except_orm(sale_order.order_line)
                for sale_order_line in sale_order.order_line:
                    is_present = False
                    for purchase_line in purchase_order.order_line:
                        if purchase_line.product_id is not False and sale_order_line.product_id is not False \
                            and purchase_line.product_id.id == sale_order_line.product_id.id:
                            is_present = True
                            purchase_line.product_qty += sale_order_line.product_qty
                            break
                    raise except_orm(is_present)
                    if is_present is False:

                        purchase_order.order_line.append({
                            'product_id': sale_order_line.product_id.id,
                            'name': sale_order_line.name,
                            'product_qty': sale_order_line.product_qty,
                            'product_uom': sale_order_line.product_uom,
                            'price_unit': sale_order_line.price_unit,
                            'taxes_id': sale_order_line.taxes_id,
                            'price_subtotal': sale_order_line.price_subtotal,
                            'price_total': sale_order_line.price_total,
                            'price_tax': sale_order_line.price_tax,
                            'purchase_id': purchase_order.id,
                            'state': sale_order_line.state,
                            'qty_invoiced': sale_order_line.qty_invoiced,
                            'qty_received': sale_order_line.qty_received,
                            'partner_id': sale_order_line.partner_id,
                            'currency_id': sale_order_line.currency_id,
                        })


