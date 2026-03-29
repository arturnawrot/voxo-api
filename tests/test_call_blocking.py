from unittest.mock import MagicMock

import pytest

from voxo.credentials import Credentials, CredentialsV1
from voxo.models.call_blocking import CallBlockingRecord
from voxo.services.call_blocking import CallBlocking


def _make_api_client(credentials=None):
    client = MagicMock()
    client.credentials = credentials or []
    client.http = MagicMock()
    return client


class TestCallBlockingConfig:

    def test_credentials_class(self):
        service = CallBlocking(_make_api_client())
        assert service.get_credentials_class() is CredentialsV1

    def test_method(self):
        service = CallBlocking(_make_api_client())
        assert service.get_method() == "GET"

    def test_url_path(self):
        service = CallBlocking(_make_api_client())
        assert service.get_url_path() == "call-blocking"

    def test_response_type(self):
        service = CallBlocking(_make_api_client())
        assert service.get_response_type() is CallBlockingRecord


class TestCallBlockingUriParameters:

    def test_returns_blocking_id_as_string(self):
        service = CallBlocking(_make_api_client())
        assert service.get_uri_parameters(blocking_id=42) == "42"

    def test_returns_string_for_large_id(self):
        service = CallBlocking(_make_api_client())
        assert service.get_uri_parameters(blocking_id=999999) == "999999"


class TestCallBlockingExecute:

    def test_execute_builds_correct_request(self):
        cred = CredentialsV1(api_token="test-token")
        client = _make_api_client(credentials=[cred])

        response = MagicMock()
        response.json.return_value = {
            "id": 1,
            "tenantId": 100,
            "callerId": "+15551234567",
            "inserted": "2024-01-01T00:00:00Z",
            "reason": "spam",
        }
        client.http.request.return_value = response

        service = CallBlocking(client)
        result = service.execute(blocking_id=1)

        client.http.request.assert_called_once_with(
            "GET",
            "call-blocking/1",
            headers={"Authorization": "Bearer test-token"},
            json=None,
        )

        assert isinstance(result, CallBlockingRecord)
        assert result.id == 1
        assert result.tenantId == 100
        assert result.callerId == "+15551234567"
        assert result.reason == "spam"


class TestCallBlockingRecord:

    def test_dataclass_fields(self):
        record = CallBlockingRecord(
            id=5,
            tenantId=200,
            callerId="+1555",
            inserted="2024-06-15",
            reason="harassment",
        )
        assert record.id == 5
        assert record.tenantId == 200
        assert record.callerId == "+1555"
        assert record.inserted == "2024-06-15"
        assert record.reason == "harassment"

    def test_equality(self):
        a = CallBlockingRecord(id=1, tenantId=1, callerId="x", inserted="t", reason="r")
        b = CallBlockingRecord(id=1, tenantId=1, callerId="x", inserted="t", reason="r")
        assert a == b

    def test_inequality(self):
        a = CallBlockingRecord(id=1, tenantId=1, callerId="x", inserted="t", reason="r")
        b = CallBlockingRecord(id=2, tenantId=1, callerId="x", inserted="t", reason="r")
        assert a != b
