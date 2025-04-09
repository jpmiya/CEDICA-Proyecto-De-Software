"""
módulo discapacidades

Este módulo define las clases `DisabilityType` y `Disability`, que 
representan los tipos de discapacidad y la información relacionada con 
las discapacidades de los jinetes, respectivamente.

Clases:
- DisabilityType: Modelo de SQLAlchemy que define los tipos de 
  discapacidad disponibles.
- Disability: Modelo de SQLAlchemy que almacena información sobre 
  las discapacidades de los jinetes, incluyendo diagnósticos y 
  certificados.

Uso:
- Crear instancias de DisabilityType para almacenar diferentes tipos 
  de discapacidad.
- Crear instancias de Disability para vincular un jinete con su 
  discapacidad y su tipo correspondiente.
"""

from src.core.database import db


class DisabilityType(db.Model):
    """Modelo de SQLAlchemy para los tipos de discapacidad."""

    __tablename__ = "disability_type"

    id = db.Column(db.Integer, primary_key=True)
    mental = db.Column(db.Boolean, nullable=False, default=False)
    motora = db.Column(db.Boolean, nullable=False, default=False)
    sensorial = db.Column(db.Boolean, nullable=False, default=False)
    visceral = db.Column(db.Boolean, nullable=False, default=False)

    disability = db.relationship(
        "Disability", back_populates="disability_type", uselist=False
    )


class Disability(db.Model):
    """Modelo de SQLAlchemy para almacenar información sobre discapacidades."""

    __tablename__ = "disabilities"

    id = db.Column(db.Integer, primary_key=True)
    disability_certificate = db.Column(db.Boolean, nullable=False)
    diagnosis = db.Column(db.String(100), nullable=True)
    other_diagnosis = db.Column(db.String(100), nullable=True)
    disability_type_fk = db.Column(
        db.Integer, db.ForeignKey("disability_type.id"), unique=True, nullable=True
    )

    # Relaciones
    rider = db.relationship("Rider", back_populates="disability", uselist=False)
    disability_type = db.relationship(
        "DisabilityType", back_populates="disability", uselist=False
    )
