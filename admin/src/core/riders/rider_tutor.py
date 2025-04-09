"""
Este módulo define el modelo `RiderTutor`, que representa la relación 
entre un jinete (Rider) y un tutor (Tutor) en la base de datos. 
Contiene información sobre la identificación del jinete y el tutor, 
el parentesco y si el tutor es el principal.
"""

from src.core.database import db

# Para asegurar que se cargue primero la tabla Tutores
from src.core.riders.tutor import Tutor


class RiderTutor(db.Model):
    """Modelo que representa la relación entre un jinete y un tutor."""

    __tablename__ = "rider_tutor"

    id = db.Column(db.Integer, primary_key=True)

    rider_id = db.Column(
        db.Integer, db.ForeignKey("riders.id", ondelete="CASCADE"), nullable=False
    )
    tutor_id = db.Column(
        db.Integer, db.ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False
    )
    kinship = db.Column(db.String(30), nullable=False)
    is_primary = db.Column(db.Boolean, nullable=False, default=True)

    # Relaciones con las tablas
    rider = db.relationship("Rider", back_populates="tutors")
    tutor = db.relationship(Tutor, back_populates="riders")
