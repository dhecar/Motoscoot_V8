# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
from zebra import zebra
from time import sleep
import unicodedata



class QzPrint(models.Model):
    _name = 'qz.print'
    _description = 'Qz Print Labels'

    copies = fields.Integer(string='Num of Copy:', required=True, default='1')

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
            # Model from I get info
            final_result = ''
            for record in record_ids:
                for i in pool_obj.browse(cr, uid, pool_ids, context=context):
                    model = i.model_id.model
                    fields= i.qz_field_ids
                    count = len(i.qz_field_ids)
                counter = 0
                semi_partial_result = []
                for field in fields:
                    counter += 1
                        # Fields name to search in model
                    name_field = field.qz_field_id.name
                        # Get fields from Model
                    printing_field = self.pool.get(model).read(cr, uid, [record], [name_field], context=context)
                        # Limit to 40 characters on long lines

                    for x in printing_field:
                        if x[name_field]:
                            print_field = x[name_field]
                            if len(print_field) > 40:
                                print_field = print_field[:40] + '..'
                            else:
                                print_field = print_field
                            # Barcode Format: Bp1,p2,p3,p4,p5,p6,p7,p8,"DATA"\n

                            if field.qz_field_type == 'barcode':
                                data = []
                                data += {'B' + str(field.h_start_p1) + ',' +
                                        str(field.v_start_p2) + ',' +
                                        str(field.rotation_p3) + ',' +
                                        str(field.bar_sel_p4) + ',' +
                                        str(field.n_bar_w_p5) + ',' +
                                        str(field.w_bar_w_p6) + ',' +
                                        str(field.bar_height_p7) + ',' +
                                        str(field.human_read_p8) + ',' + '"' +
                                        str(print_field) + '"' + '\n'}


                                # Text field Format: Ap1,p2,p3,p4,p5,p6,p7,"DATA"\n
                            else:

                                data = []
                                data += {'A' + str(field.h_start_p1) + ',' +
                                        str(field.v_start_p2) + ',' +
                                        str(field.rotation_p3) + ',' +
                                        str(field.font_p4) + ',' +
                                        str(field.h_multiplier_p5) + ',' +
                                        str(field.v_multiplier_p6) + ',' +
                                        str(field.n_r_p7) + ',' + '"' +
                                            unicodedata.normalize('NFKD', print_field.replace('"','')).encode('ascii',
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
                                    # Semi Partial result that create one line for each field to print

                            semi_partial_result += data

                        strings = '\n'.join(semi_partial_result)
                        result = '"""\n' + 'N\n'
                        result += strings
                        if counter < count:
                            continue
                        elif counter == count:
                            result += 'P1\n"""____'

                final_result +=  result

            return final_result


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
        splited = epl.split('____')
        for label in splited:
            for n in range(0, num_cop):
                z.output(label)
                ## sleep  between labels, if not, printer die ;)
                sleep(1.2)

        return True

QzPrint()
