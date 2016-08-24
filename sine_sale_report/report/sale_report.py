# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _inherit = 'sale.report'
    _columns = {
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('invoiced', 'Invoiced'),
        ], 'Order Status', readonly=True),

    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: