from openerp.osv import fields, osv
import xmlrpclib
from openerp import tools, SUPERUSER_ID

class InvoiceSaleOrder(osv.TransientModel):
    _inherit = 'sale.order.invoiced'

    def do_invoice(self, cr, uid, ids, context=None):
        res = super(InvoiceSaleOrder, self).do_invoice(cr, uid, ids, context=context)
        if context is None:
            context = {}
        sale_obj = self.pool['sale.order']
        sale_id = context.get('active_id', [])
        db_obj = self.pool['base.external.dbsource']
        db_id = db_obj.search(cr, uid, [
            ('name', '=', 'Sale_To_Invoice')
        ], context=context)

        # Wyomind Config
        conf_obj = self.pool.get('wyomind.config')
        conf_ids = conf_obj.search(cr, uid, [('id', '=', 1)])
        for x in conf_obj.browse(cr, uid, conf_ids):
            url = x.url
            user = x.apiuser
            passw = x.apipass

            # Connection
        proxy = xmlrpclib.ServerProxy(url, allow_none=True)
        session = proxy.login(user, passw)

        location = 12
        if db_id:
            if sale_id:
                for sale in sale_obj.browse(cr, uid, [sale_id],
                                            context=context):
                    for line in sale.order_line:
                        if line.product_id.magento_bind_ids:
                            cr.execute("""SELECT qty FROM stock_report_prodlots WHERE
                                   location_id =%s AND product_id = %s""" %
                                       (location, line.product_id.id))

                            qty = cr.fetchone()[0]
                            # CASE GRN
                            ads = db_obj.get_stock(cr, SUPERUSER_ID, ids, line.product_id.id,
                                                   location, context=context)

                            q = qty - ads
                            cr.execute('SELECT magento_id'
                                       ' FROM magento_product_product'
                                       ' WHERE openerp_id =%s' % line.product_id.id)
                            mag_id = cr.fetchone()[0]

                            # Out movements are computed.
                            data_basic = {'quantity_in_stock': q,
                                          'manage_stock': 1,
                                          'backorder_allowed': 0,
                                          'use_config_setting_for_backorders': 0}

                            proxy.call(session, 'advancedinventory.setData',
                                       (mag_id, 2, data_basic))
        return res

InvoiceSaleOrder()