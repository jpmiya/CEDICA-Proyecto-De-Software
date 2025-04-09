"""
Módulo de seguros

Este módulo define la clase `Insurance`, que representa los seguros 
asociados a los jinetes en la base de datos. Almacena información 
sobre el nombre del seguro, el número de afiliado, y detalles 
relacionados con la tutela.

Clases:
- Insurance: Modelo de SQLAlchemy que almacena información sobre 
  los seguros de los jinetes, incluyendo el nombre del seguro, 
  número de afiliado, y observaciones sobre la tutela.

Uso:
- Crear instancias de Insurance para gestionar la información de 
  los seguros de los jinetes.
"""

from src.core.database import db


class Insurance(db.Model):
    """Modelo de SQLAlchemy para los seguros de los jinetes."""

    __tablename__ = "insurances"

    id = db.Column(db.Integer, primary_key=True)
    insurance_name = db.Column(db.String(50), nullable=True, default="No tiene")
    affiliate_number = db.Column(db.String(50), nullable=True)
    has_guardianship = db.Column(db.Boolean, nullable=False, default=False)
    guardianship_observations = db.Column(db.String(256), nullable=True, default="")

    # Relaciones con otras tablas
    rider = db.relationship("Rider", back_populates="insurance", uselist=False)
