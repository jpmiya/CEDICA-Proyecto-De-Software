from src.core.database import db


class Permission(db.Model):
    """Modelo de un Permiso en el sistema.

    Representa un permiso que puede ser asignado a roles en el sistema. Cada
    permiso tiene un nombre y está relacionado con los roles a los que se
    asigna a través de la tabla intermedia 'role_permission'.
    """

    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roles = db.relationship(
        "Role", secondary="role_permission", back_populates="permissions", lazy=True
    )

    def __repr__(self):
        return f"{self.name}"
