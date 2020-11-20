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
    # amount_without_discount_total = fields.Monetary(compute='_amount_without_discount_total', store=True)

    @api.depends('order_line.price_total')
    def _discount_total(self):

        for order in self:
            order.discount_total = 0.00

            """
            Compute the amounts of the SO line.
            """
            for line in order.order_line:
                price = line.price_unit
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_id)

                price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_id)

                order.discount_total += -(taxes['total_excluded'] - taxes_discounted['total_excluded'])


    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.pricelist_id.id is not False:
                order.update({
                    'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax - self.discount_total,
                })


    # @api.depends('order_line.price_total')
    # def _amount_without_discount_total(self):
    #     self.amount_without_discount_total = 0.00
    #
    #
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self.order_line:
    #         price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
    #                                         product=line.product_id, partner=line.order_id.partner_id)
    #
    #         self.amount_without_discount_total += taxes_discounted['total_excluded']
    #


class SaleOrderLineTemplate(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            # line.update({
            #     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            #     'price_total': taxes['total_included'],
            #     'price_subtotal': taxes['total_excluded'],
            # })

            line.update({
                'price_tax': 1,
                'price_total': 2,
                'price_subtotal': 3,
            })

            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])


    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        return self.price_unit
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )

            raise except_orm("self._get_display_price(product)" + str(self._get_display_price(product)) \
                             + "product.taxes_id" + str(product.taxes_id) \
            + "self.tax_id" + str(self.tax_id) \
            + "self.company_id" + str(self.company_id))

            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

            raise except_orm(self.price_unit)


    @api.onchange('product_id')
    def product_id_change(self):
        self.price_unit = 4