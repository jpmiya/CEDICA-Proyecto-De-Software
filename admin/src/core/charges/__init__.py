from datetime import datetime
from typing import Dict, List

from flask import current_app

from src.core import riders
from src.core.charges.charge import Charge, PaymentMethod
from src.core.database import db
from src.core.team import Employee
from src.web.handlers.exceptions import ChargeNotFoundException


def create_charge(params: Dict[str, str]):
    """
    Crea un nuevo cobro basado en los parámetros proporcionados.

    Esta función toma un diccionario de parámetros, crea un objeto `Charge` con los datos
    proporcionados y lo guarda en la base de datos. Además, actualiza el estado de deuda
    (`has_debt`) del jinete asociado al cobro.

    Parámetros:
        params (Dict[str, str]): Diccionario que contiene los datos necesarios para crear el cobro:
            - "amount" (str): Monto del cobro.
            - "receiver_id" (str): ID del receptor del cobro.
            - "charge_date" (str): Fecha del cobro.
            - "payment_method" (str): Método de pago 
                    (debe coincidir con los valores de `PaymentMethod`).
            - "rider_id" (str): ID del jinete asociado al cobro.
            - "observations" (str, opcional): Observaciones del cobro.
            - "debt" (str): Indica si el jinete tiene deuda ("yes" o "no").

    Excepciones:
        Ninguna explícita, pero podría lanzar errores si los parámetros
        son inválidos o el método de pago no es válido.

    """
    amount : str = params.get("amount")
    amount_float : float = float(amount.replace(',', '.'))
    charge : Charge = Charge (
        amount=amount_float,
        receiver_id=params.get("receiver_id"),
        charge_date=params.get("charge_date"),
        payment_method=PaymentMethod[params.get("payment_method")],
        rider_id=params.get("rider_id"),
        observations=params.get("observations", ""),
    )

    db.session.add(charge)
    rider = riders.get_rider_by_id(params.get("rider_id"))
    rider.has_debt = params.get("debt") == "yes"
    db.session.commit()


def get_charge_by_id(id) :
    """
    Recupera un cobro por su ID.

    Busca un cobro en la base de datos utilizando su ID. Si se encuentra,
    devuelve el objeto `Charge`.
    Si no, lanza una excepción personalizada.

    Parámetros:
        id (int): Id del cobro a recuperar.

    Retorna:
        Charge: Objeto `Charge` correspondiente al ID proporcionado.

    Excepciones:
        ChargeNotFoundException: Si no se encuentra ningún cobro con el ID proporcionado.
    """
    charge : Charge = Charge.query.filter_by(id=id).first()
    if charge is not None:
        return charge
    else:
        raise ChargeNotFoundException


def delete_charge_by_id(id):
    """
    Elimina un cobro por su ID.

    Recupera un cobro de la base de datos utilizando su ID y lo elimina de forma permanente.

    Parámetros:
        id (int): Id del cobro a eliminar.

    Excepciones:
        ChargeNotFoundException: Si no se encuentra ningún cobro con el ID proporcionado.
    """
    charge: Charge = get_charge_by_id(id)
    db.session.delete(charge)
    db.session.commit()


def update_charge(id, params):
    """
    Actualiza un cobro existente con nuevos datos.

    Busca un cobro en la base de datos por su ID y actualiza sus campos con los 
    datos proporcionados.

    Parámetros:
        id (int): ID del cobro a actualizar.
        params (dict): Diccionario con los nuevos datos del cobro:
            - "rider_id" (str): ID del jinete asociado.
            - "charge_date" (str): Nueva fecha del cobro.
            - "payment_method" (str): Método de pago (debe ser válido en `PaymentMethod`).
            - "amount" (str): Nuevo monto del cobro.
            - "receiver_id" (str): Nuevo ID del receptor.
            - "observations" (str): Observaciones adicionales.
            - "debt" (str): Indica si el jinete tiene deuda ("yes" o "no").

    Excepciones:
        ValueError: Si el método de pago no es válido.
    """
    charge: Charge = get_charge_by_id(id)
    amount = params.get("amount")
    amount = float(amount.replace(',', '.'))
    charge.rider_id = params.get("rider_id")
    charge.charge_date = params.get("charge_date")
    payment_method = params.get("payment_method")
    if payment_method not in PaymentMethod.__members__:
        raise ValueError("Método de pago no válido")
    charge.payment_method = PaymentMethod[payment_method]
    charge.amount = amount
    charge.receiver_id = params.get("receiver_id")
    charge.observations = params.get("observations")
    rider = riders.get_rider_by_id(params.get("rider_id"))
    rider.has_debt = params.get("debt") == "yes"
    db.session.commit()


def order_and_filter_charges(
    page,
    order="asc",
    payment_method=None,
    start_date=None,
    end_date=None,
    receiver_first_name=None,
    receiver_last_name=None,
    rider_id=None,
):
    """
    Filtra, ordena y pagina los cobros.

    Realiza un filtrado, ordenación y paginación sobre los cobros almacenados en la base de datos
    en base a los criterios proporcionados.

    Parámetros:
        page (int): Número de página para la paginación.
        order (str, opcional): Orden de los resultados ("asc" o "desc"). Por defecto es "asc".
        payment_method (str, opcional): Método de pago a filtrar.
        start_date (str, opcional): Fecha de inicio para el rango de fechas (formato "YYYY-MM-DD").
        end_date (str, opcional): Fecha de fin para el rango de fechas (formato "YYYY-MM-DD").
        receiver_first_name (str, opcional): Nombre del receptor para filtrar.
        receiver_last_name (str, opcional): Apellido del receptor para filtrar.
        rider_id (int, opcional): ID del jinete para filtrar.
        debt (str, opcional): Filtro para deudas ("yes" o "no").

    Retorna:
        tuple: Una lista de objetos `Charge` y el objeto de paginación.

    Excepciones:
        Ninguna explícita, pero podría lanzar errores si los datos proporcionados son inválidos.
    """
    query = Charge.query.join(Charge.rider).join(
        Employee, Charge.receiver_id == Employee.id
    )
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Charge.charge_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(Charge.charge_date <= end_date)
    if payment_method:
        payment_method_enum = (
            PaymentMethod[payment_method.upper()]
            if payment_method.upper() in PaymentMethod.__members__
            else None
        )
        if payment_method_enum:
            query = query.filter(Charge.payment_method == payment_method_enum)
    if receiver_first_name:
        query = query.filter(Employee.name.ilike(f"%{receiver_first_name}%"))
    if receiver_last_name:
        query = query.filter(Employee.last_name.ilike(f"%{receiver_last_name}%"))
    if rider_id:
        query = query.filter(Charge.rider_id == rider_id)

    if order == "asc":
        query = query.order_by(Charge.charge_date.asc())
    else:
        query = query.order_by(Charge.charge_date.desc())

    pagination = query.paginate(
        page=page, per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"], error_out=False
    )

    return pagination.items, pagination


def validate_filter_params(params):
    """
    Valida y convierte los parámetros de filtro.

    Verifica que los parámetros proporcionados para filtrar cobros sean válidos y realiza
    las conversiones necesarias.

    Parámetros:
        params (dict): Diccionario con los parámetros de filtro:
            - "start_date" (str, opcional): Fecha de inicio (formato "YYYY-MM-DD").
            - "end_date" (str, opcional): Fecha de fin (formato "YYYY-MM-DD").
            - "payment_method" (str, opcional): Método de pago a filtrar.
            - "receiver_name" (str, opcional): Nombre del receptor.
            - "receiver_last_name" (str, opcional): Apellido del receptor.
            - "rider_id" (str, opcional): ID del jinete.
            - "order" (str, opcional): Orden de los resultados ("asc" o "desc").

    Retorna:
        tuple: Parámetros validados y convertidos.

    Excepciones:
        ValueError: Si algún parámetro es inválido (fechas, método de pago, etc.).
    """
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    payment_method = params.get("payment_method")
    receiver_first_name = params.get("receiver_name")
    receiver_last_name = params.get("receiver_last_name")
    rider_id = params.get("rider_id")
    order = params.get("order", "desc")

    errores: List[str] = []
    # Validar fechas
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            errores.append("La fecha de inicio no es válida")
    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            errores.append("La fecha de fin no es válida")
    if start_date and end_date and start_date > end_date:
        errores.append("La fecha de inicio debe ser menor o igual a la fecha de fin")

    # Validar método de pago
    if (
        payment_method
        and payment_method not in PaymentMethod.__members__
        and payment_method != ""
    ) :
        errores.append("Método de pago no válido")

    # Validar longitud de nombres
    if receiver_first_name and len(receiver_first_name) > 50:
        errores.append("El nombre del receptor es demasiado largo")
    if receiver_last_name and len(receiver_last_name) > 50:
        errores.append("El apellido del receptor es demasiado largo")

    # Jinete
    if rider_id :
        try:
            rider_id = int(rider_id)
        except ValueError:
            errores.append("El ID del jinete debe ser un número válido")

        if riders.get_rider_by_id(rider_id) is None:
            errores.append("No se suministró un jinete/amazona del sistema")

    # Validar orden
    if order not in ["asc", "desc", ""] :
        errores.append("El orden no es válido")

    return errores
