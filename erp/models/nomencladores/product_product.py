# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


class ProductProduct(models.Model):
    _inherit = 'product.product'

    purchase_price = fields.Float(string="Purchase Price", digits=dp.get_precision('dosDecimales'))


    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.company.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:

            if price_type != 'purchase':
                prices[product.id] = product[price_type] or 0.0

            if price_type == 'list_price':
                prices[product.id] += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id._convert(
                    prices[product.id], currency, product.company_id, fields.Date.today())


        return prices