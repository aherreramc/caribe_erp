# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


# class SaleOrderLineTemplate(models.Model):
#     _inherit = 'sale.order.line'
#
#     # def name_get(self):
#     #     result = []
#     #     for so_line in self.sudo():
#     #         name = '%s - %s' % (so_line.order_id.name, so_line.name and so_line.name.split('\n')[0] or so_line.product_id.name)
#     #         if so_line.order_partner_id.ref:
#     #             name = '%s (%s)' % (name, so_line.order_partner_id.ref)
#     #         result.append((so_line.id, name))
#     #     return result
#
#
#     def name_get(self):
#         result = []
#         for so_line in self.sudo():
#             name = '%s - %s' % (so_line.product_id.descripcion_cliente)
#             # if so_line.order_partner_id.ref:
#             #     name = '%s (%s)' % (name, so_line.order_partner_id.ref)
#             result.append((so_line.id, name))
#         return result
