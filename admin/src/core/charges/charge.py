from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum

from src.core.database import db


class PaymentMethod(Enum):
    """Enumeración para los métodos de pago disponibles."""

    EFECTIVO = "EFECTIVO"
    TARJETA_CREDITO = "TARJETA_CREDITO"
    TARJETA_DEBITO = "TARJETA_DEBITO"


class Charge(db.Model):
    """
    Modelo que representa un cargo asociado a un jinete (rider).

    Atributos:
        id (int): Identificador único del cargo.
        rider_id (int): ID del jinete asociado al cargo.
        charge_date (datetime): Fecha en que se realizó el cargo.
        payment_method (PaymentMethod): Método de pago utilizado.
        amount (int): Monto del cargo.
        receiver_id (int): ID del empleado que recibió el pago.
        observations (str): Observaciones opcionales sobre el cargo.

    Relaciones:
        rider (Rider): Relación con la tabla `Rider` (jinete).
        employee (Employee): Relación con la tabla `Employee` (empleado).
    """

    __tablename__ = "charges"

    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey("riders.id"), nullable=False)
    charge_date = db.Column(db.Date, nullable=False, default=datetime.now())
    payment_method = db.Column(
        SQLAlchemyEnum(PaymentMethod), name="payment_method", nullable=False
    )
    amount = db.Column(db.Float, nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    observations = db.Column(db.Text, nullable=True)

    # Relaciones con otras tablas
    rider = db.relationship("Rider", back_populates="charges", uselist=False)
    employee = db.relationship("Employee", back_populates="charges", uselist=False)

    def formatted_charge_date(self):
        """Devuelve la fecha del cargo en formato 'dd/mm/yyyy'."""
        return self.charge_date.strftime("%d/%m/%Y")
