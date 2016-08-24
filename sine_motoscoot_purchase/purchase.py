##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from osv import fields,osv


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        #'stock_grn': fields.related('product_id','stock_grn', type='float', string='G'),
        #'stock_bcn': fields.related('product_id','stock_bcn', type='float',  string='B'),
        #'stock_pt': fields.related('product_id','stock_pt', type='float',  string='P'),
        'sum_stock': fields.related('product_id', 'test', type='char', string='Stocks'),
        'incoming': fields.related('product_id', 'incoming_qty', type='float', string='IN'),
        'outgoing': fields.related('product_id', 'outgoing_qty', type='float', string='OUT'),

    }

purchase_order_line()
