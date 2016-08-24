# -*- coding: utf-8 -*-

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,)
from openerp.addons.magentoerpconnect.product import ProductImportMapper
from openerp.addons.connector.exception import MappingError
from .backend import magento_myversion
from openerp.addons.magentoerpconnect import product
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.magentoerpconnect.backend import magento

@magento_myversion
class MyProductImportMapper(ProductImportMapper):
    _inherit = 'product.product'

    direct = ProductImportMapper.direct + [('msrp', 'pvp_fabricante')]


@magento(replacing=product.IsActiveProductImportMapper)
class ProductImportMapper(product.IsActiveProductImportMapper):
    _model_name = 'magento.product.product'

    @mapping
    def is_active(self, record):
        """Check if the product is active in Magento
        and set Internet/Active flag in OpenERP
        status == 1 in Magento means active"""
        is_active = (record.get('status') == '1')
        if is_active is True:

            return {
                'internet': (record.get('status') == '1'),
                'active': (record.get('status') == '1')}
        else:

            return {
                'internet': (record.get('status') == '2'),
                'active': (record.get('status') == '1')}


