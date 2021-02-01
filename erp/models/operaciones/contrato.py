# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
from imp import reload


from os import walk
import shutil, os
import csv
import xlsxwriter
from io import BytesIO
import collections
import string
import io
from PIL import Image


class Contrato(models.Model):
    _name = "erp.operaciones.contrato"
    _order = "fecha_valor desc"

    @api.model
    def _default_currency(self):
        return 3

    @api.model
    def _default_currency_euro(self):
        return 1

    # @api.model
    # def _default_compannia(self):
    #     return 3

    @api.model
    def _default_tasa(self):
        return 1

    def _dominio_oferta(self):
        # dominio = "[('id', 'not in', self.env['erp.operaciones.contrato'].search([]), ('ultima_version', 'is not', False))"
        #
        # if self.cliente.id is not False:
        #     dominio += ", ('cliente', '=', " + str(self.cliente.id) + ")]"
        # else:
        #     dominio += "]"
        #
        # return dominio


        dominio = "[('ultima_version', '=', 'TRUE')]"

        return dominio

    name = fields.Char(required=True, default="Nuevo Contrato")
    compannia = fields.Many2one('res.company', required=True)
    proveedor = fields.Many2one('res.partner', domain="[('supplier', '=', True)]")
    fecha_valor = fields.Date()
    fecha_entrega_documentos_banco = fields.Date()

    # Relativos al importe de la operación
    moneda_mon = fields.Many2one('res.currency', string='Moneda', default=_default_currency)
    moneda_usd = fields.Many2one('res.currency', string='Moneda', default=_default_currency)

    importe_mon = fields.Monetary(currency_field='moneda_mon')
    tasa = fields.Float(string='Tasa', digits=dp.get_precision('seisDecimales'), default=_default_tasa)
    importe_usd = fields.Monetary(currency_field='moneda_usd')

    moneda_informativa = fields.Many2one('res.currency', string='Moneda informativa', default=_default_currency_euro)
    tasa_moneda_informativa = fields.Float(string='Tasa informativa', digits=dp.get_precision('seisDecimales'),
                                           default=_default_tasa)
    importe_moneda_informativa = fields.Monetary(string='Importe informativo', currency_field='moneda_informativa')

    flete_mon = fields.Monetary(string='Flete MON', currency_field='moneda_mon')
    flete_usd = fields.Monetary(string='Flete USD', currency_field='moneda_usd')
    flete_euro = fields.Monetary(string='Flete Euro', currency_field='moneda_informativa')

    seguro_mon = fields.Monetary(string='Seguro MON', currency_field='moneda_mon')
    seguro_usd = fields.Monetary(string='Seguro USD', currency_field='moneda_usd')
    seguro_euro = fields.Monetary(string='Seguro Euro', currency_field='moneda_informativa')

    inspeccion_mon = fields.Monetary(string='Inspección MON', currency_field='moneda_mon')
    inspeccion_usd = fields.Monetary(string='Inspección USD', currency_field='moneda_usd')
    inspeccion_euro = fields.Monetary(string='Inspección Euro', currency_field='moneda_informativa')

    financiamiento_mon = fields.Monetary(string='Financiamiento MON', currency_field='moneda_mon')

    etapa_pago = fields.Many2one('erp.nomencladores.etapa')
    dias_para_pagar = fields.Many2one('erp.nomencladores.dias_para_cobros_y_pagos')

    financiamiento_mon_importe = fields.Monetary(string='Financiamiento MON', currency_field='moneda_mon')
    financiamiento_usd_importe = fields.Monetary(string='Financiamiento USD', currency_field='moneda_usd')
    financiamiento_euro_importe = fields.Monetary(string='Financiamiento USD', currency_field='moneda_informativa')

    proveedor = fields.Many2one('res.partner', domain="[('supplier_rank', '>', 0)]")
    cliente = fields.Many2one('res.partner', required=True, domain="[('customer_rank', '>', 0)]")

    descripcion_contrato_para_facturas = fields.Text('Descripción para imprimir en las facturas')
    descripcion_contrato_para_beneficiario = fields.Text('Descripción para imprimir la declaración de beneficiario')

    observaciones = fields.Text('Observaciones')

    lista_de_precios = fields.Many2one('erp.nomencladores.lista_de_precios', string='Lista de precios')

    # Campos para calcular los importes totales de la oferta
    autocalcular = fields.Boolean('Autocalcular', default=True)

    exw = fields.Monetary(string='EXW', currency_field='moneda_mon')
    flete_terrestre = fields.Monetary(string='Flete terrestre', currency_field='moneda_mon')
    mercancia = fields.Monetary(string='Mercancía', currency_field='moneda_mon')
    flete = fields.Monetary(string='Flete', currency_field='moneda_mon')
    seguro = fields.Monetary(string='Seguro', currency_field='moneda_mon')
    inspeccion = fields.Monetary(string='Inspección', currency_field='moneda_mon')
    financiamiento_importe = fields.Monetary(string='Financiamiento', currency_field='moneda_mon')

    importe_total = fields.Monetary(string='Importe total sin repuestos', currency_field='moneda_mon')

    importe_repuestos_sin_descuento = fields.Monetary(string='Importe total repuestos', currency_field='moneda_mon')
    importe_descuento = fields.Monetary(string='Descuento sobre importe mercancías', currency_field='moneda_mon')

    porciento_repuestos = fields.Float(digits=dp.get_precision('dosDecimales'))
    opcional_1 = fields.Char()
    importe_opcional_1 = fields.Monetary(string='', currency_field='moneda_mon')
    opcional_2 = fields.Char()
    importe_opcional_2 = fields.Monetary(string='', currency_field='moneda_mon')

    importe_repuestos_con_descuento = fields.Monetary(string='Importe total repuestos con descuento',
                                                      currency_field='moneda_mon')

    otro_contrato_traer_productos = fields.Many2one('erp.operaciones.contrato')

    # Carta de crédito asociada
    numero_carta_de_credito = fields.Char()
    fecha_carta_de_credito = fields.Date()

    moneda_mon_carta_de_credito = fields.Many2one('res.currency', string='Moneda', default=_default_currency)
    moneda_usd_carta_de_credito = fields.Many2one('res.currency', string='Moneda', default=_default_currency)

    importe_mon_carta_de_credito = fields.Monetary(currency_field='moneda_mon_carta_de_credito')
    tasa_carta_de_credito = fields.Float(string='Tasa', digits=dp.get_precision('seisDecimales'), default=_default_tasa)
    importe_usd_carta_de_credito = fields.Monetary(currency_field='moneda_usd_carta_de_credito')

    fecha_expiracion_carta_de_credito = fields.Date()
    fecha_ultimo_embarque_carta_de_credito = fields.Date()

    cartas_de_credito = fields.One2many('erp.operaciones.carta_de_credito', 'contrato')

    numero = fields.Char()
    concepto = fields.Char()

    # oferta = fields.Many2one('sale.order', domain=_dominio_oferta)
    oferta = fields.Many2one('sale.order')

    lineas_de_contrato = fields.One2many('erp.operaciones.linea_de_contrato', 'contrato')

    @api.model
    def create(self, vals):
        # lineas_de_contrato = vals['lineas_de_contrato']

        contrato = super(Contrato, self).create(vals)

        # for linea in contrato.lineas_de_contrato:
        #     if linea[2]['contrato'] is False:
        #         linea[2]['contrato'] = contrato.id
        #
        #         contrato.lineas_de_contrato.create({
        #         'producto' : linea[2]['producto'],
        #
        #         'tipo_de_producto' : linea[2]['tipo_de_producto'],
        #         'orden_marca' : linea[2]['orden_marca'],
        #
        #         'cantidad_por_caja_master' : linea[2]['cantidad_por_caja_master'],
        #         'volumen_caja_master' : linea[2]['volumen_caja_master'],
        #
        #         'moneda' : linea[2]['moneda'],
        #         'importe_unitario' : linea[2]['importe_unitario'],
        #         'importe_total_de_linea' : linea[2]['importe_total_de_linea'],
        #
        #         'volumen_total_de_linea_producto' : linea[2]['volumen_total_de_linea_producto'],
        #         'importe_total_de_linea_producto' : linea[2]['importe_total_de_linea_producto'],
        #
        #         'cantidad_producto_actual_contrato' : linea[2]['cantidad_producto_actual_contrato'],
        #         'cantidad_producto_total_contrato' : linea[2]['cantidad_producto_total_contrato'],
        #
        #         'contrato' : contrato.id
        #     })

        for linea in contrato.lineas_de_contrato:
            if linea.contrato is False:
                linea.contrato = contrato.id

                contrato.lineas_de_contrato.create({
                    'producto': linea.producto.id,

                    'tipo_de_producto': linea.tipo_de_producto.id,
                    'orden_marca': linea.orden_marca,

                    'cantidad_por_caja_master': linea.cantidad_por_caja_master,
                    'volumen_caja_master': linea.volumen_caja_master,

                    'moneda': linea.moneda.id,
                    'importe_unitario': linea.importe_unitario,
                    'importe_total_de_linea': linea.importe_total_de_linea,

                    'volumen_total_de_linea_producto': linea.volumen_total_de_linea_producto,
                    'importe_total_de_linea_producto': linea.importe_total_de_linea_producto,

                    'cantidad_producto_actual_contrato': linea.cantidad_producto_actual_contrato,
                    'cantidad_producto_total_contrato': linea.cantidad_producto_total_contrato,

                    'contrato': contrato.id
                })

        return contrato

    def otro_contrato_traer_productos_funcion(self):
        if self.otro_contrato_traer_productos.id is not False:
            for linea_otro_contrato_traer_productos in self.otro_contrato_traer_productos.lineas_de_contrato:
                existe = False

                for linea in self.lineas_de_contrato:
                    if linea.producto.id == linea_otro_contrato_traer_productos.producto.id:
                        existe = True

                if existe is False:
                    linea_otro_contrato_traer_productos = linea_otro_contrato_traer_productos.copy()
                    linea_otro_contrato_traer_productos.contrato = self.id

    @api.onchange('lista_de_precios')
    def _onchange_lista_de_precios(self):
        if self.lista_de_precios.id is not False:
            if len(
                    self.lineas_de_contrato) > 0:  # Ya existen productos y por tanto no se modifica la lista, si no que se actualizan los precios
                for linea_de_contrato in self.lineas_de_contrato:
                    for linea_lista_precio in self.lista_de_precios.lineas:
                        if linea_de_contrato.producto.id == linea_lista_precio.producto.id:
                            linea_de_contrato.importe_unitario = linea_lista_precio.importe_mon_cliente
                            linea_de_contrato.importe_total_de_linea_producto = linea_de_contrato.cantidad_producto_actual_contrato * linea_de_contrato.importe_unitario
            else:
                lineas_de_contrato = []
                for linea_lista_precio in self.lista_de_precios.lineas:
                    nueva_linea_contrato = {
                        'producto': linea_lista_precio.producto.id,
                        'tipo_de_producto': linea_lista_precio.producto.tipo_de_producto.name,
                        'orden_marca': linea_lista_precio.producto.marca.orden,
                        'cantidad_por_caja_master': linea_lista_precio.producto.cantidad_por_caja_master,
                        'volumen_caja_master': linea_lista_precio.producto.volumen_caja_master,

                        'moneda': linea_lista_precio.moneda_mon.id,
                        'importe_unitario': linea_lista_precio.importe_mon_cliente,
                        'importe_total_de_linea': 0,

                        'volumen_total_de_linea_producto': 0,
                        'importe_total_de_linea_producto': 0,

                        'cantidad_producto_actual_contrato': 0,
                        'cantidad_producto_total_contrato': linea_lista_precio.producto.cantidad_minima_de_orden,
                        'contrato': self.id
                    }

                    lineas_de_contrato += [nueva_linea_contrato]

                self.lineas_de_contrato = lineas_de_contrato
        else:
            for linea in self.lineas_de_contrato:
                linea.importe_unitario = 0
                linea.importe_total_de_linea_producto = 0

    def actualizar_desde_el_nomenclador(self):
        for linea in self.lineas_de_contrato:
            linea.foto = linea.producto.image_variant
            linea.tipo_de_producto = linea.producto.tipo_de_producto.name
            linea.orden_marca = linea.producto.marca.orden
            linea.cantidad_por_caja_master = linea.producto.cantidad_por_caja_master

            linea.volumen_caja_master = linea.producto.volumen_caja_master
            linea.cantidad_producto_total_contrato = linea.producto.cantidad_minima_de_orden

            if linea.cantidad_por_caja_master != 0:
                linea.volumen_total_de_linea_producto = linea.cantidad_producto_actual_contrato * linea.volumen_caja_master / linea.cantidad_por_caja_master

    # Relacionados con las versiones del contrato
    ultima_version = fields.Boolean(default=True)
    versiones = fields.One2many('erp.operaciones.contrato', 'contrato_actual')

    contrato_actual = fields.Many2one('erp.operaciones.contrato')

    def traer_repuestos(self, default=None):
        productos_repuestos = []

        for linea_de_contrato in self.lineas_de_contrato:
            if linea_de_contrato.producto.id is not False and linea_de_contrato.producto.tipo_de_producto.id != 3:  # tipo_de_producto = 3 = Pieza de repuesto

                cr = self.env.cr

                consulta = """
                    SELECT repuesto_id
                    from erp_nomencladores_producto_respuesto
                    WHERE principal_id = '""" + str(linea_de_contrato.producto.id) + """'
                """

                cr.execute(consulta, ())
                consulta = cr.fetchall()

                for registro in consulta:  # Recorremos los respuestos para ese producto principal
                    existe = False
                    for producto_repuesto in productos_repuestos:  # Lo comparamos con los repuestos ya agregados en esta llamada al método
                        if producto_repuesto.tipo_de_producto != 3 and producto_repuesto.id == registro[
                            0]:  # tipo_de_producto = 3 = Pieza de repuesto
                            existe = True
                    for lineaa_de_contrato in self.lineas_de_contrato:  # Lo comparamos con los repuestos ya existentes en las lineas_de_contrato
                        if lineaa_de_contrato.producto.tipo_de_producto != 3 and lineaa_de_contrato.producto.id == \
                                registro[0]:  # tipo_de_producto = 3 = Pieza de repuesto
                            existe = True

                    if existe is not True:
                        repuesto = self.env['erp.nomencladores.producto'].browse(registro[0])
                        productos_repuestos.append(repuesto)

        for producto_repuesto in productos_repuestos:
            importe_unitario = 0

            if self.lista_de_precios.id is not False:
                for linea in self.lista_de_precios.lineas:
                    if linea.producto.id == producto_repuesto.id:
                        importe_unitario = linea.importe_mon_cliente

            self.lineas_de_contrato.create({
                'producto': producto_repuesto.id,

                'tipo_de_producto': producto_repuesto.tipo_de_producto,
                'orden_marca': producto_repuesto.marca.orden,

                'cantidad_por_caja_master': producto_repuesto.cantidad_por_caja_master,
                'volumen_caja_master': producto_repuesto.volumen_caja_master,

                'moneda': self.moneda_mon.id,
                'importe_unitario': importe_unitario,
                'importe_total_de_linea': 0,

                'volumen_total_de_linea_producto': 0,
                'importe_total_de_linea_producto': 0,

                'cantidad_producto_actual_contrato': 0,
                'cantidad_producto_total_contrato': 0,
                'contrato': self.id
            })

    def nueva_version(self, default=None):
        nueva_version = self.copy()

        # Duplicando las lienas del contrato
        for linea_de_contrato in self.lineas_de_contrato:
            nueva_linea = linea_de_contrato.copy()
            nueva_linea.contrato = nueva_version.id

        nueva_version.lineas_de_contrato = self.env['erp.operaciones.linea_de_contrato'].search(
            [('contrato', '=', nueva_version.id)])

        # Actualizando para que todas las versiones apunten a la última
        versiones_anteriores = self.env['erp.operaciones.contrato'].search([('contrato_actual', '=', self.id)])
        versiones_anteriores.write(
            {
                'contrato_actual': nueva_version.id
            }
        )

        self.write(
            {
                'ultima_version': False,
                'contrato_actual': nueva_version.id
            }
        )

        nueva_version.versiones = self.env['erp.operaciones.contrato'].search(
            [('contrato_actual', '=', nueva_version.id)], order='fecha_valor desc')

        view_id = self.env.ref('erp.operaciones_contrato_form').id

        return {
            'type': 'ir.actions.act_window',
            'name': '',
            'res_model': 'erp.operaciones.contrato',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': nueva_version.id,
            'target': 'current',
            'nodestroy': True,
            'context': {}
        }

    @api.onchange('importe_mon')
    def _onchange_importe_mon_tasa(self):
        self.importe_usd = self.importe_mon * self.tasa

        self.importe_mon_carta_de_credito = self.importe_mon
        self.tasa_carta_de_credito = self.tasa
        self.importe_usd_carta_de_credito = self.importe_usd

    @api.onchange('importe_mon', 'tasa_moneda_informativa')
    def _onchange_importe_mon_tasa_moneda_informativa(self):
        if self.tasa_moneda_informativa != 0:
            self.importe_moneda_informativa = self.importe_mon / self.tasa_moneda_informativa
            self.tasa_carta_de_credito = self.tasa_moneda_informativa

    @api.onchange('importe_usd')
    def _onchange_importe_usd(self):
        self.importe_usd_carta_de_credito = self.importe_usd

    @api.onchange('cliente', 'numero', 'concepto', 'fecha_valor')
    def _onchange_cliente_numero_concepto(self):
        self.name = ""

        if self.cliente.name is not False:
            self.name = self.cliente.name
        if self.numero is not False:
            self.name += ", " + self.numero
        if self.concepto is not False:
            self.name += ", " + self.concepto
        if self.fecha_valor is not False:
            self.name += ", " + self.fecha_valor

    @api.onchange('importe_mon_carta_de_credito', 'tasa_carta_de_credito')
    def _onchange_importe_mon_carta_de_credito_tasa_carta_de_credito(self):
        self.importe_usd_carta_de_credito = self.importe_mon_carta_de_credito * self.tasa_carta_de_credito

    # @api.onchange('financiamiento_mon')
    # def _onchange_financiamiento_mon(self):
    #     if self.dias_para_pagar.name is not False:
    #         self.financiamiento_mon_importe = self.importe_mon * self.financiamiento_mon * int(self.dias_para_pagar.name) / 36000
    #
    #         raise except_orm(self.financiamiento_mon_importe)
    #
    #         if self.tasa_moneda_informativa is not False and self.tasa_moneda_informativa != 0:
    #             self.financiamiento_euro_importe = self.financiamiento_mon_importe / self.tasa_moneda_informativa
    #
    #         self.financiamiento_usd_importe = self.financiamiento_mon_importe * self.tasa

    @api.onchange('financiamiento_mon')
    def _onchange_financiamiento_mon(self):
        self.actualizar_financiamiento()

    @api.onchange('exw', 'flete_terrestre', 'mercancia', 'flete', 'seguro', 'inspeccion', 'financiamiento_importe'
        , 'importe_repuestos_sin_descuento', 'porciento_repuestos', 'importe_descuento', 'importe_opcional_1',
                  'importe_opcional_2')
    def _onchange_calcular_importe_total(self):
        if self.autocalcular is True:
            self.actualizar_mercancia()


            # self.mercancia = self.exw + self.flete_terrestre
            # self.actualizar_financiamiento()
            # self.importe_total = self.mercancia - self.importe_descuento + self.flete + self.seguro + self.inspeccion + self.financiamiento_importe
            # self._onchange_calcular_importe_total_repuestos()

    def actualizar_mercancia(self):
        mercancia = 0
        self.mercancia = 0
        self.importe_repuestos_sin_descuento = 0
        importe_repuestos_sin_descuento = 0

        for linea in self.lineas_de_contrato:
            if linea.producto.id is not False:
                if linea.producto.tipo_de_producto.id is not False:
                    if linea.producto.tipo_de_producto.id != 3:  # Pieza de repuesto
                        mercancia += linea.importe_total_de_linea_producto
                    else:
                        importe_repuestos_sin_descuento += linea.importe_total_de_linea_producto

        self.exw = 0
        self.mercancia = mercancia

        if self.flete_terrestre is not False:
            self.mercancia += self.flete_terrestre

        self.actualizar_financiamiento()

        self.importe_total = self.mercancia + self.flete + self.seguro + self.inspeccion + self.financiamiento_importe

        self.importe_repuestos_sin_descuento = importe_repuestos_sin_descuento

        self.importe_descuento = self.porciento_repuestos * self.mercancia / 100

        self.importe_repuestos_con_descuento = self.importe_total + self.importe_repuestos_sin_descuento - self.importe_descuento \
                                               + self.importe_opcional_1 + self.importe_opcional_2

    def actualizar_financiamiento(self):
        if self.financiamiento_mon is not False and self.financiamiento_mon > 0:
            if self.dias_para_pagar.name is not False:
                try:
                    dias_para_pagar = int(self.dias_para_pagar.name)

                    dividir_entre = 36000
                    if dias_para_pagar > 360:
                        dividir_entre = 72000
                    if dias_para_pagar > 1080:
                        dividir_entre = 108000

                    self.financiamiento_importe = self.mercancia * self.financiamiento_mon * dias_para_pagar / dividir_entre

                except:
                    pass

    @api.onchange('oferta')
    def _onchange_oferta(self):
        # Se limpian los campos
        self.cliente = False
        self.concepto = False
        self.proveedor = False

        self.dias_para_pagar = False
        self.financiamiento_mon = False
        self.etapa_pago = False

        self.lista_de_precios = False

        self.exw = 0
        self.flete_terrestre = 0
        self.mercancia = 0
        self.flete = 0
        self.seguro = 0
        self.inspeccion = 0
        self.financiamiento_importe = 0

        self.importe_total = 0
        self.importe_descuento = 0

        # Se eliminan las líneas de contrato
        self.lineas_de_contrato = []
        lineas_de_contrato = self.env['erp.operaciones.linea_de_contrato'].search([('contrato', '=', self._origin.id)])

        cr = self.env.cr
        for linea in lineas_de_contrato:
            cr.execute("""
                delete from erp_operaciones_linea_de_contrato where id = """ + str(linea.id) + """
                """
                       , ())

        # Si hay oferta seleccionada se traen los datos de esa oferta
        if self.oferta.id is not False:
            self.cliente = self.oferta.cliente
            self.proveedor = self.oferta.proveedor
            self.concepto = self.oferta.concepto
            self.dias_para_pagar = self.oferta.dias_para_pagar
            self.etapa_pago = self.oferta.etapa_pago
            self.financiamiento_mon = self.oferta.interes_anual

            self.financiamiento_mon = self.oferta.interes_anual

            lineas_de_contrato = []

            if len(self.lineas_de_contrato) == 0:
                for linea in self.oferta.lineas_de_oferta:
                    lineas_de_contrato.append({
                        'producto': linea.producto.id,

                        'tipo_de_producto': linea.tipo_de_producto,
                        'orden_marca': linea.orden_marca,

                        'modelo': linea.modelo,
                        'codigo_proveedor': linea.codigo_proveedor,
                        'cantidad_minima_de_orden': linea.cantidad_minima_de_orden,

                        'cantidad_por_caja_master': linea.cantidad_por_caja_master,
                        'volumen_caja_master': linea.volumen_caja_master,

                        'moneda': linea.moneda.id,
                        'importe_unitario': linea.importe_unitario,
                        'importe_total_de_linea': linea.importe_total_de_linea,

                        'volumen_total_de_linea_producto': linea.volumen_total_de_linea_producto,
                        'importe_total_de_linea_producto': linea.importe_total_de_linea_producto,

                        'cantidad_producto_actual_contrato': linea.cantidad_producto_actual_oferta,
                        'cantidad_producto_total_contrato': linea.cantidad_producto_total_oferta,
                    })

                self.lineas_de_contrato = lineas_de_contrato

            if self.oferta.lista_de_precios.id is not False:
                self.lista_de_precios = self.oferta.lista_de_precios

            self.exw = self.oferta.exw
            self.flete_terrestre = self.oferta.flete_terrestre
            self.mercancia = self.oferta.mercancia
            self.flete = self.oferta.flete
            self.seguro = self.oferta.seguro
            self.inspeccion = self.oferta.inspeccion
            self.financiamiento_importe = self.oferta.financiamiento_importe

            self.importe_total = self.oferta.importe_total
            self.importe_descuento = self.oferta.importe_descuento

    def eliminar_productos_cantidad_producto_actual_cero(self):
        for linea in self.lineas_de_contrato:
            if linea.cantidad_producto_actual_contrato == 0:
                linea.unlink()

    def actualizar_productos_y_entrega(self):

        if self.oferta.id is not False:
            self.lineas_de_contrato.unlink()

        lineas_de_contrato = []
        for linea_de_oferta in self.oferta.lineas_de_oferta:
            linea_de_contrato = {
                'producto': linea_de_oferta.producto.id,

                'tipo_de_producto': linea_de_oferta.tipo_de_producto,
                'orden_marca': linea_de_oferta.marca,

                'cantidad_por_caja_master': linea_de_oferta.cantidad_por_caja_master,
                'volumen_caja_master': linea_de_oferta.volumen_caja_master,

                'moneda': linea_de_oferta.moneda.id,
                'importe_unitario': linea_de_oferta.importe_unitario,
                'importe_total_de_linea': linea_de_oferta.importe_total_de_linea,

                'volumen_total_de_linea_producto': linea_de_oferta.volumen_total_de_linea_producto,
                'importe_total_de_linea_producto': linea_de_oferta.importe_total_de_linea_producto,

                'cantidad_producto_actual_contrato': linea_de_oferta.cantidad_producto_actual_oferta,
                'cantidad_producto_total_contrato': linea_de_oferta.cantidad_producto_total_oferta,
            }

            lineas_de_contrato += [linea_de_contrato]
        self.lineas_de_contrato = lineas_de_contrato

    def imprimir_contrato(self):
        return self.env['report'].get_action(self, 'erp.imprimir_contrato')

    def imprimir_contrato_productos(self):
        return self.env['report'].get_action(self, 'erp.imprimir_contrato_productos')

    def get_resized_image_data(self, file_path, bound_width_height):
        # get the image and resize it
        im = Image.open(file_path)
        im.thumbnail(bound_width_height, Image.ANTIALIAS)  # ANTIALIAS is important if shrinking

        # stuff the image data into a bytestream that excel can read
        im_bytes = io.BytesIO()
        im.save(im_bytes, format='PNG')
        return im_bytes

    def quitarTildes(self, cadena):
        sinTildes = ""
        if cadena is not False:
            if isinstance(cadena, collections.Iterable):
                for letra in cadena:
                    if ord(letra) == 225:  # 'á'
                        letra = 'a'
                    elif ord(letra) == 233:  # 'é':
                        letra = 'e'
                    elif ord(letra) == 237:  # 'í':
                        letra = 'i'
                    elif ord(letra) == 243:  # 'ó'
                        letra = 'o'
                    elif ord(letra) == 250:  # 'ú':
                        letra = 'u'
                    elif ord(letra) == 241:  # 'ñ':
                        letra = 'nn'
                    elif ord(letra) == 193:  # 'Á':
                        letra = 'A'
                    elif ord(letra) == 201:  # 'É':
                        letra = 'E'
                    elif ord(letra) == 205:  # 'Í':
                        letra = 'I'
                    elif ord(letra) == 211:  # 'Ó':
                        letra = 'O'
                    elif ord(letra) == 218:  # 'Ú':
                        letra = 'U'
                    elif ord(letra) == 209:  # 'Ñ':
                        letra = 'NN'

                    sinTildes += letra

        return sinTildes


    def copy(self, default=None):
        registro = super(Contrato, self).copy(default)
        registro.fecha_valor = date.today()
        registro.ultima_version = True

        for linea in self.lineas_de_contrato:
            nueva_linea = linea.copy()
            nueva_linea.contrato = registro.id
            # registro.lineas_de_contrato += nueva_linea

        return registro


class LineaDeContrato(models.Model):
    _name = 'erp.operaciones.linea_de_contrato'
    _order = 'tipo_de_producto, orden_marca, producto'

    @api.model
    def _default_currency(self):
        return 3

    @api.onchange('producto')
    def _onchange_producto(self):
        self.tipo_de_producto = self.producto.tipo_de_producto.name
        self.orden_marca = self.producto.marca.orden
        self.orden_repuesto = 0

        if len(self.producto.repuestos) > 0:
            self.orden_repuesto = self.producto.repuestos[0]

        if self.producto.cantidad_minima_de_orden is not False:
            self.cantidad_producto_total_contrato = self.producto.cantidad_minima_de_orden

        # self.contrato.chequear_si_el_producto_esta_insertado(self.producto)

        self.importe_unitario = 0
        self.importe_total_de_linea = 0

        if self.contrato.lista_de_precios.id is not False:
            for linea in self.contrato.lista_de_precios.lineas:
                if linea.producto.id == self.producto.id:
                    self.importe_unitario = linea.importe_mon_cliente
                    self.importe_total_de_linea = self.cantidad_por_caja_master * self.importe_unitario
        self.cantidad_por_caja_master = self.producto.cantidad_por_caja_master
        self.volumen_caja_master = self.producto.volumen_caja_master

        self.moneda = self.contrato.moneda_mon.id

    @api.onchange('cantidad_por_caja_master')
    def _onchange_cantidad_caja_master(self):
        self.importe_total_de_linea = self.cantidad_por_caja_master * self.importe_unitario
        self.importe_total_de_linea_producto = self.cantidad_producto_actual_contrato * self.importe_unitario

        if self.cantidad_por_caja_master != 0:
            if self.cantidad_producto_total_contrato % self.cantidad_por_caja_master != 0:
                res = {}
                warning = False

                warning = {
                    'title': _('Warning!'),
                    'message': "Acaba de introducir una cantidad de producto que no es divisible entre la cantidad de caja máster.",
                }
                self.discount = 0
                res = {'warning': warning}

                return res

    @api.onchange('importe_unitario')
    def _onchange_importe_unitario(self):
        if self._origin.id:
            self.importe_total_de_linea = self.cantidad_por_caja_master * self.importe_unitario
            self.importe_total_de_linea_producto = self.cantidad_producto_actual_contrato * self.importe_unitario

            cr = self.env.cr
            consulta = """
                UPDATE public.erp_operaciones_linea_de_contrato
                SET importe_unitario = """ + str(self.importe_unitario) + """
                WHERE id = """ + str(self._origin.id) + """;

                UPDATE public.erp_operaciones_linea_de_contrato
                SET importe_total_de_linea_producto = """ + str(
                self.cantidad_producto_actual_contrato * self.importe_unitario) + """
                , importe_unitario = """ + str(self.importe_unitario) + """
                , cantidad_producto_actual_contrato = """ + str(self.cantidad_producto_actual_contrato) + """
                , cantidad_producto_total_contrato = """ + str(self.cantidad_producto_total_contrato) + """
                WHERE id = """ + str(self._origin.id) + """;
            """

            self.env.cr.execute(consulta)


    @api.onchange('cantidad_producto_actual_contrato')
    def _onchange_cantidad_producto_actual_contrato(self):
        self.importe_total_de_linea_producto = self.cantidad_producto_actual_contrato * self.importe_unitario

        if self.cantidad_por_caja_master != 0:
            self.volumen_total_de_linea_producto = self.cantidad_producto_actual_contrato * self.volumen_caja_master / self.cantidad_por_caja_master

            if self.cantidad_producto_actual_contrato % self.cantidad_por_caja_master != 0:
                res = {}
                warning = False

                warning = {
                    'title': _('Warning!'),
                    'message': "Acaba de introducir una cantidad de producto que no es divisible entre la cantidad de caja máster.",
                }
                self.discount = 0
                res = {'warning': warning}

                return res


    @api.onchange('volumen_caja_master')
    def _onchange_volumen_caja_master(self):
        if self.cantidad_por_caja_master != 0:
            self.volumen_total_de_linea_producto = self.cantidad_producto_actual_contrato * self.volumen_caja_master / self.cantidad_por_caja_master

    producto = fields.Many2one('product.product', required=True)

    foto = fields.Binary("Variant Image", attachment=True, related='producto.image_variant')

    modelo = fields.Char(string="Modelo", related='producto.name')
    codigo_proveedor = fields.Char(string="Código proveedor", related='producto.codigo_proveedor')
    cantidad_minima_de_orden = fields.Integer(string="MOQ", related='producto.cantidad_minima_de_orden')

    tipo_de_producto = fields.Char(string="Línea de producto")
    orden_marca = fields.Char(string="Orden marca")

    cantidad_por_caja_master = fields.Integer()
    volumen_caja_master = fields.Float(string='Volumen caja máster', digits=dp.get_precision('seisDecimales'))

    moneda = fields.Many2one('res.currency', string='Moneda', default=_default_currency)
    importe_unitario = fields.Monetary(string='Precio unitario', currency_field='moneda')
    importe_total_de_linea = fields.Monetary(string='Precio de la caja', currency_field='moneda')

    volumen_total_de_linea_producto = fields.Float(string='Volumen total producto',
                                                   digits=dp.get_precision('seisDecimales'))
    importe_total_de_linea_producto = fields.Monetary(string='Importe total producto', currency_field='moneda')

    cantidad_producto_actual_contrato = fields.Integer()
    cantidad_producto_total_contrato = fields.Integer()

    sequence = fields.Integer(string='Orden', default=10)

    contrato = fields.Many2one('erp.operaciones.contrato', ondelete='cascade')


class CartaDeCredito(models.Model):
    _name = "erp.operaciones.carta_de_credito"

    @api.model
    def _default_currency(self):
        return 3

    @api.model
    def _default_tasa(self):
        return 1

    numero_carta_de_credito = fields.Char(string="Número de carta de crédito")
    fecha_carta_de_credito = fields.Date(string="Fecha de carta de crédito")

    moneda_mon_carta_de_credito = fields.Many2one('res.currency', string='Moneda', default=_default_currency)
    moneda_usd_carta_de_credito = fields.Many2one('res.currency', string='Moneda', default=_default_currency)

    importe_mon_carta_de_credito = fields.Monetary(currency_field='moneda_mon_carta_de_credito', string="Importe MON")
    tasa_carta_de_credito = fields.Float(string='Tasa', digits=dp.get_precision('seisDecimales'), default=_default_tasa)
    importe_usd_carta_de_credito = fields.Monetary(currency_field='moneda_usd_carta_de_credito', string="Importe USD")

    fecha_expiracion_carta_de_credito = fields.Date(string="Fecha expiración")
    fecha_ultimo_embarque_carta_de_credito = fields.Date(string="Fecha último embarque")

    contrato = fields.Many2one('erp.operaciones.contrato', ondelete='cascade')

    @api.onchange('importe_usd_carta_de_credito', 'tasa_carta_de_credito')
    def _onchange_importe_usd_carta_de_credito_tasa_carta_de_credito(self):
        self.importe_mon_carta_de_credito = self.importe_usd_carta_de_credito / self.tasa_carta_de_credito
