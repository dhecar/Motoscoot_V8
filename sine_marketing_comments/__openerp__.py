# -*- coding: utf-8 -*-
{
    'name': "Add a comment into each sale order",
    'version': "7.0",
    'author': "David Hernández",
    'category': "Generic Modules/Others",
    'website': "http://sinergiainformatica.net",
    'description': """Provides the possibility to fill a commercial
                    comment into each sale order""",
    'depends': ["sale"],
    'data': ['security/security.xml','security/ir.model.access.csv',"sine_sale_view.xml"],
    'active': True,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: