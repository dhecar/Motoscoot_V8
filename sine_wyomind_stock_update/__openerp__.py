# -*- coding: utf-8 -*-
{
    "name": "Advanced Inventory Wyomind API update",
    "version": "7.0",
    "author": "David Hernández (Sinergiainformatica)",
    "category": "Generic Modules/Others",
    "website": "http://sinergiainformatica.net",
    "description": "This module update the product stock throught API to Magento websites that have"
                   " Advanced Inventory module from Wyomind.",
    "depends": ['stock', 'sale_to_invoice'],
    "update_xml": ["wyomind_update_view.xml"],
    "data": ['security/security.xml', 'security/ir.model.access.csv'],
    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
