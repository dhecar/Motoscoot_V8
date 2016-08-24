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

from osv import fields, osv


class res_partner(osv.osv):
    def query_sales(self, cr, uid, ids, field_name, arg, context=None):

        res = {}
        if isinstance(ids, (int, long)):
            ids = [ids]  # in case an id was passed in directly
        for main_partner in self.browse(cr, uid, ids, context=context):
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

    _inherit = 'res.partner'
    _columns = {

        'sale_history': fields.function(query_sales, type='one2many', obj='sale.order', method=True,
                                        string='Sales', ),
    }

res_partner()


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'partner_history_ids': fields.many2one('res.partner', 'Historic', select=True, readonly=True,),

        'date_order': fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'picking_status': fields.related('picking_ids', 'state', type='char', string="Estado envio"),
        'date_send': fields.related('picking_ids', 'date_done', type='char', string="Fecha Envio"),
        'invoice_status': fields.related('invoiced', type='boolean', string="Estado Factura"),
        'payment_typ': fields.related('payment_type', relation="payment.type", type='many2one', string="Tipo Pago", readonly=True),
        'traking': fields.related('picking_ids', 'carrier_tracking_ref', type='char', string="Tracking"),


    }


sale_order()

