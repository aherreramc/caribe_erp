# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


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
            entity = self.env['' + model_entity + ''].find(model_data.res_id)

            migrate_id = ""

            pila = []
            for c in reversed(model_entity.name):
                if c.isdigit():
                    pila.append(c)

            new_id = ""
            while len(pila) > 0:
                new_id = pila.pop()



            self._cr.execute("""
                    update """ + model_entity + """
                    set id = '""" + new_id + """'

                    where id = '""" + str(model_data.res_id) + """'
                """)
