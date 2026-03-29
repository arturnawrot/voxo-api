from voxo_api.credentials import Credentials
from voxo_api.http_client import HttpClient


class BaseApiClient:

    def __init__(self, credentials: list[Credentials], http: HttpClient | None = None) -> None:
        self.http = http or HttpClient()
        self.credentials = credentials
        self._verify_credentials()

    def _verify_credentials(self) -> None:
        for cred in self.credentials:
            if cred.api_token is not None:
                cred.verify_token(self.http)

    def add_credentials(self, credentials: Credentials) -> None:
        if credentials.api_token is not None:
            credentials.verify_token(self.http)
        self.credentials.append(credentials)
