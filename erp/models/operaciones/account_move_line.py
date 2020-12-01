# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.misc import formatLang, get_lang



class AccountMoveLineTemplate(models.Model):
    _inherit = 'account.move.line'

    account_id = fields.Many2one('account.account', string='Account', index=True, ondelete="restrict", check_company=True,
        domain=[('deprecated', '=', False)])

    item_currency_id = fields.Many2one('res.currency', 'Currency', related='account_id.currency_id')

    sale_percent = fields.Float('Sale comision%', default=0, digits=(16, 2), store=True)
    sale = fields.Monetary(string='Sale Comision', currency_field='item_currency_id', store=True)


    sale_order_line = fields.Many2one('sale.order.line', string ="Price list item")