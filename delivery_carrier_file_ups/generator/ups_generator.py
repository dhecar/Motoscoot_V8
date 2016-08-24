# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Guewen Baconnier
# Copyright 2012 Camptocamp SA
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
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement, tostring
from xml.dom import minidom
import xml.etree.cElementTree as ET

class UPSLine(BaseLine):
    fields = (('name', 30),
              ('name', 30),
              ('street', 35),
              ('stree2', 35),
              ('city', 120),
              ('country', 2),
              ('zip', 9),
              ('phone', 16),
              ('mail', 50),
              ('mail', 50),
              ('ups_account', 9),
              ('service', 2),
              ('package_type', 2),
              ('numpack', 2),
              ('weight', 3),
              ('goods', 15),
              ('reference1', 20),
              ('reference2', 20),
              ('cash', 1),
              ('ups_cod_price', 3),
              ('amount', 4),
              ('currency', 1),
              ('total'))

class UpsFileGenerator(CarrierFileGenerator):
    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'Ups'

    def _get_filename_single(self, picking, configuration, extension='csv'):
        return super(UpsFileGenerator, self)._get_filename_single(picking, configuration, extension='csv')

    def _get_filename_grouped(self, configuration, extension='csv'):
        return super(UpsFileGenerator, self)._get_filename_grouped(configuration, extension='csv')

    def _get_rows(self, picking, configuration):

        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate a row in the file
        :param browse_record configuration: configuration of the file to generate
        :return: list of rows
        """
        line = UPSLine()
        line.reference = picking.name
        address = picking.partner_id
        if address:
            line.name = address.name or (address.partner_id and address.partner_id.name)
            if address.street2:
                line.street = address.street
                line.street2 = address.street2

            else:
                line.street = address.street
            line.zip = address.zip
            line.city = (address.city + " (" + address.state_id.name + ")")
            line.country = address.country_id.code
            line.phone = address.phone or address.mobile
            if address.email:
                line.mail = address.email
            else:
                if address.parent_id and address.parent_id.email:
                    line.mail = address.parent_id.email
                else:
                    line.mail = ''
        line.ups_account = configuration.ups_account
        line.service = configuration.ups_service_level
        line.package_type = configuration.ups_package_type
        if picking.number_of_packages:
            line.numpack = picking.number_of_packages
        else:
            line.numpack = '1'
        line.goods = configuration.ups_description_goods
        line.reference1 = picking.name
        line.reference2 = picking.origin
        line.weight = str("%.2f" % (picking.weight)).replace('.', ',')
        line.cash = configuration.ups_cash
        line.ups_cod_price = configuration.ups_cod_price
        line.total = str(picking.sale_id.amount_total).replace('.', ',')
        line.currency = picking.company_id.currency_id.name
        line.savepath = configuration.export_path
        line.emailnotif = configuration.ups_mail_notification

        if configuration.xml_export:

            filename = line.reference1.replace('/', '_') + '.xml'

            OpenShipments = Element('OpenShipments', xmlns='x-schema:OpenShipments.xdr')
            OpenShipment = SubElement(OpenShipments, 'OpenShipment', ProcessStatus='')
            Receiver = SubElement(OpenShipment, 'Receiver')
            CompanyName = SubElement(Receiver, 'CompanyName')
            CompanyName.text = line.name
            ContactPerson = SubElement(Receiver, 'ContactPerson')
            ContactPerson.text = line.name
            AddressLine1 = SubElement(Receiver, 'AddressLine1')
            AddressLine1.text = line.street

            if address.street2:
                AddressLine2 = SubElement(Receiver, 'AddressLine2')
                AddressLine2.text = line.street2

            City = SubElement(Receiver, 'City')
            City.text = line.city
            CountryCode = SubElement(Receiver, 'CountryCode')
            CountryCode.text = line.country
            PostalCode = SubElement(Receiver, 'PostalCode')
            PostalCode.text = line.zip
            Phone = SubElement(Receiver, 'Phone')
            Phone.text = line.phone
            EmailAddress1 = SubElement(Receiver, 'EmailAddress1')
            EmailAddress1.text = line.mail
            EmailContact = SubElement(Receiver, 'EmailContact1')
            EmailContact.text = line.mail
            # <Openshipments><Openshipment/><Shipper />
            Shipper = SubElement(OpenShipment, 'Shipper')
            #
            UpsAccountNumber = SubElement(Shipper, 'UpsAccountNumber')
            UpsAccountNumber.text = line.ups_account
            # Openshipments><Openshipment/><Shipment />
            Shipment = SubElement(OpenShipment, 'Shipment')
            #
            ServiceLevel = SubElement(Shipment, 'ServiceLevel')
            ServiceLevel.text = line.service
            PackageType = SubElement(Shipment, 'PackageType')
            PackageType.text = line.package_type
            NumberOfPackages = SubElement(Shipment, 'NumberOfPackages')
            NumberOfPackages.text = str(line.numpack)
            ShipmentActualWeight = SubElement(Shipment, 'ShipmentActualWeight')
            ShipmentActualWeight.text = line.weight
            DescriptionOfGoods = SubElement(Shipment, 'DescriptionOfGoods')
            DescriptionOfGoods.text = line.goods
            Reference1 = SubElement(Shipment, 'Reference1')
            Reference1.text = line.reference1
            Reference2 = SubElement(Shipment, 'Reference2')
            Reference2.text = line.reference2

            # CONTRAREEMBOLSOS #
            if line.cash:

                BillingOption = SubElement(Shipment, 'BillingOption')
                BillingOption.text = 'PP'
                COD = SubElement(Shipment, 'COD')
                CashOnly = SubElement(COD, 'CashOnly')
                CashOnly.text = '1'
                Amount = SubElement(COD, 'Amount')
                Amount.text = str(picking.sale_id.amount_total).replace('.', ',')
                Currency = SubElement(COD, 'Currency')
                Currency.text = line.currency
            else:
                BillingOption = SubElement(Shipment, 'BillingOption')
                BillingOption.text = 'PP'
            #
            QuantumViewNotifyDetails = SubElement(Shipment, 'QuantumViewNotifyDetails')
            QuantumViewNotify = SubElement(QuantumViewNotifyDetails, 'QuantumViewNotify')
            NotificationEMailAddress = SubElement(QuantumViewNotify, 'NotificationEMailAddress')
            NotificationEMailAddress.text = line.mail
            NotificationRequest = SubElement(QuantumViewNotify, 'NotificationRequest')
            NotificationRequest.text = '1'
            QuantumViewNotify = SubElement(QuantumViewNotifyDetails, 'QuantumViewNotify')
            NotificationEMailAddress = SubElement(QuantumViewNotify, 'NotificationEMailAddress')
            NotificationEMailAddress.text = line.emailnotif
            NotificationEMailAddress = SubElement(QuantumViewNotify, 'NotificationEMailAddress')
            NotificationEMailAddress.text = line.mail
            NotificationRequest = SubElement(QuantumViewNotify, 'NotificationRequest')
            NotificationRequest.text = '2'

            def indent(elem, level=0):
                i = "\n" + level*"  "
                if len(elem):
                    if not elem.text or not elem.text.strip():
                        elem.text = i + "  "
                    if not elem.tail or not elem.tail.strip():
                        elem.tail = i
                    for elem in elem:
                        indent(elem, level+1)
                    if not elem.tail or not elem.tail.strip():
                        elem.tail = i
                else:
                    if level and (not elem.tail or not elem.tail.strip()):
                        elem.tail = i

            indent(OpenShipments)
            output_file = (open(line.savepath + filename, 'w'))
            output_file.write(ElementTree.tostring(OpenShipments, encoding='UTF-8'))
            output_file.close()

        else:
            return [line.get_fields()]

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






