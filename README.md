# voxo-api

A Python client library for the [Voxo](https://voxo.co) API. Built around a clean, extensible service pattern - adding new endpoints takes minutes.

> **Note:** This library is a work in progress. Not all Voxo API endpoints are implemented yet. See [Available Services](#available-services) for what's ready, and [Adding a New Service](#adding-a-new-service) for how to contribute the rest - the pattern is straightforward and consistent.

---

## Installation

```bash
git clone https://github.com/arturnawrot/voxo-api
pip install -r requirements.txt
```

Requires Python 3.14+.


## Quick Start

A single client instance can hold credentials for multiple API versions at once. Each service declares which credential type it needs, and the client picks the right one automatically - so you can freely mix `v1` and `v2` calls on the same object.

```python
from voxo_api.voxo_api_client import VoxoApiClient
from voxo_api.credentials import CredentialsV1, CredentialsV2

client = VoxoApiClient(credentials=[
    CredentialsV1(api_token="your-v1-token"),
    CredentialsV2(api_token="your-v2-token"),
])

# Both namespaces work on the same client instance
blocking = client.v1.CallBlocking.execute(blocking_id=42)
logs     = client.v2.CallLogs.execute(tenant_id=1001, start_date="2024-01-01", end_date="2024-01-31")
```

You can also start with no credentials and add them after authenticating (see [Authentication](#authentication)).

---

## Authentication

Most endpoints require an access token. Use `CreateAccessToken` - it needs no prior credentials - then add the result to your client. Since the client holds a list of credentials, you can authenticate against both API versions and use them all from the same instance.

```python
from voxo_api.voxo_api_client import VoxoApiClient
from voxo_api.credentials import CredentialsV1, CredentialsV2

client = VoxoApiClient(credentials=[])

# Authenticate against both versions
v1_auth = client.v1.CreateAccessToken.execute(email="you@example.com", password="secret")
v2_auth = client.v2.CreateAccessToken.execute(email="you@example.com", password="secret")

client.add_credentials(CredentialsV1(api_token=v1_auth.accessToken))
client.add_credentials(CredentialsV2(api_token=v2_auth.accessToken))

# Now both namespaces are ready on the same client
blocking  = client.v1.CallBlocking.execute(blocking_id=1)
recording = client.v2.CallRecordingByCallId.execute(call_id="abc-xyz")
```

### V2 - Validate an existing token

If you already have a V2 token stored somewhere, you can verify it without a full login:

```python
auth = client.v2.AuthenticateAccessToken.execute(access_token="stored-token")
client.add_credentials(CredentialsV2(api_token=auth.accessToken))

print(auth.user.email)   # Typed User dataclass
print(auth.user.extNum)  # Extension number
```

---

## Available Services

Services are organized under `voxo_api/services/v1/` and `voxo_api/services/v2/`. They are auto-discovered at runtime - no registration needed.

### V1 Services (`client.v1.*`)

| Service | Method | Endpoint | Description |
|---|---|---|---|
| `CreateAccessToken` | POST | `/authentication` | Login, returns access token |
| `CallBlocking` | GET | `/call-blocking/{id}` | Fetch a call-blocking record by ID |

### V2 Services (`client.v2.*`)

| Service | Method | Endpoint | Description |
|---|---|---|---|
| `CreateAccessToken` | POST | `/v2/authentication` | Login with email/password |
| `AuthenticateAccessToken` | POST | `/v2/authentication/jwt` | Validate an existing JWT |
| `CallLogs` | POST | `/v2/admin/reporting/calls/logs` | Paginated call log report |
| `CallRecordingByCallId` | GET | `/v2/admin/call-recordings/{call_id}` | Fetch recording by call ID |

---

## Usage Examples

### Fetch Call Blocking Record (V1)

```python
record = client.v1.CallBlocking.execute(blocking_id=99)
# record is a CallBlockingRecord dataclass
print(record.id)        # 99
print(record.callerId)  # "+15551234567"
print(record.reason)    # "spam"
```

### Fetch Call Logs (V2)

```python
logs = client.v2.CallLogs.execute(
    tenant_id=1001,
    start_date="2024-01-01",
    end_date="2024-01-31",
    direction="inbound",        # optional
    page=1,                     # optional
    records_per_page=50,        # optional
)

print(f"{logs.total} total records, page {logs.page} of {logs.maxPage}")
for log in logs.records:
    print(log.callId, log.startTime, log.disposition)
```

### Fetch a Call Recording (V2)

```python
recording = client.v2.CallRecordingByCallId.execute(call_id="abc-123-xyz")
print(recording.mediaURL)    # Direct URL to the audio file
print(recording.duration)    # Duration in seconds
print(recording.direction)   # "inbound" or "outbound"
```

---

## Adding a New Service

Every service follows the same pattern. Here's how to add a new one in a few minutes.

### 1. Create the folder structure

```
voxo_api/services/v1/my_endpoint/
    __init__.py
    model.py
    service.py
```

### 2. Define the response model (`model.py`)

```python
from dataclasses import dataclass

@dataclass
class MyEndpointResponse:
    id: int
    name: str
    status: str
```

### 3. Implement the service (`service.py`)

The four abstract methods are required. The three optional ones - `get_uri_parameters`, `get_body`, and `get_headers` - only need to be overridden if the endpoint uses them. Define whatever named parameters make sense for your endpoint; any arguments passed to `execute()` are forwarded through to all three methods.

```python
from voxo_api.credentials import Credentials, CredentialsV1
from voxo_api.enums import HttpMethod
from voxo_api.services.abstract_service import AbstractService
from .model import MyEndpointResponse


class MyEndpoint(AbstractService[MyEndpointResponse]):

    # --- Required ---

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV1          # or CredentialsV2, NoAuth

    def get_method(self) -> HttpMethod:
        return HttpMethod.GET         # GET, POST, PUT, PATCH, DELETE

    def get_url_path(self) -> str:
        return "my-endpoint"          # path after https://api.voxo.co/

    def get_response_type(self) -> type[MyEndpointResponse]:
        return MyEndpointResponse

    # --- Optional overrides ---

    def get_uri_parameters(self, item_id: int) -> str:
        # Appended to the URL: /my-endpoint/42
        return str(item_id)

    def get_body(self, name: str, active: bool) -> dict:
        # Used as the JSON request body for POST/PUT/PATCH
        return {"name": name, "active": active}

    def get_headers(self) -> dict:
        # Merged on top of the credential auth header
        return {"Accept": "application/json"}
```

The method signatures are yours to define - name the parameters whatever the endpoint actually needs. The base class passes all keyword arguments from `execute()` into each method, so `client.v1.MyEndpoint.execute(item_id=42, name="foo", active=True)` will route correctly.

### 4. Export from `__init__.py`

```python
from voxo_api.services.v1.my_endpoint.service import MyEndpoint
from voxo_api.services.v1.my_endpoint.model import MyEndpointResponse

__all__ = ["MyEndpoint", "MyEndpointResponse"]
```

That's it. The `ServiceFactory` auto-discovers all concrete `AbstractService` subclasses at startup - your new service will be immediately available as `client.v1.MyEndpoint`.

### How the service layer works

When you call `client.v1.MyEndpoint.execute(item_id=42)`, the following happens:

1. **Credentials lookup** - finds the first credential of the type returned by `get_credentials_class()` in the client's credential list. Raises `LookupError` if none match.
2. **URL construction** - combines `BASE_URL`, `get_url_path()`, and `get_uri_parameters(**kwargs)` into a final URL.
3. **Headers** - merges the credential's auth header with anything returned by `get_headers(**kwargs)`. Service headers take precedence on conflict.
4. **Body** - merges the credential's JSON body (if any) with `get_body(**kwargs)`. Service body takes precedence on conflict.
5. **HTTP request** - delegates to `HttpClient.request()` which uses a `requests.Session` and calls `raise_for_status()`.
6. **Deserialization** - calls `response.json()` and unpacks it into the dataclass returned by `get_response_type()`.

---

## Running Tests

```bash
pytest
```

---

## License

MIT
