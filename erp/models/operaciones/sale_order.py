# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.misc import formatLang, get_lang


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order'

    condiciones = fields.Html('Condiciones')

    discount_total = fields.Monetary(compute='_discount_total', string='Discount', store=True)
    # amount_without_discount_total = fields.Monetary(compute='_amount_without_discount_total', store=True)



    # Presentation letter
    concepto = fields.Char()


    marcas_encabezado = fields.Char(default="Por este medio, le comunicamos nuestra mejor oferta de productos de marca ")
    marcas = fields.Many2many('erp.nomencladores.marca', 'erp_operaciones_oferta_marcas', 'oferta_id', 'marca_id', 'Marcas')



    @api.depends('order_line.price_total')
    def _discount_total(self):

        for order in self:
            order.discount_total = 0.00

            """
            Compute the amounts of the SO line.
            """
            for line in order.order_line:
                price = line.price_unit
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_id)

                price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_id)

                order.discount_total += -(taxes['total_excluded'] - taxes_discounted['total_excluded'])


    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.pricelist_id.id is not False:
                order.update({
                    'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax - self.discount_total,
                })


    # @api.depends('order_line.price_total')
    # def _amount_without_discount_total(self):
    #     self.amount_without_discount_total = 0.00
    #
    #
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self.order_line:
    #         price_discounted = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes_discounted = line.tax_id.compute_all(price_discounted, line.order_id.currency_id, line.product_uom_qty,
    #                                         product=line.product_id, partner=line.order_id.partner_id)
    #
    #         self.amount_without_discount_total += taxes_discounted['total_excluded']
    #


class SaleOrderLineTemplate(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        # if self.order_id.pricelist_id and self.order_id.partner_id:
        #     vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

        for price_list_item in self.order_id.pricelist_id.item_ids:
            if price_list_item.base == 'purchase':
                if price_list_item.product_tmpl_id.id == self.product_id.product_tmpl_id.id:
                    # self.update({'price_unit': price_list_item.total_margin})
                    self.price_unit = price_list_item.total_margin
                    # vals['price_unit'] = price_list_item.total_margin


        # self.update(vals)

        # for price_list_item in self.order_id.pricelist_id.item_ids:
        #     if price_list_item.base == 'purchase':
        #         if price_list_item.product_tmpl_id.id == self.product_id.product_tmpl_id.id:
        #             self.update({'price_unit': price_list_item.total_margin})

        # title = False
        # message = False
        result = {}
        # warning = {}
        # if product.sale_line_warn != 'no-message':
        #     title = _("Warning for %s") % product.name
        #     message = product.sale_line_warn_msg
        #     warning['title'] = title
        #     warning['message'] = message
        #     result = {'warning': warning}
        #     if product.sale_line_warn == 'block':
        #         self.product_id = False


        return result





        # for price_list_item in self.order_id.pricelist_id.item_ids:
        #     if price_list_item.base == 'purchase':
        #         if price_list_item.product_tmpl_id.id == self.product_id.product_tmpl_id.id:
        #             self.update({'price_unit': price_list_item.total_margin})



        # result = {}
        # return result
