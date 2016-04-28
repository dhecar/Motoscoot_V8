# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from zebra import zebra
from time import sleep
import unicodedata
from openerp import models, exceptions, _


class QzPrint(osv.Model):
    _name = 'qz.print'
    _description = 'Qz Print Labels'

    _columns = {
        'copies': fields.integer('Num of Copy:', required=True),
    }

    _defaults = {

        'copies': 1,
    }

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

            raise exceptions.Warning(
                _('No printer configured for this User. Please contact Administrator')
            )

    # Prepare EPL data (escaped)

    def prepare_epl_data(self, cr, uid, ids, context=None):
        # Get default printer for current user
        printer = self.get_default_label_printer(cr, uid, ids, context=context)
        # Default configuration for selected printer
        pool_obj = self.pool.get('qz.config')
        pool_ids = pool_obj.search(cr, uid, [('qz_printer.system_name', '=', printer)])
        # Active IDS
        record_ids = context and context.get('active_ids', []) or []
        # Get model to print from qz.config and field_id also:

        if pool_ids:
            for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                # Model from I get info
                model = i.model_id.model
                num_fields = len(i.qz_field_ids)
                counter = 0
                for fields in i.qz_field_ids:

                    if counter == num_fields:
                        break
                    else:
                        counter += 1

                    # Fields name to search in model
                    name_field = fields.qz_field_id.name
                    # Get fields from Model
                    printing_field = self.pool.get(model).read(cr, uid, record_ids, [name_field], context=context)
                    for x in printing_field:
                        print_field = x[name_field]
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
                                 unicodedata.normalize('NFKD', print_field).encode('ascii',
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
                    partial_result = '\n'.join(data)

                result = '"""\n' + 'N\n'
                result += partial_result

                result += 'P1\n"""'

            return result

    # Print EPL data

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
        for data in self.browse(cr, uid, ids, context=context):
            num_cop = data.copies
        for n in range(0, num_cop):
            z.output(epl)
            ## sleep  between labels, if not, printer die ;)
            sleep(1.3)

        return True


QzPrint()
