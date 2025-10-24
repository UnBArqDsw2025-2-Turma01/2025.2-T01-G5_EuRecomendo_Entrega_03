from typing import List
from users.domain.repositories import UserRepository, ProfileDict

class RecommendationService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_recommendations(self, user_id: int) -> List[str]:
        profile: ProfileDict | None = self.user_repo.get_profile(user_id)
        if not profile:
            return []
        return [f"Livro recomendado para {profile['username']} #{i}" for i in range(1, 4)]
