# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.misc import formatLang, get_lang
from odoo.tools import float_is_zero, float_compare
from itertools import groupby


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order'

    def _tipo_oferta_defult(self):
        tipo_oferta_defult = False

        encontrado = self.env['erp.nomencladores.tipo_oferta'].search([('id', '=', 1)])

        if encontrado is not False and len(encontrado) > 0:
            tipo_oferta_defult = 1

        return tipo_oferta_defult

    def _estado_de_oferta_defult(self):
        estado_de_oferta_defult = False

        encontrado = self.env['erp.nomencladores.estado_oferta'].search([('id', '=', 4)])

        if encontrado is not False and len(encontrado) > 0:
            estado_de_oferta_defult = 4

        return estado_de_oferta_defult


    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")


    condiciones = fields.Html('Condiciones')

    discount_total = fields.Monetary(compute='_discount_total', string='Discount', store=True)
    # amount_without_discount_total = fields.Monetary(compute='_amount_without_discount_total', store=True)



    # Presentation letter
    nombre_oferta = fields.Char()
    concepto = fields.Char()
    tipo_oferta = fields.Many2one('erp.nomencladores.tipo_oferta', default=_tipo_oferta_defult)
    estado_oferta = fields.Many2one('erp.nomencladores.estado_oferta', string ="Estado de oferta", default=_estado_de_oferta_defult)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    representante = fields.Many2one('erp.nomencladores.representante_cliente')
    representantes_en_copia = fields.Many2many('erp.nomencladores.representante_cliente', 'erp_operaciones_oferta_representantes_cc', 'oferta_id', 'representante_id', 'Cc:')

    marcas_encabezado = fields.Char(default="Por este medio, le comunicamos nuestra mejor oferta de productos de marca ")
    marcas = fields.Many2many('erp.nomencladores.marca', 'erp_operaciones_oferta_marcas', 'oferta_id', 'marca_id', 'Marcas')

    proveedor = fields.Many2one('res.partner', domain="{'res_partner_search_mode': 'supplier'}")
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    # ('usage', '=', 'customer')
    # incoterm = fields.Many2one('erp.nomencladores.incoterm')

    embalaje_nomenclador = fields.Many2one('erp.nomencladores.embalaje')
    embalaje = fields.Text('Embalaje')

    pais = fields.Many2one('res.country', string='País')
    puerto_de_origen = fields.Many2one('erp.nomencladores.puerto', domain="[('pais', '=', pais)]")
    pais_puerto_encabezado = fields.Char()
    pais_puerto = fields.Char()

    # dias_para_entregar = fields.Many2one('erp.nomencladores.dias_para_cobros_y_pagos')
    # etapa_entrega = fields.Many2one('erp.nomencladores.etapa')
    #
    # dias_para_entregar_etapa_entrega_a_mostar = fields.Char(string="Validez de la oferta a mostrar")

    pago_nomenclador = fields.Many2one('erp.nomencladores.pago_nomenclador')
    pago = fields.Text('Pago')
    porciento_total_mercancia = fields.Float(digits=dp.get_precision('dosDecimales'))
    dias_para_pagar = fields.Many2one('erp.nomencladores.dias_para_cobros_y_pagos')
    etapa_pago = fields.Many2one('erp.nomencladores.etapa')
    interes_anual = fields.Float(digits=dp.get_precision('dosDecimales'))

    garantia_nomenclador = fields.Many2one('erp.nomencladores.garantia_nomenclador')
    garantia = fields.Text('Garantia')

    descuento = fields.Monetary(string='% descuento', currency_field='currency_id')



    tipo_oferta = fields.Many2one('erp.nomencladores.tipo_oferta', default=_tipo_oferta_defult)
    estado_oferta = fields.Many2one('erp.nomencladores.estado_oferta', string ="Estado de oferta", default=_estado_de_oferta_defult)

    partida_arancelaria_oferta = fields.Char()

    # validez_oferta_dias = fields.Integer(string="Validez de la oferta")
    # validez_oferta_compute = fields.Date(compute='_validez_oferta_compute')
    #
    # validez_oferta_a_mostrar = fields.Char(string="Validez de la oferta a mostrar")

    observaciones = fields.Html('Observaciones')

    firma = fields.Many2one('erp.nomencladores.firma')



    #Las fichas técnicas y sus dependientes
    manual_de_usuario_espannol = fields.Boolean('El manual del usuario de cada equipo está en español', default=False)
    fichas_tecnicas = fields.Boolean('En adjunto fichas técnicas', default=False)
    certificados_inhim = fields.Boolean('certificados del INHIM', default=False)
    certificados_onure = fields.Boolean('certificados de la ONURE', default=False)
    vision_explotada = fields.Boolean('Vision explotada con listas y partes', default=False)

    homologados_en_cuba = fields.Boolean('Todos los modelos ofertados están homologados para su venta en Cuba', default=False)



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


    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))


            if not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves