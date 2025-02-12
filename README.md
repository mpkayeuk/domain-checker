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
- Supports both native Python execution and Docker containerization
- Export results to CSV for spreadsheet analysis
- Displays registration and expiration dates for registered domains

## Installation & Usage

You can run this tool either natively with Python or using Docker.

### Option 1: Native Python Installation

#### Requirements
- Python 3.6 or higher
- `requests` library

#### Installation Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/mpkayeuk/domain-checker.git
   cd domain-checker
   ```

2. Install the required package:
   ```bash
   pip install requests
   ```

3. Make the script executable:
   ```bash
   chmod +x domain_check.py
   ```

#### Native Usage

Check a single domain:
```bash
./domain_check.py -d example.com
```

Check multiple domains from a file:
```bash
./domain_check.py -f domains.txt
```

Show only available domains:
```bash
./domain_check.py -f domains.txt -a
```

Export results to CSV:
```bash
./domain_check.py -f domains.txt -c results.csv
```

### Option 2: Docker Installation

#### Requirements
- Docker installed on your system

#### Installation Steps

You can either build the image locally or pull it from GitHub Container Registry.

##### Option A: Pull from GitHub Container Registry
```bash
docker pull ghcr.io/mpkayeuk/domain-checker:main
```

Or use a specific version:
```bash
docker pull ghcr.io/mpkayeuk/domain-checker:v1.0.0
```

##### Option B: Build Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/mpkayeuk/domain-checker.git
   cd domain-checker
   ```

2. Build the Docker image:
   ```bash
   docker build -t domain-checker .
   ```

#### Docker Usage

If you pulled the image from GitHub Container Registry, replace `domain-checker` with `ghcr.io/mpkayeuk/domain-checker:main` in the following commands.

Check a single domain:
```bash
docker run ghcr.io/mpkayeuk/domain-checker:main -d example.com
```

Check multiple domains from a file:
```bash
# Assuming your domains file is in the current directory
docker run -v $(pwd)/domains.txt:/app/domains.txt ghcr.io/mpkayeuk/domain-checker:main -f /app/domains.txt
```

Show only available domains:
```bash
docker run ghcr.io/mpkayeuk/domain-checker:main -d example.com -a
```

Export results to CSV:
```bash
# Export results to a CSV file in the current directory
docker run -v $(pwd):/app/output ghcr.io/mpkayeuk/domain-checker:main -f /app/domains.txt -c /app/output/results.csv
```

## Container Registry

The Docker image is automatically built and published to GitHub Container Registry on every push to the main branch and when new version tags are created. You can find all available versions at:
https://github.com/mpkayeuk/domain-checker/pkgs/container/domain-checker

Available tags:
- `main` - Latest version from the main branch
- `v1.0.0` - Specific version releases
- `sha-XXXXXXX` - Specific commit builds

## Input File Format

For checking multiple domains, create a text file (e.g., `domains.txt`) with comma-separated domain names:
```
example.com,mydomain.com,anotherdomain.net
```

## Example Output

Regular output (all statuses):
```
example.com: REGISTERED (registered: 1995-08-14, expires: 2024-08-13)
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

CSV output (results.csv):
```csv
domain,status,registration_date,expiration_date
example.com,REGISTERED,1995-08-14,2024-08-13
available-domain.com,AVAILABLE,,
pending-domain.com,PENDING DELETE,,
expired-domain.com,EXPIRED,,
```

## Command Line Options

```
usage: domain_check.py [-h] (-d DOMAIN | -f FILE) [-a] [-c CSV]

Check domain availability

options:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Single domain to check
  -f FILE, --file FILE  File containing comma-separated domains
  -a, --available-only  Show only available domains
  -c CSV, --csv CSV     Export results to CSV file
```

## Troubleshooting

### General Issues
- RDAP servers may have rate limits
- Some TLDs might not support RDAP queries
- Response times may vary based on server load

### Docker-Specific Issues
1. If you get permission errors when mounting files, ensure the file permissions are correct on your host system.
2. For any network-related issues, ensure your Docker host has internet connectivity.

## Security Notes

When running with Docker:
- The container runs with minimal privileges using a slim Python image
- Only necessary dependencies are installed
- Uses official Python base image
- No sensitive data is stored in the container

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/mpkayeuk/domain-checker.git
   cd domain-checker
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run the test suite:
```bash
pytest tests/
```

Run tests with coverage report:
```bash
pytest tests/ --cov=./ --cov-report=term-missing
```

### Code Quality

This project uses several tools to maintain code quality:

- **pre-commit hooks** for automated code formatting and checks
- **black** for code formatting
- **flake8** for code style and quality checks
- **pytest** for testing
- **pytest-cov** for test coverage reporting

The pre-commit hooks will run automatically when you commit changes. You can also run them manually:
```bash
pre-commit run --all-files
```

### Continuous Integration

The project uses GitHub Actions for continuous integration:

1. **Python Tests Workflow**
   - Runs on multiple Python versions (3.8-3.11)
   - Executes the test suite
   - Runs code quality checks
   - Reports test coverage

2. **Docker Build Workflow**
   - Builds the Docker image
   - Runs functional tests on the container
   - Publishes the image to GitHub Container Registry (on main branch and tags) 