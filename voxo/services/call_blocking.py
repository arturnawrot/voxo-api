from voxo.credentials import Credentials, CredentialsV1
from voxo.models.call_blocking import CallBlockingRecord
from voxo.services.abstract_service import AbstractService


class CallBlocking(AbstractService[CallBlockingRecord]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV1

    def get_method(self) -> str:
        return "GET"

    def get_url_path(self) -> str:
        return "call-blocking"

    def get_response_type(self) -> type[CallBlockingRecord]:
        return CallBlockingRecord

    def get_uri_parameters(self, blocking_id: int, **kwargs) -> str:
        return str(blocking_id)
