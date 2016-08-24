import time
from report import report_sxw
from osv import osv


class report_webkit_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
        })


report_sxw.report_sxw('report.sale.order.motoscoot.webkit',
                      'sale.order',
                      'addons/sine_ms_sales_webkit/report/sale_order.mako',
                      parser=report_webkit_html)
