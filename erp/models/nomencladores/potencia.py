# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning


class Pontencia(models.Model):
    _name = 'erp.nomencladores.potencia'

    name = fields.Char(required=True, string="Nombre:")

    compannia = fields.Many2one('res.company', string='Compañía', required=True,
                                default=lambda self: self.env['res.company']._company_default_get())

    def actualizar_migraciones(self):
        model_data = self.env['ir.model.data'].search(['|',
                                                       ('model', '=', "erp.nomencladores.marca"),
                                                       ('model', '=', "erp.nomencladores.material")
                                                       ])

        for model in model_data:
            model_entity = model.model

            pila = []
            for c in reversed(model.name):
                if c.isdigit():
                    pila.append(c)

            new_id = ""
            while len(pila) > 0:
                new_id += pila.pop()

            nombre_tabla = ""
            for c in model_entity:
                if c != ".":
                    nombre_tabla += c
                else:
                    nombre_tabla += "_"


            self._cr.execute("""
                    update """ + nombre_tabla + """
                    set id = '""" + new_id + """'

                    where id = '""" + str(model.res_id) + """'
                """)
