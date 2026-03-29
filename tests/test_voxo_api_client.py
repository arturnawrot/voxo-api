from unittest.mock import MagicMock, patch

import pytest

from voxo_api.credentials import CredentialsV1
from voxo_api.http_client import HttpClient
from voxo_api.voxo_api_client import VoxoApiClient
from voxo_api.services.call_blocking import CallBlocking


class TestVoxoApiClientInit:

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_creates_service_factory(self, mock_factory_cls):
        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)
        mock_factory_cls.assert_called_once()
        assert client.service_factory is mock_factory_cls.return_value

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_inherits_base_client_behavior(self, mock_factory_cls):
        http = MagicMock(spec=HttpClient)
        cred = MagicMock()
        cred.api_token = "tok"
        client = VoxoApiClient(credentials=[cred], http=http)

        assert client.http is http
        assert cred in client.credentials
        cred.verify_token.assert_called_once_with(http)


class TestGetattr:

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_returns_service_instance(self, mock_factory_cls):
        mock_service_class = MagicMock()
        mock_factory = mock_factory_cls.return_value
        mock_factory.get_service_class.return_value = mock_service_class

        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)

        result = client.SomeService
        mock_factory.get_service_class.assert_called_once_with("SomeService")
        mock_service_class.assert_called_once_with(client)
        assert result is mock_service_class.return_value

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_raises_lookup_error_for_unknown_service(self, mock_factory_cls):
        mock_factory = mock_factory_cls.return_value
        mock_factory.get_service_class.side_effect = LookupError("not found")

        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)

        with pytest.raises(LookupError):
            _ = client.NonExistent

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_creates_new_instance_each_access(self, mock_factory_cls):
        mock_service_class = MagicMock()
        mock_factory = mock_factory_cls.return_value
        mock_factory.get_service_class.return_value = mock_service_class

        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)

        instance1 = client.SomeService
        instance2 = client.SomeService
        assert mock_service_class.call_count == 2


class TestIntegration:

    def test_access_real_call_blocking_service(self):
        http = MagicMock(spec=HttpClient)
        cred = CredentialsV1(api_token="tok")
        cred.verify_token = MagicMock()  # skip real HTTP call

        client = VoxoApiClient(credentials=[cred], http=http)
        service = client.CallBlocking
        assert isinstance(service, CallBlocking)
        assert service.api_client is client
