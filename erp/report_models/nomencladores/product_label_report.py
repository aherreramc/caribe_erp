# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

from openerp.exceptions import except_orm, Warning, RedirectWarning


class ProductLabelReport(models.AbstractModel):
    _name = 'report.erp.product_label_repo'


    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('module.report_name')

        product = self.env['product.template'].browse(docids)



        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'product': product,

        }
        return docargs
