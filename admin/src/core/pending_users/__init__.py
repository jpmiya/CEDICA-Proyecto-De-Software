from typing import Optional

import sqlalchemy as sa
from sqlalchemy import func

from src.core.database import db
from src.core.pending_users.pending_user import PendingUser
from src.core.users.role import Role
from src.core.users.user import User


def find_pending_user_by_email(email: str) -> Optional[PendingUser]:
    """Encuentra un usuario pendiente por email."""
    email = email.lower()

    return PendingUser.query.filter(func.lower(PendingUser.email) == email).first()


def find_pending_user_by_id(id_pending_user: int) -> Optional[PendingUser]:
    """Encuentra un usuario pendiente por su id."""
    return PendingUser.query.filter_by(id=id_pending_user).first()


def create_pending_user(email: str) -> None:
    """Crea un nuevo usuario pendiente."""
    email_user = email.lower()
    pending_user = PendingUser(email=email_user)
    db.session.add(pending_user)
    db.session.commit()


def accept_pending_user(user_id: int, alias: str) -> None:
    """Acepta un usuario pendiente."""
    pending_user = PendingUser.query.filter_by(id=user_id).first()
    email_new_user: str = pending_user.email
    alias_new_user: str = alias
    password_new_user: str = ""

    user = User(
        email=email_new_user,
        password=password_new_user,
        alias=alias_new_user,
        active=False,
        google_logged=True,
    )

    db.session.add(user)
    user.roles.append(Role.query.filter_by(name="Voluntariado").first())
    db.session.delete(pending_user)
    db.session.commit()


def get_pending_users_ordered_by_email(ascendent: bool):
    """Obtiene usuarios pendientes ordenados por email."""
    if ascendent:
        return sa.select(PendingUser).order_by(PendingUser.email.asc())
    else:
        return sa.select(PendingUser).order_by(PendingUser.email.desc())


def get_pending_users_ordered_by_time(newer_to_older: bool):
    """Obtiene usuarios pendientes ordenados por tiempo de registro."""
    if newer_to_older:
        return sa.select(PendingUser).order_by(PendingUser.registered_at.desc())
    else:
        return sa.select(PendingUser).order_by(PendingUser.registered_at.asc())


def get_pending_users():
    """Obtiene todos los usuarios pendientes."""
    return sa.select(PendingUser).order_by(PendingUser.id.asc())


def delete_pending_user(user: PendingUser) -> None:
    """Elimina un usuario pendiente."""
    db.session.delete(user)
    db.session.commit()
