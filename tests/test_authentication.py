from unittest.mock import MagicMock

from voxo_api.credentials import NoAuth
from voxo_api.services.v1.authentication import CreateAccessToken, AuthResponse


def _make_api_client(credentials=None):
    client = MagicMock()
    client.credentials = credentials or []
    client.http = MagicMock()
    return client


class TestCreateAccessTokenConfig:

    def test_credentials_class(self):
        service = CreateAccessToken(_make_api_client())
        assert service.get_credentials_class() is NoAuth

    def test_method(self):
        service = CreateAccessToken(_make_api_client())
        assert service.get_method() == "POST"

    def test_url_path(self):
        service = CreateAccessToken(_make_api_client())
        assert service.get_url_path() == "authentication"

    def test_response_type(self):
        service = CreateAccessToken(_make_api_client())
        assert service.get_response_type() is AuthResponse


class TestCreateAccessTokenBody:

    def test_body_contains_local_strategy(self):
        service = CreateAccessToken(_make_api_client())
        body = service.get_body(email="user@example.com", password="secret")
        assert body["strategy"] == "local"

    def test_body_contains_email(self):
        service = CreateAccessToken(_make_api_client())
        body = service.get_body(email="user@example.com", password="secret")
        assert body["email"] == "user@example.com"

    def test_body_contains_password(self):
        service = CreateAccessToken(_make_api_client())
        body = service.get_body(email="user@example.com", password="secret")
        assert body["password"] == "secret"


class TestCreateAccessTokenExecute:

    def test_execute_builds_correct_request(self):
        client = _make_api_client(credentials=[NoAuth()])

        response = MagicMock()
        response.json.return_value = {
            "accessToken": "tok123",
            "authentication": {"strategy": "local"},
            "user": {"id": 1, "email": "user@example.com"},
        }
        client.http.request.return_value = response

        service = CreateAccessToken(client)
        result = service.execute(email="user@example.com", password="secret")

        client.http.request.assert_called_once_with(
            "POST",
            "https://api.voxo.co/authentication",
            headers={},
            json={"strategy": "local", "email": "user@example.com", "password": "secret"},
        )

        assert isinstance(result, AuthResponse)
        assert result.accessToken == "tok123"
        assert result.authentication == {"strategy": "local"}
        assert result.user == {"id": 1, "email": "user@example.com"}


class TestAuthResponse:

    def test_dataclass_fields(self):
        response = AuthResponse(
            accessToken="tok",
            authentication={"strategy": "local"},
            user={"id": 1},
        )
        assert response.accessToken == "tok"
        assert response.authentication == {"strategy": "local"}
        assert response.user == {"id": 1}

    def test_equality(self):
        a = AuthResponse(accessToken="t", authentication={}, user={})
        b = AuthResponse(accessToken="t", authentication={}, user={})
        assert a == b

    def test_inequality(self):
        a = AuthResponse(accessToken="t1", authentication={}, user={})
        b = AuthResponse(accessToken="t2", authentication={}, user={})
        assert a != b
