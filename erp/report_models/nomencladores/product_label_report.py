# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

from openerp.exceptions import except_orm, Warning, RedirectWarning


class ProductLabelReport(models.AbstractModel):
    _name = 'report.erp.product_label_report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # self.model = self.env.context.get('active_model')
        # product = self.env[self.model].browse(self.env.context.get('active_id'))

        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('erp.product_label_report')

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'product': self,
        }
        return docargs
         
        # docargs = {
        #     'doc_ids': self.ids,
        #     'doc_model': self.model,
        #     'product' : product,
        # }
        # return self.env['report'].render('erp.product_label_report', docargs)


    #   @api.model
    # def _get_report_values(self, docids, data=None):
    #     report_obj = self.env['ir.actions.report']
    #     report = report_obj._get_report_from_name('module.report_name')
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': report.model,
    #         'docs': self,
    #     }
    #     return docargs
