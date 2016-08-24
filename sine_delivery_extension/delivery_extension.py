# -*- coding: utf-8 -*-


import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class delivery_carrier(osv.osv):
    _inherit = 'delivery.carrier'

    _columns = {
        'cod_price': fields.float('COD Price', digits_compute=dp.get_precision('COD value'),
                                  help="Add new line with COD price"),

    }


class sale_order(osv.osv):
    _inherit = 'sale.order'
    # _columns = {
    #        'carrier_id':fields.many2one("delivery.carrier", "Delivery Method", help="Complete this field if you plan to invoice the shipping based on picking."),
    #    }
    _columns = {
    }


    def delivery_set(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        acc_fp_obj = self.pool.get('account.fiscal.position')
        for order in self.browse(cr, uid, ids, context=context):
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id], order.partner_shipping_id.id)
            if not grid_id:
                raise osv.except_osv(_('No Grid Available!'), _('No grid matching for this carrier!'))

            if not order.state in ('draft', 'sent'):
                raise osv.except_osv(_('Order not in Draft State!'),
                                     _('The order state have to be draft to add delivery lines.'))

            grid = grid_obj.browse(cr, uid, grid_id, context=context)

            taxes = grid.carrier_id.product_id.taxes_id
            fpos = order.fiscal_position or False
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
            #create the sale order line

            line_obj.create(cr, uid, {
                'order_id': order.id,
                'name': grid.carrier_id.product_id.name,
                #                'name': grid.carrier_id.name,
                'product_uom_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': grid_obj.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context),
                'tax_id': [(6, 0, taxes_ids)],
                'type': 'make_to_stock'
            })

            #If COD price is established, add new line

            if grid.carrier_id.cod_price:
                line_obj.create(cr, uid, {
                    'order_id': order.id,
                    'name': 'contrareembolso',
                    'product_uom_qty': 1,
                    'product_uom': grid.carrier_id.product_id.uom_id.id,
                    'product_id': grid.carrier_id.product_id.id,
                    'price_unit': grid.carrier_id.cod_price,
                    'tax_id': [(6, 0, taxes_ids)],
                    'type': 'make_to_stock'
                })
        return True


delivery_carrier()


