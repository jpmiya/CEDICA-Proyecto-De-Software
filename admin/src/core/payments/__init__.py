from datetime import datetime

from flask import current_app
from sqlalchemy import desc
from sqlalchemy.sql import expression as expr

from src.core import functions
from src.core.database import db
from src.core.payments.payments import Payment
from src.core.team import get_employee
from src.web.handlers.exceptions import PaymentNotFoundException


def create_payment(**kwargs):
    """Crea un nuevo pago y lo guarda en la base de datos.

    Args:
        **kwargs: Parámetros del pago, incluyendo:
            - beneficiary_id (int): ID del beneficiario.
            - payment_date (datetime): Fecha del pago.
            - payment_type (str): Tipo de pago.
            - amount (str): Monto del pago.
            - description (str): Descripción del pago.
    """
    beneficiary_id = kwargs.get("beneficiary_id")
    payment_date = kwargs.get("payment_date", datetime.now())
    payment_type = kwargs.get("payment_type", "Gastos varios")
    amount = kwargs.get("amount")
    description = kwargs.get("description", None)

    payment = Payment(
        beneficiary_id=beneficiary_id,
        payment_date=payment_date,
        payment_type=payment_type,
        amount=amount,
        description=description,
    )

    db.session.add(payment)
    db.session.commit()


def get_payment_by_id(id):
    """Recupera un pago por su ID.

    Args:
        id (int): ID del pago.

    Returns:
        Payment: Objeto del pago encontrado.

    Raises:
        PaymentNotFoundException: Si el pago no se encuentra.
    """
    payment = Payment.query.filter_by(id=id).first()

    return payment


def delete_payment_by_id(id):
    """Elimina un pago por su ID.

    Args:
        id (int): ID del pago.

    Raises:
        PaymentNotFoundException: Si el pago no se encuentra.
    """
    payment = get_payment_by_id(id)
    if payment:
        db.session.delete(payment)
        db.session.commit()
    else:
        raise PaymentNotFoundException(f"No se encontró el pago con ID {id}")


def update_payment(id, **kwargs):
    """Actualiza un pago existente con nuevos datos.

    Args:
        id (int): ID del pago.
        **kwargs: Nuevos valores para los atributos del pago.

    """
    messages = []
    payment = get_payment_by_id(id)
    if payment is None:
        messages.append("No se encontró el pago a actualizar")
        return messages
    messages.extend(check_create_params(**kwargs))
    if len(messages) > 0:
        return messages
    if (
        kwargs.get("beneficiary_id") == ""
        and kwargs.get("payment_type") != "Honorarios"
    ):
        kwargs["beneficiary_id"] = None
    for key, value in kwargs.items():
        setattr(payment, key, value)
    db.session.commit()

    return messages


def order_and_filter_payments(
    page, order="asc", search_value="", start_date=None, end_date=None
):
    """Filtra, ordena y pagina los pagos.

    Args:
        page (int): Número de página.
        order (str): Dirección de ordenamiento ("asc" o "desc").
        search_value (str): Valor para buscar en el tipo de pago.
        start_date (str): Fecha inicial en formato 'YYYY-MM-DD'.
        end_date (str): Fecha final en formato 'YYYY-MM-DD'.

    Returns:
        tuple: Contiene una lista de pagos, el objeto de paginación y un diccionario
        con los beneficiarios.
    """
    order_column = Payment.payment_date

    if order == "desc":
        order_column = desc(order_column)

    query = Payment.query

    if search_value:
        search_value = search_value.lower()

        query = query.filter(
            expr.func.lower(Payment.payment_type).like(f"%{search_value}%")
        )

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Payment.payment_date >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(Payment.payment_date <= end_date)

    pagination = query.order_by(order_column).paginate(
        page=page, per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"], error_out=False
    )

    payments = pagination.items
    beneficiaries = {}

    for i in payments:
        beneficiary = get_employee(i.beneficiary_id)
        if beneficiary:
            beneficiaries[i.id] = (
                f"{beneficiary.name} {beneficiary.last_name} {beneficiary.dni}"
            )

    return payments, pagination, beneficiaries


def check_create_params(**kwargs):
    """Valida los parámetros para crear un nuevo pago.

    Args:
        **kwargs: Parámetros a validar.
    """
    beneficiary_id = kwargs.get("beneficiary_id")
    payment_type = kwargs.get("payment_type")
    payment_date = kwargs.get("payment_date")
    amount = kwargs.get("amount")
    description = kwargs.get("description")
    messages = []

    try:
        functions.check_amount(amount)
        if len(amount) > 10:
            messages.append("Monto inválido")
    except ValueError as e:
        messages.append(str(e))

    try:
        functions.check_payment_type(payment_type)
        if payment_type == "Honorarios":
            if not beneficiary_id:
                messages.append("Debe seleccionar un empleado")
            else:
                if not beneficiary_id.isdigit() or not get_employee(beneficiary_id):
                    messages.append(
                        "Empleado seleccionado no encontrado. Por favor vuelva a intentar."
                    )
    except ValueError as e:
        messages.append(str(e))

    try:
        functions.check_is_valid_date_until_today(payment_date)
    except ValueError as e:
        messages.append(str(e))

    try:
        functions.check_description(description)
    except ValueError as e:
        messages.append(str(e))

    return messages
