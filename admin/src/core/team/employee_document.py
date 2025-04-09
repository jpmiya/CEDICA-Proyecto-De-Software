from datetime import datetime
from pathlib import Path

from src.core.database import db


class EmployeeDocument(db.Model):
    """Modelo de una instancia de un documento de un empleado"""

    __tablename__ = "employee_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)

    def get_file_type(self):
        """
        Devuelve la extensión del tipo de archivo. Si es un enlace devuelve
        Enlace
        """
        if self.format == "file":
            return Path(self.source).suffix[1:]

        return "Enlace"
