# -*- encoding: utf-8 -*-
##############################################################################
#
# Module Writen to OpenERP, Open Source Management Solution
#    Sinergiainformatica.net
#    David Hernández (soporte@sinergiainformatica.net)
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

from openerp.osv import fields, osv


class res_partner_category(osv.osv):
    _inherit = 'res.partner.category'

    _columns = {

        'pricelist': fields.many2one('product.pricelist', 'Asociated Pricelist',
                                     help="Link this Category with a Pricelist", required=True),
    }


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def onchange_category(self, cr, uid, id, category_id, context=None):
        if category_id:
            parent_id = self.pool.get('res.partner').browse(cr, uid, id[0][2], context)
            pricelist_id = self.pool.get('res.partner.category').browse(cr, uid, category_id[0][2], context)
            if not parent_id:
                if pricelist_id:
                    return {'value': {'property_product_pricelist': pricelist_id[0].pricelist.id}}
                else:
                    return {'value': {'property_product_pricelist': 1}}

            return {}

