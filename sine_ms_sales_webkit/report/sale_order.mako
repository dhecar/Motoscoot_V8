## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

        .list_main_table {
        text-align:left;
        }

        .list_main_table th {
        text-align:left;
        font-size:11;
        padding-right:3px;
        padding-left:3px;
        padding-top:10px;
        }

        .list_main_table td {
        text-align:left;
        font-size:11;
        }

        .list_main_table thead {
        border-bottom:1px solid;

        }

        div.formatted_note {
        text-align:left;
        padding-left:10px;
        font-size:11;
        }


        .ref {
        font-size:10px;
        text-align:right;
        }


        .desc {
        font-size:10px;
        text-align:right;

        padding-left:5px;
        }

        .code {
        font-size:10px;
        font-style:bold;
        text-align:left;
        white-space: nowrap;
        color:#585858;

        }

        .ref2 {
        font-size:9px;
        font-style:bold;
        text-align:center;
        }

        .totals {
        font-size:12px;
        }

       .orden {
        margin-top:20px;
        margin-bottom:20px;
        }

        thead { display: table-header-group }
        tfoot { display: table-row-group }
        tr { page-break-inside: avoid }
    </style>
</head>
<body>

 %for order in objects:
    <% setLang(order.partner_id.lang) %>
    <%
      quotation = order.state in ['draft', 'sent']
    %>
    <table class="list_main_table orden"  width="100%">
        <br style="clear:both">
      <thead>
          <tr>
            <th class="ref">${_("Ref. Art")}</th>
	        <th class="desc">${_("Description")}</th>
	        <th class=" ref ">${_("Quantity")}</th>
            <th class="ref ">${_("Precio")}</th>
            <th class=" ref ">${_("Dto%")}</th>
	        <th class=" ref ">${_("Importe")}</th>
          </tr>
      </thead>
      <tbody>
        %for line in order.order_line:
	   <div style="page-break-inside: avoid">
           <tr>
	    <td class="code">${line.product_id.default_code}</td>
	    <td class="desc align_top">
               <div class="nobreak">${line.product_id.name.replace('\n','<br/>') or '' | n}</div>
        </td>
	    <td class="ref">${ int(line.product_uos and line.product_uos_qty or line.product_uom_qty) }</td>
        <td class="ref">${formatLang(line.price_unit)}</td>
        <td class="ref">${line.discount and formatLang(line.discount, digits=get_digits(dp='Sale Price')) or '    '    } ${line.discount and '%' or ''}</td>
        <td class="ref">${formatLang(line.price_subtotal, digits=get_digits(dp='Sale Price'))}&nbsp;${order.pricelist_id.currency_id.symbol}</td>
       </tr>
        %endfor
       </div>
      </tbody>

      <tfoot>
          <td colspan="4" class="ref2"/>
          <td class ="ref">
            ${_("Net Total:")}
          </td>
          <td class="ref2">
            ${formatLang(order.amount_untaxed, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="ref2"/>
          <td class="ref">
            ${_("Taxes:")}
          </td>
          <td class="ref2">
            ${formatLang(order.amount_tax, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}
          </td>
        </tr>
        <tr >
          <td colspan="4" class="ref2" style="border-top:2px solid #000000;border-bottom:2px double #848484;"/>
          <td style="border-top:2px solid #000000;border-bottom:2px double #848484;">
            ${_("Total:")}
          </td>
          <td class="ref2" style="border-top:2px solid #000000;border-bottom:2px double #848484;">
            <b>${formatLang(order.amount_total, get_digits(dp='Sale Price'))} ${order.pricelist_id.currency_id.symbol}</b>
          </td>
        </tr>
      </tfoot>
    </table>

%endfor

    </body>

</html>
