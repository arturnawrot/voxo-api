import pytest

from voxo_api.credentials import Credentials, CredentialsV1, CredentialsV2


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

