# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class res_company(models.Model):
    _inherit = 'res.company'

    logo_taller = fields.Binary(string='Imagen Cabecera Taller')
    logo_motoscoot = fields.Binary(string='Imagen Cabecera Motoscoot')
    pie_taller = fields.Binary(string='Imagen Pie Taller')
    pie_motoscoot = fields.Binary(string='Imagen Pie Motoscoot')