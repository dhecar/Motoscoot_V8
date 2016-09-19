# import one2many_sorted
from openerp import models, fields, api, exceptions

class stock_picking(models.Model):
    _inherit = "stock.picking"

    is_printed = fields.Boolean(string='Is printed?', help='Is the picking printed?', )
    payment1_id = fields.Many2one(comodel_name='payment.type', string='Tipo Pago Magento', readonly=True)
    payment2_id = fields.Many2one(comodel_name='payment.method', string='Tipo Pago Erp', readonly=True)
    sh_id = fields.Many2one(comodel_name='sale.shop', string='Tienda', readonly=True)
    pricelist_type = fields.Many2one(comodel_name='product.pricelist', string='Tarifa', readonly=True)
    res_user = fields.Many2one(comodel_name='res.users', string='Comercial', readonly=True)
    carrier = fields.Many2one(related='carrier_id')
    carrier_ref = fields.Char(related='carrier_tracking_ref')
    paquets = fields.Integer(related='number_of_packages')

class stock_move(models.Model):
    _inherit = 'stock.move'


    prod_stock = fields.Char(related='product_id.stock_by_loc', string='Stocks')




### TODO migrate to odoo8  'Orden en los listados'.
       # 'move_lines_sorted': one2many_sorted.one2many_sorted
       # ('stock.move'
       #  , 'picking_id'
       #  , 'Moves Sorted'
       #  , states={'draft': [('readonly', False)]}
       #  , order='product_id.product_brand_id.name, product_id.default_code'
       #  )


    #def copy(self, cr, uid, id, default=None, context=None):
    #    if default is None:
    #        default = {}
    #    default = default.copy()
    #    default.update({'move_lines_sorted': []})
    #    return super(stock_picking_out, self).copy(cr, uid, id, default, context=context)


#class stock_picking_in(osv.osv):
#    _inherit = "stock.picking.in"
#    _columns = {
#
#        'move_lines_sorted': one2many_sorted.one2many_sorted
#        ('stock.move'
#         , 'picking_id'
#         , 'Moves Sorted'
#         , states={'draft': [('readonly', False)]}
#         , order='product_id.product_brand_id.name, product_id.default_code'
#         ),

#    }

#    def copy(self, cr, uid, id, default=None, context=None):
#        if default is None:
#            default = {}
#        default = default.copy()
#        default.update({'move_lines_sorted': []})
#        return super(stock_picking_in, self).copy(cr, uid, id, default, context=context)


      #  'move_lines_sorted': one2many_sorted.one2many_sorted
      #  ('stock.move'
      #   , 'picking_id'
      #   , 'Moves Sorted'
      #   , states={'draft': [('readonly', False)]}
      #   , order='product_id.product_brand_id.name, product_id.default_code'
      #   )

    #def copy(self, cr, uid, id, default=None, context=None):
    #    if default is None:
    #        default = {}
    #    default = default.copy()
    #    default.update({'move_lines_sorted': []})
    #    return super(stock_picking, self).copy(cr, uid, id, default, context=context)


