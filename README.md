# Ceeva

Ceeva is a tool for checking SSL/TLS certificates across multiple domains and ports. It provides detailed reports in various formats and supports multiple languages.

## Features

- **Certificate Retrieval:** Obtain certificates for multiple domains and ports.
- **Expiry Highlighting:**
  - **Red** for expired certificates
  - **Orange** for certificates expiring in less than 7 days
  - **Yellow** for certificates expiring in less than 30 days
  - **Green** for certificates with more than 30 days remaining
- **Data Export:** Export data to XLSX and HTML formats with sorting and highlighting.
- **Multilingual Support:** Available in multiple language

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/felicjaq/ceeva.git
    cd ceeva
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Ceeva allows you to check SSL/TLS certificates for domains and IP addresses. You can specify IP ranges, ports, and choose the report format.

```bash
    main.py [-h] --source SOURCE [--ports PORTS] [--report REPORT] [--format {xlsx,html}] [--language {en,ru}] [-v]
```

## Examples

1. Check a single domain and port:
    ```bash
    python3 main.py -s example.com -p 443
    ```
    
2. Check a range of IP addresses on all ports and create an Excel report:
    ```bash
    python3 main.py -s 192.168.1.1-192.168.1.10 -p 80,443 -f xlsx -r report
    ```
    
3. Generate an HTML report for specific domains:
    ```bash
    python3 main.py -s example.com,anotherdomain.com -f html -p 443 -r report
    ```    
