import json
from utils.certificates import extract_cert_info, format_cert_info

def generate_json_report(domains_certs, filename, language):
    json_data = []

    for domain, certs in domains_certs.items():
        for port, cert in certs:
            cert_info = format_cert_info(extract_cert_info(cert), language)
            json_data.append({
                language['domain_ip']: domain,
                language['port']: port,
                language['issued_date']: cert_info[language['issued_date']],
                language['expiry_date']: cert_info[language['expiry_date']],
                language['days_until_expiry']: cert_info[language['days_until_expiry']],
                language['subject']: cert_info[language['subject']],
                language['issuer']: cert_info[language['issuer']],
                language['serial_number']: str(cert_info[language['serial_number']])
            })

    json_data.sort(key=lambda x: x[language['days_until_expiry']])

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
