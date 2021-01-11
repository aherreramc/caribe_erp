# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

from openerp.exceptions import except_orm, Warning, RedirectWarning


class ImprimirCartaTipoReport(models.AbstractModel):
    _name = 'report.erp.imprimir_carta_tipo_report'
    
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))


        if docs.proveedor.id == 16: #"DE’LONGHI KENWOOD A.P.A"
            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Carta Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 62: #"DE'LONGHI APPLIANCES S.R.L"
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 80: #"DE'LONGHI AMERICA, INC"
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 86: #"Zeus Caribe S.A."
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        else:
            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Carta Oferta',
                'proveedor': False
            }

        return self.env['report'].render('erp.imprimir_carta_tipo_report', docargs)




    def _get_report_values(self, docids, data=None):
        # # get the report action back as we will need its data
        # report = self.env['ir.actions.report']._get_report_from_name('erp.imprimir_carta_tipo_report')
        # # get the records selected for this rendering of the report
        # obj = self.env[report.model].browse(docids)
        # # return a custom rendering context
        # return {
        #     'lines': docids.get_lines()
        # }




        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))


        if docs.proveedor.id == 16: #"DE’LONGHI KENWOOD A.P.A"
            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Carta Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 62: #"DE'LONGHI APPLIANCES S.R.L"
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 80: #"DE'LONGHI AMERICA, INC"
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        elif docs.proveedor.id == 86: #"Zeus Caribe S.A."
             docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Oferta',
                'proveedor': docs.proveedor.id
            }
        else:
            docargs = {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'docs': docs,
                'oferta':docs,
                'time': time,
                'nombre_report':'Carta Oferta',
                'proveedor': False
            }

        # return self.env['report'].render('erp.imprimir_carta_tipo_report', docargs)


        data = data if data is not None else {}
        # pricelist = self.env['product.pricelist'].browse(data.get('form', {}).get('price_list', False))
        # products = self.env['product.product'].browse(data.get('ids', data.get('active_ids')))
        # quantities = self._get_quantity(data)
        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            # 'doc_model': 'product.pricelist',
            'doc_model': self.env.context.get('active_model'),
            'docs': docargs,
            # 'data': dict(
            #     data,
            #     pricelist=pricelist,
            #     quantities=quantities,
            #     categories_data=self._get_categories(pricelist, products, quantities)
            # ),
        }