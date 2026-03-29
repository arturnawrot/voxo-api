from voxo_api.credentials import Credentials, CredentialsV2
from voxo_api.enums import HttpMethod
from voxo_api.services.v2.call_recordings.model import CallRecording
from voxo_api.services.abstract_service import AbstractService


class CallRecordingByCallId(AbstractService[CallRecording]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV2

    def get_method(self) -> HttpMethod:
        return HttpMethod.GET

    def get_url_path(self) -> str:
        return "v2/admin/call-recordings"

    def get_response_type(self) -> type[CallRecording]:
        return CallRecording

    def get_uri_parameters(self, call_id: str, **kwargs) -> str:
        return call_id

    def get_headers(self, **kwargs) -> dict:
        return {"Accept": "application/json"}
