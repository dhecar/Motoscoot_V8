# -*- coding: utf-8 -*-
##############################################################################
#
# David Hernández. 2014
# http://sinergiainformatica.net
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
import time
from openerp import tools
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp


def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r


class ProductPricelistItem(models.Model):
    _name = "product.pricelist.item"
    _inherit = "product.pricelist.item"

    brand_id = fields.Many2one(comodel_name= 'product.brand', string='Product Brand', ondelete='cascade',
                               help="Select the brand  you want to link this pricelist")


ProductPricelistItem()


class ProductPricelist(models.Model):
    _name = "product.pricelist"
    _inherit = "product.pricelist"

    user_link_ids = fields.Many2many('res.users', 'pricelist_partner_rel', 'pricelist_id', 'user_id', required=True)

    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False,
                access_rights_uid=None):
        if context and context.get('pricelist_user_only'):
            pricelist_ids = self.pool['res.users'].read(cr, user, user, ['pricelist_ids'], context=context)[
                'pricelist_ids']
            args = [('id', 'in', pricelist_ids)] + args
        return super(ProductPricelist, self)._search(cr, user, args, offset, limit, order, context, count,
                                                     access_rights_uid)

    # def price_get_multi(self, cr, uid, product_ids, context=None):
    def price_get_multi(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param pricelist_ids:
           @param products_by_qty:
               @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst

        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')
        product_pricelist_version_obj = self.pool.get('product.pricelist.version')

        # product.pricelist.version:
        if pricelist_ids:
            pricelist_version_ids = pricelist_ids
        else:
            # all pricelists:
            pricelist_version_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = list(set(pricelist_version_ids))
        plversions_search_args = [
            ('pricelist_id', 'in', pricelist_version_ids),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', date),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', date),
        ]

        plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
        print plversion_ids[0]
        if len(pricelist_version_ids) != len(plversion_ids):
            msg = "At least one pricelist has no active version !\nPlease create or activate one."
            raise Warning(_('Warning !'), _(msg))
            # product.product:
        product_ids = [i[0] for i in products_by_qty_by_partner]
        # products = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict(
            [(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = {}

        for product_id, qty, partner in products_by_qty_by_partner:

            for pricelist_id in pricelist_version_ids:
                price = False

                tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[
                    product_id].product_tmpl_id.id or False

                categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'

                product_brand_ids = products_dict[product_id].product_brand_id.id or 0

                cr.execute(
                    'SELECT i.*, pl.currency_id '
                    'FROM product_pricelist_item AS i, '
                    'product_pricelist_version AS v, product_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                    'AND (product_id IS NULL OR product_id = %s) '
                    'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                                            'AND price_version_id = %s '
                                            'AND (min_quantity IS NULL OR min_quantity <= %s) '
                                            'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                                            'AND (i.brand_id IS NULL OR i.brand_id = %s)  '
                                            'ORDER BY sequence ',
                    (tmpl_id, product_id, plversion_ids[0], qty, product_brand_ids))

                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                for res in res1:
                    if res:
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                price = 0.0
                            else:
                                price_tmp = self.price_get(cr, uid,
                                                           [res['base_pricelist_id']], product_id,
                                                           qty, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                price = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp,
                                                             round=False)
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            where = []
                            if partner:
                                where = [('name', '=', partner)]
                            sinfo = supplierinfo_obj.search(cr, uid,
                                                            [('product_id', '=', tmpl_id)] + where)
                            price = 0.0
                            if sinfo:
                                qty_in_product_uom = qty
                                product_default_uom = product_obj.read(cr, uid, [tmpl_id], ['uom_id'])[0]['uom_id'][0]
                                seller_uom = supplierinfo_obj.read(cr, uid, sinfo, ['product_uom'])[0]['product_uom'][0]
                                if seller_uom and product_default_uom and product_default_uom != seller_uom:
                                    uom_price_already_computed = True
                                    qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, product_default_uom, qty,
                                                                                      to_uom_id=seller_uom)
                                cr.execute('SELECT * ' \
                                           'FROM pricelist_partnerinfo ' \
                                           'WHERE suppinfo_id IN %s' \
                                           'AND min_quantity <= %s ' \
                                           'ORDER BY min_quantity DESC LIMIT 1', (tuple(sinfo), qty_in_product_uom,))
                                res2 = cr.dictfetchone()
                                if res2:
                                    price = res2['price']
                        else:
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            price = currency_obj.compute(cr, uid,
                                                         price_type.currency_id.id, res['currency_id'],
                                                         product_obj.price_get(cr, uid, [product_id],
                                                                               price_type.field, context=context)[
                                                             product_id], round=False, context=context)

                        if price is not False:
                            price_limit = price

                            price = price * (1.0 + (res['price_discount'] or 0.0))
                            price = rounding(price, res['price_round'])
                            price += (res['price_surcharge'] or 0.0)
                            if res['price_min_margin']:
                                price = max(price, price_limit + res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit + res['price_max_margin'])
                            break

                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False

                if price:
                    results['item_id'] = res['id']
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom = product.uos_id or product.uom_id
                        price = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, price, context['uom'])

                if results.get(product_id):
                    results[product_id][pricelist_id] = price
                else:
                    results[product_id] = {pricelist_id: price}

        return results


ProductPricelist()


class ResUsers(models.Model):
    _inherit = 'res.users'

    pricelist_ids = fields.Many2many('product.pricelist', 'pricelist_partner_rel', 'user_id', 'pricelist_id')


ResUsers()
