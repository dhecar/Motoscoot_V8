# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Obertix.com and IPGest.net.  All Rights Reserved.
#                   cubells <info@obertix.net>
#    $Id$
#
#   Adaptado para Motoscoot por Sinergiainformatica.
#   Añadida la importación del pvp fabricante
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    "name": "Importador de tarifas personalizadas",
    "version": "1.0",
    "author": "cubells de obertix.com",
    "website": "http://obertix.com",
    "category": "Generic Modules / Others",
    "description": """
        Realiza la importación de tarifas
        Se ha añadido la importación del pvp.
    """,
    "depends": [
        'sale',
    ],
    "license": "AGPL-3",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [
        'security/ir.model.access.csv',
        'wizard/tarifas_view.xml',
    ],
    "active": False,
    "installable": True,
}

