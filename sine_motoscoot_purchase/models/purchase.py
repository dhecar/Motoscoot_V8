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

from openerp import models, fields, api, exceptions


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    sum_stock = fields.Char(related='product_id.stock_by_loc', string='Stocks'),
    incoming = fields.Float(related='product_id.incoming_qty',string='IN')
    outgoing = fields.Float(related='product_id.outgoing_qty', string='OUT')

PurchaseOrderLine()
