"""
módulo de documentos de jinetes

Este módulo define la clase `RiderDocument`, que representa los 
documentos asociados a los jinetes en la base de datos. Almacena 
información sobre el título, tipo de documento, y fechas de 
creación y actualización.

Clase:
- RiderDocument: Modelo de SQLAlchemy que almacena información 
  sobre documentos de jinetes, incluyendo título, tipo de 
  documento, formato y su origen.

Métodos:
- readable_created_date: Devuelve la fecha de creación en un 
  formato legible para humanos.
"""

from datetime import datetime

from src.core.database import db


class RiderDocument(db.Model):
    """Modelo de SQLAlchemy para los documentos de los jinetes."""

    __tablename__ = "rider_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    rider_id = db.Column(
        db.Integer, db.ForeignKey("riders.id", ondelete="CASCADE"), nullable=False
    )

    # Relación
    rider = db.relationship("Rider", back_populates="documents")

    def readable_created_date(self) -> str:
        """
        Devuelve la fecha de subida en formato:
        [Día de semana] [Número] de [Mes] del [Año]

        Ejemplo:
        "Domingo 5 de marzo del 2023"
        """
        days_of_week = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]
        months_of_year = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]

        day_of_week = days_of_week[self.created_at.weekday()]  # type: ignore
        day = self.created_at.day
        month = months_of_year[self.created_at.month - 1]  # type: ignore
        year = self.created_at.year

        return f"{day_of_week} {day} de {month} del {year}"
