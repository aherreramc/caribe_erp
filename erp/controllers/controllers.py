# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from openerp.exceptions import except_orm, Warning, RedirectWarning


# class DelonguiControllers(http.Controller):
#     # @http.route('/web', auth='public')
#     # def aa(self):
#     #     return http.request.render('erp.oferta_lista', {})
#
#     @http.route('/erp.oferta_lista', auth='public')
#     def index(self, **kw):
#         # raise except_orm("FF")
#         return "Hello, world"



# class DelonguiControllers(http.Controller):
#     @http.route('/borrar_chat/', auth='public')
#     def index(self, **kw):
#         raise except_orm("FF")
#
#
#
#
#     @http.route('/nomencladores_delongui/nomencladores_delongui/', auth='public')
#     def index(self, **kw):
#         raise except_orm("FF")
#         return "Hello, world"

#     @http.route('/nomencladores_delongui/nomencladores_delongui/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nomencladores_delongui.listing', {
#             'root': '/nomencladores_delongui/nomencladores_delongui',
#             'objects': http.request.env['nomencladores_delongui.nomencladores_delongui'].search([]),
#         })

#     @http.route('/nomencladores_delongui/nomencladores_delongui/objects/<model("nomencladores_delongui.nomencladores_delongui"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nomencladores_delongui.object', {
#             'object': obj
#         })

