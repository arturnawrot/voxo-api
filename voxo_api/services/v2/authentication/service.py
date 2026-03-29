from voxo_api.credentials import Credentials, NoAuth
from voxo_api.enums import HttpMethod
from voxo_api.services.v2.authentication.model import AuthResponse
from voxo_api.services.abstract_service import AbstractService


class CreateAccessToken(AbstractService[AuthResponse]):

    def get_credentials_class(self) -> type[Credentials]:
        return NoAuth

    def get_method(self) -> HttpMethod:
        return HttpMethod.POST

    def get_url_path(self) -> str:
        return "v2/authentication"

    def get_response_type(self) -> type[AuthResponse]:
        return AuthResponse

    def get_body(self, email: str, password: str, **kwargs) -> dict:
        return {
            "email": email,
            "password": password,
        }
