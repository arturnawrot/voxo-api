from voxo_api.credentials import Credentials, CredentialsV2
from voxo_api.enums import HttpMethod
from voxo_api.services.v2.messaging.model import SendSmsResponse
from voxo_api.services.abstract_service import AbstractService


class SendSms(AbstractService[SendSmsResponse]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV2

    def get_method(self) -> HttpMethod:
        return HttpMethod.POST

    def get_url_path(self) -> str:
        return "v2/messaging/messages/send-sms"

    def get_response_type(self) -> type[SendSmsResponse]:
        return SendSmsResponse

    def get_body(
        self,
        tenant_id: int,
        to: list[str],
        from_number: str,
        text: str,
        **kwargs,
    ) -> dict:
        return {
            "tenantId": tenant_id,
            "to": to,
            "from": from_number,
            "text": text,
        }
