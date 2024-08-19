import ssl
import socket
import logging
from OpenSSL import crypto
from datetime import datetime, timedelta
from utils.language import load_language
from colorama import Fore, Style, init

init(autoreset=True)

logger = logging.getLogger(__name__)

def get_certificates(host, ports, language, retries=3, timeout=1):
    certs = []
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    for port in ports:
        logger.info(language['checking_certificate_for'].format(host, port))

        for attempt in range(retries):
            try:
                with socket.create_connection((host, port), timeout=timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert(binary_form=True)
                        certs.append((port, crypto.load_certificate(crypto.FILETYPE_ASN1, cert)))
                        logger.debug(language['successfully_retrieved_certificate'].format(host, port))
                        break
            except socket.timeout:
                logger.debug(language['timeout_occurred'].format(host, port))
                break
            except Exception as e:
                logger.debug(language['attempt_failed'].format(attempt + 1, host, port, e))
                if attempt + 1 == retries:
                    logger.debug(language['could_not_retrieve_certificate'].format(host, port, retries))

    return certs

def extract_cert_info(cert):
    not_after = cert.get_notAfter().decode('ascii')
    expiry_date = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
    days_until_expiry = (expiry_date - datetime.utcnow()).days

    cert_data = {
        'Subject': dict(cert.get_subject().get_components()),
        'Issuer': dict(cert.get_issuer().get_components()),
        'Expiry Date': not_after,
        'Days Until Expiry': days_until_expiry,
        'Serial Number': cert.get_serial_number(),
        'Issued Date': cert.get_notBefore().decode('ascii')
    }
    return cert_data

def format_cert_info(cert_info, language):
    formatted_info = {
        language['subject']: ', '.join([f"{k.decode('ascii')}: {v.decode('ascii')}" for k, v in cert_info['Subject'].items()]),
        language['issuer']: ', '.join([f"{k.decode('ascii')}: {v.decode('ascii')}" for k, v in cert_info['Issuer'].items()]),
        language['expiry_date']: format_date(cert_info['Expiry Date']),
        language['days_until_expiry']: cert_info['Days Until Expiry'],
        language['serial_number']: cert_info['Serial Number'],
        language['issued_date']: format_date(cert_info['Issued Date'])
    }
    return formatted_info

def format_date(date):
    return datetime.strptime(date, '%Y%m%d%H%M%SZ').strftime('%Y-%m-%d %H:%M:%S')

def get_color_for_days(days_until_expiry):
    if days_until_expiry < 0:
        return Fore.RED
    elif days_until_expiry < 7:
        return Fore.YELLOW
    elif days_until_expiry < 30:
        return Fore.LIGHTYELLOW_EX
    else:
        return Fore.GREEN

def print_cert_info_to_console(domains_certs, language):
    cert_entries = []

    for domain, certs in domains_certs.items():
        for port, cert in certs:
            cert_info = format_cert_info(extract_cert_info(cert), language)
            days_until_expiry = cert_info[language['days_until_expiry']]
            cert_entries.append((domain, port, cert_info, days_until_expiry))

    cert_entries.sort(key=lambda x: x[3])

    for domain, port, cert_info, days_until_expiry in cert_entries:
        color = get_color_for_days(days_until_expiry)
        print(f"{language['domain_ip']}: {domain}")
        print(f"{language['port']}: {port}")
        print(f"{language['issued_date']}: {cert_info[language['issued_date']]}")
        print(f"{language['expiry_date']}: {cert_info[language['expiry_date']]}")
        print(f"{language['days_until_expiry']}: {color}{days_until_expiry}{Style.RESET_ALL}")
        print(f"{language['subject']}: {cert_info[language['subject']]}")
        print(f"{language['issuer']}: {cert_info[language['issuer']]}")
        print(f"{language['serial_number']}: {cert_info[language['serial_number']]}")
        print("-" * 40)
