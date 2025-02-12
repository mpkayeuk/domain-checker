# Domain Availability Checker

A simple command-line tool to check domain name availability using RDAP (Registration Data Access Protocol). This tool can check single domains or process multiple domains from a file, with no API keys or registration required.

## Features

- Check single domains or multiple domains from a file
- No API keys or registration required
- Shows detailed domain statuses:
  - AVAILABLE - Domain is free to register
  - REGISTERED - Domain is currently registered and active
  - PENDING DELETE - Domain is in the process of being deleted
  - PENDING TRANSFER - Domain is in the process of being transferred
  - ON HOLD - Domain is suspended or on hold
  - EXPIRED - Domain registration has expired
  - RATE LIMITED - Too many requests to the RDAP server
  - ERROR - Any other errors with details
- Option to show only available domains
- Simple comma-separated file input format

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/domain-checker.git
   cd domain-checker
   ```

2. Install the required package:
   ```bash
   pip install requests
   ```

3. Make the script executable:
   ```bash
   chmod +x domain-check
   ```

## Usage

### Check a single domain:
```bash
./domain-check -d example.com
```

### Check multiple domains from a file:
Create a text file (e.g., `domains.txt`) with comma-separated domain names:
```
example.com, mydomain.com, anotherdomain.net
```

Then run:
```bash
./domain-check -f domains.txt
```

### Show only available domains:
```bash
./domain-check -f domains.txt -a
```

## Example Output

Regular output (all statuses):
```
example.com: REGISTERED
available-domain.com: AVAILABLE
pending-domain.com: PENDING DELETE
expired-domain.com: EXPIRED
```

Available-only output:
```
Available domains:
-----------------
available-domain.com
```

## Command Line Options

```
usage: domain-check [-h] (-d DOMAIN | -f FILE) [-a]

Check domain availability

options:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Single domain to check
  -f FILE, --file FILE  File containing comma-separated domains
  -a, --available-only  Show only available domains
```

## Limitations

- RDAP servers may have rate limits
- Some TLDs might not support RDAP queries
- Response times may vary based on server load

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 