# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning

from odoo.tools import float_repr


class PriceListTemplate(models.Model):
    _inherit = 'product.pricelist'





class PriceListItemTemplate(models.Model):
    _inherit = 'product.pricelist.item'

    def _default_pricelist_id(self):
        return self.env['product.pricelist'].search([
            '|', ('company_id', '=', False),
            ('company_id', '=', self.env.company.id)], limit=1)

    purchase_order_line = fields.Many2one('purchase.order.line', string='Order Line')
    purchase_price = fields.Float(string='Purchase price', digits=dp.get_precision('Product Price'), related='purchase_order_line.price_unit')
    # purchase_price = fields.Monetary(string='Purchase price', related='purchase_order_line.price_unit')

    purchase_order = fields.Many2one('purchase.order', string='Purchase order')

    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', index=True, ondelete='cascade', required=True, default=_default_pricelist_id)
    item_currency_id = fields.Many2one('res.currency', 'Currency', related='pricelist_id.currency_id')

    price_purchase = fields.Float('Price Purchase', default=0, digits=(16, 2), compute='_compute_price_purchase', store=True)
    price_discount = fields.Float('Margin', default=0, digits=(16, 2))


    spare_parts_percent = fields.Float('Spare parts %', default=0, digits=(16, 2))
    spare_parts = fields.Monetary(string='Spare parts', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    transit_percent = fields.Float('Transit %', default=0, digits=(16, 2))
    transit = fields.Monetary(string='Transit', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    fob_percent = fields.Float('FOB %', default=0, digits=(16, 2))
    fob = fields.Monetary(string='FOB', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    inspection_percent = fields.Float('Inspection %', default=0, digits=(16, 2))
    inspection = fields.Monetary(string='Inspection', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    freight_percent = fields.Float('Freight %', default=0, digits=(16, 2))
    freight = fields.Monetary(string='Freight', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    insurance_percent = fields.Float('Insurance %', default=0, digits=(16, 2))
    insurance = fields.Monetary(string='Insurance', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    issuing_percent = fields.Float('BL Issuing %', default=0, digits=(16, 2))
    issuing = fields.Monetary(string='BL Issuing', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    zeus_margin_percent = fields.Float('Zeus margin %', default=0, digits=(16, 2))
    zeus_margin = fields.Monetary(string='Zeus margin', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    marketing_percent = fields.Float('Marketing %', default=0, digits=(16, 2))
    marketing = fields.Monetary(string='Marketing', currency_field='item_currency_id', compute='_compute_part_prices', store=True)

    total_percent = fields.Float('Total %', default=0, digits=(16, 2), compute='_compute_part_prices', store=True)
    total_margin = fields.Monetary(string='Total margin', currency_field='item_currency_id', compute='_compute_part_prices', store=True)


    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula')], index=True, default='formula', required=True)


    base = fields.Selection([
        ('purchase', 'Purchase Price'),
        ('list_price', 'Sales Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist')], "Based on",
        default='purchase', required=True,
        help='Base price for computation.\n'
             'Purchase Price: The base price will be the Purchase Price.\n'
             'Sales Price: The base price will be the Sales Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')


    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge', 'price_purchase')
    def _get_pricelist_item_name_price(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s") % (item.product_id.with_context(display_default_code=False).display_name)
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                decimal_places = self.env['decimal.precision'].precision_get('Product Price')
                if item.currency_id.position == 'after':
                    item.price = "%s %s" % (
                        float_repr(
                            item.fixed_price,
                            decimal_places,
                        ),
                        item.currency_id.symbol,
                    )
                else:
                    item.price = "%s %s" % (
                        item.currency_id.symbol,
                        float_repr(
                            item.fixed_price,
                            decimal_places,
                        ),
                    )
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount") % (item.percent_price)
            else:
                item.price = _("%s %% discount and %s surcharge") % (item.price_discount, item.price_surcharge)



    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        if self.compute_price != 'fixed':
            self.fixed_price = 0.0
        if self.compute_price != 'percentage':
            self.percent_price = 0.0
        if self.compute_price != 'formula':
            self.update({
                'price_purchase': 0.0,
                'price_discount': 0.0,
                'price_surcharge': 0.0,
                'price_round': 0.0,
                'price_min_margin': 0.0,
                'price_max_margin': 0.0,
            })

    @api.depends('purchase_order')
    def _compute_price_purchase(self):
        for price_item in self:
            sum = 0.0

            for order_line in price_item.purchase_order.order_line:
                if price_item.applied_on == '3_global':
                    sum += order_line.price_total

                if price_item.applied_on == '1_product'  \
                    and order_line.product_id.id == price_item.product_tmpl_id.id:
                    sum += order_line.price_total

            price_item.price_purchase = sum


    @api.depends('price_purchase', 'spare_parts_percent', 'transit_percent', 'fob_percent', 'inspection_percent'
                 , 'freight_percent', 'insurance_percent', 'issuing_percent', 'zeus_margin_percent', 'marketing_percent')
    def _compute_part_prices(self):
        for price_item in self:
            price_item.spare_parts = 0.0
            spare_parts_total = 0.0

            if price_item.spare_parts_percent is not False and price_item.spare_parts_percent != 100:
                spare_parts_total = price_item.price_purchase / (1 - price_item.spare_parts_percent / 100)
                price_item.spare_parts = spare_parts_total - price_item.price_purchase


            price_item.transit = 0.0
            transit_total = 0.0

            if price_item.transit_percent is not False and price_item.transit_percent != 100:
                transit_total = spare_parts_total / (1 - price_item.transit_percent / 100)
                price_item.transit = transit_total - spare_parts_total


            price_item.fob = 0.0
            fob_total = 0.0

            if price_item.fob_percent is not False and price_item.fob_percent != 100:
                fob_total = transit_total / (1 - price_item.fob_percent / 100)
                price_item.fob = fob_total - transit_total


            price_item.inspection = 0.0
            inspection_total = 0.0

            if price_item.inspection_percent is not False and price_item.inspection_percent != 100:
                inspection_total = fob_total / (1 - price_item.inspection_percent / 100)
                price_item.inspection = inspection_total - fob_total


            price_item.freight = 0.0
            freight_total = 0.0

            if price_item.freight_percent is not False and price_item.freight_percent != 100:
                freight_total = inspection_total / (1 - price_item.freight_percent / 100)
                price_item.freight = freight_total - inspection_total


            price_item.insurance = 0.0
            insurance_total = 0.0

            if price_item.insurance_percent is not False and price_item.insurance_percent != 100:
                insurance_total = freight_total / (1 - price_item.insurance_percent / 100)
                price_item.insurance = insurance_total - freight_total


            price_item.issuing = 0.0
            issuing_total = 0.0

            if price_item.issuing_percent is not False and price_item.issuing_percent != 100:
                issuing_total = insurance_total / (1 - price_item.issuing_percent / 100)
                price_item.issuing = issuing_total - insurance_total


            price_item.zeus_margin = 0.0
            zeus_margin_total = 0.0

            if  price_item.zeus_margin_percent is not False and price_item.zeus_margin_percent != 100:
                zeus_margin_total = issuing_total / (1 - price_item.zeus_margin_percent / 100)
                price_item.zeus_margin = zeus_margin_total - issuing_total


            price_item.marketing = 0.0
            marketing_total = 0.0

            if price_item.marketing_percent is not False and price_item.marketing_percent != 100:
                marketing_total = zeus_margin_total / (1 - price_item.marketing_percent / 100)
                price_item.marketing = marketing_total - zeus_margin_total


            # price_item.total_percent = price_item.spare_parts_percent + price_item.transit_percent \
            #                       + price_item.fob_percent + price_item.inspection_percent \
            #                       + price_item.freight_percent + price_item.insurance_percent \
            #                       + price_item.issuing_percent + price_item.zeus_margin_percent \
            #                       + price_item.marketing_percent

            price_item.total_margin = price_item.price_purchase + price_item.spare_parts + price_item.transit \
                      + price_item.fob + price_item.inspection \
                      + price_item.freight + price_item.insurance \
                      + price_item.issuing + price_item.zeus_margin \
                      + price_item.marketing


            price_item.total_percent = 0.00
            if price_item.total_margin != 0:
                price_item.total_percent = (price_item.total_margin - price_item.price_purchase) / price_item.total_margin * 100



    @api.onchange('price_purchase', 'spare_parts_percent', 'transit_percent', 'fob_percent', 'inspection_percent'
                  , 'freight_percent', 'insurance_percent', 'issuing_percent', 'zeus_margin_percent', 'marketing_percent')
    def _compute_part_prices_change(self):
        for price_item in self:
            price_item._compute_part_prices()



