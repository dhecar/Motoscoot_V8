# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _


class QzConfig(models.Model):
    _name = 'qz.config'
    _table = 'qz_config'
    _rec_name = 'qz_printer'
    _description = 'Qz Print configuration'


    name = fields.Char(string="Action Name", size=64, required=True, select=1)
    qz_printer = fields.Many2one(comodel_name='printing.printer', string='Printer', required=True, select=1)
    qz_direct_thermal = fields.Boolean('Direct Thermal')
    qz_label_height = fields.Integer('Label Height in dots')
    qz_label_gap = fields.Integer('Label gap size in dots')
    qz_label_width = fields.Integer('Label width in dots')
    model_id = fields.Many2one(comodel_name='ir.model', string='Model', required=True, select=1)
    qz_field_ids = fields.One2many(comodel_name="qz.fields", inverse_name='report_id', string='Fields')
    model_list = fields.Char('Model List', size=256)
    ref_ir_act_window = fields.Many2one(comodel_name= 'ir.actions.act_window', string ='Sidebar action', readonly=True,
                                             help="Sidebar action to make this template available on records "
                                                  "of the related document model")
    ref_ir_value = fields.Many2one(comodel_name='ir.values', string='Sidebar button', readonly=True,
                                        help="Sidebar button to open the sidebar action")


    def onchange_model(self, cr, uid, ids, model_id):
        model_list = ""
        if model_id:
            model_obj = self.pool.get('ir.model').search(cr, uid, {('model', '=', 'product.template')})
            model_data = model_obj.browse(cr, uid, model_id)
            model_list = "[" + str(model_id) + ""
            active_model_obj = self.pool.get(model_data.model)
            if active_model_obj._inherits:
                for key, val in active_model_obj._inherits.items():
                    model_ids = model_obj.search(cr, uid, [('model', '=', key)])
                    if model_ids:
                        model_list += "," + str(model_ids[0]) + ""
            model_list += "]"
        return {'value': {'model_list': model_list}}

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        ir_values_obj = self.pool.get('ir.values')
        action_obj = self.pool.get('ir.actions.act_window')
        for data in self.browse(cr, uid, ids, context=context):
            src_obj = data.model_id.model
            button_name = _('Labels(%s)') % data.name
            vals['ref_ir_act_window'] = action_obj.create(
                cr, uid,
                {
                    'name': button_name,
                    'type': 'ir.actions.act_window',
                    'res_model': 'qz.print',
                    'src_model': src_obj,
                    'view_type': 'form',
                    'context': "{'label_print' : %d}" % data.id,
                    'view_mode': 'form,tree',
                    'target': 'new',
                    'auto_refresh': 1,
                },
                context)
            vals['ref_ir_value'] = ir_values_obj.create(
                cr, uid,
                {
                    'name': button_name,
                    'model': src_obj,
                    'key2': 'client_action_multi',
                    'value': (
                        "ir.actions.act_window," +
                        str(vals['ref_ir_act_window'])),
                    'object': True,
                },
                context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
        }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        ir_values_obj = self.pool.get('ir.values')
        act_window_obj = self.pool.get('ir.actions.act_window')
        for template in self.browse(cr, uid, ids, context=context):
            try:
                if template.ref_ir_act_window:
                    act_window_obj.unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    ir_values_obj.unlink(cr, uid, template.ref_ir_value.id, context)
            except Exception, e:
                raise orm.except_osv(_("Warning"), _("Deletion of the action record failed. %s" % (e)))
        return True


QzConfig()


class QzFields(models.Model):
    _name = "qz.fields"
    _rec_name = "sequence"

    report_id = fields.Many2one(comodel_name='qz.config', string='ID')
    sequence = fields.Integer(string="Sequence", required=True)
    qz_field_id = fields.Many2one(comodel_name='ir.model.fields', string='Fields', required=True, select=1)
    qz_field_type = fields.Selection([('barcode', 'Barcode'), ('text', 'Text')], string='Type', default='barcode')
    h_start_p1 = fields.Integer(string='Horizontal Start (dots)')
    v_start_p2 = fields.Integer(string='Vertical Start (dots)')
    rotation_p3 = fields.Selection([('0', 'No rotation'), ('1', '90 degrees'), ('2', '180 degrees'),
                                         ('3', '270 degrees')], string='Rotation', default='0')
    font_p4 = fields.Selection([('1', '203 dpi(8 x 12 dots) or 300 dpi(12 x 20 dots)'),
                                     ('2', '203 dpi(10 x 16 dots) or 300 dpi(16 x 28 dots)'),
                                     ('3', '203 dpi(12 x 20 dots) or 300 dpi(20 x 36 dots)'),
                                     ('4', '203 dpi(14 x 24 dots) or 300 dpi(24 x 44 dots)'),
                                     ('5', '203 dpi(32 x 48 dots) or 300 dpi(48 x 80 dots)')],
                                    string='Font Type', default='1')

    h_multiplier_p5 = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                                             ('6', '6'), ('8', '8')], string='Horizontal Multiplier', default='1')
    v_multiplier_p6 = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                                             ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')], string='Vertical Multiplier',
                                       default='1')
    n_r_p7 = fields.Selection([('N', 'Normal'), ('R', 'Reverse')], string='Normal/Reverse', default='N')
    bar_sel_p4 = fields.Selection([('3', 'Code 39 std. or extended'),
                                        ('3C', 'Code 39 with check digit'),
                                        ('9', 'Code 93'),
                                        ('0', 'Code 128 UCC'),
                                        ('1', 'Code 128 auto A, B, C modes'),
                                        ('1A', 'Code 128 mode A'),
                                        ('1B', 'Code 128 mode B'),
                                        ('1C', 'Code 128 mode C'),
                                        ('K', 'Codabar'),
                                        ('E80', 'EAN8'),
                                        ('E82', 'EAN8 2 digit add-on'),
                                        ('E85', 'EAN8 5 digit add-on'),
                                        ('E30', 'EAN13'),
                                        ('E32', 'EAN13 2 digit add-on'),
                                        ('E35', 'EAN13 5 digit add-on'),
                                        ('2G', 'German Post Code'),
                                        ('2', 'Interleaved 2 of 5'),
                                        ('2C', 'Interleaved 2 of 5 with mod 10 check digit'),
                                        ('2D', 'Interleaved 2/5 readable check digit'),
                                        ('P', 'Postnet 5, 9, 11 & 13 digit'),
                                        ('J', 'Japanese Postnet'),
                                        ('1E', 'UCC/EAN 128*'),
                                        ('UA0', 'UPC A'),
                                        ('UA2', 'UPC A 2 digit add-on'),
                                        ('UA5', 'UPC A 5 digit add-on'),
                                        ('UE0', 'UPC E'),
                                        ('UE2', 'UPC E 2 digit add-on'),
                                        ('UE5', 'UPC E 5 digit add-on'),
                                        ('2U', 'UPC Interleaved 2 of 5'),
                                        ('L', 'Plessey (MSI-1) with mod. 10 check digit'),
                                        ('M', 'MSI-3 with mod. 10 check digit')], string='Barcode Type')
    n_bar_w_p5 = fields.Integer(string='Narrow Bar width in dots')
    w_bar_w_p6 = fields.Integer(string='Wide bar width in dots')
    bar_height_p7 = fields.Integer(string='Barcode Height in dots')
    human_read_p8 = fields.Selection([('B', 'Yes'), ('N', 'No')], string='Human Readable')


QzFields()
