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
        for purchaseOrder in self:
            purchaseOrder.price_list.unlink();

            for purchase_line in purchaseOrder.order_line:
                raise except_orm(purchase_line.price_unit)




class PriceListItemTemplate(models.Model):
    _inherit = 'product.pricelist.item'

    purchase_order_line = fields.Many2one('purchase.order.line', string='Order Line')
    purchase_price = fields.Float(string='Purchase price', digits=dp.get_precision('Product Price'), related='purchase_order_line.price_unit')
    # purchase_price = fields.Monetary(string='Purchase price', related='purchase_order_line.price_unit')





