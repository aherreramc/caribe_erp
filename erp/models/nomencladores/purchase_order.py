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