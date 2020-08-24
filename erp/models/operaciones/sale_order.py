# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order'

    condiciones = fields.Html('Condiciones')

    discount_total = fields.Monetary(compute='_discount_total', string='Discount', store=True)
    amount_without_discount_total = fields.Monetary(compute='_amount_without_discount_total', store=True)

    @api.depends('order_line.price_total')
    def _discount_total(self):
        self.discount_total = 0.00

        """
        Compute the amounts of the SO line.
        """
        for line in self.order_line:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)

            price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)

            self.discount_total += -(taxes['total_excluded'] - taxes_discounted['total_excluded'])


    @api.depends('order_line.price_total')
    def _amount_without_discount_total(self):
        self.amount_without_discount_total = 0.00


        """
        Compute the amounts of the SO line.
        """
        for line in self.order_line:
            price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)

            self.amount_without_discount_total += taxes_discounted['total_excluded']

            raise except_orm(self.amount_without_discount_total)



