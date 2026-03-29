from voxo_api.credentials import Credentials, CredentialsV1
from voxo_api.enums import HttpMethod
from voxo_api.services.call_blocking.model import CallBlockingRecord
from voxo_api.services.abstract_service import AbstractService


class CallBlocking(AbstractService[CallBlockingRecord]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV1

    def get_method(self) -> HttpMethod:
        return HttpMethod.GET

    def get_url_path(self) -> str:
        return "call-blocking"

    def get_response_type(self) -> type[CallBlockingRecord]:
        return CallBlockingRecord

    def get_uri_parameters(self, blocking_id: int, **kwargs) -> str:
        return str(blocking_id)
