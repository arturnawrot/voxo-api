import logging
from urllib.parse import urljoin

import requests

from voxo.constants import BASE_URL

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class HttpClient:

    def __init__(self, base_url: str = BASE_URL, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url, path.lstrip("/"))
        kwargs.setdefault("timeout", self.timeout)

        logger.debug("HTTP %s %s", method, url)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
        except requests.ConnectionError as exc:
            logger.error("Connection failed for %s %s: %s", method, url, exc)
            raise
        except requests.Timeout as exc:
            logger.error("Request timed out for %s %s: %s", method, url, exc)
            raise
        except requests.HTTPError as exc:
            logger.error(
                "HTTP %s for %s %s: %s",
                response.status_code,
                method,
                url,
                response.text[:200],
            )
            raise

        return response
