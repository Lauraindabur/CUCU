from __future__ import annotations

from ..dto import UserDTO


class GetUserProfileUseCase:
    def execute(self, *, user) -> UserDTO:
        return UserDTO.from_model(user)