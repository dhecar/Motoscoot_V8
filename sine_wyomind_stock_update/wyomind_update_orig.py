# -*- coding: utf-8 -*-
##############################################################################
# Author : David Hernandez. 2015. http://sinergiainformatica.net
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
import xmlrpclib
import time
from openerp import netsvc
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class WyomindConfig(osv.osv):
    _name = 'wyomind.config'
    _description = 'Configuration for Wyomind API stock update'
    _table = 'wyomind_config'
    _columns = {
        'url': fields.char('Api Url', help="Example --> http://WEBSITE/index.php/api/xmlrpc/", size=60),
        'apiuser': fields.char('Api User', size=15),
        'apipass': fields.char('Api Password', size=15)
    }


WyomindConfig()


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _description = 'Update the stock from Openerp to Magento (Advanced Inventory) when the move' \
                   ' go to done state'

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == "draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done', 'cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id', 'not in', move_ids),
                                                                ('state', 'not in', ['done', 'cancel']),
                                                                ('move_dest_id', '=', move.move_dest_id.id)],
                                                      context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._update_average_price(cr, uid, move, context=context)
            self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed', 'done', 'assigned'):
                self.action_confirm(cr, uid, [move.id], context=context)

            self.write(cr, uid, [move.id],
                       {'state': 'done',
                        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
                       context=context)

            # Update xmlrpc. Wyomind Advanced Inventory
            # Get configuration from wyomind_config
            conf_obj = self.pool.get('wyomind.config')
            conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
            for i in conf_obj.browse(cr, uid, conf_ids):
                url = i.url
                user = i.apiuser
                passw = i.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)

            # We get the product qty from stock_report_prodlots
            # For internal movements, two updates are made, one for each location (origin/destination)
            # For in movements, we update the destination location
            # For out movements, we update the origin location

            def get_stock(self, cr, uid, ids, context=None):
                stock_prod_obj = self.pool.get('stock.report.prodlots')
                db_obj = self.pool['base.external.dbsource']
                '''usage:internal, type :in '''
                if move.picking_id.type == 'in' and move.location_dest_id.usage == 'internal':
                    result = {}
                    for prod_id in move_ids:
                        stock_prod_ids = stock_prod_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                                                         ('location_id', '=', move.location_dest_id.id)]
                                                               , context=context)
                        ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, prod_id,
                                               move.location_id.id,
                                               context=context)
                        if stock_prod_ids:
                            for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                                result = i.qty - ads
                    return result

                '''usage:internal, type :out '''
                if move.picking_id.type == 'out' and move.location_id.usage == 'internal':
                    result = {}
                    for prod_id in move_ids:
                        stock_prod_ids = stock_prod_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                                                         ('location_id', '=', move.location_id.id)],
                                                               context=context)
                        ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, prod_id,
                                               move.location_id.id,
                                               context=context)
                        if stock_prod_ids:
                            for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                                result = i.qty - ads

                    return result

            # We get magento product_id

            def get_mag_prod_id(self, cr, uid, ids, context=None):
                mag_prod_obj = self.pool.get('magento.product.product')
                result = {}
                for magento_prod_id in move_ids:
                    mag_prod_ids = mag_prod_obj.search(cr, uid, [('openerp_id', '=', move.product_id.id)],
                                                       context=context)

                    if mag_prod_ids:
                        for prod in mag_prod_obj.browse(cr, uid, mag_prod_ids, context=context):
                            result = prod.magento_id

                return result

            # we hardcoded the mapping local-remote warehouse
            location = 0
            if move.location_id.id == 12 or move.location_dest_id.id == 12:
                location = 2
            if move.location_id.id == 15 or move.location_dest_id.id == 15:
                location = 4
            if move.location_id.id == 19 or move.location_dest_id.id == 19:
                location = 3

            data_basic = {'quantity_in_stock': get_stock(self, cr, uid, ids, context=context),
                          'manage_stock': 1,
                          'backorder_allowed': 0,
                          'use_config_setting_for_backorders': 1}

            proxy.call(session, 'advancedinventory.setData', (get_mag_prod_id(self, cr, uid, ids, context=context),
                                                              location, data_basic))

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True


stock_move()


class stock_change_product_qty(osv.osv_memory):
    _inherit = "stock.change.product.qty"

    def change_product_qty(self, cr, uid, ids, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')

        inventry_obj = self.pool.get('stock.inventory')
        inventry_line_obj = self.pool.get('stock.inventory.line')
        prod_obj_pool = self.pool.get('product.product')

        res_original = prod_obj_pool.browse(cr, uid, rec_id, context=context)
        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
            inventory_id = inventry_obj.create(cr, uid, {'name': _('INV: %s') % tools.ustr(res_original.name)},
                                               context=context)
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': data.new_quantity,
                'location_id': data.location_id.id,
                'product_id': rec_id,
                'product_uom': res_original.uom_id.id,
                'prod_lot_id': data.prodlot_id.id
            }

            inventry_line_obj.create(cr, uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)

            # Update Stock in Magento
            conf_obj = self.pool.get('wyomind.config')
            conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
            for i in conf_obj.browse(cr, uid, conf_ids):
                url = i.url
                user = i.apiuser
                passw = i.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)

            def get_mag_prod_id(self, cr, uid, ids, context=None):
                mag_prod_obj = self.pool.get('magento.product.product')
                result = {}
                mag_prod_ids = mag_prod_obj.search(cr, uid, [('openerp_id', '=', rec_id)],
                                                   context=context)

                if mag_prod_ids:
                    for prod in mag_prod_obj.browse(cr, uid, mag_prod_ids, context=context):
                        result = prod.magento_id

                    return result

            # we hardcoded the mapping local-remote warehouse

            location = 0
            if data.location_id.id == 12:
                location = 2
            if data.location_id.id == 15:
                location = 4
            if data.location_id.id == 19:
                location = 3

            data_basic = {'quantity_in_stock': data.new_quantity,
                          'manage_stock': 1,
                          'backorder_allowed': 0,
                          'use_config_setting_for_backorders': 1}

            proxy.call(session, 'advancedinventory.setData', (get_mag_prod_id(self, cr, uid, ids, context=context),
                                                              location, data_basic))

        return {}


stock_change_product_qty()


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        db_obj = self.pool['base.external.dbsource']
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date': partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:

            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            # Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            # Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor <> 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _(
                        'The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (
                                             wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                # Check rounding Quantity.ex.
                # picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                # partial delivery: 253g
                # => result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                # Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty,
                                 precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'), _(
                        'The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (
                                             wizard_line.quantity, line_uom.name,
                                             wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name,
                                             initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {'name': self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                      'product_id': wizard_line.product_id.id,
                                                      'product_qty': wizard_line.quantity,
                                                      'product_uom': wizard_line.product_uom.id,
                                                      'prodlot_id': wizard_line.prodlot_id.id,
                                                      'location_id': wizard_line.location_id.id,
                                                      'location_dest_id': wizard_line.location_dest_id.id,
                                                      'picking_id': partial.picking_id.id
                                                      }, context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
                partial_data['move%s' % (move_id)] = {
                    'product_id': wizard_line.product_id.id,
                    'product_qty': wizard_line.quantity,
                    'product_uom': wizard_line.product_uom.id,
                    'prodlot_id': wizard_line.prodlot_id.id,
                }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % wizard_line.move_id.id].update(product_price=wizard_line.cost,
                                                                       product_currency=wizard_line.currency.id)

        done = stock_picking.do_partial(
            cr, uid, [partial.picking_id.id], partial_data, context=context)

        if done[partial.picking_id.id]['delivered_picking'] == partial.picking_id.id:

            def get_stock_origin(self, cr, uid, ids, context=None):
                stock_prod_obj = self.pool.get('stock.report.prodlots')
                if partial.picking_id.type == 'internal' and wizard_line.location_id.usage == 'internal':

                    result = {}
                    stock_prod_ids = stock_prod_obj.search(cr, uid, [('product_id', '=', wizard_line.product_id.id),
                                                                     ('location_id', '=', wizard_line.location_id.id)],
                                                           context=context)
                    ads = db_obj.get_stock(cr, uid, SUPERUSER_ID,
                                           wizard_line.product_id.id,
                                           wizard_line.location_id.id,
                                           context=context)
                    if stock_prod_ids:
                        for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                            result = i.qty - ads

                        return result

            def get_stock_dest(self, cr, uid, ids, context=None):
                stock_prod_obj = self.pool.get('stock.report.prodlots')
                if partial.picking_id.type == 'internal' and wizard_line.location_dest_id.usage == 'internal':
                    result = {}
                    stock_prod_ids = stock_prod_obj.search(cr, uid, [('product_id', '=', wizard_line.product_id.id),
                                                                     ('location_id', '=',
                                                                      wizard_line.location_dest_id.id)],
                                                           context=context)
                    ads = db_obj.get_stock(cr, uid, SUPERUSER_ID,
                                           wizard_line.product_id.id,
                                           wizard_line.location_dest_id.id,
                                           context=context)
                    if stock_prod_ids:
                        for i in stock_prod_obj.browse(cr, uid, stock_prod_ids, context=context):
                            result = i.qty - ads

                        return result

            def get_mag_prod_id(self, cr, uid, ids, context=None):

                mag_prod_obj = self.pool.get('magento.product.product')
                result = {}
                mag_prod_ids = mag_prod_obj.search(cr, uid, [('openerp_id', '=', wizard_line.product_id.id)],
                                                   context=context)

                if mag_prod_ids:
                    for prod in mag_prod_obj.browse(cr, uid, mag_prod_ids, context=context):
                        result = prod.magento_id

                    return result

                    # Do the partial delivery and open the picking that was delivered
                    # We don't need to find which view is required, stock.picking does it.

            def get_location(cr, uid):
                location = 0
                if wizard_line.location_dest_id.id == 12:
                    location = 2
                if wizard_line.location_dest_id.id == 15:
                    location = 4
                if wizard_line.location_dest_id.id == 19:
                    location = 3
                return location

            def get_location2(cr, uid):
                location2 = 0
                if wizard_line.location_id.id == 12:
                    location2 = 2
                if wizard_line.location_id.id == 15:
                    location2 = 4
                if wizard_line.location_id.id == 19:
                    location2 = 3
                return location2

            conf_obj = self.pool.get('wyomind.config')
            conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
            for x in conf_obj.browse(cr, uid, conf_ids):
                url = x.url
                user = x.apiuser
                passw = x.apipass

            # Connection
            proxy = xmlrpclib.ServerProxy(url, allow_none=True)
            session = proxy.login(user, passw)
            # Wyomind stock update
            for wizard_line in partial.move_ids:
                data_basic = {'quantity_in_stock': get_stock_dest(self, cr, uid, ids, context=context),
                              'manage_stock': 1,
                              'backorder_allowed': 0,
                              'use_config_setting_for_backorders': 1}

                if partial.picking_id.type == 'internal':
                    proxy.call(session, 'advancedinventory.setData',
                               (get_mag_prod_id(self, cr, uid, ids, context=context),
                                get_location(cr, uid), data_basic))

                data_basic2 = {'quantity_in_stock': get_stock_origin(self, cr, uid, ids, context=context),
                               'manage_stock': 1,
                               'backorder_allowed': 0,
                               'use_config_setting_for_backorders': 1}

                if partial.picking_id.type == 'internal':
                    proxy.call(session, 'advancedinventory.setData',
                               (get_mag_prod_id(self, cr, uid, ids, context=context),
                                get_location2(cr, uid), data_basic2))

            return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'res_model': context.get('active_model', 'stock.picking'),
            'name': _('Partial Delivery'),
            'res_id': done[partial.picking_id.id]['delivered_picking'],
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'context': context,
        }


stock_partial_picking()
