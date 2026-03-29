from dataclasses import dataclass, fields


@dataclass
class User:
    id: int
    email: str
    userRole: int
    avatarPath: str
    avatarThumbnailPath: str
    tenantId: int
    partnerId: int
    timezone: str
    coverPhoto: str
    darkMode: int
    mobileDarkMode: int
    otp: str
    mfaEnabled: int
    mfaMode: str
    mfaPhoneNumber: str
    mfaSmsVerified: int
    mfaAppSecret: str
    mfaAppVerified: int
    mfaEmailVerified: int
    title: str
    enableCallNotifications: int
    enableChatNotifications: int
    enableTextNotifications: int
    extId: int
    extName: str
    extNum: str
    dnd: str
    outboundRecord: str
    peerName: str
    peerSecret: str
    enableMeetings: int
    branchId: int
    branchName: str


@dataclass
class AuthResponse:
    accessToken: str
    user: User

    def __post_init__(self):
        if isinstance(self.user, dict):
            known = {f.name for f in fields(User)}
            self.user = User(**{k: v for k, v in self.user.items() if k in known})
