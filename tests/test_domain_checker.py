"""Test suite for domain checker functionality."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add parent directory to Python path to import domain_check.py
sys.path.append(str(Path(__file__).parent.parent))
from domain_check import check_domain, parse_date  # noqa: E402


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
