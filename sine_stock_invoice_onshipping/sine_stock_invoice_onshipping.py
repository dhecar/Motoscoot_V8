# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
# Add auto validate and print Invoice
# David Hernández.
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

from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _


class stock_invoice_onshipping(osv.osv_memory):
    _inherit = 'stock.invoice.onshipping'

    def create_invoice(self, cr, uid, ids, context=None):
        res = super(stock_invoice_onshipping, self).create_invoice(cr, uid, ids, context=context)
        invoice_ids = []
        invoice_ids += res.values()
        if invoice_ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', invoice_ids[0], 'invoice_open', cr)
        return res

    def validate_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = []
        res = self.create_invoice(cr, uid, ids, context=context)
        invoice_ids += res.values()
        if not invoice_ids:
            raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
        if invoice_ids:
            data = self.pool.get('account.invoice').read(cr, uid, [invoice_ids[0]], [], context=None)
            datas = {
                'ids': invoice_ids,
                'model': 'account.invoice',
                'form': data
            }
            wf_service = netsvc.LocalService("workflow")

            # Pay Invoice

            wf_service.trg_validate(uid, 'account.voucher', invoice_ids[0], 'proforma_voucher', cr)

            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'motoscoot.account.invoice',
                'datas': datas,
                'report_type': 'webkit',
                'nodestroy': True,
                'context': context
            }

