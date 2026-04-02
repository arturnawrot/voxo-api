from dataclasses import dataclass, fields


@dataclass
class Conversation:
    id: int
    tenantId: int
    createdAt: str
    updatedAt: str
    sourceDID: str
    participants: str
    hidden: int
    name: str
    conversationName: str


@dataclass
class SendSmsResponse:
    createdConversations: list
    postBody: dict
    messageIds: list
    updatedAt: str

    def __post_init__(self):
        known_fields = {f.name for f in fields(Conversation)}
        self.createdConversations = [
            Conversation(**{k: v for k, v in c.items() if k in known_fields})
            for c in self.createdConversations
        ]
