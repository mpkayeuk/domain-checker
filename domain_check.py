#!/usr/bin/env python3
"""Domain availability checker using RDAP protocol.

This module provides functionality to check domain availability
and registration information using RDAP.
"""

import sys
import csv
import requests
import argparse
from datetime import datetime


def parse_date(date_str):
    """Parse date string to a consistent format.

    Args:
        date_str (str): Date string in ISO format with optional timezone.

    Returns:
        str or None: Formatted date string (YYYY-MM-DD) or None if
        parsing fails.
    """
    if not date_str:
        return None
    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


def check_domain(domain):
    """Check if a domain is registered using RDAP.

    Args:
        domain (str): The domain name to check.

    Returns:
        dict: A dictionary containing domain status and registration
        details.
    """
    try:
        url = f"https://rdap.org/domain/{domain}"
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return {
                "domain": domain,
                "status": "AVAILABLE",
                "registration_date": None,
                "expiration_date": None,
            }
        elif response.status_code == 200:
            data = response.json()
            status = data.get("status", [])
            events = data.get("events", [{}])

            # Get registration date from first event
            reg_date = None
            if events:
                reg_date = parse_date(events[0].get("eventDate"))

            # Look for expiration date in events
            exp_date = None
            for event in data.get("events", []):
                if event.get("eventAction") == "expiration":
                    exp_date = parse_date(event.get("eventDate"))
                    break

            result = {
                "domain": domain,
                "registration_date": reg_date,
                "expiration_date": exp_date,
            }

            # Check domain status
            status_checks = [
                ("pending delete", "PENDING DELETE"),
                ("redemption period", "PENDING DELETE"),
                ("pending transfer", "PENDING TRANSFER"),
                ("client hold", "ON HOLD"),
                ("expired", "EXPIRED"),
            ]

            for check, result_status in status_checks:
                if check in status:
                    result["status"] = result_status
                    break
            else:
                result["status"] = "REGISTERED"

            return result
        elif response.status_code == 429:
            return {
                "domain": domain,
                "status": "RATE LIMITED",
                "registration_date": None,
                "expiration_date": None,
            }
        else:
            return {
                "domain": domain,
                "status": f"ERROR ({response.status_code})",
                "registration_date": None,
                "expiration_date": None,
            }
    except Exception as e:
        error_msg = str(e)
        return {
            "domain": domain,
            "status": f"ERROR ({error_msg})",
            "registration_date": None,
            "expiration_date": None,
        }


def write_csv(results, filename):
    """Write domain check results to a CSV file.

    Args:
        results (list): List of domain check result dictionaries.
        filename (str): Path to the output CSV file.
    """
    fields = ["domain", "status", "registration_date", "expiration_date"]
    try:
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
    except IOError as e:
        print(f"Error writing CSV file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Run the domain checker command line interface."""
    parser = argparse.ArgumentParser(description="Check domain availability")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Single domain to check")
    group.add_argument("-f", "--file", help="Input file with domains")
    parser.add_argument(
        "-a",
        "--available-only",
        action="store_true",
        help="Show only available domains",
    )
    parser.add_argument("-c", "--csv", help="Export results to CSV file")

    args = parser.parse_args()

    domains = []
    if args.domain:
        domains = [args.domain]
    elif args.file:
        try:
            with open(args.file, "r") as f:
                content = f.read().strip()
                domains = [d.strip() for d in content.split(",") if d.strip()]
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

    results = []
    for domain in domains:
        result = check_domain(domain)
        results.append(result)

        if args.available_only:
            if result["status"] == "AVAILABLE":
                print(domain)
        else:
            output = f"{domain}: {result['status']}"
            if result["status"] == "REGISTERED":
                dates = []
                if result["registration_date"]:
                    dates.append(f"registered: {result['registration_date']}")
                if result["expiration_date"]:
                    dates.append(f"expires: {result['expiration_date']}")
                if dates:
                    output += f" ({', '.join(dates)})"
            print(output)

    if args.csv:
        try:
            write_csv(results, args.csv)
            print(f"\nResults exported to {args.csv}")
        except Exception as e:
            print(f"Error writing CSV file: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
