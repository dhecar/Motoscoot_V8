from openerp.osv import fields, osv
from zebra import zebra
from time import sleep
import unicodedata


class stock_partial_picking(osv.osv):
    _inherit = "stock.picking"

    # Get default label printer for current user
    def get_default_label_printer(self, cr, uid, field_names=None, arg=None, context=None):
        result = {}
        pool_obj = self.pool.get('res.users')
        pool_ids = pool_obj.search(cr, uid, [('id', '=', uid)])
        if pool_ids:
            for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                result = i.epl_printer_id.system_name
            return result
        else:

            msg = "The current user don't have any printer configured. Please contact the master of pupets"
            raise osv.except_osv(_('Warning !'), _(msg))

    def prepare_epl_data(self, cr, uid, ids, context=None):
        # Get default printer for current user
        printer = self.get_default_label_printer(cr, uid, ids, context=context)
        # Default configuration for selected printer
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_printer.system_name', '=', printer)])
        # Pickings
        partial_pick_obj = self.pool.get('stock.picking.line')
        line_ids = context.get('line_id', []) or []
        partial_ids = partial_pick_obj.search(cr, uid, [('wizard_id', '=', ids), ('id', '=', line_ids)])

        for line in partial_pick_obj.browse(cr, uid, partial_ids, context=context):
            product = line.product_id.id

            if pool_ids:
                for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                    # Model from I get info
                    model = i.model_id.model
                    partial_result = []

                    for fields in i.qz_field_ids:
                        # Fields name to search in model
                        name_field = fields.qz_field_id.name
                        # Get fields from Model
                        printing_field = self.pool.get(model).read(cr, uid, [product], [name_field], context=context)
                        # Limit to 40 characters on long lines

                        for x in printing_field:
                            if x[name_field]:
                                print_field = x[name_field]
                                if len(print_field) > 40:
                                    print_field = print_field[:40] + '..'
                                else:
                                    print_field = print_field
                                    # Barcode Format: Bp1,p2,p3,p4,p5,p6,p7,p8,"DATA"\n

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
                                     str(print_field) + '"' + '\n'}


                            # Text field Format: Ap1,p2,p3,p4,p5,p6,p7,"DATA"\n
                            else:

                                data = []
                                data += {'A' + str(fields.h_start_p1) + ',' +
                                     str(fields.v_start_p2) + ',' +
                                     str(fields.rotation_p3) + ',' +
                                     str(fields.font_p4) + ',' +
                                     str(fields.h_multiplier_p5) + ',' +
                                     str(fields.v_multiplier_p6) + ',' +
                                     str(fields.n_r_p7) + ',' + '"' +
                                     unicodedata.normalize('NFKD', print_field.replace('"', '')).encode('ascii',
                                                                                       'ignore') + '"' + '\n'}

                            """
                            Example of ELP commands to send
                            N
                            A40,80,0,4,1,1,N,"Tangerine Duck 4.4%"
                            A40,198,0,3,1,1,N,"Duty paid on 39.9l"
                            A40,240,0,3,1,1,N,"Gyle: 127     Best Before: 16/09/2011"
                            A40,320,0,4,1,1,N,"Pump & Truncheon"
                            P1
                            """
                            # Partial result that create one line for each field to print

                            partial_result += data

                        strings = '\n'.join(partial_result)
                        result = '"""\n' + 'N\n'
                        result += strings
                        result += 'P1\n"""'

                return result

    def send_epl_data(self, cr, uid, ids, context=None):
        z = zebra()
        printer = self.get_default_label_printer(cr, uid, ids, context=context)
        conf_obj = self.pool.get('qz.config')
        conf_id = conf_obj.search(cr, uid, [('qz_printer.system_name', '=', printer)])
        z.setqueue(printer)
        if conf_id:
            for x in conf_obj.browse(cr, uid, conf_id):
                thermal = x.qz_direct_thermal
                h = x.qz_label_height
                gap = x.qz_label_gap
                height = [h, gap]
                width = x.qz_label_width
                z.setup(direct_thermal=thermal, label_height=height, label_width=width)
        epl = self.prepare_epl_data(cr, uid, ids, context=context)
        partial_pick_obj = self.pool.get('stock.partial.line')
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
