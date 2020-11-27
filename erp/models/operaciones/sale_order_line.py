# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.misc import formatLang, get_lang



class SaleOrderLineTemplate(models.Model):
    _inherit = 'sale.order.line'

    discount_total = fields.Monetary(string='Discount', readonly=True, store=True)

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    item_currency_id = fields.Many2one('res.currency', 'Currency', related='order_id.currency_id')

    # sale_percent = fields.Float('Sale comision%', default=0, digits=(16, 2), compute='_compute_sale_comision')
    # sale = fields.Monetary(string='Sale Comision', currency_field='item_currency_id', compute='_compute_sale_comision', store=True)

    sale_percent = fields.Float('Sale comision%', default=0, digits=(16, 2), store=True)
    sale = fields.Monetary(string='Sale Comision', currency_field='item_currency_id', store=True)

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLineTemplate, self).product_id_change()
        self.name = self.product_id.descripcion_cliente

        return result



    price_list_item = fields.Many2one('product.pricelist.item', string ="Price list item")


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

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)

        for price_list_item in self.order_id.pricelist_id.item_ids:
            if price_list_item.base == 'purchase':
                if price_list_item.product_tmpl_id.id == self.product_id.product_tmpl_id.id:
                    vals['price_unit'] = price_list_item.total_margin
                    vals['price_list_item'] = price_list_item.id



        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result


    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

            if line.price_list_item.id is not False:
                if line.sale_percent != 100:
                    line.sale_percent = line.price_list_item.sale_percent - line.discount
                    line.sale = price / (1 - line.sale_percent / 100)


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:


            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

            if line.price_list_item.id is not False:
                if line.sale_percent != 100:
                    line.sale_percent = line.price_list_item.sale_percent - line.discount
                    line.sale = line.price_list_item.price_before_sale_comision() \
                                - line.price_list_item.price_before_sale_comision() / (1 - line.sale_percent / 100)


