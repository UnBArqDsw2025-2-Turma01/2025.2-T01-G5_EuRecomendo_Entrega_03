from typing import Protocol, TypedDict, Optional

class ProfileDict(TypedDict, total=False):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

class UserRepository(Protocol):
    def get_profile(self, user_id: int) -> Optional[ProfileDict]: ...
