# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools.misc import formatLang, get_lang
from odoo.tools import float_is_zero, float_compare
from itertools import groupby

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime, timedelta


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
    fecha_valor = fields.Date(string="Fecha")
    nombre_oferta = fields.Char()
    concepto = fields.Char()
    tipo_oferta = fields.Many2one('erp.nomencladores.tipo_oferta', default=_tipo_oferta_defult)
    estado_oferta = fields.Many2one('erp.nomencladores.estado_oferta', string ="Estado de oferta", default=_estado_de_oferta_defult)
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    representante = fields.Many2one('erp.nomencladores.representante_cliente')
    representantes_en_copia = fields.Many2many('erp.nomencladores.representante_cliente', 'erp_operaciones_oferta_representantes_cc', 'oferta_id', 'representante_id', 'Cc:')

    marcas_encabezado = fields.Char(default="Por este medio, le comunicamos nuestra mejor oferta de productos de marca ")
    marcas = fields.Many2many('erp.nomencladores.marca', 'erp_operaciones_oferta_marcas', 'oferta_id', 'marca_id', 'Marcas')

    proveedor = fields.Many2one('res.partner')
    cliente = fields.Many2one('res.partner')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

    # ('usage', '=', 'customer')
    incoterm = fields.Many2one('account.incoterms')

    embalaje_nomenclador = fields.Many2one('erp.nomencladores.embalaje')
    embalaje = fields.Text('Embalaje')

    pais = fields.Many2one('res.country', string='País')
    puerto_de_origen = fields.Many2one('erp.nomencladores.puerto', domain="[('pais', '=', pais)]")
    pais_puerto_encabezado = fields.Char()
    pais_puerto = fields.Char()

    dias_para_entregar = fields.Many2one('erp.nomencladores.dias_para_cobros_y_pagos')
    etapa_entrega = fields.Many2one('erp.nomencladores.etapa')

    dias_para_entregar_etapa_entrega_a_mostar = fields.Char(string="Validez de la oferta a mostrar")

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

    validez_oferta_dias = fields.Integer(string="Validez de la oferta")

    validez_oferta_a_mostrar = fields.Char(string="Validez de la oferta a mostrar")

    observaciones = fields.Html('Observaciones')

    firma = fields.Many2one('erp.nomencladores.firma')



    #Las fichas técnicas y sus dependientes
    manual_de_usuario_espannol = fields.Boolean('El manual del usuario de cada equipo está en español', default=False)
    fichas_tecnicas = fields.Boolean('En adjunto fichas técnicas', default=False)
    certificados_inhim = fields.Boolean('certificados del INHIM', default=False)
    certificados_onure = fields.Boolean('certificados de la ONURE', default=False)
    vision_explotada = fields.Boolean('Vision explotada con listas y partes', default=False)

    homologados_en_cuba = fields.Boolean('Todos los modelos ofertados están homologados para su venta en Cuba', default=False)


    otra_oferta_traer_productos = fields.Many2one('sale.order')

    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced', readonly=True)
    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", readonly=True, copy=False, search="_search_invoice_ids")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_get_invoice_status', store=True, readonly=True)




    #Campos para configurar la tabla a mostrar en el reporte "Imprimir Ofertas"
    image = fields.Boolean('Imagen', default=True)
    modelo = fields.Boolean('Modelo', default=True) #name
    marca = fields.Boolean('Marca', default=True)
    tipo_de_producto = fields.Boolean('Línea', default=True)
    descripcion_cliente = fields.Boolean('Descripcion-cliente', default=True)
    descripcion_proveedor = fields.Boolean('descripcion-cliente_ingles', default=False)
    sintesis = fields.Boolean(u'Síntesis', default=False)

    codigo_cliente = fields.Boolean('codigo-cliente', default=False)
    codigo_proveedor = fields.Boolean('Código DL / SAP', default=False)

    partida_arancelaria = fields.Boolean('partida arancelaria', default=True)
    codigo_de_barra = fields.Boolean('codigo de barra', default=True)
    tipo_de_espiga = fields.Boolean('tipo de espiga', default=True)

    volumen_caja_master = fields.Boolean('volumen caja master', default=True)
    cantidad_por_caja_master = fields.Boolean('cantidad por caja master', default=True)
    cantidad_minima_de_orden = fields.Boolean('cantidad mínima de orden', default=True)

    medidas = fields.Boolean('Medida', default=False)


    cantidad_producto = fields.Boolean('Cantidad de producto', default=True)
    volumen_total_de_linea_producto = fields.Boolean('Volumen total', default=True)
    importe_total_de_linea = fields.Boolean('Importe total', default=True)


    explotado = fields.Boolean('Explotado en español', default=False)
    explotado_ingles = fields.Boolean('Explotado en inglés', default=False)
    ficha_tecnica = fields.Boolean('Ficha técnica en español', default=False)
    ficha_tecnica_ingles = fields.Boolean('Ficha técnica en inglés', default=False)
    caja = fields.Boolean('Caja', default=False)
    manual_de_usuario = fields.Boolean('Manual de usuario en español', default=False)
    certificado_de_onure = fields.Boolean('Manual de usuario en inglés', default=False)


    imprimir_totales_oferta = fields.Boolean('Imprimir totales oferta', default=True)



    #Campos para calcular los importes totales de la oferta
    autocalcular = fields.Boolean('Autocalcular', default=True)

    exw = fields.Monetary(string='EXW', currency_field='currency_id')
    flete_terrestre = fields.Monetary(string='Flete terrestre', currency_field='currency_id')
    mercancia = fields.Monetary(string='Mercancía', currency_field='currency_id')
    flete = fields.Monetary(string='Flete', currency_field='currency_id')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    inspeccion = fields.Monetary(string='Inspección', currency_field='currency_id')
    financiamiento_importe = fields.Monetary(string='Financiamiento', currency_field = 'currency_id')

    importe_total = fields.Monetary(string='Importe total sin repuestos', currency_field='currency_id')

    importe_repuestos_sin_descuento = fields.Monetary(string='Importe total repuestos', currency_field='currency_id')
    importe_descuento = fields.Monetary(string='Descuento sobre importe mercancías', currency_field='currency_id')

    porciento_repuestos = fields.Float(digits=dp.get_precision('dosDecimales'))
    opcional_1 = fields.Char()
    importe_opcional_1 = fields.Monetary(string='', currency_field='currency_id')
    opcional_2 = fields.Char()
    importe_opcional_2 = fields.Monetary(string='', currency_field='currency_id')

    importe_repuestos_con_descuento = fields.Monetary(string='Importe total repuestos con descuento', currency_field='currency_id')



    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    def otra_oferta_traer_productos_funcion(self):
        for order in self:
            if order.otra_oferta_traer_productos.id is not False:
                for linea_otra_oferta_traer_productos in order.otra_oferta_traer_productos.order_line:
                    existe = False

                    raise except_orm("A")

                    for linea in order.order_line:
                        if linea.producto.id == linea_otra_oferta_traer_productos.producto.id:
                            existe = True


                    if existe is False:
                        linea_otra_oferta_traer_productos = linea_otra_oferta_traer_productos.copy()
                        linea_otra_oferta_traer_productos.oferta = order.id
                        linea_otra_oferta_traer_productos.importe_unitario = 0
                        linea_otra_oferta_traer_productos.importe_total_de_linea_producto = 0

    def eliminar_productos_cantidad_producto_actual_cero(self):
        for linea in self.order_line:
            if linea.product_uom_qty == 0:
                linea.unlink()


    def actualizar_desde_el_nomenclador(self):
        pass
        # for linea in self.order_line:
        #     linea.foto = linea.producto.image_variant
        #     linea.tipo_de_producto = linea.producto.tipo_de_producto.name
        #     linea.orden_marca = linea.producto.marca.orden
        #     linea.cantidad_por_caja_master = linea.producto.cantidad_por_caja_master
        #
        #     linea.volumen_caja_master = linea.producto.volumen_caja_master
        #     linea.cantidad_producto_total_oferta = linea.producto.cantidad_minima_de_orden
        #
        #     if linea.cantidad_por_caja_master != 0:
        #         linea.volumen_total_de_linea_producto = linea.product_uom_qty * linea.volumen_caja_master / linea.cantidad_por_caja_master
        #
        #
        # for entrega in self.entregas:
        #     for contenedor_20 in entrega.contenedores_20:
        #         for linea in contenedor_20.contenedor.lineas_contenedor_20:
        #             linea.foto = linea.producto.image_variant
        #             linea.tipo_de_producto = linea.producto.tipo_de_producto.name
        #             linea.orden_marca = linea.producto.marca.orden
        #             linea.cantidad_por_caja_master = linea.producto.cantidad_por_caja_master
        #             linea.cantidad_producto_total_oferta = linea.producto.cantidad_minima_de_orden
        #
        #             if linea.cantidad_por_caja_master != 0:
        #                 linea.volumen = linea.cantidad_producto * linea.producto.volumen_caja_master / linea.cantidad_por_caja_master
        #
        #
        #     for contenedor_40 in entrega.contenedores_40:
        #         for linea in contenedor_40.contenedor.lineas_contenedor_40:
        #             linea.foto = linea.producto.image_variant
        #             linea.tipo_de_producto = linea.producto.tipo_de_producto.name
        #             linea.orden_marca = linea.producto.marca.orden
        #             linea.cantidad_por_caja_master = linea.producto.cantidad_por_caja_master
        #             linea.cantidad_producto_total_oferta = linea.producto.cantidad_minima_de_orden
        #
        #             if linea.cantidad_por_caja_master != 0:
        #                 linea.volumen = linea.cantidad_producto * linea.producto.volumen_caja_master / linea.cantidad_por_caja_master
        #
        #
        #     for contenedor_40_hq in entrega.contenedores_40_hq:
        #         for linea in contenedor_40_hq.contenedor.lineas_contenedor_40_hq:
        #             linea.foto = linea.producto.image_variant
        #             linea.tipo_de_producto = linea.producto.tipo_de_producto.name
        #             linea.orden_marca = linea.producto.marca.orden
        #             linea.cantidad_por_caja_master = linea.producto.cantidad_por_caja_master
        #             linea.cantidad_producto_total_oferta = linea.producto.cantidad_minima_de_orden
        #
        #             if linea.cantidad_por_caja_master != 0:
        #                 linea.volumen = linea.cantidad_producto * linea.producto.volumen_caja_master / linea.cantidad_por_caja_master


    def poner_cantidades_a_cero(self):
        pass

        for linea in self.order_line:
            linea.product_uom_qty = 0
            linea.volumen_total_de_linea_producto = 0
            linea.importe_total_de_linea_producto = 0

        self.actualizar_mercancia()

    @api.onchange('concepto', 'cliente', 'fecha_valor')
    def _onchange_concepto_cliente(self):
        #Modificando el nombre de la oferta

        for order in self:
            order.nombre_oferta = ""

            if order.cliente.name is not False:
                order.nombre_oferta += order.cliente.name.capitalize()

            if order.concepto is not False:
                order.nombre_oferta += ", " + order.concepto

            if order.fecha_valor is not False:
                order.nombre_oferta += ", " + str(order.fecha_valor)

    @api.onchange('representante')
    def _onchange_representante(self):
        if self.representante.empresa is not False:
            self.cliente = self.representante.empresa.id

    @api.onchange('garantia_nomenclador')
    def _onchange_garantia_nomenclador(self):
        # if self.garantia is False and self.garantia_nomenclador.name is not False:
            self.garantia = self.garantia_nomenclador.name

            if self.garantia_nomenclador.name == 'Se realizará un descuento de hasta el 1% del valor FOB de la mercancía en la compra de repuestos.':
                self.descuento = 1

    @api.onchange('pago_nomenclador')
    def _onchange_pago_nomenclador(self):
        # if self.pago is False and self.pago_nomenclador.name is not False:
        self.pago = self.pago_nomenclador.name



    @api.onchange('embalaje_nomenclador')
    def _onchange_embalaje_nomenclador(self):
        # if self.embalaje is False and self.embalaje_nomenclador.name is not False or self.embalaje == "":
            self.embalaje = self.embalaje_nomenclador.name

    @api.onchange('manual_de_usuario_espannol', 'fichas_tecnicas', 'certificados_inhim', 'certificados_onure', 'vision_explotada')
    def _onchange_tasa(self):

        if self.vision_explotada is True:
            self.explotado = True
        else:
            self.explotado = False

        if self.manual_de_usuario_espannol is True:
            self.manual_de_usuario = True
        else:
            self.manual_de_usuario = False

        if self.fichas_tecnicas is True:
            self.ficha_tecnica = True
        else:
            self.ficha_tecnica = False

        if self.certificados_onure is True:
            self.certificado_de_onure = True
        else:
            self.certificado_de_onure = False

        if self.certificados_inhim is True or self.certificados_onure is True:
            self.homologados_en_cuba = True
        else:
            self.homologados_en_cuba = False


    def marcas_to_string(self):

        for order in self:
            marcas = ""

            cantidad_de_marcas_restantes = len(order.marcas)

            for marca in order.marcas:
                marcas += str(marca.name)

                if len(order.marcas) > 1:
                    if cantidad_de_marcas_restantes > 2:
                        marcas += ", "
                        cantidad_de_marcas_restantes -= 1
                    elif cantidad_de_marcas_restantes == 2:
                        marcas += " y "
                        cantidad_de_marcas_restantes -= 1


            marcas += "."

            # if len(marcas) - 2 > 0:
            #     marcas = marcas[0:len(marcas) - 2] + "."

            return marcas


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

            if order.autocalcular is True:
                order.mercancia = amount_untaxed

            self.calcular_importes(order)



    def calcular_importes(self, order):
        order.importe_repuestos_con_descuento = order.exw + order.flete_terrestre + order.mercancia \
                + order.flete + order.seguro + order.inspeccion + order.financiamiento_importe + order.importe_descuento \
                + order.importe_opcional_1 + order.importe_opcional_2


    def actualizar_mercancia(self):
        self.calcular_importes(self)


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


    def imprimir_carta_tipo(self):
        #Se exportan, en caso de estar marcados, los distintos adjuntos que pueda contener el producto
        # self.exportar_adjuntos()

        for order in self:
            un_solo_producto = 1
            if len(order.order_line) > 1:
                un_solo_producto = 0

            view_id = self.env.ref('erp.imprimir_carta_tipo_report').id
            data = {}
            data["oferta"] = view_id
            data["un_solo_producto"] = un_solo_producto
            # return self.env['report'].get_action(self, 'erp.imprimir_carta_tipo_report', data=data)

            return self.env.ref('erp.imprimir_carta_tipo_report').report_action(self, data=data)