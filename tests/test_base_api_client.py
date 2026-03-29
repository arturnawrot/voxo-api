from unittest.mock import MagicMock, patch, call

from voxo_api.base_api_client import BaseApiClient
from voxo_api.credentials import CredentialsV1, CredentialsV2
from voxo_api.http_client import HttpClient


class TestBaseApiClientInit:

    def test_uses_provided_http_client(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)
        assert client.http is http

    @patch("voxo_api.base_api_client.HttpClient")
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



class TestAddCredentials:

    def test_adds_credentials(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred = MagicMock()
        client.add_credentials(cred)

        assert cred in client.credentials

    def test_add_multiple_credentials(self):
        http = MagicMock(spec=HttpClient)
        client = BaseApiClient(credentials=[], http=http)

        cred1 = MagicMock()
        cred2 = MagicMock()
        client.add_credentials(cred1)
        client.add_credentials(cred2)

        assert len(client.credentials) == 2
