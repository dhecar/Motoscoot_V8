# -*- coding: utf-8 -*-
{
    "name" : "Adaptaciones para Motoscoot.net",
    "version" : "7.0",
    "author" : "SinergiaInformatica. David Hernández",
    "category" : "Custom",
    "website" : "http://sinergiainformatica.net",
    "description": "Varias adaptaciones para Motoscoot.net",

    "depends" : ["base_delivery_carrier_files",
                 "product",
                 "stock",
                 "purchase",
                 "delivery"],

    "data" : ["views/sale_view.xml",
              "views/purchase_view.xml",
              "views/product_motoscoot_view.xml",
              "views/stock_moves_view.xml",
              "views/partner_motoscoot_view.xml",
              "security/security.xml",
              "security/ir.model.access.csv",
              "views/restrict/product_restrict_view.xml",
              "views//restrict/res_partner_restrict_view.xml",
              "views//restrict/sale_order_restrict_view.xml"],
    "active": True,
    "installable": True
}    ##
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
