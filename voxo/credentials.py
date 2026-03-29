from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from voxo.http_client import HttpClient


class Credentials(ABC):

    def __init__(self, api_token: str | None = None) -> None:
        self.api_token = api_token

    def verify_token(self, http: HttpClient) -> None:
        pass

    @abstractmethod
    def get_header(self) -> dict | None:
        pass

    @abstractmethod
    def get_json_body(self) -> dict | None:
        pass

    @abstractmethod
    def get_api_token(self) -> str:
        pass


class CredentialsV1(Credentials):

    def verify_token(self, http: HttpClient) -> None:
        http.request(
            "POST",
            "authentication",
            json={"strategy": "jwt", "accessToken": self.api_token},
        )

    def set_token_from_credentials(self, login: str, password: str) -> str:
        # V1 login logic — exchange login/password for a token via HTTP
        raise NotImplementedError

    def get_header(self) -> dict | None:
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_json_body(self) -> dict | None:
        return None

    def get_api_token(self) -> str:
        return self.api_token


class CredentialsV2(Credentials):

    def verify_token(self, http: HttpClient) -> None:
        # V2 token verification logic
        pass

    def set_token_from_credentials(self, login: str, password: str) -> str:
        # V2 login logic — exchange login/password for a token via HTTP
        raise NotImplementedError

    def get_header(self) -> dict | None:
        return {"Authorization": f"Bearer {self.api_token}"}

    def get_json_body(self) -> dict | None:
        return None

    def get_api_token(self) -> str:
        return self.api_token
