# -*- coding: utf-8 -*-
from openerp.osv import orm, fields


class magento_backend(orm.Model):
    _inherit = 'magento.backend'
    _columns = {
        'remote_warehouse': fields.char('Remote warehouse', size=1)
    }

    def select_versions(self, cr, uid, context=None):
        """ Available versions in the backend.

        Can be inherited to add custom versions.
        """
        versions = super(magento_backend, self).select_versions(cr, uid, context=context)
        versions.append(('1.9.0.1', '1.9.0.1'))
        return versions