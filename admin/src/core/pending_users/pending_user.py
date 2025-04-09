from datetime import datetime

from src.core.database import db


class PendingUser(db.Model):
    """
    Modelo que representa a los usuarios pendientes de registro en el sistema.
    (Se registraron por Google)

    Atributos:
        id (int): Identificador único del usuario pendiente.
        email (str): Dirección de correo electrónico del usuario pendiente.
        registered_at (datetime): Fecha y hora en que el usuario fue registrado como pendiente.
    """

    __tablename__ = "pending_users"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Email de usuario pendiente: {self.email}"

    def registered_date(self) -> str:
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

        day_of_week = days_of_week[self.registered_at.weekday()]  # type: ignore
        day = self.registered_at.day
        month = months_of_year[self.registered_at.month - 1]  # type: ignore
        year = self.registered_at.year

        return f"{day_of_week} {day} de {month} del {year}"
