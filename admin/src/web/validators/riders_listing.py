from typing import List

from src.web.validators.general_validations import (
    check_dni,
    check_select,
    validate_string,
)

EXPECTED_KEYS = {"name", "last_name", "dni", "professionals", "employee", "order"}
VALID_ORDERS = (
    "",
    "nombreA-Z",
    "nombreZ-A",
    "apellidoA-Z",
    "apellidoZ-A",
)


def check_search_rider_params(params: dict) -> List[str]:
    """
    Validar los parámetros para buscar jinetes.

    Esta función verifica que los parámetros enviados para buscar jinetes sean válidos
    y estén dentro de los valores permitidos. Si se encuentran errores, se devuelven
    en forma de una lista de mensajes descriptivos.

    Parámetros:
        params (dict): Un diccionario con los parámetros de búsqueda.
        Puede incluir las siguientes claves:
            - "name" (str): Nombre del jinete. Opcional, máx. 50 caracteres.
            - "last_name" (str): Apellido del jinete. Opcional, máx. 50 caracteres.
            - "dni" (str): DNI del jinete. Opcional, debe ser válido si se incluye.
            - "order" (str): Criterio de ordenamiento. Opcional, valores permitidos:
                - String vacío
                - "nombreA-Z": Ordenar nombres de A a Z.
                - "nombreZ-A": Ordenar nombres de Z a A.
                - "apellidoA-Z": Ordenar apellidos de A a Z.
                - "apellidoZ-A": Ordenar apellidos de Z a A.

    Retorna:
        List[str]: Una lista de mensajes de error. Si no se encuentran errores,
        la lista estará vacía.
    """
    message: List[str] = []

    extra_keys = set(params.keys()) - EXPECTED_KEYS
    if extra_keys:
        message.append("Ingreso parámetros no permitidos en la URL")
        return message

    message.extend(
        validate_string(
            s=params.get("name"),
            label="Nombre",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=False,
        )
    )

    message.extend(
        validate_string(
            s=params.get("last_name"),
            label="Apellido",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=False,
        )
    )

    if params.get("dni") != "":
        message.extend(check_dni(dni=params.get("dni"), label="D.N.I"))

    message.extend(
        check_select(
            field=params.get("order"), label="Orden", permitted_values=VALID_ORDERS
        )
    )

    return message
