# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
import psycopg2
import openerp.tools as tools


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'

    def test(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result

        context['only_with_stock'] = True

        for id in ids:
            context['product_id'] = id
            location_obj = self.pool.get('stock.location')
            result[id] = location_obj.search(cr, uid, [('usage', '=', 'internal')], context=context)

        return result

    # STOCK IN EACH LOCATION

    def StockByLocation(self, cr, uid, ids, name, args, context=None):

        db_obj = self.pool['base.external.dbsource']
        location_id = 12
        res = {}
        for i in ids:
            ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, i, location_id,
                                   context=context)

            cr.execute(""" SELECT qty AS QTY, CASE
                        WHEN location_id='12' THEN 'G'
                        WHEN location_id='19' THEN 'B'
                        WHEN location_id='15' THEN 'P'
                        END AS LOC FROM stock_report_prodlots
                        WHERE (location_id ='12' OR location_id ='19' OR location_id='15')
                        AND product_id = '%s' ORDER BY location_id""" % i)
            res[i] = cr.dictfetchall()

            if not res[i]:
                res[i] = {}
            else:
                # GRN
                if res[i][0]['loc'] == 'G':
                    res[i][0]['qty'] = res[i][0]['qty'] - ads
            counter = 0
            qty = ""
            for location in res[i]:
                counter += 1
                qty += '[' + str(res[i][counter - 1]['loc']) + ":" + str(res[i][counter - 1]['qty']) + ']'

            res[i] = qty
        return res

    _columns = {

        'test': fields.function(StockByLocation, type='char', string='Stocks'),
        'locations': fields.function(test, type='one2many', relation='stock.location', string='Stock by Location'),
        # 'scooters_ids': fields.many2many('scooter.asociaciones', 'scooter_compat_with_product_rel', 'product_id',
        #                                  'scooter_id', 'scooter models'),
        'internal_note': fields.text('Nota Interna', translate=True),
        'shared': fields.boolean('Shared', help='Share this product with SCTV?'),
        'pvp_fabricante': fields.float('Precio Base TT',
                                       digits_compute=dp.get_precision('Precio Base TT (Tarifa Fabricante sin IVA)')),
        'internet': fields.boolean('Internet?', help='Está activo en Magento?'),
        'label_print': fields.boolean('Label Print?', help='Se debe imprimir la etiqueta en albaranes de entrada?'),
    }

    _defaults = {
        'label_print': True
    }


product_product()
