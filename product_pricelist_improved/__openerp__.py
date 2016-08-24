# -*- encoding: utf-8 -*-
##############################################################################
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2015 OBERTIX FREE SOLUTIONS (<http://obertix.net>).
#                       cubells <vicent@vcubells.net>
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

{
    "name": "Product Pricelist Improved",
    "version": "1.0",
    "depends": [
        'product',
    ],
    "author": "cubells",
    "contributors": [
    ],
    "category": "Others",
    "website": "http://www.vcubells.net",
    "summary": """
        Several improvements in product pricelist
    """,
    'description': """
        
    """,
    "data": [
        'wizard/calculate_pricelist_view.xml',
        'views/product_view.xml',
    ],
    "installable": True,
    "auto_install": False,
}
