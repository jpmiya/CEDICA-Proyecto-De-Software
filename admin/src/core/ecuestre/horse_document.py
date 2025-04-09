from datetime import datetime

from src.core.database import db


class HorseDocument(db.Model):
    """
    Modelo que representa los documentos asociados a un caballo en el sistema.

    Atributos:
        id (int): Identificador único del documento.
        title (str): Título del documento.
        type (str): Tipo del documento (e.g., contrato, ficha médica).
        format (str): Formato del documento (e.g., PDF, JPG).
        source (str): URL o ubicación del documento.
        created_at (datetime): Fecha y hora de creación del documento.
        updated_at (datetime): Fecha y hora de la última actualización del documento.
        horse_id (int): ID del caballo asociado al documento.
    """

    __tablename__ = "horse_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    horse_id = db.Column(db.Integer, db.ForeignKey("horses.id"), nullable=False)

    def __repr__(self):
        """
        Representación textual del documento para depuración.

        Devuelve:
            str: Representación del objeto HorseDocument con detalles clave.
        """
        return (
            f'<HorseDocument title="{self.title}" type="{self.type}" '
            f'format="{self.format}" source="{self.source}">'
        )
