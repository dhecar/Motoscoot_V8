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


class SaleOrderLine(osv.osv):
    #    def product_id_change(self, cr, uid, ids, pricelist, product,  qty=0,
    #                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
    #                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
    #                          flag=False, order=False,  context=None):
    #        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product,  qty=qty,
    #                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name,
    #                                                             partner_id=partner_id,
    #                                                             lang=lang, update_tax=update_tax, date_order=date_order,
    #                                                             packaging=packaging, fiscal_position=fiscal_position,
    #                                                             flag=flag, order=order, context=context)
    #
    #        sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order)], context=context)
    #
    #        for line in sale_line_ids:
    #
    #            if line.product_id == product:
    #                warning = {
    #                    'title': 'EH Campeon!!!',
    #                    'message': 'Este producto ya lo tienes en el pedido, estas seguro de volverlo a meter?'
    #                    }
    #                return {'warning': warning}

    #        return res

    _inherit = 'sale.order.line'
    _columns = {

        'incoming': fields.related('product_id', 'incoming_qty', type='float', string='IN'),
        'outgoing': fields.related('product_id', 'outgoing_qty', type='float', string='OUT'),
        'date_ordered': fields.related('order_id', 'date_order', type='char', relation='sale.order',
                                       string='Fecha Orden'),

    }


SaleOrderLine()


class SaleOrder(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'sale_internal_comment': fields.text('Internal Comment', help=''),
        'picking_status': fields.related('picking_ids', 'state', type='char', string="Estado envio"),
        'date_send': fields.related('picking_ids', 'date_done', type='char', string="Fecha Envio"),
        'invoice_status': fields.related('invoiced', type='boolean', string="Estado Factura"),
        'traking': fields.related('picking_ids', 'carrier_tracking_ref', type='char', string="Tracking"),
        'alert': fields.related('partner_id', 'sale_warn_msg', type='char', help='Sale Alert', string='Alerta'),

    }
SaleOrder()
