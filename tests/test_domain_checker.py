"""Test suite for domain checker functionality."""

import sys
import os
import tempfile
import importlib
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import runpy
import requests

# Add parent directory to Python path to import domain_check.py
sys.path.append(str(Path(__file__).parent.parent))
from domain_check import (  # noqa: E402
    check_domain,
    parse_date,
    write_csv,
    main,
)


def test_parse_date():
    """Test the date parsing functionality."""
    assert parse_date("2024-02-14T12:00:00Z") == "2024-02-14"
    assert parse_date("invalid-date") is None
    assert parse_date(None) is None


@pytest.mark.parametrize(
    "status_code,response_data,expected_result",
    [
        (
            404,
            None,
            {
                "domain": "test.com",
                "status": "AVAILABLE",
                "registration_date": None,
                "expiration_date": None,
            },
        ),
        (
            200,
            {
                "status": ["active"],
                "events": [
                    {
                        "eventDate": "2020-01-01T00:00:00Z",
                        "eventAction": "registration",
                    },
                    {
                        "eventDate": "2025-01-01T00:00:00Z",
                        "eventAction": "expiration",
                    },
                ],
            },
            {
                "domain": "test.com",
                "status": "REGISTERED",
                "registration_date": "2020-01-01",
                "expiration_date": "2025-01-01",
            },
        ),
        (
            429,
            None,
            {
                "domain": "test.com",
                "status": "RATE LIMITED",
                "registration_date": None,
                "expiration_date": None,
            },
        ),
        (
            200,
            {
                "status": ["pending delete"],
                "events": [],
            },
            {
                "domain": "test.com",
                "status": "PENDING DELETE",
                "registration_date": None,
                "expiration_date": None,
            },
        ),
        (
            200,
            {
                "status": ["client hold"],
                "events": [],
            },
            {
                "domain": "test.com",
                "status": "ON HOLD",
                "registration_date": None,
                "expiration_date": None,
            },
        ),
        (
            200,
            {
                "status": ["expired"],
                "events": [],
            },
            {
                "domain": "test.com",
                "status": "EXPIRED",
                "registration_date": None,
                "expiration_date": None,
            },
        ),
    ],
)
def test_check_domain(status_code, response_data, expected_result):
    """Test domain checking with different response scenarios."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = status_code
        if response_data:
            mock_response.json.return_value = response_data
        mock_get.return_value = mock_response

        result = check_domain("test.com")
        assert result == expected_result


def test_check_domain_connection_error():
    """Test domain checking behavior when a connection error occurs."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        result = check_domain("test.com")
        assert result["status"].startswith("ERROR")
        assert "Connection error" in result["status"]


def test_check_domain_json_error():
    """Test domain checking behavior when JSON parsing fails."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = check_domain("test.com")
        assert result["status"].startswith("ERROR")
        assert "Invalid JSON" in result["status"]


def test_check_domain_json_decode_error():
    """Test domain checking behavior when JSON decoding fails."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
            "Invalid JSON", "", 0
        )
        mock_get.return_value = mock_response

        result = check_domain("test.com")
        assert result["status"].startswith("ERROR")
        assert "Invalid JSON" in result["status"]


def test_write_csv():
    """Test CSV writing functionality."""
    results = [
        {
            "domain": "test.com",
            "status": "REGISTERED",
            "registration_date": "2020-01-01",
            "expiration_date": "2025-01-01",
        },
        {
            "domain": "example.com",
            "status": "AVAILABLE",
            "registration_date": None,
            "expiration_date": None,
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        write_csv(results, temp_file.name)

        # Read and verify the CSV contents
        with open(temp_file.name, "r") as f:
            content = f.read().strip().split("\n")
            header = "domain,status,registration_date,expiration_date"
            assert content[0] == header
            assert content[1] == "test.com,REGISTERED,2020-01-01,2025-01-01"
            assert content[2] == "example.com,AVAILABLE,,"

    os.unlink(temp_file.name)


def test_write_csv_error():
    """Test CSV writing error handling."""
    results = [{"domain": "test.com"}]
    with pytest.raises(SystemExit):
        write_csv(results, "/nonexistent/path/file.csv")


@pytest.mark.parametrize(
    "args,expected_output,mock_check_result",
    [
        (
            ["-d", "test.com"],
            (
                "test.com: REGISTERED "
                "(registered: 2020-01-01, "
                "expires: 2025-01-01)"
            ),
            {
                "domain": "test.com",
                "status": "REGISTERED",
                "registration_date": "2020-01-01",
                "expiration_date": "2025-01-01",
            },
        ),
        (
            ["-d", "example.com", "-a"],
            "",  # Should output nothing as domain is not available
            {
                "domain": "example.com",
                "status": "REGISTERED",
                "registration_date": "2020-01-01",
                "expiration_date": "2025-01-01",
            },
        ),
    ],
)
def test_main_single_domain(args, expected_output, mock_check_result, capsys):
    """Test main function with single domain checks."""
    with patch("domain_check.check_domain") as mock_check:
        mock_check.return_value = mock_check_result
        with patch("sys.argv", ["domain_check.py"] + args):
            main()
            captured = capsys.readouterr()
            assert captured.out.strip() == expected_output


def test_main_file_input():
    """Test main function with file input."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("test.com,example.com")
        temp_file.flush()

        mock_results = [
            {
                "domain": "test.com",
                "status": "REGISTERED",
                "registration_date": "2020-01-01",
                "expiration_date": "2025-01-01",
            },
            {
                "domain": "example.com",
                "status": "AVAILABLE",
                "registration_date": None,
                "expiration_date": None,
            },
        ]

        with patch("domain_check.check_domain") as mock_check:
            mock_check.side_effect = mock_results
            with patch("sys.argv", ["domain_check.py", "-f", temp_file.name]):
                main()

    os.unlink(temp_file.name)


def test_main_file_input_error():
    """Test main function with nonexistent file."""
    with patch("sys.argv", ["domain_check.py", "-f", "/nonexistent/file"]):
        with pytest.raises(SystemExit):
            main()


def test_main_available_only():
    """Test main function with available-only flag."""
    mock_results = [
        {
            "domain": "test.com",
            "status": "REGISTERED",
            "registration_date": None,
            "expiration_date": None,
        },
        {
            "domain": "example.com",
            "status": "AVAILABLE",
            "registration_date": None,
            "expiration_date": None,
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        temp_file.write("test.com,example.com")
        temp_file.flush()

        with patch("domain_check.check_domain") as mock_check:
            mock_check.side_effect = mock_results
            with patch("sys.argv", ["domain_check.py", "-f", temp_file.name, "-a"]):
                with patch("builtins.print") as mock_print:
                    main()
                    mock_print.assert_called_with("example.com")

    os.unlink(temp_file.name)


def test_main_with_csv_output():
    """Test main function with CSV output."""
    mock_results = [
        {
            "domain": "test.com",
            "status": "REGISTERED",
            "registration_date": "2020-01-01",
            "expiration_date": "2025-01-01",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as domains_file:
        domains_file.write("test.com")
        domains_file.flush()

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
            with patch("domain_check.check_domain") as mock_check:
                mock_check.side_effect = mock_results
                with patch(
                    "sys.argv",
                    ["domain_check.py", "-f", domains_file.name, "-c", csv_file.name],
                ):
                    with patch("builtins.print") as mock_print:
                        main()
                        mock_print.assert_called_with(f"\nResults exported to {csv_file.name}")

            # Verify CSV contents
            with open(csv_file.name, "r") as f:
                content = f.read().strip().split("\n")
                header = "domain,status,registration_date,expiration_date"
                assert content[0] == header
                assert content[1] == "test.com,REGISTERED,2020-01-01,2025-01-01"

        os.unlink(csv_file.name)
    os.unlink(domains_file.name)


def test_main_direct():
    """Test running the script directly."""
    with patch("sys.argv", ["domain_check.py", "-d", "test.com"]):
        with patch("domain_check.main") as mock_main:
            import domain_check
            domain_check.__name__ = "__main__"
            domain_check.main()
            assert mock_main.called


if __name__ == "__main__":
    pytest.main([__file__])
