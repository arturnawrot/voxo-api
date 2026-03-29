from dataclasses import dataclass
from unittest.mock import MagicMock, PropertyMock

import pytest

from voxo_api.credentials import Credentials, CredentialsV1, CredentialsV2
from voxo_api.services.abstract_service import AbstractService


# --- Helpers ---

@dataclass
class FakeModel:
    name: str
    value: int


class FakeService(AbstractService[FakeModel]):
    """Minimal concrete service for testing."""

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV1

    def get_method(self) -> str:
        return "GET"

    def get_url_path(self) -> str:
        return "fake-endpoint"

    def get_response_type(self) -> type[FakeModel]:
        return FakeModel


def _make_api_client(credentials=None):
    client = MagicMock()
    client.credentials = credentials or []
    client.http = MagicMock()
    return client


# --- Cannot instantiate abstract ---

class TestAbstractServiceABC:

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            AbstractService(MagicMock())

    def test_must_implement_all_abstract_methods(self):
        class Incomplete(AbstractService):
            def get_credentials_class(self): return CredentialsV1
            # missing get_method, get_url_path, get_response_type

        with pytest.raises(TypeError):
            Incomplete(MagicMock())


# --- Init ---

class TestInit:

    def test_stores_api_client(self):
        client = _make_api_client()
        service = FakeService(client)
        assert service.api_client is client

    def test_stores_http_from_client(self):
        client = _make_api_client()
        service = FakeService(client)
        assert service.http is client.http


# --- get_credentials ---

class TestGetCredentials:

    def test_returns_matching_credentials(self):
        cred = CredentialsV1(api_token="tok")
        client = _make_api_client(credentials=[cred])
        service = FakeService(client)

        assert service.get_credentials() is cred

    def test_returns_first_matching_when_multiple(self):
        cred1 = CredentialsV1(api_token="first")
        cred2 = CredentialsV1(api_token="second")
        client = _make_api_client(credentials=[cred1, cred2])
        service = FakeService(client)

        assert service.get_credentials() is cred1

    def test_skips_wrong_credential_type(self):
        v2 = CredentialsV2(api_token="v2")
        v1 = CredentialsV1(api_token="v1")
        client = _make_api_client(credentials=[v2, v1])
        service = FakeService(client)

        assert service.get_credentials() is v1

    def test_raises_when_no_matching_credentials(self):
        v2 = CredentialsV2(api_token="v2")
        client = _make_api_client(credentials=[v2])
        service = FakeService(client)

        with pytest.raises(LookupError, match="CredentialsV1"):
            service.get_credentials()

    def test_raises_when_no_credentials_at_all(self):
        client = _make_api_client(credentials=[])
        service = FakeService(client)

        with pytest.raises(LookupError):
            service.get_credentials()


# --- _build_url ---

class TestBuildUrl:

    def test_path_only(self):
        service = FakeService(_make_api_client())
        assert service._build_url("") == "https://api.voxo.co/fake-endpoint"

    def test_with_uri_params(self):
        service = FakeService(_make_api_client())
        assert service._build_url("123") == "https://api.voxo.co/fake-endpoint/123"

    def test_strips_slashes_from_path_and_params(self):
        class SlashyService(FakeService):
            def get_url_path(self):
                return "/slashy/"

        service = SlashyService(_make_api_client())
        assert service._build_url("/456/") == "https://api.voxo.co/slashy/456"

    def test_empty_uri_params_no_trailing_slash(self):
        service = FakeService(_make_api_client())
        result = service._build_url("")
        assert not result.endswith("/")


# --- _build_headers ---

class TestBuildHeaders:

    def test_merges_credential_headers(self):
        cred = CredentialsV1(api_token="tok")
        service = FakeService(_make_api_client())
        headers = service._build_headers(cred)
        assert headers == {"Authorization": "Bearer tok"}

    def test_service_headers_override_credential_headers(self):
        class CustomHeaderService(FakeService):
            def get_headers(self, **kwargs):
                return {"Authorization": "Custom override", "X-Extra": "val"}

        cred = CredentialsV1(api_token="tok")
        service = CustomHeaderService(_make_api_client())
        headers = service._build_headers(cred)
        assert headers["Authorization"] == "Custom override"
        assert headers["X-Extra"] == "val"

    def test_no_credential_headers(self):
        cred = MagicMock()
        cred.get_header.return_value = None
        service = FakeService(_make_api_client())
        headers = service._build_headers(cred)
        assert headers == {}

    def test_kwargs_passed_to_get_headers(self):
        class KwargsService(FakeService):
            def get_headers(self, **kwargs):
                return {"X-Tenant": str(kwargs.get("tenant_id", ""))}

        cred = MagicMock()
        cred.get_header.return_value = None
        service = KwargsService(_make_api_client())
        headers = service._build_headers(cred, tenant_id=42)
        assert headers == {"X-Tenant": "42"}


# --- _build_body ---

class TestBuildBody:

    def test_no_body_no_cred_body(self):
        cred = CredentialsV1(api_token="tok")  # get_json_body returns None
        service = FakeService(_make_api_client())  # get_body returns None
        assert service._build_body(cred) is None

    def test_service_body_only(self):
        class BodyService(FakeService):
            def get_body(self, **kwargs):
                return {"data": "value"}

        cred = CredentialsV1(api_token="tok")
        service = BodyService(_make_api_client())
        assert service._build_body(cred) == {"data": "value"}

    def test_cred_body_only(self):
        cred = MagicMock()
        cred.get_json_body.return_value = {"cred_key": "cred_val"}
        service = FakeService(_make_api_client())  # get_body returns None
        assert service._build_body(cred) == {"cred_key": "cred_val"}

    def test_merges_both_bodies(self):
        class BodyService(FakeService):
            def get_body(self, **kwargs):
                return {"service_key": "svc"}

        cred = MagicMock()
        cred.get_json_body.return_value = {"cred_key": "cred"}
        service = BodyService(_make_api_client())
        result = service._build_body(cred)
        assert result == {"cred_key": "cred", "service_key": "svc"}

    def test_service_body_overrides_cred_body_on_conflict(self):
        class BodyService(FakeService):
            def get_body(self, **kwargs):
                return {"shared": "from_service"}

        cred = MagicMock()
        cred.get_json_body.return_value = {"shared": "from_cred"}
        service = BodyService(_make_api_client())
        result = service._build_body(cred)
        assert result["shared"] == "from_service"


# --- _parse_response ---

class TestParseResponse:

    def test_parses_valid_json_into_model(self):
        service = FakeService(_make_api_client())
        response = MagicMock()
        response.json.return_value = {"name": "test", "value": 42}

        result = service._parse_response(response)
        assert isinstance(result, FakeModel)
        assert result.name == "test"
        assert result.value == 42

    def test_raises_value_error_on_non_json(self):
        service = FakeService(_make_api_client())
        response = MagicMock()
        response.json.side_effect = ValueError("No JSON")
        response.headers = {"Content-Type": "text/html"}

        with pytest.raises(ValueError, match="Expected JSON response"):
            service._parse_response(response)

    def test_raises_type_error_on_bad_fields(self):
        service = FakeService(_make_api_client())
        response = MagicMock()
        response.json.return_value = {"wrong_field": "oops"}

        with pytest.raises(TypeError, match="Failed to deserialize"):
            service._parse_response(response)

    def test_raises_type_error_on_missing_fields(self):
        service = FakeService(_make_api_client())
        response = MagicMock()
        response.json.return_value = {"name": "partial"}  # missing 'value'

        with pytest.raises(TypeError, match="Failed to deserialize"):
            service._parse_response(response)


# --- Default method implementations ---

class TestDefaults:

    def test_get_uri_parameters_returns_empty(self):
        service = FakeService(_make_api_client())
        assert service.get_uri_parameters() == ""

    def test_get_body_returns_none(self):
        service = FakeService(_make_api_client())
        assert service.get_body() is None

    def test_get_headers_returns_empty_dict(self):
        service = FakeService(_make_api_client())
        assert service.get_headers() == {}


# --- execute (integration of all build/parse steps) ---

class TestExecute:

    def test_execute_full_flow(self):
        cred = CredentialsV1(api_token="tok")
        client = _make_api_client(credentials=[cred])

        response = MagicMock()
        response.json.return_value = {"name": "result", "value": 99}
        client.http.request.return_value = response

        service = FakeService(client)
        result = service.execute()

        client.http.request.assert_called_once_with(
            "GET", "https://api.voxo.co/fake-endpoint", headers={"Authorization": "Bearer tok"}, json=None
        )
        assert result == FakeModel(name="result", value=99)

    def test_execute_with_uri_parameters(self):
        class ParamService(FakeService):
            def get_uri_parameters(self, item_id=None, **kwargs):
                return str(item_id)

        cred = CredentialsV1(api_token="tok")
        client = _make_api_client(credentials=[cred])

        response = MagicMock()
        response.json.return_value = {"name": "item", "value": 1}
        client.http.request.return_value = response

        service = ParamService(client)
        service.execute(item_id=42)

        call_args = client.http.request.call_args
        assert call_args[0][1] == "https://api.voxo.co/fake-endpoint/42"

    def test_execute_with_body(self):
        class PostService(FakeService):
            def get_method(self):
                return "POST"
            def get_body(self, **kwargs):
                return {"payload": kwargs.get("payload")}

        cred = CredentialsV1(api_token="tok")
        client = _make_api_client(credentials=[cred])

        response = MagicMock()
        response.json.return_value = {"name": "created", "value": 1}
        client.http.request.return_value = response

        service = PostService(client)
        service.execute(payload="data")

        call_kwargs = client.http.request.call_args[1]
        assert call_kwargs["json"] == {"payload": "data"}

    def test_execute_raises_when_no_credentials(self):
        client = _make_api_client(credentials=[])
        service = FakeService(client)

        with pytest.raises(LookupError):
            service.execute()

    def test_execute_propagates_http_error(self):
        cred = CredentialsV1(api_token="tok")
        client = _make_api_client(credentials=[cred])
        client.http.request.side_effect = Exception("500 Server Error")

        service = FakeService(client)
        with pytest.raises(Exception, match="500 Server Error"):
            service.execute()
