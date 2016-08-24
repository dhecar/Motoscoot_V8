# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Add auto validate and print Invoice
#    David Hernández.
#    (C) Sinergiainformatica.net (2016)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
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

{

    "name": "Auto  Invoice",
    "description": "Validate and print invoice once the delivery is done",
    "author": "David Hernández",
    "website": "http://sinergiainformatica.net",
    "category": "Invoice",
    "update_xml": ["sine_stock_invoice_onshipping.xml"],
    "css": [],
    "js": [],
    "depends": ['stock', 'account', 'account_voucher'],
    "installable": True,
    "auto_install": False,
}