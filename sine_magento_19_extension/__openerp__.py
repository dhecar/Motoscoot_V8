# -*- coding: utf-8 -*-
{'name': 'Magento Connector version 1.9',
 'version': '1.0.0',
 'category': 'Connector',
 'depends': ['magentoerpconnect', 'product_brand'],
 'author': 'Sinergiainformatica.net. David Hernández',
 'license': 'AGPL-3',
 'description': """
  -- Magento Connector Customization:

  * Added direct mapping for msrp
  * Added @mapping for manufacturer in product view. Requires product_brand module.""",
 'data': [],
 'update_xml': ['product_brand_view.xml', 'partner_view.xml'],
 'installable': True,
 'application': True,
}
