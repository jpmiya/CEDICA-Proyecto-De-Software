from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Table

from src.core.database import db


# Tabla intermedia para la relación muchos a muchos entre caballos y empleados
horse_employee = Table(
    "horse_employee",
    db.Model.metadata,
    Column(
        "horse_id",
        Integer,
        ForeignKey("horses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "employee_id",
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    extend_existing=True,
)


class Horse(db.Model):
    """
    Modelo que representa a un caballo en el sistema.

    Atributos:
        id (int): Identificador único del caballo.
        name (str): Nombre del caballo.
        birth_date (date): Fecha de nacimiento del caballo.
        gender (str): Género del caballo.
        breed (str): Raza del caballo.
        fur (str): Tipo de pelaje del caballo.
        acquisition_type (str): Tipo de adquisición del caballo (compra o donación).
        entry_date (date): Fecha de ingreso del caballo.
        sede (str): Sede donde se encuentra el caballo.
        rider_type (str): Tipo de jinete asignado al caballo.
        active (bool): Estado del caballo (activo o inactivo).
        trainer_id (int): ID del entrenador asignado al caballo.
        conductor_id (int): ID del conductor asignado al caballo.
    """

    __tablename__ = "horses"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)  # Raza
    fur = db.Column(db.String(100), nullable=False)  # Pelaje
    acquisition_type = db.Column(
        db.String(100), nullable=False
    )  # Tipo de adquisición (compra o donación)
    entry_date = db.Column(db.Date, default=datetime.now)
    sede = db.Column(db.String(100), nullable=False)
    rider_type = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True)

    trainer_id = db.Column(
        db.Integer, db.ForeignKey("employees.id"), nullable=False
    )  # Un solo entrenador
    conductor_id = db.Column(
        db.Integer, db.ForeignKey("employees.id"), nullable=False
    )  # Un solo conductor

    # Relaciones con otros modelos
    documents = db.relationship("HorseDocument", backref="horse", lazy=True)
    institutional_works = db.relationship("InstitutionalWork", back_populates="horses")

    def __repr__(self):
        """
        Representación del objeto Horse para facilitar su depuración.

        Devuelve:
            str: Representación del caballo con detalles clave.
        """
        return f"<Horse {self.name} - {self.breed} - {self.active}>"
