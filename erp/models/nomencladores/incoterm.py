# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
import odoo.addons.decimal_precision as dp

from openerp.exceptions import except_orm, Warning, RedirectWarning

class Incoterm(models.Model):
    _name = 'erp.nomencladores.incoterm'

    name = fields.Char(required=True, string="Incoterm")

