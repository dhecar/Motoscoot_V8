# -*- coding: utf-8 -*-
##############################################################################
# Author: David Hernández
# Sinergiainformatica.net. 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
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
import logging
import xmlrpclib
from openerp.osv import orm, fields

from openerp.addons.magentoerpconnect.unit.backend_adapter import (GenericAdapter,
                                                           MAGENTO_DATETIME_FORMAT,)

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper, )
from .backend import magento_myversion
from openerp.addons.connector.exception import (MappingError,
                                                InvalidDataError,
                                                IDMissingInBackend
                                                )

_logger = logging.getLogger(__name__)


class magento_product_manufacturer(orm.Model):
    _name = 'magento.product.manufacturer'
    _inherit = 'magento.binding'
    _inherits = {'product.brand': 'openerp_id'}
    _description = 'Magento Product Manufacturer'

    _columns = {
        'openerp_id': fields.many2one('product.brand',
                                      string='Product Brand',
                                      required=True,
                                      ondelete='cascade'),
        'name': fields.text('Brand Name', translate=True),

        'magento_id': fields.many2one(
            'magento.product.manufacturer',
            string='Magento Brand',
            ondelete='cascade'),

    }

    _sql_constraints = [
        ('magento_uniq', 'unique(backend_id, magento_id)',
         'A Product Brand with the same ID on Magento already exists.'),
    ]


class product_brand(orm.Model):
    _inherit = 'product.brand'

    _columns = {
        'magento_bind_ids': fields.one2many(
            'magento.product.manufacturer',
            'openerp_id',
            string="Magento Bindings", ),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['magento_bind_ids'] = False
        return super(product_brand, self).copy_data(cr, uid, id,
                                                    default=default,
                                                    context=context)


@magento_myversion
class ProductBrandAdapter(GenericAdapter):
    _model_name = 'magento.product.manufacturer'
    _magento_model = 'catalog_product'
    _admin_path = '/{model}/edit/id/{id}'

    def _call(self, method, arguments):
        try:
            return super(ProductBrandAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Magento API
            # when the product does not exist
            if err.faultCode == 101:
                raise IDMissingInBackend
            else:
                raise

    def get_manufacturer(self, id, manufacturer, storeview_id=None):
        return self._call('ol_catalog_product_attribute.info',
                          [int(id), manufacturer, storeview_id, 'id'])

@magento_myversion
class ManufacturerProductImportMapper(ImportMapper):
    _model_name = 'magento.product.manufacturer'

    @mapping
    def manufacturer(self, record):
        {'name': record.get('manufacturer')}



@magento_myversion
class ProductImportMapper(ImportMapper):
    _model_name = 'magento.product.product'

    @mapping
    def prod_manufacturer(self, record):
        """Manufacturer linked to the product"""
        mapper = self.get_connector_unit_for_model(ManufacturerProductImportMapper)
        return mapper.map_record(record).values()






