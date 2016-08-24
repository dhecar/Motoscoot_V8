# -*- coding: utf-8 -*-
{
    "name": "Tarifas de precio asociadas a la marca del producto",
    "version": "7.0",
    "author": "David Hernández",
    "category": "Generic Modules/Others",
    "website": "http://sinergiainformatica.net",
    "description": """ * Extiende el creador de tarifas para soportar la aplicacion de la misma
                      a la marca del producto. Requiere de product_brand.
                      * Añade relación entre usuario y tarifa""",
    "depends": ["product", "product_brand", "base"],
    "update_xml": ["pricelist_view.xml"],
    "active": True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
