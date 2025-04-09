import re
from datetime import datetime
from typing import List
from flask import current_app
from werkzeug.datastructures import FileStorage
from src.web.handlers.exceptions import (
    AmountNotNumberException,
    StringNotValidException,
)


def check_number(number):
    """
    Verifica si un número es válido.

    Args:
        number (str): El número a verificar.

    Returns:
        bool: True si el número es válido, False en caso contrario.
    """
    if not number or not number.isdigit():
        raise AmountNotNumberException(f"El número {number} no es un número válido")

    return True


def check_dni(dni: str):
    """
    Verifica si el DNI es correcto.

    Args:
        dni (str): El DNI a verificar.

    Returns:
        List[str]: Lista de mensajes de error si el DNI no es válido.
    """
    messages: List[str] = []
    if not isinstance(dni, str):
        messages.append("El DNI fue suministrado con un formato no válido")
    if len(messages) > 0:
        return messages
    if not dni or len(dni) != 8:
        messages.append("El DNI debe consistir de 8 dígitos")
    if not dni[0:7].isdigit():
        messages.append("El DNI debe consistir de sólamente dígitos")

    return messages


def check_email(email):
    """
    Verifica si el correo electrónico es correcto.

    Args:
        email (str): El correo electrónico a verificar.

    Returns:
        List[str]: Lista de mensajes de error si el correo no es válido.
    """
    messages: List[str] = []
    if not email:
        messages.append("El correo electrónico es obligatorio")
    if email.count("@") != 1 or email.count(".") == 0:
        messages.append("El correo electrónico es obligatorio")

    return messages


def check_name(name: str):
    """
    Verifica si los nombres son correctos: solo letras y no vacíos.

    Args:
        name (str): El nombre a verificar.

    Returns:
        List[str]: Lista de mensajes de error si el nombre no es válido.
    """
    messages: List[str] = []
    patron = r"^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ']+(?: [A-Za-zÁÉÍÓÚÜáéíóúüÑñ']+)*$"

    if not name or not name.strip():
        messages.append("El campo de nombre es obligatorio")
    if len(name) > 50:
        messages.append(
            f"El campo de nombre tiene como máximo 50 caracteres. Usted proporcionó {len(name)}"
        )
    if not re.match(patron, name):
        messages.append("El campo de nombre tiene caracteres no permitidos")

    return messages


def check_is_string(value):
    """
    Verifica si el valor es una cadena válida.

    Args:
        value (str): El valor a verificar.

    Returns:
        bool: True si el valor es una cadena válida, False en caso contrario.
    """
    if (
        not value
        or len(value) > 50
        or not isinstance(value, str)
        or value == ""
        or not all(char.isalpha() or char.isspace() for char in value)
    ):
        raise StringNotValidException

    return True


def check_alias(alias):
    """
    Verifica si el alias es correcto: solo letras, números y guiones bajos, y no solo guiones bajos.

    Args:
        alias (str): El alias a verificar.

    Returns:
        List[str]: Lista de mensajes de error si el alias no es válido.
    """
    messages: List[str] = []

    if not alias:
        messages.append("El alias no puede estar vacío.")
    if len(alias) > 50:
        messages.append("El alias no puede tener más de 50 caracteres.")
    if not re.match(r"^(?!_)[A-Za-z0-9_]+(?<!_)$", alias):
        messages.append(
            """El alias solo puede contener letras, números y guiones bajos,
            y no puede comenzar ni terminar con un guion bajo."""
        )

    return messages


def format_name(name):
    """
    Formatea un string para que aparezca todo en minúsculas y la primera letra mayúscula.

    Args:
        name (str): El nombre a formatear.

    Returns:
        str: El nombre formateado.
    """
    formatted_name = name.lower().title()

    return formatted_name


def delete_document(source):
    """
    Elimina el documento de MinIO con la fuente especificada.

    Args:
        source (str): Fuente del documento.

    Returns:
        str: La fuente del documento eliminado.
    """
    client = current_app.storage.client
    bucket_name = "grupo13"
    client.remove_object(bucket_name, source)

    return source


def check_valid_format(file: FileStorage):
    """
    Verifica si el formato del archivo es válido.

    Args:
        file (FileStorage): El archivo a verificar.

    Returns:
        bool: True si el formato es válido, False en caso contrario.
    """
    permitidos = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/jpeg",
        "image/jpg",
    ]

    return file.content_type in permitidos


def is_valid_url(url):
    """
    Verifica si la URL es válida.

    Args:
        url (str): La URL a verificar.

    Returns:
        bool: True si la URL es válida, False en caso contrario.
    """
    url_pattern = re.compile(
        r"^("
        r"http://|https://"
        r")?"
        r"(www\.)?"
        r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}"
        r"(/[a-zA-Z0-9@:%._+~#=/?&-]*)?$"
    )

    return re.match(url_pattern, url) is not None


def check_is_valid_date(date, label: str = "Fecha"):
    """
    Verifica si la fecha es correcta y cumple con los criterios de año.
    La fecha debe estar en formato 'YYYY-MM-DD', y el año debe ser un número de 4 dígitos
    y estar dentro del rango de 2000 en adelante.
    También verifica que el mes esté en el rango de 1-12 y el día en el rango de 1-31.

    Args:
        date (str): La fecha a revisar.
        label (str): El nombre del campo de fecha.

    Returns:
        List[str]: Lista de mensajes de error si la fecha no es válida.
    """
    messages: List[str] = []
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        if (
            len(str(parsed_date.year)) != 4
            or parsed_date.year < 2000
            or parsed_date.year > 2100
        ):
            messages.append(
                f"""En el campo {label} el año debe ser un número de
                4 dígitos y mayor o igual a 2000."""
            )
        if parsed_date.month < 1 or parsed_date.month > 12:
            messages.append(
                f"En el campo {label} el mes debe estar en el rango de 1 a 12."
            )
        if parsed_date.day < 1 or parsed_date.day > 31:
            messages.append(
                f"En el campo {label} el día debe estar en el rango de 1 a 31."
            )
        datetime(year=parsed_date.year, month=parsed_date.month, day=parsed_date.day)
    except ValueError:
        messages.append(
            f"En el campo {label} la fecha suministrada obtuvo un valor no válido"
        )

    return messages


def check_is_valid_date_until_today(date):
    """
    Verifica si la fecha es correcta y cumple con los criterios de año.
    La fecha debe estar en formato 'YYYY-MM-DD', y el año debe ser un número de 4 dígitos
    y estar dentro del rango de 2000 en adelante.
    También verifica que el mes esté en el rango de 1-12 y el día en el rango de 1-31.

    Args:
        date (str): La fecha a revisar.

    Returns:
        bool: True si la fecha es válida, False en caso contrario.

    Raises:
        ValueError: Si la fecha es inválida.
    """
    try:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("La fecha no tiene el formato correcto")
        if (
            len(str(parsed_date.year)) != 4
            or parsed_date.year < 2000
            or parsed_date.year > 2100
        ):
            raise ValueError(
                "El año debe ser un número de 4 dígitos y mayor o igual a 2000."
            )
        if parsed_date.month < 1 or parsed_date.month > 12:
            raise ValueError("El mes debe estar en el rango de 1 a 12.")
        if parsed_date.day < 1 or parsed_date.day > 31:
            raise ValueError("El día debe estar en el rango de 1 a 31.")
        datetime(year=parsed_date.year, month=parsed_date.month, day=parsed_date.day)
        if parsed_date > datetime.now():
            raise ValueError("La fecha no puede ser mayor a la fecha actual")
    except ValueError as e:
        raise ValueError(f"Fecha inválida: {e}")


def check_roles(roles, system_admin):
    """
    Verifica si los roles son correctos.

    Args:
        roles (list): Los roles a verificar.
        system_admin (bool): Indica si es un administrador del sistema.

    Returns:
        List[str]: Lista de mensajes de error si los roles no son válidos.
    """
    messages: List[str] = []
    if not roles and not system_admin:
        messages.append("Debe seleccionar al menos 1 rol")
    for role in roles:
        if role not in [
            "Administracion",
            "Tecnica",
            "Ecuestre",
            "Voluntariado",
            "Editor",
        ]:
            messages.append("Se suministró un rol inválido")
            break

    return messages


def check_condition(condition):
    """
    Verifica si la condición es válida.

    Args:
        condition (str): La condición a verificar.

    Returns:
        List[str]: Lista de mensajes de error si la condición no es válida.
    """
    messages: List[str] = []
    conditions = ["Personal Rentado", "Voluntario"]
    if not condition:
        messages.append("La condición es obligatoria")
        return messages
    if condition not in conditions:
        messages.append("La condición no es válida")

    return messages


def check_profession(profession):
    """
    Verifica si la profesión es válida.

    Args:
        profession (str): Profesión a verificar.

    Returns:
        List[str]: Lista de mensajes de error si la profesión no es válida.
    """
    messages: List[str] = []
    professions = [
        "Psicologo/a",
        "Medico/a",
        "Kinesiologo/a",
        "Psicomotricista",
        "Terapista Ocupacional",
        "Psicopedagogo/a",
        "Fonoaudiologo/a",
        "Profesor/a",
        "Docente",
        "Veterinario/a",
        "Otra",
    ]
    if profession not in professions:
        messages.append("Profesión inválida")

    return messages


def check_job_position(job_position):
    """
    Verifica si el cargo es válido.

    Args:
        job_position (str): Cargo a verificar.

    Returns:
        List[str]: Lista de mensajes de error si el cargo no es válido.
    """
    messages: List[str] = []
    job_positions = [
        "Administrativo/a",
        "Terapeuta",
        "Conductor",
        "Auxiliar de pista",
        "Herrero",
        "Veterinario",
        "Entrenador de Caballos",
        "Domador",
        "Profesor de Equitacion",
        "Docente de Capacitacion",
        "Auxiliar de mantenimiento",
        "Otra",
    ]
    if job_position not in job_positions:
        messages.append("El puesto de trabajo suministrado no es válido")

    return messages


def check_password(password):
    """
    Verifica si la contraseña es válida.

    Requisitos:
    - Al menos 6 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número

    Args:
        password (str): La contraseña a verificar.

    Returns:
        List[str]: Lista de mensajes de error si la contraseña no es válida.
    """
    messages: List[str] = []
    if (
        len(password) < 6
        or len(password) > 200
        or not re.search(r"[A-Z]", password)
        or not re.search(r"[a-z]", password)
        or not re.search(r"\d", password)
        or re.search(r" ", password)
    ):
        messages.append(
            """La contraseña debe tener al menos 6 caracteres sin espacios en blanco,
            contener una mayúscula, una minúscula y un número"""
        )
    return messages


def get_max_number():
    """
    Obtiene el número máximo de la base de datos.

    Returns:
        int: El número máximo de la base de datos.
    """
    return current_app.config["MAX_NUMBER_ON_DATABASE"]


def check_payment_type(payment_type):
    """
    Verifica si el tipo de pago es válido.

    Args:
        payment_type (str): El tipo de pago a verificar.

    Returns:
        bool: True si el tipo de pago es válido, False en caso contrario.

    Raises:
        ValueError: Si el tipo de pago no es válido.
    """
    if payment_type not in ["Honorarios", "Gastos varios", "Proveedor"]:
        raise ValueError("El tipo de pago no es válido. Por favor intentelo de nuevo")


def check_amount(amount):
    """
    Verifica si el monto es válido.

    Args:
        amount (str): El monto a verificar.

    Returns:
        bool: True si el monto es válido, False en caso contrario.

    Raises:
        ValueError: Si el monto no es válido.
    """
    if not re.match(r"^\d+(\.\d{1,2})?$", amount):
        raise ValueError("El monto no es válido. Por favor, ingrese un número válido.")
    return True


def check_file_size(file: FileStorage, limite_mb: int = 15):
    """
    Verifica si el tamaño del archivo es válido.

    Args:
        file (FileStorage): El archivo a verificar.
        limite_mb (int): El límite de tamaño en megabytes.

    Returns:
        bool: True si el tamaño del archivo es válido, False en caso contrario.
    """
    limite_bytes = limite_mb * 1024 * 1024
    return file.content_length < limite_bytes


def check_description(description):
    """
    Verifica si la descripción es válida.

    Args:
        description (str): La descripción a verificar.

    Returns:
        bool: True si la descripción es válida, False en caso contrario.

    Raises:
        ValueError: Si la descripción no es válida.
    """
    if len(description) > 200:
        raise ValueError("La descripción no puede tener más de 200 caracteres")
    return True


def check_contacts_state(state):
    """
    Verifica si el estado de los contactos es válido.

    Args:
        state (str): El estado a verificar.

    Returns:
        bool: True si el estado es válido, False en caso contrario.

    Raises:
        ValueError: Si el estado no es válido.
    """
    if state not in ["pendiente", "en proceso", "terminado"]:
        raise ValueError("Estado no válido.")
