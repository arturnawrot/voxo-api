from dataclasses import dataclass


@dataclass
class CallRecording:
    mediaURL: str
    time: str
    tenantId: int
    direction: str
    callerIdNum: str
    callerIdName: str
    duration: int
    dialedNum: str
    uniqueId: str
