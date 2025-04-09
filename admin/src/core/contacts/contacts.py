from datetime import datetime
from src.core.database import db


class Contact(db.Model):
    """
    Modelo de base de datos para gestionar contactos.

    Atributos:
        id (int): Identificador único del contacto.
        state (str): Estado del contacto ('pendiente', 'en proceso', 'terminado').
        comment (str): Comentario opcional sobre el contacto.
        creation_date (date): Fecha de creación del contacto.
        closed_date (date): Fecha en la que se cerró el contacto.
        title (str): Título del contacto.
        full_name (str): Nombre completo del remitente.
        email (str): Correo electrónico del remitente.
        message (str): Mensaje asociado al contacto.
    """

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(
        db.Enum("pendiente", "en proceso", "terminado", name="contact_state"),
        nullable=False,
    )
    comment = db.Column(db.String(256), nullable=True)
    creation_date = db.Column(db.Date, default=datetime.now())
    closed_date = db.Column(db.Date, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Diccionarios para días de la semana y meses en español
    DAYS = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }
    MONTHS = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    def format_date_in_spanish(self, date):
        """
        Formatea una fecha en español al estilo: 'Día de la semana día/mes/año'.

        Args:
            date (datetime): Fecha a formatear.

        Returns:
            str: Fecha formateada en español, o None si la fecha no es válida.
        """
        if date:
            day_name = self.DAYS[
                date.weekday()
            ]  # Obtiene el nombre del día de la semana

            return f"{day_name} {date.day}/{date.month}/{date.year}"
        return None

    @property
    def get_readable_creation_date(self):
        """
        Devuelve la fecha de creación en formato legible en español.

        Returns:
            str: Fecha de creación en formato legible o None si no existe.
        """
        return self.format_date_in_spanish(self.creation_date)

    @property
    def get_readable_closed_date(self):
        """
        Devuelve la fecha de cierre en formato legible en español.

        Returns:
            str: Fecha de cierre en formato legible o None si no existe.
        """
        return self.format_date_in_spanish(self.closed_date)
