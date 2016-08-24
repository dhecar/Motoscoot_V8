## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
        .line {border:#000 1px solid }

        @font-face
{
    font-family: barcode;
    src: url(/opt/odoo/custom/code128.ttf);
}

/* Use the new font in a css class */
    .barcode-class
    {
    font-family: barcode;
    font-size: 80px;
    float:left;
    position:absolute;
    top:50px;

    }

   table {
    border-collapse: collapse;
}


    </style>
</head>

<body>

    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>
    %for picking in objects:
        <% setLang(picking.partner_id.lang) %>

    %if picking.sale_id:



    <h1 style="clear:both;margin-top:30px;">${_(u'Picking List') } ${picking.name}</h1>
    <div style="float:right;margin-top:15px;margin-bottom:15px;">
            <table class="recipient" style="border:1px solid #C0C0C0;">

                <%
                prod_qty = total_prod(picking)
                %>

                %if picking.partner_id.parent_id:
                <%
                shipping_addr = shipping_address(picking)
                %>
                <thead><th style="font-weight:bold;">Dirección de Envio</th></thead>
                <tr>
                    <td class="name">${shipping_addr.name or ''}</td>
                    <td>${shipping_addr.title and shipping_addr.name or ''} ${shipping_addr.name }</td>
                </tr>
                %else:
                <%
                shipping_addr = shipping_address(picking)
                %>
                <thead><th style="font-weight:bold;width=50">Dirección de Envio</th></thead>
                <tr>
                    <td nowrap style="width=250">
                    ${shipping_addr.title and shipping_addr.name or ''} ${shipping_addr.name }<br>
                    ${shipping_addr.street or ''}<br>
                    ${shipping_addr.city or ''}<br>
                    ${shipping_addr.zip or ''}, ${shipping_addr.state_id.name or ''}, ${shipping_addr.country_id.name or ''}<br>
                    Teléfono: ${shipping_addr.phone or ''}<br>
                    Móbil: ${shipping_addr.mobile or ''}<br>
                    Email: ${shipping_addr.email or ''}</td>

                </tr>
                %endif
            </table>

            </div>
            <div style="float:right;margin-top:15px;margin-bottom:15px;margin-right:30px;">
            <%
            invoice_addr = invoice_address(picking)
            %>
            <table class="invoice" style="border:1px solid #C0C0C0;">
                <thead><th style="font-weight:bold;width=50">Dirección Facturación</th></thead>
                <tr>

                <td nowrap style="width=250">
                ${invoice_addr.title and invoice_addr.title.name or ''} ${invoice_addr.name }<br>
                ${invoice_addr.street or ''}<br>
                ${invoice_addr.city or ''}<br>
                ${invoice_addr.zip or ''}, ${invoice_addr.state_id.name or ''}, ${invoice_addr.country_id.name or ''}<br>
                Teléfono: ${invoice_addr.phone or ''}<br>
                Móbil: ${invoice_addr.mobile or ''}<br>
                Email: ${invoice_addr.email or ''}<br>
                </td>
                </tr>
            </table>
            </div>

    ${helper.embed_image('png', generate_barcode(picking.name))| n}
    <!--Tabla cabecera-->
        <table class="basic_table" width="100%">

            %if picking.origin and picking.sale_id:
                <tr>
                    <td style="font-weight:bold;">Num. Art</td>
                    <td style="font-weight:bold;">${_("Vendedor")}</td>
                    <td style="font-weight:bold;">${_("Pedido")}</td>
                    <td style="font-weight:bold;">${_("C. Final")}</td>
                    <td style="font-weight:bold;">${_("F. envío")}</td>
                    <td style="font-weight:bold;">${_('Weight')}</td>
                    <td style="font-weight:bold;">${_('Transporte')}</td>
                    <td style="font-weight:bold;">${_('Nº Track')}</td>
                    <td style="font-weight:bold;">${_("Total €")}</td>


                </tr>
                <tr>
                    <td>${prod_qty} art.</td>
                    <td>${user.name}</td>

                    <td>${picking.origin or ''}</td>

                    %if 'MAG-4' in picking.origin:
                        <td>Toptaller</td>
                    %elif 'MAG-1' in picking.origin:
                        <td>Motoscoot</td>
                    %elif 'MAG-5' in picking.origin:
                        <td>Motoscoot</td>
                    %elif 'MAG-6' in picking.origin:
                        <td>Toptaller</td>
                    %elif 'SO' in picking.origin and picking.partner_id.category_id:

                        %if 'General' in picking.partner_id.category_id.name or 'Piloto' in picking.partner_id.category_id.name:
                            <td>Motoscoot</td>
                        %elif 'Taller' in picking.partner_id.category_id.name or 'Taller NO VAT' in picking.partner_id.category_id.name:
                            <td>Toptaller</td>
                        %endif

                    %elif 'SO' in picking.origin and not picking.partner_id.category_id:
                        <td>N/A</td>
                    %endif

                        <td>${formatLang(picking.date_done, date=True)}</td>
                        <td>${picking.weight}</td>
                        <td>${picking.carrier_id and picking.carrier_id.carrier_file_id.name or ''}</td>
                        <td>${picking.carrier_tracking_ref or ''}</td>
                        <td>${formatLang(picking.sale_id.amount_total)}</td>
            %elif not picking.origin and not picking.sale_id:
            <tr>
                <td style="font-weight:bold;">${_("Vendedor")}</td>
                <td style="font-weight:bold;">${_("Pedido")}</td>
                <td style="font-weight:bold;">${_("C. Final")}</td>
                <td style="font-weight:bold;">${_("F. envío")}</td>
                <td style="font-weight:bold;">${_('Weight')}</td>
                <td style="font-weight:bold;">${_('Transporte')}</td>
                <td style="font-weight:bold;">${_('Nº Track')}</td>
                <td style="font-weight:bold;">${_("Total €")}</td>


            </tr>
            <tr>
                <td>${user.name}</td>

                    <td>${picking.origin or ''}</td>

                    %if 'General' in picking.partner_id.category_id.name or 'Piloto' in picking.partner_id.category_id.name:
                        <td>Motoscoot</td>
                    %elif 'Taller' in picking.partner_id.category_id.name or 'Taller NO VAT' in picking.partner_id.category_id.name:
                        <td>Toptaller</td>

                    %else:
                        <td>Final</td>
                    %endif
                <td>${formatLang(picking.date_done, date=True)}</td>
                <td>${picking.weight}</td>
                <td>${picking.carrier_id and picking.carrier_id.carrier_file_id.name or ''}</td>
                <td>${picking.carrier_tracking_ref or ''}</td>
                <td>N/A</td>
            </tr>
            %endif

        </table>

    <!-- Tabla lineas pedido-->
        <table class="list_sale_table" width="100%" style="margin-top: 20px;">
            <thead>
            %if picking.origin and picking.sale_id:
                <tr>
                    <th> Hecho?</th>
                    <th style="text-align:left; ">${_("Qt")}</th>
                    <th style="text-align:left; ">${_("Ref")}</th>
                    <th style="text-align:left; ">${_("Nota")}</th>
                    <th style="text-align:left; ">${_("Marca")}</th>
                    <th style="text-align:left; ">${_("Description")}</th>
                    <!--<th style="text-align:left; ">${_("Ubicación")}</th>-->
                    <th style="text-align:left; ">${_("STOCKS")}</th>

                </tr>
            </thead>
                <tbody>

                %for line in picking.move_lines_sorted:

                    <tr style="border-top:1px solid grey;border-right:1px solid grey;">            </td>
                        <td style="height:40px;text-align:left;border-right:1px solid grey;border-left:1px solid grey" >                    </td>
                        <td style="font-size:18px;height:40px;text-align:left;border-right:1px solid grey; " >${ int(line.product_qty) }</td>
                        <td style="height:40px;width:60px;font-size:14px;text-align:left;bottom-border:1px solid grey">
                            <b>${( line.product_id.default_code )}</b>
                             %if line.product_id.loc_rack:
                            <br>${( line.product_id.loc_rack)} || ${( line.product_id.loc_row)} || ${( line.product_id.loc_case)}
                            %endif;
                        </td>
                        %if line.product_id.internal_note:
                            <td style="height:40px;text-align:center;font-size:20px; " >*</td>
                        %else:
                        <td></td>
                        %endif
                        <td style="height:40px;text-align:left; " >${( line.product_id.product_brand_id.name )}</td>
                        <td style="height:40px;text-align:left; " >${( line.product_id.name ) }</td>


                        <td style="height:40px;text-align:left;" >${ str(line.product_id.test) }</td>



                    </tr>
                    %if line.product_id.internal_note:
                    <tr>
                        <td style="height:40px;border-left:1px solid grey"></td><td></td><td></td>
                        <td colspan="3" style="font-size:12px;font-weight:bold;">${line.product_id.internal_note}</td>
                    </tr>
                    %endif
                %endfor

            %elif not picking.origin and not picking.sale_id:
                    <tr>
                        <th> Hecho?</th>
                        <th style="text-align:left; ">${_("Qt")}</th>
                        <th style="text-align:left; ">${_("Ref")}</th>
                        <th style="text-align:left; ">${_("Nota")}</th>
                        <th style="text-align:left; ">${_("Marca")}</th>
                        <th style="text-align:left; ">${_("Description")}</th>
                        <!--<th style="text-align:left; ">${_("Ubicación")}</th>-->
                        <th style="text-align:left; ">${_("Stocks")}</th>

                    </tr>
            </thead>
                <tbody>
                %for line in picking.move_lines_sorted:
                    <tr style="border-top:3px solid grey;border-right:1px solid grey;">           </td>
                        <td style="height:40px;text-align:left;border-right:1px solid grey;border-left:1px solid grey" >                    </td>
                        <td style="font-size:18px;height:40px;text-align:left;border-right:1px solid grey; " >${ int(line.product_qty) }</td>
                        <td style="height:40px;width:60px;font-size:14px;text-align:left"><b>${( line.product_id.default_code )}</b>
                         %if line.product_id.loc_rack:
                            <br>${( line.product_id.loc_rack)} || ${( line.product_id.loc_row)} || ${( line.product_id.loc_case)}
                            %endif;
                        </td>
                        %if line.product_id.internal_note:
                            <td style="text-align:center;font-size:20px; " >*</td>
                        %else:
                        <td></td>
                        %endif
                        <td style="height:40px;text-align:left; " >${( line.product_id.product_brand_id.name )}</td>
                        <td style="height:40px;text-align:left; " >${( line.product_id.name ) }</td>
                        <!--<td style="text-align:left; ">${( line.product_id.loc_rack )}  ${( line.product_id.loc_row )}  ${( line.product_id.loc_case)}</td>-->
                        <td style="height:40px;text-align:left;" > ${ str(line.product_id.test) }</td>


                    </tr>
                %if line.product_id.internal_note:
                    <tr>
                        <td style="border-left:1px solid grey"></td><td></td><td></td>
                        <td colspan="3" style="font-size:12px;font-weight:bold;">${line.product_id.internal_note}</td>
                    </tr>
                %endif
                %endfor
            %endif

        </table>

    <br>
    <br/>
        %if picking.sale_id.sale_internal_comment :
            <p class="std_text">${picking.sale_id.sale_internal_comment | carriage_returns}</p>
        %endif

    <p style="page-break-before: always"/>


    </body>
</html>


    %else:

        <h1 style="clear:both;margin-top:30px;">${_(u'Picking List') } ${picking.name}</h1>


    <!--Tabla cabecera-->
        <table class="basic_table" width="100%">



             <%
                prod_qty = total_prod(picking)
                %>
              <tr>
                    <td>${prod_qty} art.</td>
                    <td>${picking.partner_id.name or ''}</td>
                    <td>${picking.date_done or ''}


            <tr>

        </table>

    <!-- Tabla lineas pedido-->
        <table class="list_sale_table" width="100%" style="margin-top: 20px;">
            <thead>

                <tr>
                    <th style="text-align:left; ">${_("Qt")}</th>
                    <th style="text-align:left; ">${_("Ref")}</th>
                    <th style="text-align:left; ">${_("Marca")}</th>
                    <th style="text-align:left; ">${_("Description")}</th>
                    <th style="text-align:left; ">${_("Stocks")}</th>


                </tr>
            </thead>
                <tbody>

                %for line in picking.move_lines_sorted:

                    <tr style="border-top:1px solid grey;border-right:1px solid grey;">            </td>

                        <td style="font-size:18px;height:40px;text-align:left;border-right:1px solid grey; " >${ int(line.product_qty) }</td>
                        <td style="height:40px;width:60px;font-size:14px;text-align:left;bottom-border:1px solid grey"><b>${( line.product_id.default_code )}</b>
                            %if line.product_id.loc_rack:
                            <br>${( line.product_id.loc_rack)} || ${( line.product_id.loc_row)} || ${( line.product_id.loc_case)}
                            %endif;
                        </td>
                        <td style="height:40px;text-align:left; " >${( line.product_id.product_brand_id.name )}</td>
                        <td style="height:40px;text-align:left; " >${( line.product_id.name ) }</td>
                        <td style="height:40px;text-align:left;" >${ str(line.product_id.test) }</td>

                    </tr>

                %endfor


            </table>

    <br>
    <br/>



    %endif
    %endfor
    <p style="page-break-before: always"/>
    </body>
    </html>
