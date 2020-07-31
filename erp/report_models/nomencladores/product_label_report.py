# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

from openerp.exceptions import except_orm, Warning, RedirectWarning


class ProductLabelReport(models.AbstractModel):
    _name = 'report.erp.product_label_report'
    
    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        product = self.env[self.model].browse(self.env.context.get('active_id'))

        fecha_desde = data['form']['fecha_desde']
        fecha_hasta = data['form']['fecha_hasta']
        cartas = []
         
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'product' : product,
        }
        return self.env['report'].render('erp.product_label_report', docargs)
