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
from openerp import models, fields, api, exceptions
from openerp import SUPERUSER_ID


class SaleOrderLine(models.Model):

    def StockSearch(self):
        for rec in self:
            rec.sum_stock = rec.sum_stock

    # STOCK IN EACH LOCATION

    _inherit = 'sale.order.line'

    sum_stock = fields.Char(related='product_id.stock_by_loc', string='Stocks')
    #sum_stock = fields.Char(compute='StockByLocation', string='Stocks', size=40)
    incoming = fields.Float(related='product_id.incoming_qty', string='IN')
    outgoing = fields.Float(related='product_id.outgoing_qty', string='OUT')
    product_id = fields.Many2one(comodel_name='product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True)


SaleOrderLine()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_internal_comment = fields.Text('Internal Comment', help='')
    picking_status = fields.Selection(related='picking_ids.state', string="Estado envio")
    # date_send = fields.Datetime(related='picking_ids.date_done', string="Fecha Envio")
    invoice_status = fields.Boolean(related='invoiced', string="Estado Factura")
    traking = fields.Char(related='picking_ids.carrier_tracking_ref', string="Tracking")

SaleOrder()
