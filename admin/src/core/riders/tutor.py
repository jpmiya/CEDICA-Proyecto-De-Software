"""
Este módulo define el modelo Tutor, que representa a un tutor en el sistema.
Contiene información personal relevante sobre el tutor y su relación con los jinetes.
"""

from src.core.database import db


class Tutor(db.Model):
    """Modelo que representa a un tutor con información personal y de contacto."""

    __tablename__ = "tutors"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    department_number = db.Column(db.String(3), nullable=True)
    phone_number = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    scholarity_level = db.Column(db.String(30), nullable=False)
    occupation = db.Column(db.String(100), nullable=False, default="Desocupad@")

    # Relación con el modelo RiderTutor
    riders = db.relationship("RiderTutor", back_populates="tutor")

    def __repr__(self):
        return (
            f"Tutor => Nombre: {self.name}, Apellido: {self.last_name}, DNI: {self.dni}"
        )
