"""
Módulo de trabajo institucional.

Este módulo define la clase `InstitutionalWork`, que representa los 
trabajos institucionales y su relación con los jinetes y empleados 
en la base de datos.

Clases:
- InstitutionalWork: Modelo de SQLAlchemy que almacena la información 
  sobre los trabajos institucionales, incluyendo la propuesta, 
  las sedes, los días de operación y las relaciones con empleados y 
  caballos.

Uso:
- Crear instancias de InstitutionalWork para gestionar los trabajos 
  institucionales y su asociación con los jinetes y empleados.
"""

from src.core.database import db


class InstitutionalWork(db.Model):
    """Modelo de SQLAlchemy para los trabajos institucionales."""

    __tablename__ = "institutional_works"

    id = db.Column(db.Integer, primary_key=True)
    proposal = db.Column(db.String(50), nullable=False)
    headquarters = db.Column(db.String(100), nullable=False)
    monday = db.Column(db.Boolean, nullable=False, default=False)
    tuesday = db.Column(db.Boolean, nullable=False, default=False)
    wednesday = db.Column(db.Boolean, nullable=False, default=False)
    thursday = db.Column(db.Boolean, nullable=False, default=False)
    friday = db.Column(db.Boolean, nullable=False, default=False)
    saturday = db.Column(db.Boolean, nullable=False, default=False)
    sunday = db.Column(db.Boolean, nullable=False, default=False)

    # Foreign keys
    teacher_therapist_id = db.Column(
        db.Integer, db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=True
    )
    horse_conductor_id = db.Column(
        db.Integer, db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=True
    )
    track_assistant_id = db.Column(
        db.Integer, db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=True
    )
    horse_id = db.Column(db.Integer, db.ForeignKey("horses.id"), nullable=True)

    # Relaciones con otras tablas
    rider = db.relationship("Rider", back_populates="institutional_work", uselist=False)
    teacher_therapist = db.relationship("Employee", foreign_keys=[teacher_therapist_id])
    horse_conductor = db.relationship("Employee", foreign_keys=[horse_conductor_id])
    track_assistant = db.relationship("Employee", foreign_keys=[track_assistant_id])
    horses = db.relationship(
        "Horse", back_populates="institutional_works", uselist=False
    )
