""" 
Módulo de validación de datos personales para el sistema de registro de jinetes.    
"""

import re
from typing import List
from flask import current_app

from src.core import riders
from src.core.riders.rider import Rider

from src.web.validators.general_validations import (
    check_dni,
    check_number,
    check_valid_birthday,
    check_phone,
    validate_string,
    check_select,
    check_radio_value,
)


def check_all_required_data_submitted(params: dict) -> List[str]:
    """
    Verifica si todos los campos requeridos están presentes en el diccionario 'params'.

    Args:
        params (dict): Un diccionario con los datos a validar.

    Returns:
        List[str]: Retorna una lista con los campos que faltan.
    """
    message: List[str] = []
    params_required = [
        "dni",
        "name",
        "last_name",
        "birthday",
        "locality",
        "street",
        "house_num",
        "dpto",
        "province",
        "province_address",
        "locality_address",
        "actual_tel",
        "emergency_contact_name",
        "emergency_contact_tel",
        "scholarship_holder",
    ]

    params_labels = {
        "dni": "D.N.I",
        "name": "Nombre/s",
        "last_name": "Apellido",
        "birthday": "Fecha de nacimiento",
        "locality": "Localidad de nacimiento",
        "locality_address": "Localidad del domicilio",
        "street": "Calle",
        "house_num": "Número de domicilio",
        "province_address": "Provincia del domicilio",
        "province": "Provincia de Nacimiento",
        "actual_tel": "Teléfono actual",
        "emergency_contact_name": "Nombre de contacto de emergencia",
        "emergency_contact_tel": "Contacto de emergencia",
        "scholarship_holder": "Es becado",
    }

    missing_keys = [key for key in params_required if key not in params]

    if missing_keys:
        missing_labels = [params_labels[key] for key in missing_keys]
        for elem in missing_labels:
            message.append(f"El campo {elem} no fue suministrado")

    return message


def check_dpto(field: str, label: str, max_length: int = 3) -> List[str]:
    """
    Verifica si el campo proporcionado es válido según las siguientes reglas:

    - El campo debe ser una cadena de texto.
    - No puede tener más de un número máximo de caracteres especificado por max_length.
    - Solo puede contener letras, números y un espacio
        (el espacio debe estar entre caracteres, no al inicio o al final).
    - No puede contener múltiples espacios consecutivos.

    Args:
        field (str): El valor del campo a validar.
        label (str): El nombre del campo (usado en mensajes de error).
        max_length (int): Longitud máxima permitida para el campo (por defecto es 3).

    Returns:
        List[str]: Lista de mensajes de error si las validaciones fallan;
        lista vacía si el campo es válido.
    """
    message: List[str] = []

    # Verificar que el campo sea una cadena de texto
    if not isinstance(field, str):  # type: ignore
        message.append(f"El campo {label} recibió un formato no válido.")
        return message

    # Verificar longitud máxima
    if len(field) > max_length:
        message.append(
            f"El campo {label} no puede tener más de {max_length} caracteres."
        )

    # Verificar que el campo esté conformado solo por letras, números y espacios válidos
    pattern = r"^[A-Za-z0-9 ]{1,3}$"
    if not re.match(pattern, field):
        message.append(
            f"""El campo {label} solo puede contener letras,
            números y un único espacio entre caracteres."""
        )

    # Verificar que el campo no contenga espacios múltiples consecutivos
    if "  " in field:
        message.append(
            f"El campo {label} no puede contener múltiples espacios consecutivos."
        )

    return message


def validate_personal_data(
    params: dict[str, str], rider: Rider = None, updating: bool = False
) -> List[str]:
    """
    Validar los datos personales proporcionados en el diccionario 'params'.
    Verifica que todos los campos requeridos estén presentes, y chequea cada uno de los campos.

    Args:
        params (ImmutableMultiDict): Un "diccionario de flask" con los datos personales a validar,
            como DNI, nombre, teléfono, etc.
        rider (Rider): Un objeto del modelo Rider
        updating: Un valor booleano que indica si se está actualizando valores de un rider
    Returns:
        list: Una lista con los mensajes a poner en flash de lo que salió mal
    """
    message: List[str] = []

    # Convertir params a un diccionario mutable
    mutable_params = params.to_dict()  # type: ignore

    message.extend(check_all_required_data_submitted(params))
    if len(message) > 0:
        return message

    dni: str = mutable_params["dni"]
    message.extend(check_dni(dni=dni, label="DNI"))  # type: ignore
    if not updating:
        is_unique: bool = riders.unique_dni(dni)  # type: ignore

        if not is_unique:
            message.append(
                "El DNI ingresado ya le pertenece a un jinete/amazona en el sistema"
            )
    else:
        dni_actual = str(rider.dni)
        if (dni_actual != dni) and (not riders.unique_dni(dni)):
            # Esta actualizandolo a uno ya en uso
            message.append("El DNI ingresado ya le pertenece a un jinete")

    message.extend(
        validate_string(
            s=mutable_params["name"],
            label="Nombre",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )

    message.extend(
        validate_string(
            s=mutable_params["last_name"],
            label="Apellido",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )

    message.extend(
        check_valid_birthday(mutable_params["birthday"], label="Fecha de nacimiento")
    )

    message.extend(
        check_select(
            mutable_params["province"],
            label="Provincia de nacimiento",
            permitted_values=current_app.config["ARGENTINIAN_PROVINCES"],
        )
    )

    message.extend(
        validate_string(
            s=mutable_params["locality"],
            label="Localidad de nacimiento",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )

    message.extend(
        check_select(
            mutable_params["province_address"],
            label="Provincia de domicilio",
            permitted_values=current_app.config["ARGENTINIAN_PROVINCES"],
        )
    )

    message.extend(
        validate_string(
            s=mutable_params["locality_address"],
            label="Localidad de domicilio",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )

    message.extend(
        validate_string(
            s=mutable_params["street"],
            label="Calle del domicilio",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", "."),
            spaced=True,
            required=True,
            only_numbers_accepted=True,
        )
    )

    message.extend(
        check_number(field=mutable_params["house_num"], label="Número de domicilio")
    )

    if mutable_params["dpto"] != "":
        message.extend(
            check_dpto(field=mutable_params["dpto"], label="Departamento de domicilio")
        )

    message.extend(
        check_phone(phone=mutable_params["actual_tel"], label="Teléfono actual")
    )
    message.extend(
        validate_string(
            s=mutable_params["emergency_contact_name"],
            label="Nombre de contacto de emergencia",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )
    message.extend(
        check_phone(
            phone=mutable_params["emergency_contact_tel"],
            label="Teléfono de emergencia",
        )
    )

    message.extend(
        check_radio_value(
            field=mutable_params["scholarship_holder"],
            label="¿Es becado?",
            permitted_values=("yes", "no"),
        )
    )

    message.extend(
        validate_string(
            s=mutable_params["rider_observations"],
            label="Observaciones",
            maxlength=256,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "@", "(", ")"),
            spaced=True,
            required=False,
        )
    )

    return message
