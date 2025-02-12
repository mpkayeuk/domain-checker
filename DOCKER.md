# Docker Instructions for Domain Checker

This document provides instructions for building and running the Domain Checker utility using Docker.

## Prerequisites

- Docker installed on your system
- Git (to clone the repository)

## Building the Docker Image

To build the Docker image, run the following command from the project root directory:

```bash
docker build -t domain-checker .
```

## Running the Container

The domain checker container can be run in two modes:

### 1. Check a Single Domain

```bash
docker run domain-checker -d example.com
```

### 2. Check Multiple Domains from a File

To check multiple domains from a file, you'll need to mount the file into the container:

```bash
# Assuming your domains file is named domains.txt and is in the current directory
docker run -v $(pwd)/domains.txt:/app/domains.txt domain-checker -f /app/domains.txt
```

### Additional Options

- Show only available domains:
  ```bash
  docker run domain-checker -d example.com -a
  ```

- Check multiple domains and show only available ones:
  ```bash
  docker run -v $(pwd)/domains.txt:/app/domains.txt domain-checker -f /app/domains.txt -a
  ```

## Example domains.txt Format

Your domains.txt file should contain comma-separated domain names:

```
example.com,example.net,example.org
```

## Notes

- The container runs with minimal privileges using a slim Python image
- All dependencies are installed during the build process
- The application runs as an entrypoint, so you only need to provide the arguments

## Troubleshooting

1. If you get permission errors when mounting files, ensure the file permissions are correct on your host system.
2. If you encounter rate limiting, wait a few minutes before trying again.
3. For any network-related issues, ensure your Docker host has internet connectivity.

## Security Considerations

- The container runs without root privileges
- Only necessary dependencies are installed
- Uses official Python base image
- No sensitive data is stored in the container 