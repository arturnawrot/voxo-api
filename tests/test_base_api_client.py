from unittest.mock import MagicMock, patch, call

import pytest

from voxo.base_api_client import BaseApiClient
from voxo.credentials import CredentialsV1, CredentialsV2
from voxo.http_client import HttpClient


class TestBaseApiClientInit:

    def test_uses_provided_http_client(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)
        assert client.http is http

    @patch("voxo.base_api_client.HttpClient")
    def test_creates_default_http_client(self, mock_http_cls):
        client = BaseApiClient(credentials=[])
        mock_http_cls.assert_called_once()
        assert client.http is mock_http_cls.return_value

    def test_stores_credentials(self):
        cred = CredentialsV1(api_token="tok")
        client = BaseApiClient(credentials=[cred], http=MagicMock(spec=HttpClient))
        assert client.credentials == [cred]

    def test_empty_credentials_list(self):
        client = BaseApiClient(credentials=[], http=MagicMock(spec=HttpClient))
        assert client.credentials == []


class TestVerifyCredentials:

    def test_verifies_credentials_with_token(self):
        cred = MagicMock()
        cred.api_token = "tok"
        http = MagicMock(spec=HttpClient)

        BaseApiClient(credentials=[cred], http=http)
        cred.verify_token.assert_called_once_with(http)

    def test_skips_credentials_without_token(self):
        cred = MagicMock()
        cred.api_token = None
        http = MagicMock(spec=HttpClient)

        BaseApiClient(credentials=[cred], http=http)
        cred.verify_token.assert_not_called()

    def test_verifies_multiple_credentials(self):
        cred1 = MagicMock()
        cred1.api_token = "tok1"
        cred2 = MagicMock()
        cred2.api_token = "tok2"
        cred3 = MagicMock()
        cred3.api_token = None
        http = MagicMock(spec=HttpClient)

        BaseApiClient(credentials=[cred1, cred2, cred3], http=http)
        cred1.verify_token.assert_called_once_with(http)
        cred2.verify_token.assert_called_once_with(http)
        cred3.verify_token.assert_not_called()

    def test_propagates_verification_error(self):
        cred = MagicMock()
        cred.api_token = "bad"
        cred.verify_token.side_effect = Exception("invalid token")
        http = MagicMock(spec=HttpClient)

        with pytest.raises(Exception, match="invalid token"):
            BaseApiClient(credentials=[cred], http=http)


class TestAddCredentials:

    def test_adds_and_verifies(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred = MagicMock()
        cred.api_token = "new-tok"
        client.add_credentials(cred)

        assert cred in client.credentials
        cred.verify_token.assert_called_once_with(http)

    def test_adds_without_verification_when_no_token(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred = MagicMock()
        cred.api_token = None
        client.add_credentials(cred)

        assert cred in client.credentials
        cred.verify_token.assert_not_called()

    def test_add_multiple_credentials(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred1 = MagicMock()
        cred1.api_token = "a"
        cred2 = MagicMock()
        cred2.api_token = "b"
        client.add_credentials(cred1)
        client.add_credentials(cred2)

        assert len(client.credentials) == 2

    def test_propagates_verification_error_on_add(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred = MagicMock()
        cred.api_token = "bad"
        cred.verify_token.side_effect = Exception("bad token")

        with pytest.raises(Exception, match="bad token"):
            client.add_credentials(cred)
        # Should not be appended on failure
        assert cred not in client.credentials
