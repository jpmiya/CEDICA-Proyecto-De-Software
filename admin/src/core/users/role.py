from src.core.database import db


role_permission = db.Table(
    "role_permission",
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "permission_id",
        db.Integer,
        db.ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(db.Model):
    """Modelo de la instancia de un Rol en el sistema.

    Representa un rol que puede ser asignado a usuarios y tiene permisos asociados.
    Cada rol tiene un nombre y una descripción, y está relacionado con los permisos
    y los usuarios a través de las tablas intermedias 'role_permission' y 'user_roles'.
    """

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    permissions = db.relationship(
        "Permission", secondary="role_permission", back_populates="roles", lazy=True
    )

    users = db.relationship(
        "User", secondary="user_roles", back_populates="roles", lazy=True
    )

    def __repr__(self):
        return f" {self.name} >"
