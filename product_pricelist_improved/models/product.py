# -*- encoding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OBERTIX FREE SOLUTIONS (<http://obertix.net>).
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

from osv import osv, fields
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class ProductCategory(osv.osv):
    _inherit = "product.category"

    _columns = {
        'margin_pricelist': fields.float(
            'Pricelist margin (%)', help="Minimum profit margin on the price "
                                         "of products in this category"),
    }
    _defaults = {
        'margin_pricelist': 0.0,
    }


class ProductProduct(osv.osv):
    _inherit = "product.product"

    _columns = {
        'margin_pricelist': fields.float(
            'Pricelist margin (%)', help="Minimum profit margin on the price "
                                         "of products in this product"),
    }
    _defaults = {
        'margin_pricelist': 0.0,
    }

    def create(self, cr, uid, vals, context=None):
        categ_obj = self.pool['product.category']
        if not vals.get('margin_pricelist'):
            categ_id = vals.get('categ_id')
            categ = categ_obj.browse(cr, uid, categ_id)
            vals['margin_pricelist'] = categ.margin_pricelist or 0.0
        return super(ProductProduct, self).create(cr, uid, vals,
                                                  context=context)
