from datetime import datetime
from typing import List

from flask import current_app

from src.core import riders, team
from src.core.charges.charge import PaymentMethod
from src.web.validators.general_validations import check_radio_value


def validate_charge_params(params):
    """
    Validar los parámetros de un pago.

    Args:
        params (dict): Diccionario que contiene los parámetros del pago.

    Returns:
        List[str]: Una lista con los errores.
    """
    errors: List[str] = []

    # Jinete
    rider_id = params.get("rider_id")
    if rider_id is None:
        errors.append("El jinete/amazona es obligatorio")
    else:
        try:
            rider_id = int(rider_id)
        except ValueError:
            errors.append("El jinete/amazona fue suministrado de manera inválida")
        else:
            if riders.get_rider_by_id(rider_id) is None:
                errors.append("No se suministró un jinete/amazona del sistema")
    # Fecha
    try:
        fecha: datetime = datetime.strptime(params.get("charge_date"), "%Y-%m-%d")
        if fecha > datetime.now():
            errors.append("La fecha del cobro no puede ser mayor a la fecha de hoy")
    except ValueError:
        errors.append("El formato de la fecha es inválido")

    # Método de pago
    payment_method = params.get("payment_method")
    if payment_method is None:
        errors.append("El método de pago es requerido")
    else:
        payment_method = payment_method.upper()
        if payment_method not in [pm.name for pm in PaymentMethod]:
            errors.append("Medio de cobro fue suministrado de manera inválida")

    # Monto
    amount = params.get("amount")
    if amount is None:
        errors.append("El monto es requerido")
        return errors

    try:
        amount = float(amount.replace(",", "."))
        if amount <= 0:
            errors.append("El monto ingresado debe ser positivo")
        elif amount > current_app.config["MAX_NUMBER_ON_DATABASE"]:
            errors.append("El monto ingresado es excesivamente grande, reintente")
    except ValueError:
        errors.append("El monto debe ser un número válido")

    # Deudor
    errors.extend(
        check_radio_value(
            field=params.get("debt"),
            label="Deudor",
            permitted_values=("yes", "no"),
        )
    )

    # Empleado
    receiver_id = params.get("receiver_id")
    if receiver_id is None:
        errors.append("El receptor es obligatorio")
    else:
        try:
            receiver_id = int(receiver_id)
        except ValueError:
            errors.append("El receptor fue suministrado de manera inválida")
        else:
            employee = team.get_employee(receiver_id)
            if employee is None or not employee.active:
                errors.append("El receptor no es un empleado activo en el sistema")

    # Observaciones
    observations = params.get("observations")
    if observations and len(observations) > 256:
        errors.append(
            f"Las observaciones tienen un límite máximo de 256 caracteres. "
            f"Usted proporcionó {len(observations)}"
        )

    return errors
