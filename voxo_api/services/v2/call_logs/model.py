from dataclasses import dataclass, fields
from typing import Optional


@dataclass
class CallLogRecord:
    callId: str
    startTime: str
    direction: str
    endTime: str
    cidNum: str
    cidName: str
    dialedNum: str
    dialedName: str
    disposition: str
    recorded: int
    isTollFree: int
    isInternational: int
    presented: int
    tag: Optional[str]
    outcome: Optional[int]
    outcomeName: Optional[str]
    geolocation: Optional[str] = None
    queueCall: Optional[int] = None
    mos: Optional[float] = None
    uniqueId: Optional[str] = None
    answeredAt: Optional[str] = None
    isTransferred: Optional[int] = None


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
