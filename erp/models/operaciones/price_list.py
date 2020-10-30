# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning


class PriceListTemplate(models.Model):
    _inherit = 'product.pricelist'

    purchase_order = fields.Many2one('purchase.order', string='Purchase order')

    @api.onchange('purchase_order')
    def purchase_order_change(self):

        for pricelist in self:
            if pricelist.purchase_order is not False:

                purchase_order = pricelist.purchase_order
                pricelist.item_ids.unlink();

                new_lines = []

                for purchase_line in purchase_order.order_line:
                    new_line = {
                        'base': 'list_price',
                        'applied_on': '1_product',
                        'pricelist_id': pricelist.id,
                        'product_tmpl_id': purchase_line.product_id.id,
                        'price_discount': 0,
                        'min_quantity': 0,
                        'compute_price': 'fixed',
                    }


                    # self.env['product.pricelist.item'].create({
                    #     'base': 'list_price',
                    #     'applied_on': '1_product',
                    #     'pricelist_id': pricelist.id,
                    #     'product_tmpl_id': product_template.id,
                    #     'price_discount': 20,
                    #     'min_quantity': 2,
                    #     'compute_price': 'formula',
                    # })

                    new_lines.append(new_line)
                #
                #
                # self.item_ids = new_lines




class PriceListItemTemplate(models.Model):
    _inherit = 'product.pricelist.item'

    purchase_order_line = fields.Many2one('purchase.order.line', string='Order Line')
    purchase_price = fields.Float(string='Purchase price', digits=dp.get_precision('Product Price'), related='purchase_order_line.price_unit')
    # purchase_price = fields.Monetary(string='Purchase price', related='purchase_order_line.price_unit')





