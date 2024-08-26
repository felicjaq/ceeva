import re
import logging
import argparse
import ipaddress
from utils.logging import setup_logging
from utils.certificates import get_certificates, extract_cert_info, print_cert_info_to_console
from reports.xlsx import generate_excel_report
from reports.html import generate_html_report
from reports.json import generate_json_report
from utils.language import load_language

def expand_source_range(source):
    ips = []
    if '-' in source:
        start_ip, end_ip = source.split('-')
        start_ip = ipaddress.ip_address(start_ip.strip())
        end_ip = ipaddress.ip_address(end_ip.strip())
        for ip_int in range(int(start_ip), int(end_ip) + 1):
            ips.append(str(ipaddress.ip_address(ip_int)))
    else:
        try:
            network = ipaddress.ip_network(source, strict=False)
            ips.extend([str(ip) for ip in network.hosts()])
        except ValueError:
            ips.append(source)
    return ips

def main():
    parser = argparse.ArgumentParser(
        description='Check SSL certificates and generate a report in the specified format (Excel or HTML).'
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Comma-separated list of domains, IP addresses, CIDR blocks, or IP ranges to check for SSL certificates.'
    )
    parser.add_argument(
        '--ports', '-p',
        default='443',
        help='Comma-separated list of ports to check for SSL certificates. Defaults to 443 if not specified.'
    )
    parser.add_argument(
        '--report', '-r',
        help='The output file for the report. This argument is required if --format is specified.'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['xlsx', 'html', 'json'],
        help='The format of the report.'
    )
    parser.add_argument(
        '--language', '-l',
        choices=['en', 'ru'],
        default='en',
        help='Language for the report output. Defaults to English.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Increase output verbosity for debugging.'
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    language = load_language(args.language)

    if args.format and not args.report:
        parser.error(language['report_required'])

    if not args.format and args.report:
        parser.error(language['format_required'])

    sources = []
    for source in args.source.split(','):
        sources.extend(expand_source_range(source.strip()))

    ports = []
    if args.ports:
        if not re.match(r'^(\d+(?:-\d+)?,?)+$|all$', args.ports):
            parser.error('Invalid port range')
        for port_range in args.ports.split(','):
            if '-' in port_range:
                start, end = map(int, port_range.split('-'))
                ports.extend(range(start, end + 1))
            elif port_range.lower() == 'all':
                ports = list(range(1, 65536))
            else:
                ports.append(int(port_range))

    report_file = args.report
    report_format = args.format

    logger.debug(language['checking_certificates'].format(', '.join(sources), ', '.join(map(str, ports))))

    domains_certs = {}

    try:
        for source in sources:
            certs = get_certificates(source, ports, language)
            domains_certs[source] = certs
            logger.debug(language['found_certificates'].format(len(certs), source))

        if report_format and report_file:
            if report_format == 'xlsx':
                report_file += '.xlsx'
                generate_excel_report(domains_certs, report_file, language)
            elif report_format == 'html':
                report_file += '.html'
                generate_html_report(domains_certs, report_file, language)
            elif report_format == 'json':
                report_file += '.json'
                generate_json_report(domains_certs, report_file, language)    
            logger.info(language['report_saved'].format(report_file))
        else:
            print_cert_info_to_console(domains_certs, language)

    except Exception as e:
        logger.error(language['error_occurred'].format(e))

if __name__ == "__main__":
    main()
