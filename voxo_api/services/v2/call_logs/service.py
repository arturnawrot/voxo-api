from typing import Optional

from voxo_api.credentials import Credentials, CredentialsV2
from voxo_api.enums import HttpMethod
from voxo_api.services.v2.call_logs.model import CallLogsResponse
from voxo_api.services.abstract_service import AbstractService


class CallLogs(AbstractService[CallLogsResponse]):

    def get_credentials_class(self) -> type[Credentials]:
        return CredentialsV2

    def get_method(self) -> HttpMethod:
        return HttpMethod.POST

    def get_url_path(self) -> str:
        return "v2/admin/reporting/calls/logs"

    def get_response_type(self) -> type[CallLogsResponse]:
        return CallLogsResponse

    def get_body(
        self,
        tenant_id: int,
        start_date: str,
        end_date: str,
        direction: Optional[str] = None,
        tag: Optional[list[str]] = None,
        users: Optional[list[str] | str] = None,
        groups: Optional[list[dict]] = None,
        call_outcome: Optional[list[int]] = None,
        page: Optional[int] = None,
        records_per_page: Optional[int] = None,
        cid_num: Optional[str] = None,
        report_type: Optional[str] = None,
        **kwargs,
    ) -> dict:
        body: dict = {
            "tenantId": tenant_id,
            "startDate": start_date,
            "endDate": end_date,
        }
        if direction is not None:
            body["direction"] = direction
        if tag is not None:
            body["tag"] = tag
        if users is not None:
            body["users"] = users
        if groups is not None:
            body["groups"] = groups
        if call_outcome is not None:
            body["callOutcome"] = call_outcome
        if page is not None:
            body["page"] = page
        if records_per_page is not None:
            body["recordsPerPage"] = records_per_page
        if cid_num is not None:
            body["cidNum"] = cid_num
        if report_type is not None:
            body["reportType"] = report_type
        return body
