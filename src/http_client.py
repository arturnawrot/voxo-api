import logging

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class HttpClient:

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
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
