"""
Este módulo define las funciones generales para las validaciones
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from flask import current_app


def check_dni(dni: str, label: str) -> List:
    """
    Verifica si el DNI es correcto y devuelve una lista de mensajes de error si hay alguno.
    """
    error_messages: List[str] = []

    if not isinstance(dni, str):
        error_messages.append(
            f"El campo de {label} se suministró con un formato inesperado. Reintente"
        )
        return error_messages

    if not dni.isdigit():
        error_messages.append(f"El campo de {label} solo acepta dígitos numéricos")
    if len(dni) != 8:
        error_messages.append(
            f"El campo de {label} debe de ser de 8 dígitos. Usted proporcionó {len(dni)} dígitos"
        )

    return error_messages


def check_valid_birthday(date: str, label: str) -> List[str]:
    """
    Validar que la fecha de nacimiento sea válida, es decir, que esté entre hoy y hace 100 años.

    Args:
        date (str): La fecha de nacimiento en formato 'YYYY-MM-DD'.
        label(str): Nombre del campo para un mensaje más informativo.

    Returns:
        list: Lista de mensajes de error si hay alguno, de lo contrario, lista vacía.
    """
    error_messages: List[str] = []

    try:
        birthday: datetime = datetime.strptime(
            date, "%Y-%m-%d"
        )  # Convierte la fecha de cadena a datetime
        today: datetime = datetime.today()
        hundred_years_ago: datetime = today - timedelta(days=365 * 100)

        # Comprobar si la fecha está entre hoy y hace 100 años
        if birthday >= today:
            error_messages.append(
                f"El campo {label} no puede sobrepasar la fecha actual"
            )

        if birthday < hundred_years_ago:
            error_messages.append(f"El campo {label} no puede haber sido hace 100 años")

    except ValueError:
        error_messages.append(
            f"El campo {label} fue suministrado con un formato inválido"
        )

    return error_messages  # Devuelve la lista de mensajes de error


def check_phone(phone: str, label: str) -> List[str]:
    """
    Verifica si el número de teléfono es válido.

    Args:
        phone (str): El número de teléfono en formato de cadena.
        label (str): Etiqueta para el campo de teléfono.

    Returns:
        list: Lista de mensajes de error si hay alguno, de lo contrario, lista vacía.
    """
    error_messages: List[str] = []

    if not isinstance(phone, str):
        error_messages.append(f"El campo {label} obtuvo un formato no esperado")
        return error_messages

    if not phone.isdigit():
        error_messages.append(f"El campo {label} debe de consistir solo de dígitos")

    if len(phone) != 10:
        error_messages.append(
            f"El campo {label} requiere de 10 dígitos y usted proporcionó {len(phone)}"
        )

    return error_messages


def validate_string(
    s: str,
    label: str,
    maxlength: int,
    numbers_permitted: bool,
    allowed_special_chars: Tuple[str, ...],
    spaced: bool,
    required: bool = True,
    only_numbers_accepted: bool = False,
) -> List[str]:
    """
    Verifica si un string es válido en función de los parámetros de configuración y
    devuelve una lista de mensajes de error si falla.

    Args:
    - s (str): El string a validar.
    - label (str): Nombre del campo (para mensajes personalizados).
    - maxlength (int): Longitud máxima permitida para el string.
    - numbers_permitted (bool): Permite números si es True.
    - allowed_special_chars (Tuple[str, ...]): Caracteres especiales permitidos.
    - spaced (bool): Permite espacios si es True.
    - required (bool): Indica si el campo es obligatorio.
    - only_numbers_accepted (bool): Si True, solo se permite números.

    Returns:
    - list: Lista de mensajes de error si los hay, de lo contrario, lista vacía.
    """
    error_messages: List[str] = []

    if not isinstance(s, str):  # type: ignore
        error_messages.append(
            f"El campo {label} fue suministrado con un formato no permitido."
        )
        return error_messages

    if required and s.strip() == "":
        error_messages.append(
            f"El campo {label} es obligatorio y no lo puede dejar vacío."
        )
        return error_messages

    if len(s) > maxlength:
        error_messages.append(
            f"El campo {label} solo permite un máximo de {maxlength} caracteres."
        )

    allowed_chars_pattern = r"A-Za-zÁÉÍÓÚáéíóúÜüñÑ"
    if numbers_permitted:
        allowed_chars_pattern += r"0-9"
    if allowed_special_chars:
        escaped_special_chars = "".join(
            re.escape(char) for char in allowed_special_chars
        )
        allowed_chars_pattern += escaped_special_chars

    full_pattern = f"^[{allowed_chars_pattern + (r' ' if spaced else '')}]+$"
    if required and not re.fullmatch(full_pattern, s):
        error_messages.append(f"El campo {label} contiene caracteres no permitidos.")

    if allowed_special_chars:
        consecutive_special_chars_pattern = (
            f"[{re.escape(''.join(allowed_special_chars))}]" + r"{2,}"
        )
        if re.search(consecutive_special_chars_pattern, s):
            error_messages.append(
                f"El campo {label} no puede tener caracteres especiales consecutivos."
            )

    if spaced and re.search(r" {2,}", s):
        error_messages.append(
            f"El campo {label} no puede contener múltiples espacios consecutivos."
        )
    elif not spaced and " " in s:
        error_messages.append(f"El campo {label} no puede contener espacios.")

    if not only_numbers_accepted and s.isdecimal():
        error_messages.append(
            f"El campo {label} no puede consistir únicamente de números"
        )

    return error_messages


def check_number(
    field: str, label: str, min_n: int = 0, max_n: Optional[int] = None
) -> List[str]:
    """
    Verifica si el valor de un campo de texto contiene un número dentro de un rango específico.

    Esta función toma un campo (`field`) y una etiqueta (`label`) para identificarlo,
    y opcionalmente un rango numérico mínimo (`min_n`) y máximo (`max_n`). Verifica que el campo sea
    una cadena de texto que solo contenga dígitos. Luego convierte el campo a un número entero y
    validar que esté dentro del rango especificado. Si alguna de estas condiciones no se cumple,
    devuelve una lista de mensajes de error.

    Parámetros:
    - field (str): El valor del campo a verificar, esperado como una cadena de texto que
        representa un número.
    - label (str): La etiqueta o nombre del campo, utilizada en el mensaje de error.
    - min_n (int, opcional): El valor mínimo permitido para el campo. Por defecto es 0.
    - max_n (int, opcional): El valor máximo permitido para el campo. Por defecto es el
        mayor número en la base de datos configurado en la configuración de la app.

    Retorna:
    - list: Lista de mensajes de error si hay, de lo contrario, lista vacía.

    Excepciones:
    - ValueError: Si `field` no es una cadena de texto.
    - NotANumberException: Si `field` no contiene solo dígitos.
    - OverflowError: Si el número está fuera del rango permitido (`min_n`, `max_n`).
    """
    error_messages = []

    if not isinstance(field, str):
        error_messages.append(f"El campo {label} obtuvo un formato no permitido")
        return error_messages

    if not field.isdigit():
        error_messages.append(f"El campo {label} solo permite números")
        return error_messages

    numero: int = int(field)
    if max_n is None:
        max_n: int = current_app.config["MAX_NUMBER_ON_DATABASE"]

    if numero < min_n:
        error_messages.append(f"El campo {label} no acepta valores menores a {min_n}")
    if numero > max_n:
        error_messages.append(
            f"El campo {label} supera el límite aceptable de {max_n}. Reintente"
        )

    return error_messages


def check_radio_value(
    field: str, label: str, permitted_values: Optional[tuple[str]] = None
) -> List[str]:
    """
    Verifica si el valor de un campo de tipo opción múltiple (radio button) es válido.

    Esta función toma un valor (`field`) y una etiqueta (`label`) para identificarlo,
    junto con una lista opcional de valores permitidos (`permitted_values`).
    Verifica que el campo sea una cadena de texto y que su valor esté en la tupla de
    valores permitidos. Si no cumple con estos requisitos, devuelve una lista de mensajes de error.

    Parámetros:
    - field (str): El valor del campo a comprobar, esperado como una cadena de texto.
    - label (str): La etiqueta o nombre del campo, utilizada en el mensaje de error.
    - permitted_values (tuple[str], opcional): Una lista de valores permitidos para el campo.
      Por defecto, ["yes", "no"].

    Retorna:
    - list: Lista de mensajes de error si hay, de lo contrario, lista vacía.

    Excepciones:
    - ValueError: Si `field` no es una cadena de texto o si su valor no está en `permitted_values`.
    """
    error_messages: List[str] = []

    if not isinstance(field, str):
        error_messages.append(f"El campo {label} obtuvo un formato no válido")
        return error_messages

    if permitted_values is None:
        permitted_values = ("yes", "no")

    if field not in permitted_values:
        error_messages.append(f"El campo {label} obtuvo un valor inesperado")

    return error_messages


def check_select(
    field: str, label: str, permitted_values: Optional[tuple[str]] = None
) -> List[str]:
    """Verifica si el valor de un campo tipo select es válido.

    Esta función toma un valor (`field`) y una etiqueta (`label`) para identificarlo,
    junto con una lista opcional de valores permitidos (`permitted_values`). Verifica
    que el campo sea una cadena de texto y que su valor esté en la tupla de valores
    permitidos. Si el valor no es válido, devuelve una lista de mensajes de error.

    Parámetros:
    - field (str): El valor del campo a revisar, esperado como una cadena de texto.
    - label (str): La etiqueta o nombre del campo, utilizada en el mensaje de error.
    - permitted_values (tuple[str], opcional): Una lista de valores permitidos para el campo.

    Retorna:
    - List[str]: Una lista de mensajes de error si el campo contiene valores no válidos,
                 o una lista vacía si es válido."""
    error_messages: List[str] = []
    if not isinstance(field, str):
        error_messages.append(f"El campo {label} obtuvo un formato no esperado")
        return error_messages
    if permitted_values is None:
        permitted_values = tuple()

    if field not in permitted_values:
        error_messages.append(
            f"El campo {label} fue suministrado con un valor no esperado"
        )

    return error_messages


def check_checkbox_selection(
    selected_values: list[str],
    label: str,
    permitted_values: tuple[str],
    min_options: int = 0,
    max_options: Optional[int] = None,
) -> List[str]:
    """
    Verifica que las opciones seleccionadas en un formulario cumplan con las
    restricciones de valores permitidos, así como los límites mínimo y máximo
    de opciones seleccionadas.

    Args:
        selected_values (list[str]): Lista de valores seleccionados por el usuario.
        label (str): Etiqueta del campo para incluir en los mensajes de error.
        permitted_values (tuple[str]): Tupla de valores válidos que se pueden seleccionar.
        min_options (int, opcional): Número mínimo de opciones que el usuario debe seleccionar.
                                     El valor predeterminado es 0.
        max_options (Optional[int], opcional): Número máximo de opciones que el usuario puede
                                                seleccionar.
                                               Si no se especifica, no se aplicará restricción
                                               superior.

    Returns:
        List[str]: Una lista de mensajes de error si hay algún problema con la selección,
                   o una lista vacía si la validación es exitosa.
    """
    error_messages: List[str] = []
    for value in selected_values:
        if value not in permitted_values:
            error_messages.append(
                f"El campo {label} fue suministrado con un valor no esperado: {value}"
            )
            return error_messages

    num_selected = len(selected_values)
    if num_selected < min_options:
        error_messages.append(
            f"En el campo {label} debe elegir al menos {min_options} de las opciones posibles"
        )
    if max_options is None:
        max_options = len(permitted_values)

    if num_selected > max_options:
        error_messages.append(
            f"El campo {label} debe elegir como máximo {max_options} de las opciones posibles"
        )

    return error_messages


def check_email(
    field: str, label: str = "Correo electrónico", max_length: int = 256
) -> List[str]:
    """
    Verifica si el valor de un campo de texto contiene un correo electrónico válido.

    Esta función toma un valor (`field`) y una etiqueta (`label`) para identificarlo,
    y verifica que el valor sea una cadena de texto que cumpla con el patrón de un
    correo electrónico válido. También comprueba que el campo no exceda un límite de
    longitud de caracteres.

    Parámetros:
    - field (str): El valor del campo a revisar, esperado como una cadena de texto.
    - label (str): La etiqueta o nombre del campo, utilizada en el mensaje de error.
    - max_length (int, opcional): Longitud máxima permitida para el campo. Por defecto es 256.

    Retorna:
    - bool: `True` si el campo contiene un correo electrónico válido dentro del límite de longitud.

    Excepciones:
    - ValueError: Si `field` no es una cadena de texto, si no cumple con el formato de
      correo electrónico o si excede la longitud máxima.
    """
    error_messages: List[str] = []
    patron_correo = r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$"
    if not isinstance(field, str):
        error_messages.append(f"El campo {label} obtuvo un formato no esperado")
        return error_messages
    if not re.match(patron_correo, field):
        error_messages.append(
            f"El correo electrónico de {label} tiene un formato inválido"
        )
    if len(field) > max_length:
        error_messages.append(
            f"El campo {label} supera el límite de caracteres de {max_length}"
        )

    return error_messages
