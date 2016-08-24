# -*- encoding: utf-8 -*-
##############################################################################
#
# Module Writen to OpenERP, Open Source Management Solution
# Copyright (C) 2015 OBERTIX FREE SOLUTIONS (<http://obertix.net>).
#                       cubells <vicent@vcubells.net>
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import osv, fields, orm
import logging

_logger = logging.getLogger(__name__)


class CalculatePricelist(orm.TransientModel):
    _name = "calculate.pricelist"
    _description = "Calculate Pricelist"

    _columns = {
        'pricelist_ids': fields.one2many('calculate.pricelist.line',
                                         'wizard_id', 'Pricelist line',
                                         domain=[('pricelist_id.type', '=', 'sale')]),
        'state': fields.selection([
            ('initial', 'Initial'),
            ('done', 'Done'),
        ], 'State', readonly=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      domain=[('sale_ok', '=', True)],
                                      required=True),
        'qty': fields.integer('Quantity', required=True),

        'pricelist_ids2': fields.one2many('calculate.pricelist.line',
                                          'wizard_id', 'Pricelist line',
                                          domain=[('pricelist_id.type', '=', 'purchase')]),
    }

    _defaults = {
        'state': lambda *a: 'initial',
        'qty': 1.0,
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        model = context.get('active_model', False)
        product_id = False
        if model and model == 'product.product':
            product_id = context.get('active_id')
        res = super(CalculatePricelist, self).default_get(cr, uid, fields,
                                                          context)
        if product_id and 'product_id' in fields:
            res['product_id'] = product_id
        return res

    def button_calculate(self, cr, uid, ids, context=None):

        def get_real_price(res_dict, product_id, qty, pricelist):
            pricelist_obj = self.pool['product.pricelist']
            item_obj = self.pool['product.pricelist.item']
            price_type_obj = self.pool['product.price.type']
            product_obj = self.pool.get('product.product')
            field_name = 'list_price'
            item = res_dict.get('item_id', False) and res_dict['item_id'].get(
                pricelist, False)
            if item:
                if item_obj.read(cr, uid, [item], ['base']):
                    item_base = item_obj.read(
                        cr, uid, [item], ['base'])[0]['base']
                    if item_base > 0:
                        field_name = price_type_obj.browse(
                            cr, uid, item_base).field
                else:
                    pricelist = pricelist_obj.browse(cr, uid, pricelist)
                    version = pricelist.version_id and \
                              pricelist.version_id[0].id or False
                    if version:
                        item = item_obj.search(cr, uid, [
                            ('price_version_id', '=', version)
                        ])
                        if item:
                            item_base = item_obj.read(
                                cr, uid, item, ['base'])[0]['base']
                            if item_base > 0:
                                field_name = price_type_obj.browse(
                                    cr, uid, item_base).field
            product = product_obj.browse(cr, uid, product_id, context)
            product_read = product_obj.read(
                cr, uid, product_id, [field_name], context=context)
            return product_read[field_name]

        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'done'})
        pricelist_obj = self.pool['product.pricelist']
        line_obj = self.pool['calculate.pricelist.line']
        line_ids = line_obj.search(cr, uid, [('wizard_id', 'in', ids)],
                                   context=context)
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            line_obj.unlink(cr, uid, line.id, context=context)
        data = self.browse(cr, uid, ids[0], context)
        price_ids = pricelist_obj.search(cr, uid, [('type', 'in', ['sale', 'purchase'])],
                                         context=context)
        for plist in pricelist_obj.browse(cr, uid, price_ids, context=context):
            tax = data.product_id.taxes_id and \
                  data.product_id.taxes_id[0].amount or 0.0
            tax += 1
            if plist.version_id:
                if plist.version_id[0].items_id:
                    print plist.version_id[0].items_id[0].base
            price = pricelist_obj.price_get(
                cr, uid, [plist.id], data.product_id.id, data.qty, False,
                context=context)[plist.id]
            list_price = data.product_id.list_price or 0.0
            percent = 0.0

            base = get_real_price(
                pricelist_obj.price_get(
                    cr, uid, [plist.id], data.product_id.id, data.qty, False,
                    context=context),
                data.product_id.id, float(data.qty), plist.id)
            if base:
                percent = 100 - ((price * 100) / base)
            standard_price = data.product_id.standard_price or 0.0
            default_code = data.product_id.default_code or ''
            if default_code:
                default_code = '[%s]' % default_code

            values = {
                'wizard_id': ids[0],
                'pricelist_id': plist.id,
                'product_id': data.product_id.id,
                'default_code': default_code,
                'qty': float(data.qty),
                'base': base,
                'price': price,
                'standard_price': standard_price,
                'margin': price - standard_price,
                'percent': percent,
                'total': price * tax,
            }
            line_obj.create(cr, uid, values, context=context)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calculate.pricelist',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }


class CalculatePricelistLine(orm.TransientModel):
    _name = "calculate.pricelist.line"

    _columns = {
        'wizard_id': fields.many2one('calculate.pricelist', 'Wizard',
                                     readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist',
                                        readonly=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      readonly=True),
        'default_code': fields.char('Product', size=64, readonly=True),
        'qty': fields.integer('Quantity', readonly=True),
        'base': fields.float('Base Price', readonly=True),
        'price': fields.float('Final Price', readonly=True),
        'standard_price': fields.float('Standard Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'percent': fields.float('Discount', readonly=True),
        'total': fields.float('Price with Tax', readonly=True),
    }

