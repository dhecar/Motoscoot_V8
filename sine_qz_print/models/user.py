from openerp import models, fields


class res_qz_users(models.Model):
    """
    Users
    """
    _name = 'res.users'
    _inherit = 'res.users'

    epl_printer_id = fields.Many2one(comodel_name='printing.printer',
                                     string='Default Label Printer')
