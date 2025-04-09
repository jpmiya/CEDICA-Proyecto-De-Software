from datetime import datetime

from src.core.database import db


class Payment(db.Model):
    """
    Modelo que representa un pago realizado a un beneficiario.

    Atributos:
        id (int): Identificador único del pago.
        beneficiary_id (int): ID del beneficiario, referencia a la tabla 'employees'.
        amount (float): Monto del pago.
        payment_date (datetime): Fecha en que se realizó el pago.
        payment_type (str): Tipo de pago (ej. efectivo, tarjeta, etc.).
        description (str): Descripción del pago (opcional).
    """

    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.now())
    payment_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Payment {self.amount} - {self.payment_type} - {self.payment_date}>"
