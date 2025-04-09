from datetime import datetime

from src.core.database import db


user_roles = db.Table(
    "user_roles",
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(db.Model):
    """Modelo de instancia de un usuario de CEDICA"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)
    alias = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    inserted_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    system_admin = db.Column(db.Boolean, nullable=False, default=False)
    google_logged = db.Column(db.Boolean, nullable=False, default=False)

    roles = db.relationship(
        "Role", secondary="user_roles", back_populates="users", lazy=True
    )
