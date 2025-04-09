"""
Este módulo define el modelo School, que representa una escuela en el sistema.
Contiene información relevante sobre la escuela y su relación con los jinetes.
"""

from src.core.database import db


class School(db.Model):
    """Modelo que representa una escuela con información de contacto y observaciones."""

    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    school_observations = db.Column(db.String(256), nullable=True, default="")
    professionals = db.Column(db.String(500), nullable=True, default="")

    # Relaciones con otras tablas
    rider = db.relationship("Rider", back_populates="school", uselist=False)

    def __repr__(self):
        return f"Escuela => Nombre: {self.name}, Dirección: {self.address}"
