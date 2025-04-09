from typing import List

from flask import current_app

from src.web.validators.general_validations import (
    check_phone,
    validate_string,
    check_number,
    check_radio_value,
)


def check_all_required_data_submitted(params):
    """
    Verifica que se hayan enviado todos los datos requeridos.

    Args:
        params (dict): Un diccionario que contiene los parámetros enviados.

    Returns:
        list: Una lista con los mensajes de error encontrados. Si está vacía, no hay errores.
    """
    required = {
        "insurance_name": "Obra Social",
        "affiliate_number": "N° de afiliado",
        "has_guardianship": "Posee Curatela",
        "school_name": "Nombre de la institución escolar",
        "school_address": "Dirección",
        "school_telephone": "Teléfono",
        "rider_school_grade": "Grado",
    }

    # Lista para almacenar los mensajes de error
    error_messages = []

    # Encuentra claves faltantes
    missing_keys = [required[key] for key in required if key not in params]
    if missing_keys:
        missing_fields = ", ".join(missing_keys)
        error_messages.append(f"Faltan los siguientes campos: {missing_fields}")

    # Retorna la lista de errores (vacía si no hay errores)
    return error_messages


def validate_insurance_and_school_data(params):
    """
    Validar los datos relacionados con la obra social y la institución escolar.

    Esta función verifica que los parámetros enviados cumplan con los requisitos
    necesarios y recopila los errores encontrados en una lista de mensajes. Si
    no se encuentran errores, la lista estará vacía.

    Parámetros:
        params (dict): Un diccionario con los datos a validar. Se espera que
        contenga las siguientes claves:
            - "insurance_name": Nombre de la obra social (requerido).
            - "affiliate_number": Número de afiliado (requerido).
            - "has_guardianship": Indica si posee curatela (requerido).
            - "guardianship_observations": Observaciones sobre la curatela
              (opcional).
            - "school_name": Nombre de la institución escolar (requerido).
            - "school_address": Dirección de la institución escolar (requerido).
            - "school_telephone": Teléfono de la institución escolar (requerido).
            - "rider_school_grade": Grado escolar (requerido).
            - "school_observations": Observaciones sobre la institución escolar
              (opcional).
            - "professionals": Profesionales que lo atienden (opcional).

    Retorna:
        List[str]: Una lista con los mensajes de error encontrados durante la
        validación. Si no se encuentran errores, la lista estará vacía.

    Validaciones realizadas:
        - Revisa que todos los datos requeridos estén presentes usando
          `check_all_required_data_submitted`.
        - Validar que el nombre de la obra social:
            - No exceda los 50 caracteres.
            - Permita espacios y ciertos caracteres especiales ("'", ".", "&").
            - No permita números.
        - Verifica que el número de afiliado:
            - Sea un número válido dentro de un rango específico.
        - Revisa el valor del radio button "Posee Curatela":
            - Debe ser "yes" o "no".
        - Validar las observaciones de curatela:
            - No excedan los 256 caracteres.
            - Permitan números, espacios y ciertos caracteres especiales
              ("'", ".", "&", "@").
        - Verifica que el nombre de la institución escolar:
            - No exceda los 100 caracteres.
            - Permita números, espacios y ciertos caracteres especiales
              ("'", ".", "&").
        - Validar la dirección de la institución escolar:
            - No exceda los 100 caracteres.
            - Permita números y ciertos caracteres especiales ("'", ".", "&").
            - Requiera espacios.
        - Validar el teléfono de la institución escolar usando `check_phone`.
        - Verifica que el grado escolar:
            - Sea un número entre 1 y 7.
        - Validar las observaciones de la institución escolar:
            - No excedan los 256 caracteres.
            - Permitan números, espacios y ciertos caracteres especiales
              ("'", ".", "&", "@").
        - Validar los datos de los profesionales:
            - No excedan los 500 caracteres.
            - Permitan números, espacios y ciertos caracteres especiales
              ("'", ".", "&", "@").
    """
    message: List[str] = []

    # Validación de datos requeridos
    message.extend(check_all_required_data_submitted(params))

    # Si hay errores iniciales, se devuelven directamente
    if len(message) != 0:
        return message

    # Validaciones específicas
    message.extend(
        validate_string(
            s=params["insurance_name"],
            label="Obra social",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'", ".", "&"),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        check_number(
            params["affiliate_number"],
            label="Número de afiliado",
            min_n=0,
            max_n=current_app.config["MAX_NUMBER_ON_DATABASE"],
        )
    )

    message.extend(
        check_radio_value(
            field=params["has_guardianship"],
            label="Posee Curatela",
            permitted_values=("yes", "no"),
        )
    )

    message.extend(
        validate_string(
            s=params["guardianship_observations"],
            label="Observaciones de curatela",
            maxlength=256,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&", "@"),
            spaced=True,
            required=False,
        )
    )

    message.extend(
        validate_string(
            s=params["school_name"],
            label="Nombre de la institución escolar",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&"),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        validate_string(
            s=params["school_address"],
            label="Dirección de la institución escolar",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&"),
            spaced=True,
            required=True,
            only_numbers_accepted=True,
        )
    )

    message.extend(
        check_phone(
            phone=params["school_telephone"], label="Teléfono de la institución escolar"
        )
    )

    message.extend(
        check_number(
            field=params["rider_school_grade"], label="Grado", min_n=1, max_n=7
        )
    )

    message.extend(
        validate_string(
            s=params["school_observations"],
            label="Observaciones de la institución escolar",
            maxlength=256,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&", "@"),
            spaced=True,
            required=False,
        )
    )

    message.extend(
        validate_string(
            s=params["professionals"],
            label="Profesionales que lo atienden",
            maxlength=500,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&", "@"),
            spaced=True,
            required=False,
        )
    )
    return message
