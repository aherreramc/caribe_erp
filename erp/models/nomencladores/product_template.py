# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, SUPERUSER_ID, tools, _

import odoo.addons.decimal_precision as dp

class Product(models.Model):
    _inherit = 'product.product'

    # product_tmpl_id = fields.Many2one(
    #     'product.template', 'Product Template',
    #     auto_join=True, index=True, ondelete="cascade", onupdate="cascade", required=True)


    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        auto_join=True, index=True, ondelete="cascade", onupdate="cascade", required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(string="Nombre")
    descripcion_cliente = fields.Char(string="Descripción-cliente-español")
    descripcion_proveedor = fields.Char(string="Descripción-proveedor")
    descripcion_cliente_ingles = fields.Char(string="Descripción-cliente-inglés")
    codigo_cliente = fields.Char(string="Código-cliente")
    codigo_cliente_distribuidor = fields.Char(string="Código-cliente-distribuidor")
    codigo_proveedor = fields.Char(string="Código-proveedor")
    partida_arancelaria = fields.Char(string="Partida arancelaria")
    codigo_de_barra = fields.Char(string="Código de barra")
    tipo_de_espiga = fields.Many2one('erp.nomencladores.tipo_de_espiga', string='Tipo de espiga')
    potencia = fields.Many2one('erp.nomencladores.potencia', string='Potencia')
    active = fields.Boolean('Activo', default=True)

    volumen_caja_master = fields.Float(string='Volumen caja máster', digits=dp.get_precision('seisDecimales'))
    cantidad_por_caja_master = fields.Integer(string='Cantidad por caja master')

    peso_neto = fields.Float(string='Peso neto', digits=dp.get_precision('seisDecimales'))
    peso_bruto = fields.Float(string='Peso bruto', digits=dp.get_precision('seisDecimales'))

    largo = fields.Float(string="Largo", digits=dp.get_precision('dosDecimales'))
    alto = fields.Float(string="Alto", digits=dp.get_precision('dosDecimales'))
    profundidad = fields.Float(string="Profundidad", digits=dp.get_precision('dosDecimales'))

    medidas = fields.Char(string="Medida", compute='_compute_medidas')


    cantidad_minima_de_orden = fields.Integer(string='Cantidad mínima de orden')

    cantidad_contenedor_20 = fields.Integer(string='Cantidad contenedor de 20')
    cantidad_contenedor_40 = fields.Integer(string='Cantidad contenedor de 40')
    cantidad_contenedor_40_hc = fields.Integer(string='Cantidad contenedor de 40 HC')

    tipo_de_producto = fields.Many2one('erp.nomencladores.tipo_de_producto', string='Tipo de producto')

    marca = fields.Many2one('erp.nomencladores.marca', ondelete='cascade')

    repuestos = fields.Many2many('product.template', 'erp_nomencladores_producto_respuesto', 'repuesto_id', 'principal_id', 'Producto principal:')
    posicion = fields.Char(string="Posición")

    materiales = fields.Many2many('erp.nomencladores.material', 'erp_productos_materiales', 'producto_id', 'material_id', 'Materiales')

    #Falta lo de la categoría del producto. Valorar crear una nueva entidad y poner un manyToMany

    image_variant = fields.Binary(
        "Variant Image", attachment=True,
        help="This field holds the image used as image for the product variant, limited to 1024x1024px.")
    image = fields.Binary(
        "Big-sized image", compute='_compute_images', inverse='_set_image',
        help="Image of the product variant (Big-sized image of product template if false). It is automatically "
             "resized as a 1024x1024px image, with aspect ratio preserved.")
    image_small = fields.Binary(
        "Small-sized image", compute='_compute_images', inverse='_set_image_small',
        help="Image of the product variant (Small-sized image of product template if false).")
    image_medium = fields.Binary(
        "Medium-sized image", compute='_compute_images', inverse='_set_image_medium',
        help="Image of the product variant (Medium-sized image of product template if false).")

    porciento_max_gasto_marketing = fields.Float(digits=dp.get_precision('dosDecimales'))


    explotado = fields.Binary("", attachment=True, help="")
    explotado_ingles = fields.Binary("", attachment=True, help="")
    ficha_tecnica = fields.Binary("", attachment=True, help="")
    ficha_tecnica_ingles = fields.Binary("", attachment=True, help="")
    caja = fields.Binary("", attachment=True, help="")
    manual_de_usuario = fields.Binary("", attachment=True, help="")
    certificado_de_onure = fields.Binary("", attachment=True, help="")

    fecha_registro_onure = fields.Date(string="Fecha de registro ONURE")
    numero_registro_onure = fields.Char(string="Número de registro ONURE")
    fecha_vencimiento_onure = fields.Date(string="Fecha de vencimiento ONURE")

    no_tiene_explotado = fields.Boolean('No tiene', default=False)
    no_tiene_explotado_ingles = fields.Boolean('No tiene', default=False)
    no_tiene_ficha_tecnica = fields.Boolean('No tiene', default=False)
    no_tiene_ficha_tecnica_ingles = fields.Boolean('No tiene', default=False)
    no_tiene_caja = fields.Boolean('No tiene', default=False)
    no_tiene_manual_de_usuario = fields.Boolean('No tiene', default=False)
    no_tiene_certificado_onure = fields.Boolean('No tiene', default=False)

    def name_get(self):

        res = super(ProductTemplate, self).name_get()
        data = []
        for producto in self:
            display_value = ''

            if producto.descripcion_cliente is not False:
                display_value += "" + producto.descripcion_cliente

            if producto.name is not False:
                display_value += ", Modelo: " + producto.name

            if producto.tipo_de_producto.id is not False and producto.tipo_de_producto.name == 'Pieza de repuesto':
                if len(producto.repuestos) > 0:
                    display_value += ", Repuesto de: "
                    cantidad_de_repuestos_restantes = len(producto.repuestos)

                    for repuesto in producto.repuestos:
                        display_value += repuesto.name

                        if cantidad_de_repuestos_restantes > 2:
                            display_value += ", "
                            cantidad_de_repuestos_restantes -= 1
                        elif cantidad_de_repuestos_restantes == 2:
                            display_value += " y "
                            cantidad_de_repuestos_restantes -= 1

                if producto.posicion is not False:
                    display_value += ", Posición: " + producto.posicion

            if producto.marca.name is not False:
                display_value += ", Marca: " + producto.marca.name

            data.append((producto.id, display_value))
        return data

    def name_get_to_string(self):
        nombre_a_mostrar = ""
        for llave in self.name_get():
            nombre_a_mostrar += llave[1]

        return nombre_a_mostrar




    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search((args + ['|', '|', '|', ('name', 'ilike', name), ('descripcion_cliente', 'ilike', name)
                                , ('tipo_de_espiga', 'ilike', name), ('marca', 'ilike', name)]),
                               limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


    @api.depends('name', 'alto', 'profundidad')
    def _compute_name_to_search(self):
        self.name_to_search = str(self.name)

        if self.descripcion_cliente is not False:
            self.name_to_search += str(self.descripcion_cliente)


    @api.onchange('volumen_caja_master', 'cantidad_por_caja_master', 'cantidad_minima_de_orden', 'cantidad_contenedor_20'
                  , 'cantidad_contenedor_40', 'cantidad_contenedor_40_hc')
    def _onchange_actualizar_ofertas_y_contratos(self):
        if self._origin.id is not False:
            lineas_de_ofertas = self.env['erp.operaciones.linea_de_oferta'].search([('producto', '=', self._origin.id)])

            for linea_de_oferta in lineas_de_ofertas:
                #Actualizando en caso que proceda el/los campo volumen_caja_master y volumen_total_de_linea_producto
                volumen_total_de_linea_producto = 0

                if linea_de_oferta.cantidad_por_caja_master != 0:
                    volumen_total_de_linea_producto = linea_de_oferta.cantidad_producto_total_oferta * self.volumen_caja_master / linea_de_oferta.cantidad_por_caja_master


                linea_de_oferta.write({
                    'volumen_caja_master': self.volumen_caja_master,
                    'volumen_total_de_linea_producto': volumen_total_de_linea_producto
                })

                #Actualizando en caso que proceda el/los campo cantidad_por_caja_master
                linea_de_oferta.write({
                    'cantidad_por_caja_master': self.cantidad_por_caja_master
                })

    @api.depends('largo', 'alto', 'profundidad')
    def _compute_medidas(self):
        self.medidas = str(self.largo) + "*" + str(self.alto) + "*" + str(self.profundidad)


    @api.depends('image_variant', 'image')
    def _compute_images(self):
        if self._context.get('bin_size'):
            self.image_medium = self.image_variant
            self.image_small = self.image_variant
            self.image = self.image_variant
        else:
            resized_images = tools.image_get_resized_images(self.image_variant, return_big=True, avoid_resize_medium=True)
            self.image_medium = resized_images['image_medium']
            self.image_small = resized_images['image_small']
            self.image = resized_images['image']
        if not self.image_medium:
            self.image_medium = self.image_medium
        if not self.image_small:
            self.image_small = self.image_small

        if not self.image:
            self.image = self.image


    def _set_image(self):
        self._set_image_value(self.image)

    def _set_image_medium(self):
        self._set_image_value(self.image_medium)

    def _set_image_small(self):
        self._set_image_value(self.image_small)

    def _set_image_value(self, value):
        image = tools.image_resize_image_big(value)
        if self.image is not False:
            self.image_variant = image