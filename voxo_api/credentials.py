from __future__ import annotations

from abc import ABC, abstractmethod

class Credentials(ABC):

    def __init__(self, api_token: str | None = None) -> None:
        self.api_token = api_token

    @abstractmethod
    def get_header(self) -> dict | None:
        pass

    @abstractmethod
    def get_json_body(self) -> dict | None:
        pass

    @abstractmethod
    def get_api_token(self) -> str:
        pass


class NoAuth(Credentials):

    def __init__(self) -> None:
        super().__init__(api_token=None)

    def get_header(self) -> dict | None:
        return None

    def get_json_body(self) -> dict | None:
        return None

    def get_api_token(self) -> str:
        return None


class CredentialsV1(Credentials):

    def get_header(self) -> dict | None:
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_json_body(self) -> dict | None:
        return None

    def get_api_token(self) -> str:
        return self.api_token


class CredentialsV2(Credentials):

    def get_header(self) -> dict | None:
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_json_body(self) -> dict | None:
        return None

    def get_api_token(self) -> str:
        return self.api_token
