from voxo_api.credentials import Credentials, CredentialsV2
from voxo_api.enums import HttpMethod
from voxo_api.services.v2.provisioned_numbers.model import ProvisionedNumbersResponse
from voxo_api.services.abstract_service import AbstractService


class GetProvisionedNumbers(AbstractService[ProvisionedNumbersResponse]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV2

    def get_method(self) -> HttpMethod:
        return HttpMethod.GET

    def get_url_path(self) -> str:
        return "v2/messaging/get-provisioned-numbers"

    def get_response_type(self) -> type[ProvisionedNumbersResponse]:
        return ProvisionedNumbersResponse

    def get_headers(self, **kwargs) -> dict:
        return {"Accept": "application/json"}
