import logging
from typing import Optional
from django.contrib.auth import get_user_model
from users.domain.repositories import UserRepository, ProfileDict

logger = logging.getLogger("eu.profile")  # outro logger

class ProfileService(UserRepository):
    def get_profile(self, user_id: int) -> Optional[ProfileDict]:
        logger.info("DB_HIT get_profile user_id=%s", user_id)  # <-- prova do acesso ao banco
        User = get_user_model()
        try:
            u = User.objects.only("id","username","email","first_name","last_name").get(pk=user_id)
        except User.DoesNotExist:
            return None
        return ProfileDict(
            id=u.id,
            username=u.username,
            email=u.email or "",
            first_name=u.first_name or "",
            last_name=u.last_name or "",
        )
