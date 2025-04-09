"""
Este módulo define el modelo Rider, que representa a un jinete en el sistema.
Contiene información personal, detalles de tutores y relaciones con otros modelos,
como beneficios, discapacidades, seguros, instituciones educativas y documentos del jinete.
"""

from typing import Optional

from src.core.database import db
from src.core.charges.charge import Charge
from src.core.riders.benefits import Benefits
from src.core.riders.disability import Disability
from src.core.riders.insurance import Insurance
from src.core.riders.institutional_work import InstitutionalWork
from src.core.riders.rider_document import RiderDocument
from src.core.riders.rider_tutor import RiderTutor
from src.core.riders.school import School
from src.core.riders.tutor import Tutor


class Rider(db.Model):
    """Modelo que representa a un jinete con información personal, tutores y
    relaciones a otros modelos."""

    __tablename__ = "riders"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    province_address = db.Column(db.String(100), nullable=False)
    locality_address = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    house_num = db.Column(db.Integer, nullable=False)
    dpto = db.Column(db.String(3), nullable=True)

    actual_tel = db.Column(db.String(10), nullable=False)
    emergency_contact_name = db.Column(db.String(50), nullable=False)
    emergency_contact_tel = db.Column(db.String(10), nullable=False)
    scholarship_holder = db.Column(db.Boolean, nullable=False)
    rider_observations = db.Column(db.String(256), nullable=True)
    inserted_at = db.Column(db.Date, nullable=False, default=db.func.now())
    has_debt = db.Column(db.Boolean, nullable=False, default=False)
    condition = db.Column(db.Boolean, nullable=False, default=True)

    # Claves foráneas
    disability_id = db.Column(
        db.Integer, db.ForeignKey("disabilities.id"), unique=True, nullable=True
    )
    benefit_id = db.Column(
        db.Integer, db.ForeignKey("benefits.id"), unique=True, nullable=True
    )
    insurance_id = db.Column(
        db.Integer, db.ForeignKey("insurances.id"), unique=True, nullable=True
    )
    school_id = db.Column(
        db.Integer, db.ForeignKey("schools.id"), unique=True, nullable=True
    )
    institutional_work_id = db.Column(
        db.Integer, db.ForeignKey("institutional_works.id"), unique=True, nullable=True
    )

    # Relaciones con otros modelos
    disability = db.relationship(Disability, back_populates="rider")
    benefits = db.relationship(Benefits, back_populates="rider")
    insurance = db.relationship(Insurance, back_populates="rider")
    school = db.relationship(School, back_populates="rider")
    tutors = db.relationship(RiderTutor, back_populates="rider")
    institutional_work = db.relationship(InstitutionalWork, back_populates="rider")
    charges = db.relationship(
        Charge, back_populates="rider", cascade="all, delete-orphan"
    )
    documents = db.relationship(
        RiderDocument, back_populates="rider", cascade="all, delete-orphan"
    )

    @property
    def primary_tutor(self) -> Optional[Tutor]:
        """Obtiene el tutor primario."""
        return next((tutor.tutor for tutor in self.tutors if tutor.is_primary), None)

    @property
    def secondary_tutor(self) -> Optional[Tutor]:
        """Obtiene el tutor secundario."""
        return next(
            (tutor.tutor for tutor in self.tutors if not tutor.is_primary), None
        )

    def __repr__(self):
        return f"Amazona/Jinete => Nombre: {self.name} ; Apellido: {self.last_name}"
