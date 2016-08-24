# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
# Copyright 2012 Camptocamp SA

# Adaptation to NACEX Camaleon by David Hernández
# http://sinergiainformatica.net
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

from osv import osv, fields
import openerp.addons.decimal_precision as dp


class carrier_file(osv.osv):
    _inherit = 'delivery.carrier.file'


    def _get_reembolso(self, cursor, user_id, context=None):
        return (
            ('N', 'NO'),
            ('O', 'Origen'),
            ('D', 'Destino'),
            ('A', 'Adelanto'))

    def _get_typo(self, cursor, user_id, context=None):
        return (
            ('2', 'Nacex 10H'),
            ('8', 'Nacex 19H'),
            ('27', 'E Nacex'))

    def _get_alerta(self, cursor, user_id, context=None):
        return (
            ('E', 'Email'),
            ('S', 'SMS'))

    def _get_tipo_paq(self, cursor, user_id, context):
        return (
            ('1', 'Bolsa'),
            ('2', 'Paquete'))


    def get_type_selection(self, cr, uid, context=None):
        result = super(carrier_file, self).get_type_selection(cr, uid, context=context)
        if 'Nacex' not in result:
            result.append(('Nacex', 'Envíos Nacex'))
        return result

    _columns = {
        'type': fields.selection(get_type_selection, 'Type'),
        'nacex_account': fields.char('Nacex Account', size=9),
        'nacex_typo': fields.selection(_get_typo, 'Tipo de servicio'),
        'nacex_reembolso': fields.selection(_get_reembolso, 'Tipo de Reembolso'),
        'nacex_paquete': fields.selection(_get_tipo_paq, 'Tipo Paquete'),
        'nacex_cod_price': fields.float('Precio contrareembolso',
                                        digits_compute=dp.get_precision('Precio de reembolso'),
                                        help="Este precio es indicativo, para poder añadir un valor a la linea de venta"
                                             "debes hacerlo a mano o utilizar el módulo sine_delivery_extension"
                                             "para añadir esta linea. (ten en cuenta que el precio debe ir sin IVA"),
        'nacex_ealerta': fields.selection(_get_alerta, 'Tipo de Alerta',
                                          help="Tipo de E-Alerta [Email o SMS que se envía al "
                                               "remitente para indicar que se ha entregado el envió]"),
        'nacex_prealerta': fields.selection(_get_alerta, 'Tipo Prealerta',
                                            help=" Tipo de Prealerta [Email o SMS que se envía al"
                                                 " destinatario para avisar previamente de la entrega]"),
        'nacex_cash': fields.boolean('Contrareembolso?', help="Marcar para contrareembolso"),

    }

    _defaults = {
        'nacex_paquete': lambda *a: 2,
        }
carrier_file()
