# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2015 sinergiainformatica.net.  All Rights Reserved.
# David <soporte@sinergiainformatica.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def query_sales(self, name, args):

        res = {}
        for main_partner in self.browse(id):
            main_sales = main_partner.sale_order_ids or []  # in case it was False
            sales = [sale.id for sale in main_sales]
            for child_partner in main_partner.child_ids:
                child_sales = child_partner.sale_order_ids or []
                sales.extend([sale.id for sale in child_sales])
            # at this point we should have all the sale ids
            # use a set to get rid of duplicates
            sales = list(set(sales))
            # and store in res to be returned
            res[main_partner.id] = sales

        return res

    sale_history = fields.One2many(compute='query_sales',comodel_name='sale.order', string='Sales' )


ResPartner()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_history_ids =  fields.Many2one(comodel_name='res.partner', string="Historic", readonly=True,)
    date_order = fields.Date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    picking_status = fields.Selection(related='picking_ids.state',  string="Estado envio",readonly=True)
    date_send = fields.Datetime(related='picking_ids.date_done',  string="Fecha Envio")
    invoice_status = fields.Boolean(related='invoiced', string="Estado Factura")
    payment_typ = fields.Many2one(comodel_name="payment.type", inverse_name="payment_type" , string="Tipo Pago", readonly=True)
    traking = fields.Char(related='picking_ids.carrier_tracking_ref',  string="Tracking", store=True)

SaleOrder()

