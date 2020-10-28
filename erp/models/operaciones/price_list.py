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
    #     # pass
    #     raise except_orm(self)
    # #
        for purchaseOrder in self:
            raise except_orm("E")




class PriceListItemTemplate(models.Model):
    _inherit = 'product.pricelist.item'

    purchase_order_line = fields.Many2one('purchase.order.order_line', string='Order Line')
    purchase_price = fields.Float(string='Purchase price', digits=dp.get_precision('Product Price'), related='purchase_order_line.price_unit')
    # purchase_price = fields.Monetary(string='Purchase price', related='purchase_order_line.price_unit')





