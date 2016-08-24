from osv import fields, osv
import one2many_sorted
from zebra import zebra
from time import sleep
import unicodedata
from openerp.tools.translate import _

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {

        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?', ),
        'payment1_id': fields.related('sale_id', 'payment_type', type='many2one', relation='payment.type',
                                      string='Tipo Pago Magento', readonly=True),
        'payment2_id': fields.related('sale_id', 'payment_method_id', type='many2one', relation='payment.method',
                                      string='Tipo Pago Erp', readonly=True),
        'sh_id': fields.related('sale_id', 'shop_id', type='many2one', relation='sale.shop',
                                string='Tienda', readonly=True),
        'pricelist_type': fields.related('sale_id', 'pricelist_id', type='many2one', relation='product.pricelist',
                                         string='Tarifa', readonly=True),

        'res_user': fields.related('sale_id', 'user_id', type='many2one', relation='res.users',
                                   string='Comercial', readonly=True),

        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         )

    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking_out, self).copy(cr, uid, id, default, context=context)


class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {

        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         ),

    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking_in, self).copy(cr, uid, id, default, context=context)


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {

        'is_printed': fields.boolean('Is printed?', help='Is the picking printed?'),
        'payment1_id': fields.related('sale_id', 'payment_type', type='many2one', relation='payment.type',
                                      string='Tipo Pago Magento', readonly=True),
        'payment2_id': fields.related('sale_id', 'payment_method_id', type='many2one', relation='payment.method',
                                      string='Tipo Pago Erp ', readonly=True),
        'sh_id': fields.related('sale_id', 'shop_id', type='many2one', relation='sale.shop',
                                string='Tienda', readonly=True),
        'pricelist_type': fields.related('sale_id', 'pricelist_id', type='many2one', relation='product.pricelist',
                                         string='Tarifa', readonly=True),

        'res_user': fields.related('sale_id', 'user_id', type='many2one', relation='res.users',
                                    string='Comercial', readonly=True),
        'move_lines_sorted': one2many_sorted.one2many_sorted
        ('stock.move'
         , 'picking_id'
         , 'Moves Sorted'
         , states={'draft': [('readonly', False)]}
         , order='product_id.product_brand_id.name, product_id.default_code'
         )
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'move_lines_sorted': []})
        return super(stock_picking, self).copy(cr, uid, id, default, context=context)


class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {

        'prod_stock': fields.related('product_id', 'test', type='char', string='Stocks')

    }


### Redefine the class to get fields from in moviments


class stock_partial_picking(osv.osv):
    _inherit = "stock.partial.picking"

    # Get default queue name
    def get_queue(self, cr, uid, field_names=None, arg=None, context=None):
        result = {}
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_default', '=', 1)])
        if pool_ids:
            for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                result = i.qz_printer.system_name
            return result

    # Prepare EPL data (escaped)

    def prepare_epl_data(self, cr, uid, ids, context=None):
        # Impresora
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_default', '=', 1)])
        # Pickings
        partial_pick_obj = self.pool.get('stock.partial.picking.line')
        line_ids = context.get('line_id', []) or []
        partial_ids = partial_pick_obj.search(cr, uid, [('wizard_id', '=', ids), ('id', '=', line_ids)])
        # For
        for line in partial_pick_obj.browse(cr, uid, partial_ids, context=context):

            # Limit size:

            if len(line.product_id.name_template) > 40:
                product_name = line.product_id.name_template[:40] + '..'
            else:
                product_name = line.product_id.name_template

            if pool_ids:
                for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                    for fields in i.qz_field_ids:

                        # Format: Bp1,p2,p3,p4,p5,p6,p7,p8,"DATA"\n

                        if fields.qz_field_type == 'barcode':

                            data = []
                            data += {'B' + str(fields.h_start_p1) + ',' +
                                     str(fields.v_start_p2) + ',' +
                                     str(fields.rotation_p3) + ',' +
                                     str(fields.bar_sel_p4) + ',' +
                                     str(fields.n_bar_w_p5) + ',' +
                                     str(fields.w_bar_w_p6) + ',' +
                                     str(fields.bar_height_p7) + ',' +
                                     str(fields.human_read_p8) + ',' + '"' +
                                     str(line.product_id.default_code) + '"' + '\n'}
                            # TODO get value to print from qz.config

                            # text field Format: Ap1,p2,p3,p4,p5,p6,p7,"DATA"\n

                        else:

                            data2 = []
                            data2 += {'A' + str(fields.h_start_p1) + ',' +
                                      str(fields.v_start_p2) + ',' +
                                      str(fields.rotation_p3) + ',' +
                                      str(fields.font_p4) + ',' +
                                      str(fields.h_multiplier_p5) + ',' +
                                      str(fields.v_multiplier_p6) + ',' +
                                      str(fields.n_r_p7) + ',' +
                                      unicodedata.normalize('NFKD', product_name).encode('ascii',
                                                                                         'ignore') + '"' + '\n'}

                            # TODO get value to print from qz.config
                """
                    Example of ELP commands to send
                    N
                    A40,80,0,4,1,1,N,"Tangerine Duck 4.4%"
                    A40,198,0,3,1,1,N,"Duty paid on 39.9l"
                    A40,240,0,3,1,1,N,"Gyle: 127     Best Before: 16/09/2011"
                    A40,320,0,4,1,1,N,"Pump & Truncheon"
                    P1
                 """

            result = '"""\n' + 'N\n' + ''.join(data) + ''.join(data2) + 'P1\n"""'

            return result

    def send_epl_data(self, cr, uid, ids, context=None):
        z = zebra()
        queue = self.get_queue(cr, uid, context=context)
        z.setqueue(queue)
        conf_obj = self.pool.get('qz.config')
        conf_id = conf_obj.search(cr, uid, [('qz_default', '=', 1)])
        if conf_id:
            for x in conf_obj.browse(cr, uid, conf_id):
                thermal = x.qz_direct_thermal
                h = x.qz_label_height
                gap = x.qz_label_gap
                height = [h, gap]
                width = x.qz_label_width
                z.setup(direct_thermal=thermal, label_height=height, label_width=width)
        epl = self.prepare_epl_data(cr, uid, ids, context=context)
        partial_pick_obj = self.pool.get('stock.partial.picking.line')
        line_ids = context.get('line_id', []) or []
        partial_ids = partial_pick_obj.search(cr, uid, [('wizard_id', '=', ids), ('id', '=', line_ids)])
        partial = partial_pick_obj.browse(cr, uid, partial_ids, context=context)
        for line in partial:
            num_cop = int(line.quantity)
            for n in range(0, num_cop):
                z.output(epl)
                ## sleep  between labels, if not, printer die ;)
                sleep(1.3)

            return True

    def do_partial_print(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=context)
        # record_ids = context and context.get('active_ids', []) or []
        partial = self.browse(cr, uid, ids[0], context=context)
        # Select Printable Labels  products
        for wizard_line in partial.move_ids:
            # Update the context with each line value in each cicle.
            context.update({'line_id': wizard_line.id})
            # Quantity must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))
            # Product to print label
            if wizard_line.product_id.label_print is True:

                self.send_epl_data(cr, uid, ids[0], context)

        return res
