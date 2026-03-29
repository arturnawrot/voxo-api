from unittest.mock import MagicMock, patch

import pytest

from voxo_api.credentials import CredentialsV1
from voxo_api.http_client import HttpClient
from voxo_api.voxo_api_client import VoxoApiClient, ServiceNamespace
from voxo_api.services.v1.call_blocking import CallBlocking


class TestVoxoApiClientInit:

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_creates_service_factory(self, mock_factory_cls):
        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)
        mock_factory_cls.assert_called_once()
        assert client.service_factory is mock_factory_cls.return_value

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_inherits_base_client_behavior(self, mock_factory_cls):
        mock_factory_cls.return_value._services = {}
        http = MagicMock(spec=HttpClient)
        cred = MagicMock()
        cred.api_token = "tok"
        client = VoxoApiClient(credentials=[cred], http=http)

        assert client.http is http
        assert cred in client.credentials

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_creates_namespace_for_each_version(self, mock_factory_cls):
        v1_services = {"MyService": MagicMock()}
        v2_services = {"OtherService": MagicMock()}
        mock_factory_cls.return_value._services = {"v1": v1_services, "v2": v2_services}

        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)

        assert isinstance(client.v1, ServiceNamespace)
        assert isinstance(client.v2, ServiceNamespace)

    @patch("voxo_api.voxo_api_client.ServiceFactory")
    def test_namespace_names_match_folder_names(self, mock_factory_cls):
        mock_factory_cls.return_value._services = {"myapi": {}, "experimental": {}}

        http = MagicMock(spec=HttpClient)
        client = VoxoApiClient(credentials=[], http=http)

        assert isinstance(client.myapi, ServiceNamespace)
        assert isinstance(client.experimental, ServiceNamespace)


class TestServiceNamespace:

    def _make_client(self):
        http = MagicMock(spec=HttpClient)
        return VoxoApiClient.__new__(VoxoApiClient), http

    def test_returns_service_instance(self):
        mock_client = MagicMock()
        mock_service_class = MagicMock()
        namespace = ServiceNamespace(mock_client, {"SomeService": mock_service_class})

        result = namespace.SomeService

        mock_service_class.assert_called_once_with(mock_client)
        assert result is mock_service_class.return_value

    def test_raises_attribute_error_for_unknown_service(self):
        namespace = ServiceNamespace(MagicMock(), {})

        with pytest.raises(AttributeError, match="Service 'NonExistent' not found"):
            _ = namespace.NonExistent

    def test_creates_new_instance_each_access(self):
        mock_client = MagicMock()
        mock_service_class = MagicMock()
        namespace = ServiceNamespace(mock_client, {"SomeService": mock_service_class})

        namespace.SomeService
        namespace.SomeService

        assert mock_service_class.call_count == 2


class TestIntegration:

    def test_access_real_call_blocking_service(self):
        http = MagicMock(spec=HttpClient)
        cred = CredentialsV1(api_token="tok")
        client = VoxoApiClient(credentials=[cred], http=http)

        service = client.v1.CallBlocking
        assert isinstance(service, CallBlocking)
        assert service.api_client is client
