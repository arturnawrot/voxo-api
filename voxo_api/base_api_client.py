from voxo_api.credentials import Credentials
from voxo_api.http_client import HttpClient


class BaseApiClient:

    def __init__(self, credentials: list[Credentials], http: HttpClient | None = None) -> None:
        self.http = http or HttpClient()
        self.credentials = credentials

    def add_credentials(self, credentials: Credentials) -> None:
        self.credentials.append(credentials)
