from datetime import datetime

from sqlalchemy import Enum

from src.core.database import db


class Publication(db.Model):
    """
    Modelo que representa una publicación en el sistema.

    Atributos:
        id (int): Identificador único de la publicación.
        publication_date (date): Fecha de publicación.
        creation_date (date): Fecha de creación de la publicación.
        update_date (date): Fecha de última actualización de la publicación.
        title (str): Título de la publicación.
        summary (str): Resumen de la publicación.
        content (str): Contenido de la publicación.
        author_id (int): ID del autor de la publicación, clave foránea que
            referencia al modelo `User`.
        state (str): Estado de la publicación.
    """

    __tablename__ = "publications"

    id = db.Column(db.Integer, primary_key=True)
    publication_date = db.Column(db.Date, nullable=True)
    creation_date = db.Column(db.Date, default=datetime.now, nullable=False)
    update_date = db.Column(db.Date, onupdate=datetime.now, nullable=True)
    title = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(1000), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    state = db.Column(
        Enum("Borrador", "Publicado", "Archivado", name="state_enum"), nullable=False
    )

    def __repr__(self) -> str:
        return f"Publicación {self.title}"
