from dataclasses import dataclass, fields
from typing import Optional


@dataclass
class CallLogRecord:
    callId: str
    startTime: str
    direction: str
    endTime: str
    cidNumber: str
    cidName: str
    dialedNumber: str
    dialedName: str
    disposition: str
    queueCall: int
    recorded: int
    isTollFree: int
    isInternational: int
    presented: int
    mos: float
    geolocation: str
    uniqueId: str
    answeredAt: str
    isTransferred: int
    tag: Optional[str]
    outcome: Optional[int]
    outcomeName: Optional[str]


@dataclass
class CallLogsResponse:
    records: list
    total: int
    page: int
    maxPage: int

    def __post_init__(self):
        known_fields = {f.name for f in fields(CallLogRecord)}
        self.records = [
            CallLogRecord(**{k: v for k, v in r.items() if k in known_fields})
            for r in self.records
        ]
