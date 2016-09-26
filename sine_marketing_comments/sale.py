# -*- coding: utf-8 -*-
# David Hernández. http://sinergiainformatica.net
#
# ##################################################

from openerp import models, fields, api, exceptions


class sale_order(models.Model):

    _inherit = "sale.order"

    comment_id = fields.Many2one(comodel_name='sale.comment',string= 'Comment for the order',  ondelete='restrict')

sale_order()


class sale_comment(models.Model):
    _name = "sale.comment"
    _description = "Add a comment for the sales orders"
    _table = "sale_comment"
    _rec_name = "group"

    comment = fields.Html(string='Comment', help="Comment for sales",required=True, size=120)
    group = fields.Selection([('MS', 'Motoscoot'), ('TT', 'TopTaller'),('PIL', 'Piloto')], string='Grupo', required=True, select=True)

sale_comment()
