# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning

from odoo.tools import float_repr


class PriceListTemplate(models.Model):
    _inherit = 'product.pricelist'

    # purchase_order = fields.Many2one('purchase.order', string='Purchase order')
    #
    # @api.onchange('purchase_order')
    # def purchase_order_change(self):
    #
    #     for pricelist in self:
    #         if pricelist.purchase_order is not False:
    #
    #             purchase_order = pricelist.purchase_order
    #             # pricelist.item_ids.unlink();
    #
    #             new_lines = []
    #
    #             for purchase_line in purchase_order.order_line:
    #                 raise except_orm(purchase_line.name)
    #                 new_line = {
    #                     'base': 'list_price',
    #                     # 'applied_on': '1_product',
    #                     # 'pricelist_id': pricelist.id,
    #                     'product_tmpl_id': purchase_line.product_id.id,
    #                     'price_discount': 0,
    #                     'min_quantity': 0,
    #                     # 'compute_price': 'fixed',
    #                 }
    #
    #
    #                 # self.env['product.pricelist.item'].create({
    #                 #     'base': 'list_price',
    #                 #     'applied_on': '1_product',
    #                 #     'pricelist_id': pricelist.id,
    #                 #     'product_tmpl_id': product_template.id,
    #                 #     'price_discount': 20,
    #                 #     'min_quantity': 2,
    #                 #     'compute_price': 'formula',
    #                 # })
    #
    #                 # new_lines.append(new_line)
    #
    #                 # self.item_ids.
    #             #
    #             #
    #             # self.item_ids = new_lines




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

    price_purchase = fields.Float('Price Purchase', default=0, digits=(16, 2), compute='_compute_price_purchase')
    price_discount = fields.Float('Margin', default=0, digits=(16, 2))


    spare_parts_percent = fields.Float('Spare parts %', default=0, digits=(16, 2))
    spare_parts = fields.Monetary(string='Spare parts', currency_field='item_currency_id')

    transit_percent = fields.Float('Transit %', default=0, digits=(16, 2))
    transit = fields.Monetary(string='Transit', currency_field='item_currency_id')

    fob_percent = fields.Float('FOB %', default=0, digits=(16, 2))
    fob = fields.Monetary(string='FOB', currency_field='item_currency_id')

    inspection_percent = fields.Float('Inspection %', default=0, digits=(16, 2))
    inspection = fields.Monetary(string='Inspection', currency_field='item_currency_id')

    freight_percent = fields.Float('Freight %', default=0, digits=(16, 2))
    freight = fields.Monetary(string='Freight', currency_field='item_currency_id')

    insurance_percent = fields.Float('Insurance %', default=0, digits=(16, 2))
    insurance = fields.Monetary(string='Insurance', currency_field='item_currency_id')

    issuing_percent = fields.Float('BL Issuing %', default=0, digits=(16, 2))
    issuing = fields.Monetary(string='BL Issuing', currency_field='item_currency_id')

    zeus_margin_percent = fields.Float('Zeus margin %', default=0, digits=(16, 2))
    zeus_margin = fields.Monetary(string='Zeus margin', currency_field='item_currency_id')

    marketing_percent = fields.Float('Marketing %', default=0, digits=(16, 2))
    marketing = fields.Monetary(string='Marketing', currency_field='item_currency_id')


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
        sum = 0.0

        for order_line in self.purchase_order.order_line:
            if self.applied_on == '3_global':
                sum += order_line.price_total

            if self.applied_on == '1_product'  \
                and order_line.product_id.id == self.pricelist_id.product_tmpl_id.id:
                sum += order_line.price_total

        self.price_purchase = sum




