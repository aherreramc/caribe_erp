# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


class Pontencia(models.Model):
    _name = 'erp.nomencladores.potencia'

    name = fields.Char(required=True, string="Nombre:")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                                default=lambda self: self.env['res.company']._company_default_get())

    # def actualizar_migraciones(self):
    #     # model_data = self.env['ir.model.data'].search(['|',
    #     #                                                ('model', '=', "erp.nomencladores.marca"),
    #     #                                                ('model', '=', "erp.nomencladores.material"),
    #     #                                                ('model', '=', "product.template"),
    #     #                                                ])
    #
    #     model_data = self.env['ir.model.data'].search([
    #                                            ('model', '=', "product.template")
    #                                            ])
    #
    #     for model in model_data:
    #         model_entity = model.model
    #
    #         pila = []
    #         for c in reversed(model.name):
    #             if c.isdigit():
    #                 pila.append(c)
    #
    #         new_id = ""
    #         while len(pila) > 0:
    #             new_id += pila.pop()
    #
    #         nombre_tabla = ""
    #         for c in model_entity:
    #             if c != ".":
    #                 nombre_tabla += c
    #             else:
    #                 nombre_tabla += "_"
    #
    #
    #         if nombre_tabla != "product_template":
    #             consulta = """
    #                     update """ + nombre_tabla + """
    #                     set id = '""" + new_id + """'
    #
    #                     where id = '""" + str(model.res_id) + """'
    #                 """
    #
    #             self._cr.execute(consulta)
    #
    #         else: #sustituto
    #             consulta_eliminar_product_product_inicial = """
    #                     DELETE FROM product_product
    #                     WHERE product_tmpl_id = 7234
    #             """
    #
    #             self._cr.execute(consulta_eliminar_product_product_inicial)
    #
    #
    #             #poniendo un temporal
    #             consulta_product_product = """
    #                     update product_product
    #                     set product_tmpl_id = 7234
    #
    #                     where product_tmpl_id = '""" + str(model.res_id) + """'
    #             """
    #
    #             self._cr.execute(consulta_product_product)
    #
    #             #Actualizando product_template id
    #             consulta_product_template = """
    #                     update """ + nombre_tabla + """
    #                     set id = '""" + new_id + """'
    #
    #                     where id = '""" + str(model.res_id) + """'
    #             """
    #
    #             self._cr.execute(consulta_product_template)
    #
    #             #Actualizando product.product
    #             consulta_product_product = """
    #                     update product_product
    #                     set product_tmpl_id = '""" + new_id + """'
    #
    #                     where product_tmpl_id = 7234
    #             """
    #
    #             self._cr.execute(consulta_product_product)



    def actualizar_migraciones(self):
        consulta_product_template = """
                update ir_attachment
                set res_model = 'product.template',
                res_id = 6,
                file_size = 109449,
                index_content = 'ALICIA EMK6  Automatic shut-off: the moka switches off automatically Keep-warm function: this special device keeps coffee hot for 30 minutes Transparent coffee container and lid to monitor coffee brewing. Cool-touch base: you can put the moka on every surface, thanks to the cool touch base. 3 or 6 cups: you can make 6 cups of coffee or 3 cups by using the special 3 cups adaptor. Independent base: cordless coffee maker with 360° rotational base Dimensions (wxdxh)mm122x185x235WeightKg1Input max powerW450Rated voltage/FrequencyV~Hz110-50Capacitycups3-6TECHNICAL DATA ELECTRIC COFFEE MAKER HOUSEHOLD APPLIANCES ALICIA LA MOKA DE™ LONGHI EMK6 Transparent lid and coffee container, unbreakable and easy to clean The cool touch base allows to put the moka everywhere The electric coffee maker switches off automatically and keeps coffee warm for 30 minutes. Coffee doesn™t boil over. ﬁKEEP-WARMﬂ SYSTEM: coffee is kept warm and good for 30 minutes. The coffee maker switches off when you lift it from the electric base, but switching it on again coffee is kept warm for another 30 minutes  ',
                res_field = 'ficha_tecnica',
                mimetype = 'application/pdf'



                where id = 290
        """



        self._cr.execute(consulta_product_template)