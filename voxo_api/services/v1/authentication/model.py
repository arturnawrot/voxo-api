from dataclasses import dataclass


@dataclass
class AuthResponse:
    accessToken: str
    authentication: dict
    user: dict
