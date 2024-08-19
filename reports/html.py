from utils.certificates import extract_cert_info, format_cert_info
from datetime import datetime

def calculate_days_until_expiry(expiry_date):
    expiry = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
    remaining_days = (expiry - datetime.now()).days
    return remaining_days

def get_background_color_for_expiry(remaining_days):
    if remaining_days < 0:
        return '#FFC7CE'
    elif remaining_days < 7:
        return '#FFCC99'
    elif remaining_days < 30:
        return '#FFEB9C'
    else:
        return '#C6EFCE'

def generate_html_report(domains_certs, filename, language):
    domain_info = []
    for domain, certs in domains_certs.items():
        certs_sorted = sorted(certs, key=lambda x: calculate_days_until_expiry(format_cert_info(extract_cert_info(x[1]), language)[language['expiry_date']]))
        domain_info.append((domain, certs_sorted))
    
    domain_info_sorted = sorted(domain_info, key=lambda x: calculate_days_until_expiry(format_cert_info(extract_cert_info(x[1][0][1]), language)[language['expiry_date']]))

    html_content = f"""
    <html>
    <head>
        <title>{language['sheet_title']}</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }}
            .container {{
                width: 80%;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                border: 1px solid #ccc;
            }}
            h1 {{
                text-align: center;
                font-size: 24px;
                color: #333;
                margin-bottom: 40px;
            }}
            h2 {{
                font-size: 18px;
                color: #555;
                margin-bottom: 20px;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
                border: 1px solid #ddd;
                table-layout: fixed;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
                box-sizing: border-box;
            }}
            th {{
                background-color: #f7f7f7;
                color: #555;
                font-weight: bold;
                text-align: center;
            }}
            td {{
                background-color: #ffffff;
                border-bottom: 1px solid #ddd;
                text-align: center;
            }}
            td.expiry {{
                font-weight: bold;
                background-color: {get_background_color_for_expiry(0)};
            }}
            tr:nth-child(even) td {{
                background-color: #f9f9f9;
            }}
            .spacer {{
                height: 20px;
                background-color: #fff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{language['sheet_title']}</h1>
    """

    for domain, certs in domain_info_sorted:
        html_content += f"<h2>{language['domain_ip']}: {domain}</h2>"

        for port, cert in certs:
            cert_info = extract_cert_info(cert)
            formatted_info = format_cert_info(cert_info, language)
            expiry_date = formatted_info[language['expiry_date']]
            remaining_days = calculate_days_until_expiry(expiry_date)
            color = get_background_color_for_expiry(remaining_days)

            html_content += f"""
            <table>
                <tr>
                    <th>{language['port']}</th>
                    <td>{port}</td>
                </tr>
                <tr>
                    <th>{language['issued_date']}</th>
                    <td>{formatted_info[language['issued_date']]}</td>
                </tr>
                <tr>
                    <th>{language['expiry_date']}</th>
                    <td>{expiry_date}</td>
                </tr>
                <tr>
                    <th>{language['days_until_expiry']}</th>
                    <td class="expiry" style="background-color: {color};">{remaining_days}</td>
                </tr>
                <tr>
                    <th>{language['subject']}</th>
                    <td><pre>{formatted_info[language['subject']]}</pre></td>
                </tr>
                <tr>
                    <th>{language['issuer']}</th>
                    <td><pre>{formatted_info[language['issuer']]}</pre></td>
                </tr>
                <tr>
                    <th>{language['serial_number']}</th>
                    <td>{formatted_info[language['serial_number']]}</td>
                </tr>
            </table>
            <div class="spacer"></div>
            """

    html_content += """
        </div>
    </body>
    </html>
    """

    with open(filename, 'w') as file:
        file.write(html_content)
