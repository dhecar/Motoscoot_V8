## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}

 table {
        width:98%;
        position:relative;
        left:15px;
        }

.list_main_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_main_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_main_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_main_table thead {
    display:table-header-group;
}

div.formatted_note {
    text-align:left;
    padding-left:10px;
    font-size:11;
}


.list_bank_table {
    text-align:center;
    border-collapse: collapse;
    page-break-inside: avoid;
    display:table;
}

.act_as_row {
   display:table-row;
}
.list_bank_table .act_as_thead {
    background-color: #EEEEEE;
    text-align:left;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
    white-space:nowrap;
    background-clip:border-box;
    display:table-cell;
}
.list_bank_table .act_as_cell {
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
    white-space:nowrap;
    display:table-cell;
}


.list_tax_table {
}
.list_tax_table td {
    text-align:left;
    font-size:12;
}
.list_tax_table th {
}
.list_tax_table thead {
    display:table-header-group;
}


.list_total_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_total_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px
    padding-left:3px
}
.list_total_table thead {
    display:table-header-group;
}


.no_bloc {
    border-top: thin solid  #ffffff ;
}

.right_table {
    right: 4cm;
    width:"100%";
}

.std_text {
    font-size:12;
}

tfoot.totals tr:first-child td{
    padding-top: 15px;
}

th.date {
    width: 90px;
}

td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}
.header_table {
    text-align: center;
    border: 1px solid lightGrey;
    border-collapse: collapse;
}
.header_table th {
    font-size: 12px;
    border: 1px solid lightGrey;
}
.header_table td {
    font-size: 12px;
    border: 1px solid lightGrey;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}
.address .recipient {
    font-size: 12px;
    margin-left: 350px;
    margin-right: 120px;
    float: right;
}

.nobreak {
     page-break-inside: avoid;
 }

.align_top {
     vertical-align:text-top;
 }

        .ref {
        text-align:right;
        }

        .code {
        font-size:10px;
        font-style:bold;
        text-align:left;
        white-space: nowrap;
        color:#585858;

        }

        .ref2 {
        font-size:12px;
        font-style:bold;
        }

        .ref3{
        font-size:10px;
        font-style:bold;
        text-align:right;
        }

        .totals {
        font-size:12px;
        }


       .orden {
        margin-top:20px;
        margin-bottom:20px;
        }

    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>

    %for inv in objects:
    <% setLang(inv.partner_id.lang) %>
       <table class="list_main_table orden">
        <br style="clear:both">
      <thead>
          <tr>
            <th class="ref">${_("Ref. Art")}</th>
	        <th class="ref ">${_("Description")}</th>
	        <th class=" ref ">${_("Quantity")}</th>
            <th class="ref ">${_("Precio")}</th>
            <th class=" ref ">${_("Dto%")}</th>
            <th class=" ref ">${_("Importe")}</th>
          </tr>
      </thead>
      <tbody>
        %for line in inv.invoice_line:
	   <tr>
	    <td class="code">${line.product_id.default_code or '' | n}</td>
	    <td class="ref align_top">

                %if line.product_id:
                <div class="nobreak">${line.product_id.name.replace('\n','<br/>') or '' | n}
                    %if line.formatted_note:
                    <br/>
                    <div class="formatted_note">${line.formatted_note| n}</div>
                    %endif
               </div>
                %else:
                <div class="nobreak">${line.name.replace('\n','<br/>') or '' | n}
                    %if line.formatted_note:
                    <br/>
                    <div class="formatted_note">${line.formatted_note| n}</div>
                    %endif
               </div>

                %endif
        </td>
	    <td class="ref" style="text-align:center">${ int(line.quantity) }</td>
	   <td class="ref" style="text-align:center">${formatLang(line.price_unit)}</td>
       <td class="ref" style="text-align:center">${line.discount and formatLang(line.discount, digits=get_digits(dp='Sale Price')) or '    '    } ${line.discount and '%' or ''}</td>
       <td class="ref" style="text-align:center">${formatLang(line.price_subtotal, digits=get_digits(dp='Sale Price'))}${inv.currency_id.symbol}</td>
       </tr>
        %endfor
        </tbody>
        <tfoot>
          <td colspan="4" class="ref2"/>
          <td >
            ${_("Net Total:")}
          </td>
          <td class="ref2">
            ${formatLang(inv.amount_untaxed, get_digits(dp='Sale Price'))}${inv.currency_id.symbol}
          </td>
        </tr>
        <tr>
          <td colspan="4" class="ref2"/>
          <td >
            ${_("Taxes:")}
          </td>
          <td class="ref2">
            ${formatLang(inv.amount_tax, get_digits(dp='Sale Price'))}${inv.currency_id.symbol}
          </td>
            %if inv.tax_line:
                %for x in inv.tax_line:
                <tr><td colspan="4" class="ref2"/>
                    <td colspan="2" class="ref3">${x.name}:  <b>${x.amount}${inv.currency_id.symbol}</b></td>
                </tr>
                %endfor
            %endif
        </tr>
        <tr >
          <td colspan="4" class="ref2" style="border-top:2px solid #000000;border-bottom:2px double #848484;"/>
          <td style="border-top:2px solid #000000;border-bottom:2px double #848484;">
            ${_("Total:")}
          </td>
          <td class="ref2" style="border-top:2px solid #000000;border-bottom:2px double #848484;">
            <b>${formatLang(inv.amount_total, get_digits(dp='Sale Price'))}${inv.currency_id.symbol}</b>
          </td>
        </tr>
         </tfoot>
        </table>
        <br/>

    %if inv.comment:
        <p class="std_text">${inv.comment | carriage_returns}</p>
    %endif
    %if inv.note2 :
        <p class="std_text">${inv.note2 | n}</p>
    %endif
    %if inv.fiscal_position and inv.fiscal_position.note:
        <br/>
        <p class="std_text">
        ${inv.fiscal_position.note | n}
        </p>
    %endif

    %if not loop.last:
    <p style="page-break-after:always"></p>
    %endif

    %endfor
</body>
</html>
