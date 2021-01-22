# -*- coding: utf-8 -*-
from openerp import http

# class FinancieraSid(http.Controller):
#     @http.route('/financiera_sid/financiera_sid/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financiera_sid/financiera_sid/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financiera_sid.listing', {
#             'root': '/financiera_sid/financiera_sid',
#             'objects': http.request.env['financiera_sid.financiera_sid'].search([]),
#         })

#     @http.route('/financiera_sid/financiera_sid/objects/<model("financiera_sid.financiera_sid"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financiera_sid.object', {
#             'object': obj
#         })