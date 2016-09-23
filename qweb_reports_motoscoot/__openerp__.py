# -*- coding: utf-8 -*-
#
#   Motoscoot Sale/Invoice/picking reports
#

{
    'name': 'Motoscoot Reports templates',
    'version': '1.0',
    'category': 'Custom',
    'sequence': 14,
    'summary': 'Custom Reports',
    'description': """
        Custom Sale, Invoice, picking, reports for Motoscoot.net
    """,
    'author': 'SinergiaInformatica',
    'website': 'http://sinergiainformatica.net',
    'depends': ['report','sale','account','stock'],
    'data': ['views/sale_order_report.xml',
             'views/invoice_report.xml',
             'views/picking_report.xml',
             'views/layouts.xml',
             'reports.xml'
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: