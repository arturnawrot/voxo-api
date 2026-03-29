from unittest.mock import MagicMock

import pytest

from voxo.credentials import Credentials, CredentialsV1, CredentialsV2


# --- Credentials ABC ---

class TestCredentialsABC:

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            Credentials("token")

    def test_subclass_must_implement_abstract_methods(self):
        class Incomplete(Credentials):
            pass

        with pytest.raises(TypeError):
            Incomplete("token")

    def test_api_token_stored(self):
        cred = CredentialsV1(api_token="abc123")
        assert cred.api_token == "abc123"

    def test_api_token_defaults_to_none(self):
        cred = CredentialsV1()
        assert cred.api_token is None

    def test_base_verify_token_is_noop(self):
        """Credentials.verify_token does nothing by default (non-abstract)."""
        class MinimalCreds(Credentials):
            def get_header(self): return None
            def get_json_body(self): return None
            def get_api_token(self): return self.api_token

        cred = MinimalCreds("tok")
        http = MagicMock()
        cred.verify_token(http)  # should not raise
        http.request.assert_not_called()


# --- CredentialsV1 ---

class TestCredentialsV1:

    def test_get_header(self):
        cred = CredentialsV1(api_token="my-token")
        assert cred.get_header() == {"Authorization": "Bearer my-token"}

    def test_get_header_with_none_token(self):
        cred = CredentialsV1()
        assert cred.get_header() == {"Authorization": "Bearer None"}

    def test_get_json_body_returns_none(self):
        cred = CredentialsV1(api_token="tok")
        assert cred.get_json_body() is None

    def test_get_api_token(self):
        cred = CredentialsV1(api_token="secret")
        assert cred.get_api_token() == "secret"

    def test_verify_token_calls_http(self):
        http = MagicMock()
        cred = CredentialsV1(api_token="jwt-token")
        cred.verify_token(http)

        http.request.assert_called_once_with(
            "POST",
            "authentication",
            json={"strategy": "jwt", "accessToken": "jwt-token"},
        )

    def test_verify_token_propagates_http_error(self):
        http = MagicMock()
        http.request.side_effect = Exception("connection refused")
        cred = CredentialsV1(api_token="bad")

        with pytest.raises(Exception, match="connection refused"):
            cred.verify_token(http)

    def test_set_token_from_credentials_not_implemented(self):
        cred = CredentialsV1(api_token="tok")
        with pytest.raises(NotImplementedError):
            cred.set_token_from_credentials("user", "pass")


# --- CredentialsV2 ---

class TestCredentialsV2:

    def test_get_header(self):
        cred = CredentialsV2(api_token="v2-token")
        assert cred.get_header() == {"Authorization": "Bearer v2-token"}

    def test_get_json_body_returns_none(self):
        cred = CredentialsV2(api_token="tok")
        assert cred.get_json_body() is None

    def test_get_api_token(self):
        cred = CredentialsV2(api_token="v2-secret")
        assert cred.get_api_token() == "v2-secret"

    def test_verify_token_is_noop(self):
        http = MagicMock()
        cred = CredentialsV2(api_token="v2-token")
        cred.verify_token(http)
        http.request.assert_not_called()

    def test_set_token_from_credentials_not_implemented(self):
        cred = CredentialsV2(api_token="tok")
        with pytest.raises(NotImplementedError):
            cred.set_token_from_credentials("user", "pass")
