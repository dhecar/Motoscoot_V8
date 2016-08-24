# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2011-2013 Camptocamp SA (http://www.camptocamp.com)
# @author Nicolas Bessi
#   Copyright (c) 2013 Agile Business Group (http://www.agilebg.com)
#   @author Lorenzo Battistini
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from osv import fields, osv
from report import report_sxw
import time
import base64
from barcode.writer import ImageWriter
from barcode import generate
from StringIO import StringIO
from barcode.writer import mm2px

class SetPrinted(osv.osv):
    _name = 'set.printed'

    def get_set(self, cr, uid, ids, context=None):

        pick_obj = self.pool.get('stock.picking.out')
        record_ids = context and context.get('active_ids', []) or []
        for pick in pick_obj.browse(cr, uid, record_ids, context=context):
            if pick.is_printed is False:
                pick_obj.write(cr, uid, pick.id, {'is_printed': True})


        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'webkit.motoscoot_picking',
            'datas': {
                'model': 'stock.picking.out',
                'ids': record_ids,
            }
        }


class BarcodeImageWriter(ImageWriter):
    def calculate_size(self, modules_per_line, number_of_lines, dpi=100):
        width = 2 * self.quiet_zone + modules_per_line * self.module_width
        height = 6

        self.size = int(mm2px(width, dpi)), int(mm2px(height, dpi))
        return self.size


class DeliverySlip(report_sxw.rml_parse):


    def generate_barcode(self, barcode_string):

        fp = StringIO()
        generate('code128', barcode_string, writer=BarcodeImageWriter(), output=fp)
        contents = fp.getvalue()
        return base64.standard_b64encode(contents)

    def _get_invoice_address(self, picking):
        if picking.sale_id:
            return picking.sale_id.partner_invoice_id
        partner_obj = self.pool.get('res.partner')
        invoice_address_id = picking.partner_id.address_get(
            adr_pref=['invoice']
        )['invoice']
        return partner_obj.browse(
            self.cr, self.uid, invoice_address_id)

    def _get_shipping_address(self, picking):
        if picking.sale_id:
            return picking.sale_id.partner_shipping_id
        partner_obj = self.pool.get('res.partner')
        shipping_address_id = picking.partner_id.address_get(
            adr_pref=['shipping']
        )['shipping']
        return partner_obj.browse(
            self.cr, self.uid, shipping_address_id)

    def _sum_total_products(self, picking):
        if picking.move_lines:
            total = int(sum(picking.move_lines.product_qty))
            return total

    def __init__(self, cr, uid, name, context):
        super(DeliverySlip, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'invoice_address': self._get_invoice_address,
            'shipping_address': self._get_shipping_address,
            'total_prod': self._sum_total_products,
            'generate_barcode': self.generate_barcode
        })


report_sxw.report_sxw('report.webkit.motoscoot_picking',
                      'stock.picking.out',
                      'addons/sine_ms_packing_webkit/report/delivery_slip.mako',
                      parser=DeliverySlip)
