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

    purchase_order_line = fields.Many2one('purchase.order.line', string='Order Line')
    purchase_price = fields.Float(string='Purchase price', digits=dp.get_precision('Product Price'), related='purchase_order_line.price_unit')
    # purchase_price = fields.Monetary(string='Purchase price', related='purchase_order_line.price_unit')

    purchase_order = fields.Many2one('purchase.order', string='Purchase order')

    price_purchase = fields.Float('Price Purchase', default=0, digits=(16, 2))
    price_discount = fields.Float('Margin', default=0, digits=(16, 2))


    spare_parts_percent = fields.Float('Spare parts %', default=0, digits=(16, 2))
    spare_parts = fields.Monetary(string='Spare parts cost', currency_field='pricelist_id.currency_id')

    # po_double_validation_amount = fields.Monetary(related='company_id.po_double_validation_amount', string="Minimum Amount", currency_field='company_currency_id', readonly=False)


#
#     Spare parts cost
# Transit to SZ
# FOB charges
# Inspection cost
# Sea freight cost
# Insurance cost
# BL issuing cost
# Zeus´margin
# MKT



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


