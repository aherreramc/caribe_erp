# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning


class PriceListTemplate(models.Model):
    _inherit = 'product.pricelist'

    purchaseOrder = fields.Many2one('purchase.order', string='Purchase order')

    @api.onchange('purchaseOrder')
    def purchaseOrder(self):
        raise except_orm(self)

        for purchaseOrder in self:
            raise except_orm("E")
