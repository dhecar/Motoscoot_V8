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

from openerp import models, fields, api, exceptions
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    # STOCK IN EACH LOCATION
    @api.model
    def StockByLocation(self):

        db_obj = self.pool['base.external.dbsource']
        location_id = 12
        res = {}
        for i in self:
            # 'B' DB
            # ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, i, location_id,
            #                       context=context)

            self.env.cr.execute(""" SELECT SUM(qty) AS QTY, CASE
                                        WHEN location_id='12' THEN 'G'
                                        WHEN location_id='19' THEN 'B'
                                        WHEN location_id='15' THEN 'P'
                                        END AS LOC FROM stock_quant

                                        WHERE (location_id ='12' OR location_id ='19' OR location_id='15')
                                        AND product_id = '%s'  GROUP BY location_id ORDER BY location_id""" % i.id)
            res[i] = self.env.cr.dictfetchall()

            if not res[i]:
                res[i] = {}
            else:
                # GRN
                if res[i][0]['loc'] == 'G':
                    res[i][0]['qty'] = res[i][0]['qty']
                    # res[i][0]['qty'] = res[i][0]['qty'] - ads
            counter = 0
            qty = ""
            qty_final = ""
            for location in res[i]:
                counter += 1
                qty += '  ' + str(res[i][counter - 1]['loc']) + "=" + str(res[i][counter - 1]['qty']) + '    '
            qty_final += qty

            i.stock_by_loc = qty_final


    stock_by_loc = fields.Char(compute='StockByLocation', string='Stocks')
    internal_note = fields.Text(string='Nota Interna', translate=True)
    shared = fields.Boolean(string='Shared', help='Share this product with SCTV?')
    pvp_fabricante = fields.Float(string='Precio Base TT',
                                  digits_compute=dp.get_precision('Precio Base TT (Tarifa Fabricante sin IVA)'))
    internet = fields.Boolean(string='Internet?', help='Está activo en Magento?')
    label_print = fields.Boolean(string='Label Print?', help='Se debe imprimir la etiqueta en albaranes de entrada?',
                                 default='True')


ProductTemplate()


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    # STOCK IN EACH LOCATION
    @api.model
    def _compute_stock_by_location(self):

        db_obj = self.pool['base.external.dbsource']
        location_id = 12
        res = {}
        for i in self:
            # 'B' DB
            # ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, i, location_id,
            #                       context=context)

            self.env.cr.execute(""" SELECT SUM(qty) AS QTY, CASE
                                        WHEN location_id='12' THEN 'G'
                                        WHEN location_id='19' THEN 'B'
                                        WHEN location_id='15' THEN 'P'
                                        END AS LOC FROM stock_quant

                                        WHERE (location_id ='12' OR location_id ='19' OR location_id='15')
                                        AND product_id = '%s'  GROUP BY location_id ORDER BY location_id""" % i.id)
            res[i] = self.env.cr.dictfetchall()

            if not res[i]:
                res[i] = {}
            else:
                # GRN
                if res[i][0]['loc'] == 'G':
                    res[i][0]['qty'] = res[i][0]['qty']
                    # res[i][0]['qty'] = res[i][0]['qty'] - ads
            counter = 0
            qty = ""
            qty_final = ""
            for location in res[i]:
                counter += 1
                qty += '  ' + str(res[i][counter - 1]['loc']) + "=" + str(res[i][counter - 1]['qty']) + '    '

            qty_final += qty
            i.stock_by_loc = qty_final

    stock_by_loc = fields.Char(compute=_compute_stock_by_location, string='Stocks')
    internal_note = fields.Text(string='Nota Interna', translate=True)
    shared = fields.Boolean(string='Shared', help='Share this product with SCTV?')
    pvp_fabricante = fields.Float(string='Precio Base TT',
                                  digits_compute=dp.get_precision('Precio Base TT (Tarifa Fabricante sin IVA)'))
    internet = fields.Boolean(string='Internet?', help='Está activo en Magento?')
    label_print = fields.Boolean(string='Label Print?', help='Se debe imprimir la etiqueta en albaranes de entrada?',
                                 default='True')


ProductProduct()
