from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar
from urllib.parse import urljoin

from voxo_api.constants import BASE_URL
from voxo_api.credentials import Credentials
from voxo_api.enums import HttpMethod

if TYPE_CHECKING:
    from voxo_api.base_api_client import BaseApiClient

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AbstractService(ABC, Generic[T]):

    def __init__(self, api_client: BaseApiClient) -> None:
        self.api_client = api_client
        self.http = api_client.http

    @abstractmethod
    def get_credentials_class(self) -> type[Credentials]:
        pass

    @abstractmethod
    def get_method(self) -> HttpMethod:
        pass

    @abstractmethod
    def get_url_path(self) -> str:
        pass

    @abstractmethod
    def get_response_type(self) -> type[T]:
        pass

    def get_uri_parameters(self, **kwargs) -> str:
        return ""

    def get_body(self, **kwargs) -> dict | None:
        return None

    def get_headers(self, **kwargs) -> dict:
        return {}

    def get_credentials(self) -> Credentials:
        credentials_class = self.get_credentials_class()
        cred = next(
            (c for c in self.api_client.credentials if isinstance(c, credentials_class)),
            None,
        )
        if cred is None:
            raise LookupError(f"No credentials of type '{credentials_class.__name__}' found")
        return cred

    def _build_url(self, uri_params: str) -> str:
        path = self.get_url_path().strip("/")
        if uri_params:
            path = f"{path}/{uri_params.strip('/')}"
        return urljoin(BASE_URL.rstrip("/") + "/", path)

    def _build_headers(self, credentials: Credentials, **kwargs) -> dict:
        headers = self.get_headers(**kwargs)
        cred_headers = credentials.get_header()
        if cred_headers:
            headers = {**cred_headers, **headers}
        return headers

    def _build_body(self, credentials: Credentials, **kwargs) -> dict | None:
        json_body = self.get_body(**kwargs)
        cred_body = credentials.get_json_body()
        if json_body and cred_body:
            return {**cred_body, **json_body}
        return json_body or cred_body

    def _parse_response(self, response) -> T:
        response_type = self.get_response_type()
        try:
            data = response.json()
        except ValueError as exc:
            raise ValueError(
                f"Expected JSON response from {self.get_url_path()}, "
                f"got Content-Type: {response.headers.get('Content-Type')}"
            ) from exc

        try:
            return response_type(**data)
        except TypeError as exc:
            raise TypeError(
                f"Failed to deserialize response into {response_type.__name__}: {exc}"
            ) from exc

    def execute(self, **kwargs) -> T:
        credentials = self.get_credentials()
        headers = self._build_headers(credentials, **kwargs)
        json_body = self._build_body(credentials, **kwargs)
        uri_params = self.get_uri_parameters(**kwargs)
        url = self._build_url(uri_params)

        logger.debug("Executing %s %s", self.get_method(), url)

        response = self.http.request(
            self.get_method(), url, headers=headers, json=json_body
        )
        return self._parse_response(response)
