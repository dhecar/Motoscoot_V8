# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Obertix.com and IPGest.net.  All Rights Reserved.
#                   cubells <info@obertix.net>
#    $Id$
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

import csv
import base64
import StringIO
from osv import fields, osv
import math

import logging
_logger = logging.getLogger(__name__)


def EanChecksum(eancode):
    """
        returns the checksum of an ean string of length 13,
        returns -1 if the string has the wrong length
    """
    if len(eancode) <> 13:
        return -1
    oddsum = 0
    evensum = 0
    total = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]
    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum
    check = int(10 - math.ceil(total % 10.0)) %10
    return check


def CheckEan(eancode):
    """
        returns True if eancode is a valid ean13 string, or null
    """
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return EanChecksum(eancode) == int(eancode[-1])


class TarifasImporter(osv.osv_memory):
    _name = "tarifas.importer"
    _description = "Tarifas Importer"

    _columns = {
        'input_file': fields.binary('File', filters="*.csv", required=True),
        'input_file_name': fields.char('File name', size=256),
        'ean13': fields.boolean(
            'Importar el código de barras',
            help="""Si se marca, se importará el código de barras también.
            Si no, solamente referencia, descripción y precio."""),
        'cost_price': fields.boolean(
            'Realizar la importación del precio de coste',
            help="De manera predeterminada se importa el precio de venta del "
                 "producto. Si se marca esta opción, se importará  también el precio "
                 "de coste."
        ),

        'supplier_price': fields.boolean(
            'Realizar la importación del precio proveedor (pvp)',
            help="De manera predeterminada se importa el precio de venta del "
                 "producto. Si se marca esta opción, se importará  también el precio "
                 "de proveedor."
        ),

        'create': fields.boolean(
            'Crea productos si referencia no existe',
            help='Si se marca esta opción y se confirma, se crearán los '
                 'productos si la referencia de la tarifa no existe en la base'
                 ' de datos.'
        ),
        'confirm_create': fields.boolean(
            'Confirmar creación de productos',
            help='Necesario confirmar para poder crear los productos nuevos.'
        ),
        'write_name': fields.boolean(
            'Sobreescribir nombre del producto',
            help='Si se marca, se sobreescribirá el nombre del producto con el'
                 ' que tiene la tarifa'
        )
    }
    
    _defaults = {
        'ean13': False,
        'cost_price': True,
        'supplier_price': True,
    }

    def action_import(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        imported_product_ids = []
        
        for wiz in self.browse(cr, uid, ids, context):
            if not wiz.input_file:
                raise osv.except_osv("Error",
                                     "Has de seleccionar un fichero...")

            data = base64.b64decode(wiz.input_file)

            reader = csv.reader(StringIO.StringIO(data),
                                delimiter=';',
                                quotechar='"')
            
            product_obj = self.pool['product.product']
            product_template = self.pool['product.template']
            for record in reader:
                ean13 = False
                try:
                    if wiz.ean13:
                        default_code, name_template, list_price, cost_price, supplier_price, ean13 = record

                    else:
                        default_code, name_template, list_price, cost_price, supplier_price = record
                except:
                    raise osv.except_osv(
                        "Error", "El formato del fichero es incorrecto.")
                if default_code and name_template and list_price and cost_price and supplier_price:
                    default_code = default_code.strip()
                    name_template = name_template.strip()
                    try:
                        list_price = float(list_price.replace(',', '.').replace('€', ''))

                        cost_price = float(cost_price.replace(',', '.').replace('€', ''))

                        supplier_price = float(supplier_price.replace(',', '.').replace('€', ''))
                    except:
                        raise osv.except_osv(
                            "Error!",
                            'Formato de fichero incorrecto.\n'
                            'El precio no es la columna correcta.'
                        )
                           
                    ids = product_obj.search(cr, uid, [
                        ('default_code', '=', default_code)
                    ], context=context)
                    
                    valors = {
                        'default_code': default_code,
                        'company_id': 1,
                    }
                    valors_template = {
                        'purchase_ok': True,
                        'sale_ok': True,
                        'type': 'product',
                        'company_id': 1,
                    }
                    valors.update({'name_template': name_template})
                    valors_template.update({'name': name_template})
                    # si coste y pvp, actualizamos los tres campos
                    if wiz.cost_price and wiz.supplier_price:

                        valors.update(
                            {
                                'list_price': float(list_price),
                                'standard_price': float(cost_price),
                                'pvp_fabricante': float(supplier_price)
                            })

                        valors_template.update(
                            {
                                'list_price': float(list_price),
                                'standard_price': float(cost_price),
                                'pvp_fabricante': float(supplier_price)
                            })

                    #  si marco coste solamente, actualizamos coste y precio de venta

                    elif wiz.cost_price and not wiz.supplier_price:
                        valors.update(
                            {
                                'list_price': float(list_price),
                                'standard_price': float(cost_price)

                            })
                        valors_template.update(
                            {
                                'list_price': float(list_price),
                                'standard_price': float(cost_price)
                            })

                    # Si marco supplier solamente, actualizo precio venta + pvp

                    elif wiz.supplier_price and not wiz.cost_price:
                        valors.update(
                            {
                                'list_price': float(list_price),
                                'pvp_fabricante': float(supplier_price)
                            })
                        valors_template.update(
                            {
                                'list_price': float(list_price),
                                'pvp_fabricante': float(supplier_price)
                            })

                    # Si no marco nada, actualizo solo el precio de venta
                    else:
                        valors.update(
                            {
                                'list_price': float(list_price)
                            })
                        valors_template.update(
                            {
                                'list_price': float(list_price)
                            })
                    context.update({'tarifa_update': True})
                    # Hay producto con ese código
                    if ids:
                        if not wiz.write_name:
                            name_template = product_obj.read(cr, uid, ids, [
                                'name_template'
                            ], context=context)[0]['name_template']
                            valors['name_template'] = name_template
                            valors_template['name'] = name_template
                        if ean13:
                            ean13 = CheckEan(ean13)
                            valors.update({'ean13': ean13})
                        product_obj.write(cr, uid, ids, valors,
                                          context=context)
                        imported_product_ids.append(ids[0])                        
                        ids = product_obj.read(cr, uid, ids, [
                            'product_tmpl_id'
                        ], context=context)[0]['product_tmpl_id'][0]
                        product_template.write(cr, uid, [ids], valors_template,
                                               context=context)
                    # No hay producto con ese código
                    else:
                        if wiz.create and wiz.confirm_create:
                            if ean13:
                                ean13 = CheckEan(ean13)
                                valors.update({'ean13': ean13})
                            product_id = product_template.create(
                                cr, uid, valors_template)
                            valors['product_tmpl_id'] = product_id
                            product_id = product_obj.create(cr, uid, valors)
                            imported_product_ids.append(product_id)
                    
        return {
            'name': "Productos Importados o Modificados",
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': "[('id', 'in', %s)]" % imported_product_ids,
            'context': context,
        }

TarifasImporter()


