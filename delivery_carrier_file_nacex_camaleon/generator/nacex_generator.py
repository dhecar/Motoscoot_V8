# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
#
# Adaptation to Nacex Chamaleon
# Author: David Hernandez
#    http://sinergiainformatica.net
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
import csv

from openerp.addons.base_delivery_carrier_files.generator import CarrierFileGenerator
from openerp.addons.base_delivery_carrier_files.generator import BaseLine
from openerp.addons.base_delivery_carrier_files.csv_writer import UnicodeWriter


class NacexLine(BaseLine):
    fields = (('empty', 1),
              ('nacex_account', 5),
              ('reference', 20),
              ('nacex_typo', 2),
              ('tipo_paq', 1),
              ('weight', 6),
              ('num_paq', 2),
              ('name', 35),
              ('name', 35),
              ('street', 45),
              ('country', 2),
              ('zip', 15),
              ('city', 30),
              ('phone', 16),
              ('tipo_reembolso', 1),
              ('total', 5),
              ('observaciones', 150),
              ('ealerta', 1),
              ('mail', 50),
              ('prealerta', 1),
              ('mail', 50))

class NacexFileGenerator(CarrierFileGenerator):
    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'Nacex'

    def _get_filename_single(self, picking, configuration, extension='csv'):
        return super(NacexFileGenerator, self)._get_filename_single(picking, configuration, extension='csv')

    def _get_filename_grouped(self, configuration, extension='csv'):
        return super(NacexFileGenerator, self)._get_filename_grouped(configuration, extension='csv')

    def _get_rows(self, picking, configuration):
        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate a row in the file
        :param browse_record configuration: configuration of the file to generate
        :return: list of rows
        """
        line = NacexLine()
        line.empty = ""
        line.nacex_account = configuration.nacex_account
        line.reference = picking.name
        line.nacex_typo = configuration.nacex_typo
        line.tipo_paq = configuration.nacex_paquete
        line.weight = "%.2f" % (picking.weight,)
        line.num_paq = picking.number_of_packages
        address = picking.partner_id
        if address:
            line.name = address.name or (address.partner_id and address.partner_id.name)
            line.name = address.name or (address.partner_id and address.partner_id.name)
            if address.street2:
                line.street = address.street + "  " + address.street2
            else:
                line.street = address.street

            line.country = address.country_id.code
            line.zip = address.zip
            line.city = address.city
            line.phone = address.phone or address.mobile

            # Reembolso ?
            if configuration.nacex_cash:
                line.tipo_reembolso = configuration.nacex_reembolso
                line.total = picking.sale_id.amount_total
            else:
                line.tipo_reembolso = 'N'
                line.total = '0'

            line.observaciones = 'Observaciones'
            line.ealerta = configuration.nacex_ealerta
            if address.email:
                line.mail = address.email
            else:
                if address.parent_id and address.parent_id.email:
                    line.mail = address.parent_id.email
                else:
                    line.mail = ''
            line.prealerta = configuration.nacex_prealerta
            if address.email:
                line.mail = address.email
            else:
                if address.parent_id and address.parent_id.email:
                    line.mail = address.parent_id.email
                else:
                    line.mail = ''

        return [line.get_fields()]

    def _write_rows(self, file_handle, rows, configuration):
        """
        Write the rows in the file (file_handle)

        :param StringIO file_handle: file to write in
        :param rows: rows to write in the file
        :param browse_record configuration: configuration of the file to
               generate
        :return: the file_handle as StringIO with the rows written in it
        """

        writer = UnicodeWriter(file_handle, delimiter=';', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_NONE)
        writer.writerows(rows)
        return file_handle
