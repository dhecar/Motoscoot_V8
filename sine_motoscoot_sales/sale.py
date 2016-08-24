##############################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import fields, osv
from openerp import SUPERUSER_ID


class sale_order_line(osv.osv):
    def final_price(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                res[line.id] = round(line.price_subtotal - (
                    (line.purchase_price or line.product_id.standard_price) * line.product_uos_qty), 2)
        return res



        # STOCK IN EACH LOCATION

    def StockByLocation(self, cr, uid, ids, name, args, context=None):

        db_obj = self.pool['base.external.dbsource']

        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id:
                product = line.product_id.id
                location_id = 12
                ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, product, location_id,
                                       context=context)

                cr.execute(""" SELECT qty AS QTY, CASE
                            WHEN location_id='12' THEN 'G'
                            WHEN location_id='19' THEN 'B'
                            WHEN location_id='15' THEN 'P'
                            END AS LOC FROM stock_report_prodlots
                            WHERE (location_id ='12' OR location_id ='19' OR location_id='15')
                            AND product_id = '%s' ORDER BY location_id""" % product)
                res[line.id] = cr.dictfetchall()

                if not res[line.id]:
                    res[line.id] = []
                else:
                    # GRN
                    if res[line.id][0]['loc'] == 'G':
                        res[line.id][0]['qty'] = res[line.id][0]['qty'] - ads
                counter = 0
                qty = ""
                qty_final = ""
                for location in res[line.id]:
                    counter += 1
                    qty += '[' + str(res[line.id][counter - 1]['loc']) + ":" + str(
                        res[line.id][counter - 1]['qty']) + ']'
                qty_final += '[' + qty + ']'

                res[line.id] = qty_final
        return res

    _inherit = 'sale.order.line'
    _columns = {

        'sum_stock': fields.function(StockByLocation, type='char', string='Stocks'),
        'incoming': fields.related('product_id', 'incoming_qty', type='float', string='IN'),
        'outgoing': fields.related('product_id', 'outgoing_qty', type='float', string='OUT'),
        'date_ordered': fields.related('order_id', 'date_order', type='char', relation='sale.order',
                                       string='Fecha Orden'),
        'margin_ok': fields.function(final_price, string='Margin'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True),

    }


sale_order_line()


class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'sale_internal_comment': fields.text('Internal Comment', help=''),
        'picking_status': fields.related('picking_ids', 'state', type='char', string="Estado envio"),
        'date_send': fields.related('picking_ids', 'date_done', type='char', string="Fecha Envio"),
        'invoice_status': fields.related('invoiced', type='boolean', string="Estado Factura"),
        'traking': fields.related('picking_ids', 'carrier_tracking_ref', type='char', string="Tracking"),
        'alert': fields.related('partner_id', 'sale_warn_msg', type='char', help='Sale Alert', string='Alerta'),

    }


sale_order()
