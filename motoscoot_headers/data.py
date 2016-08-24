# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tools.translate import _


class partner_category(osv.osv):
    def get_partner_category(self, cr, uid, ids, context=None):
        parent_cat = self.browse(ids).parent_id.vat
        partner_cat = self.browse(ids).partner_id.vat
        if parent_cat:
            return parent_cat
        elif partner_cat:
            return partner_cat

        else:
            raise osv.except_osv(_('Error!!!'), _('Falta la categoria en el cliente'))
