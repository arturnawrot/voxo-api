from dataclasses import dataclass


@dataclass
class CallBlockingRecord:
    id: int
    tenantId: int
    callerId: str
    inserted: str
    reason: str
