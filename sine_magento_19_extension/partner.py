# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
# Copyright 2013 Camptocamp SA
#
# Enhanced By Sinergiainformatica.net 2016
# Add category_id sync in contact partners
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from openerp.osv import orm, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper
                                                  )

from openerp.addons.magentoerpconnect.partner import (BaseAddressImportMapper, AddressImportMapper)
_logger = logging.getLogger(__name__)

from openerp.addons.magentoerpconnect import partner


from openerp.addons.magentoerpconnect.backend import magento

class magento_address(orm.Model):
    _inherit = 'magento.address'

    _columns = {

        'group_id': fields.many2one('magento.res.partner.category',
                                    string='Magento Group (Category)'),
        'pricelist': fields.many2one('product.pricelist', 'Asociated Pricelist',
                                     help="Link this Category with a Pricelist", required=True),

    }


class BaseAddressImportMapper(ImportMapper):

    _inherit = 'magento.address'

    @only_create
    @mapping
    def group_son_id(self, record):
        parent = self.options.parent_partner
        if parent:
            if parent.group_id:
                return {'group_id': parent.group_id.id}
        else:
            return {'group_id': False}
        # Don't return anything, we are merging into an existing partner
        return super(BaseAddressImportMapper, self).group_son_id(ImportMapper)


