from typing import List

from src.web.validators.general_validations import check_number, check_select

EXPECTED_KEYS = {"email", "order"}
VALID_ORDERS = (
    "",
    "emailA-Z",
    "emailZ-A",
    "newer",
    "older",
)


def check_search_pending_user_params(params: dict[str, str]) -> List[str]:
    """
    Validar los parámetros de búsqueda de usuarios pendientes.

    Esta función verifica que los parámetros enviados en la búsqueda de usuarios
    pendientes cumplan con las claves esperadas y los valores permitidos. Si se
    detectan errores, se devuelven en forma de una lista de mensajes.

    Parámetros:
        params (dict[str, str]): Un diccionario con los parámetros de búsqueda.
        Puede incluir las claves:
            - "email": (opcional) El correo electrónico a buscar.
            - "order": (opcional) El criterio de ordenamiento. Los valores válidos son:
                - String vacío
                - "emailA-Z": Ordenar correos de A a Z.
                - "emailZ-A": Ordenar correos de Z a A.
                - "newer": Ordenar por los más recientes.
                - "older": Ordenar por los más antiguos.

    Retorna:
        List[str]: Una lista de mensajes de error. Si no se encuentran errores,
        la lista estará vacía.
    """
    message: List[str] = []
    extra_keys = set(params.keys()) - EXPECTED_KEYS
    if extra_keys:
        message.append("Ingreso parámetros no permitidos en la URL")
        return message
    field = params.get("order") if params.get("order") is not None else ""
    message.extend(
        check_select(field=field, label="Orden", permitted_values=VALID_ORDERS)
    )

    return message


def check_delete_pending_user(params: dict) -> List[str]:
    """
    Validar los parámetros para eliminar un usuario pendiente.

    Esta función verifica que los parámetros enviados para eliminar un usuario
    pendiente sean válidos. Específicamente, revisa que se proporcione un
    identificador de usuario válido.

    Args:
        params (dict): Un diccionario con los parámetros necesarios. Debe incluir:
            - "pending_user_id" (str/int): El identificador del usuario pendiente.

    Returns:
        List[str]: Una lista de mensajes de error. Si la validación es exitosa,
                   la lista estará vacía. Si hay errores, se incluyen los mensajes
                   correspondientes.
    """
    message: List[str] = []

    message.extend(
        check_number(
            params.get("pending_user_id", ""),
            label="Usuario pendiente de aceptación",
            min_n=0,
        )
    )

    return message
