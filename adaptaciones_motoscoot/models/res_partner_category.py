# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class res_partner_category(models.Model):
    _inherit = 'res.partner.category'

    taller = fields.Boolean(string='Taller?')


