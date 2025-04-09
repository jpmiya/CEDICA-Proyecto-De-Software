from datetime import datetime

from src.core.database import db


class Employee(db.Model):
    """Modelo de un empleado en el sistema"""

    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(12), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(), nullable=False)
    telephone = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    job_position = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, default=datetime.now)
    end_date = db.Column(db.Date, nullable=True)
    emergency_contact_name = db.Column(db.String(100), nullable=False)
    emergency_contact_num = db.Column(db.String(100), nullable=False)
    social_insurance = db.Column(db.String(100), nullable=False)
    affiliate_num = db.Column(db.String(20), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Relaciones con otras tablas
    charges = db.relationship("Charge", back_populates="employee")
    documents = db.relationship("EmployeeDocument", backref="employee", lazy=True)

    def is_in_institutional_work(self):
        """Verifica si el empleado está asociado a alguna entrada de InstitutionalWork."""
        # Importación local para evitar importación circular
        from src.core.riders.institutional_work import InstitutionalWork

        return (
            db.session.query(InstitutionalWork)
            .filter(
                (InstitutionalWork.teacher_therapist_id == self.id)
                | (InstitutionalWork.horse_conductor_id == self.id)
                | (InstitutionalWork.track_assistant_id == self.id)
            )
            .first()
            is not None
        )

    def format_date_in_spanish(self, date):
        """
        Formatea una fecha en español al estilo: 'Día de la semana día/mes/año'.

        Args:
            date (datetime): Fecha a formatear.

        Returns:
            str: Fecha formateada en español, o None si la fecha no es válida.
        """
        if date:
            return f"{date.day}/{date.month}/{date.year}"

        return None

    @property
    def get_readable_creation_date(self):
        """
        Devuelve la fecha de creación en formato legible en español.

        Returns:
            str: Fecha de creación en formato legible o None si no existe.
        """
        return self.format_date_in_spanish(self.start_date)

    def __repr__(self):
        return f"Empleado {self.name} {self.last_name}"
