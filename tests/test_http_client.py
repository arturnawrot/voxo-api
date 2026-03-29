from unittest.mock import patch, MagicMock

import pytest
import requests

from voxo.http_client import HttpClient, DEFAULT_TIMEOUT


class TestHttpClientInit:

    def test_default_base_url(self):
        client = HttpClient()
        assert client.base_url == "https://api.voxo.co/"

    def test_custom_base_url_trailing_slash_normalized(self):
        client = HttpClient(base_url="https://example.com/")
        assert client.base_url == "https://example.com/"

    def test_custom_base_url_no_trailing_slash(self):
        client = HttpClient(base_url="https://example.com")
        assert client.base_url == "https://example.com/"

    def test_default_timeout(self):
        client = HttpClient()
        assert client.timeout == DEFAULT_TIMEOUT

    def test_custom_timeout(self):
        client = HttpClient(timeout=60)
        assert client.timeout == 60

    def test_session_is_requests_session(self):
        client = HttpClient()
        assert isinstance(client.session, requests.Session)


class TestHttpClientRequest:

    def _make_client(self):
        client = HttpClient(base_url="https://api.test.com")
        client.session = MagicMock()
        return client

    def _mock_response(self, status_code=200):
        resp = MagicMock(spec=requests.Response)
        resp.status_code = status_code
        resp.raise_for_status = MagicMock()
        return resp

    def test_builds_url_from_base_and_path(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        client.request("GET", "users/1")
        call_args = client.session.request.call_args
        assert call_args[0] == ("GET", "https://api.test.com/users/1")

    def test_strips_leading_slash_from_path(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        client.request("GET", "/users/1")
        call_args = client.session.request.call_args
        assert call_args[0] == ("GET", "https://api.test.com/users/1")

    def test_sets_default_timeout(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        client.request("GET", "test")
        call_kwargs = client.session.request.call_args[1]
        assert call_kwargs["timeout"] == DEFAULT_TIMEOUT

    def test_caller_can_override_timeout(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        client.request("GET", "test", timeout=99)
        call_kwargs = client.session.request.call_args[1]
        assert call_kwargs["timeout"] == 99

    def test_passes_kwargs_to_session(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        client.request("POST", "data", json={"key": "val"}, headers={"X-Custom": "1"})
        call_kwargs = client.session.request.call_args[1]
        assert call_kwargs["json"] == {"key": "val"}
        assert call_kwargs["headers"] == {"X-Custom": "1"}

    def test_returns_response_on_success(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        result = client.request("GET", "ok")
        assert result is resp

    def test_raises_on_connection_error(self):
        client = self._make_client()
        client.session.request.side_effect = requests.ConnectionError("refused")

        with pytest.raises(requests.ConnectionError):
            client.request("GET", "fail")

    def test_raises_on_timeout(self):
        client = self._make_client()
        client.session.request.side_effect = requests.Timeout("timed out")

        with pytest.raises(requests.Timeout):
            client.request("GET", "slow")

    def test_raises_on_http_error(self):
        client = self._make_client()
        resp = self._mock_response(status_code=404)
        resp.text = "Not Found"
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
        client.session.request.return_value = resp

        with pytest.raises(requests.HTTPError):
            client.request("GET", "missing")

    def test_supports_all_http_methods(self):
        client = self._make_client()
        resp = self._mock_response()
        client.session.request.return_value = resp

        for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            client.request(method, "resource")
            assert client.session.request.call_args[0][0] == method
