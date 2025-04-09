"""
Este módulo define la clase `Benefits`, que representa las pensiones
y asignaciones asociadas a los jinetes. También define la enumeración
`PensionType`, que categoriza el tipo de pensión que puede recibir un 
beneficiario.

Clases:
- PensionType: Enum que representa los tipos de pensión (NACIONAL, PROVINCIAL).
- Benefits: Modelo de SQLAlchemy que define los beneficios que un 
  jinete puede tener.

Uso:
- Crear instancias de Benefits para almacenar información sobre 
  beneficios para jinetes.
"""

from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum

from src.core.database import db


class PensionType(Enum):
    """Enum que representa los tipos de pensión."""

    NACIONAL = "Nacional"
    PROVINCIAL = "Provincial"


class Benefits(db.Model):
    """Modelo de SQLAlchemy para almacenar asignaciones y pensiones de jinetes."""

    __tablename__ = "benefits"

    id = db.Column(db.Integer, primary_key=True)
    asignacion_familiar = db.Column(db.Boolean, nullable=False, default=False)
    asignacion_por_hijo = db.Column(db.Boolean, nullable=False, default=False)
    asignacion_por_hijo_con_discapacidad = db.Column(
        db.Boolean, nullable=False, default=False
    )
    asignacion_por_ayuda_escolar = db.Column(db.Boolean, nullable=False, default=False)
    beneficiario_de_pension = db.Column(db.Boolean, nullable=False, default=False)
    naturaleza_pension = db.Column(SQLAlchemyEnum(PensionType), name="pension_type")

    rider = db.relationship("Rider", back_populates="benefits", uselist=False)
