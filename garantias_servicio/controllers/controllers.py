# -*- coding: utf-8 -*-
# from odoo import http


# class Garantias(http.Controller):
#     @http.route('/garantias/garantias', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/garantias/garantias/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('garantias.listing', {
#             'root': '/garantias/garantias',
#             'objects': http.request.env['garantias.garantias'].search([]),
#         })

#     @http.route('/garantias/garantias/objects/<model("garantias.garantias"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('garantias.object', {
#             'object': obj
#         })

