# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import odoo.addons.decimal_precision as dp
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

from openerp.exceptions import except_orm, Warning, RedirectWarning

class Incoterm(models.Model):
    _name = 'erp.nomencladores.incoterm'

    name = fields.Char(required=True, string="Incoterm")

