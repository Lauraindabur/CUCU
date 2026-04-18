from __future__ import annotations

from .models import User


class DjangoUserRepository:
    def exists_by_email(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def get_by_email(self, email: str) -> User | None:
        return User.objects.filter(email=email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return User.objects.filter(id=user_id).first()

    def create_user(self, *, nombre: str, email: str, password: str) -> User:
        user = User(
            username=email,
            email=email,
            nombre=nombre,
        )
        user.set_password(password)
        user.save()
        return user

    def update_password(self, *, user: User, password: str) -> User:
        user.set_password(password)
        user.save(update_fields=["password"])
        return user