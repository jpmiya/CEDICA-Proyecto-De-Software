from typing import List

from src.web.validators.general_validations import check_select, validate_string


def validate_update_contact(params):
    """
    Validar los datos enviados para actualizar una consulta de contacto.

    Esta función realiza validaciones sobre los campos proporcionados en el diccionario
    `params` para asegurar que cumplen con los requisitos esperados. Recopila todos
    los errores encontrados en una lista y los devuelve.

    Parámetros:
        params (dict): Diccionario que contiene los parámetros enviados para la
        actualización. Las claves esperadas son:
            - 'state': Estado de la consulta, debe ser uno de los valores permitidos.
            - 'comment': Comentario o mensaje asociado a la consulta.

    Retorna:
        List[str]: Una lista de mensajes de error encontrados durante la validación.
        Si no hay errores, la lista estará vacía.

    Validaciones realizadas:
        - El estado ('state') debe ser uno de los valores permitidos: "pendiente",
          "terminado" o "en proceso".
        - El comentario ('comment') debe cumplir con las siguientes condiciones:
            - Longitud máxima de 256 caracteres.
            - Puede contener caracteres especiales permitidos como "'", "@", ".".
            - Puede incluir espacios si `spaced` es True.
            - Es opcional (no obligatorio).
            - Permite números en el texto, pero si `only_numbers_accepted` es True,
              solo puede contener números.

    """
    error_messages: List[str] = []

    error_messages.extend(
        check_select(
            field=params.get("state"),
            label="Estado de la consulta",
            permitted_values=("pendiente", "terminado", "en proceso"),
        )
    )

    error_messages.extend(
        validate_string(
            s=params.get("comment"),
            label="Mensaje",
            maxlength=256,
            allowed_special_chars=("'", "@", "."),
            spaced=True,
            required=False,
            numbers_permitted=True,
            only_numbers_accepted=True,
        )
    )

    return error_messages
