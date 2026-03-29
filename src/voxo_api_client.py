from voxo_api.base_api_client import BaseApiClient
from voxo_api.credentials import Credentials
from voxo_api.http_client import HttpClient
from voxo_api.service_factory import ServiceFactory


class VoxoApiClient(BaseApiClient):

    def __init__(self, credentials: list[Credentials], http: HttpClient | None = None) -> None:
        self.service_factory = ServiceFactory()
        super().__init__(credentials, http)

    def __getattr__(self, service_name: str):
        service_class = self.service_factory.get_service_class(service_name)
        return service_class(self)
