"""
Módulo de validación de datos para los tutores en un formulario web.

Este módulo define una función `validate_tutors` para validar los datos
de los tutores ingresados en un formulario web, sin realizar consultas
a la base de datos. Incluye validaciones de formato, longitud y consistencia
para distintos campos como DNI, nombres, apellidos, direcciones, teléfonos,
correo electrónico y ocupación, entre otros.

"""

from typing import List

from flask import current_app

from src.web.validators.general_validations import (
    check_email,
    check_number,
    check_phone,
    check_radio_value,
    check_select,
    validate_string,
    check_dni,
)


def validate_tutors(params) -> List[str]:
    """
    NO REALIZA VALIDACIONES CONTRA LA BASE DE DATOS,
    únicamente verifica la validez de los datos ingresados.
    Valida los datos de los tutores ingresados.

    Este método valida los datos de los tutores, asegurándose de que cumplen con
    las reglas de formato, longitud y consistencia para cada campo.

    Args:
        params (MultiDictKey): Datos del formulario de tutores.

    Returns:
        tuple: Una tupla (error, message) donde `error` es un booleano que indica
               si hubo algún error de validación, y `message` es una descripción
               del error (o una cadena vacía si no hubo errores).

    """
    message: List[str] = []

    message.extend(
        check_radio_value(
            field=params.get("second_tutor_enabled"),
            label="Habilitar segundo tutor",
            permitted_values=("yes", "no"),
        )
    )
    if len(message) > 0:
        return message

    second_tutor = params["second_tutor_enabled"] == "yes"

    message.extend(
        check_dni(dni=params.get("dni_primario"), label="DNI del tutor primario")
    )

    message.extend(
        validate_string(
            s=params.get("parentesco_primario"),
            label="Parentesco del tutor primario",
            maxlength=30,
            numbers_permitted=False,
            allowed_special_chars=tuple(),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        validate_string(
            s=params.get("nombre_primario"),
            label="Nombre del tutor primario",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        validate_string(
            s=params.get("apellido_primario"),
            label="Apellido del tutor primario",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        check_select(
            field=params.get("provincia_primario"),
            label="Provincia del tutor primario",
            permitted_values=current_app.config["ARGENTINIAN_PROVINCES"],
        )
    )

    message.extend(
        validate_string(
            s=params.get("localidad_primario"),
            label="Localidad del tutor primario",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&"),
            spaced=True,
            required=True,
        )
    )

    message.extend(
        validate_string(
            s=params.get("calle_primario"),
            label="Calle del tutor primario",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", ".", "&"),
            spaced=True,
            required=True,
            only_numbers_accepted=True,
        )
    )

    message.extend(
        check_number(
            field=params.get("numero_calle_primario"),
            label="Número de calle del tutor primario",
        )
    )
    if params.get("piso_primario") != "":
        message.extend(
            check_number(
                field=params.get("piso_primario"),
                label="Piso del tutor primario",
                min_n=0,
            )
        )

    message.extend(
        validate_string(
            s=params.get("departamento_primario"),
            label="Departamento del tutor primario",
            maxlength=3,
            numbers_permitted=True,
            allowed_special_chars=("°",),
            spaced=False,
            required=False,
            only_numbers_accepted=True,
        )
    )

    message.extend(
        check_phone(
            phone=params.get("celular_primario"), label="Celular del tutor primario"
        )
    )

    message.extend(
        check_email(
            field=params.get("email_primario"), label="Email del tutor primario"
        )
    )

    niveles_de_escolaridad = ("primario", "secundario", "terciario", "universitario")
    message.extend(
        check_select(
            field=params.get("escolaridad_primario"),
            label="Nivel de escolaridad del tutor primario",
            permitted_values=niveles_de_escolaridad,
        )
    )

    message.extend(
        validate_string(
            s=params.get("ocupacion_primario"),
            label="Ocupación del tutor primario",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=("'", ".", "-"),
            spaced=True,
            required=True,
        )
    )

    if second_tutor:
        message.extend(
            check_dni(
                dni=params.get("dni_secundario"), label="DNI del tutor secundario"
            )
        )

        message.extend(
            validate_string(
                s=params.get("parentesco_secundario"),
                label="Parentesco del tutor secundario",
                maxlength=30,
                numbers_permitted=False,
                allowed_special_chars=tuple(),
                spaced=True,
                required=True,
            )
        )

        message.extend(
            validate_string(
                s=params.get("nombre_secundario"),
                label="Nombre del tutor secundario",
                maxlength=50,
                numbers_permitted=False,
                allowed_special_chars=("'",),
                spaced=True,
                required=True,
            )
        )

        message.extend(
            validate_string(
                s=params.get("apellido_secundario"),
                label="Apellido del tutor secundario",
                maxlength=50,
                numbers_permitted=False,
                allowed_special_chars=("'",),
                spaced=True,
                required=True,
            )
        )

        message.extend(
            check_select(
                field=params.get("provincia_secundario"),
                label="Provincia del tutor secundario",
                permitted_values=current_app.config["ARGENTINIAN_PROVINCES"],
            )
        )

        message.extend(
            validate_string(
                s=params.get("localidad_secundario"),
                label="Localidad del tutor secundario",
                maxlength=100,
                numbers_permitted=True,
                allowed_special_chars=("'", ".", "&"),
                spaced=True,
                required=True,
            )
        )

        message.extend(
            validate_string(
                s=params.get("calle_secundario"),
                label="Calle del tutor secundario",
                maxlength=100,
                numbers_permitted=True,
                allowed_special_chars=("'", ".", "&"),
                spaced=True,
                required=True,
                only_numbers_accepted=True,
            )
        )

        message.extend(
            check_number(
                field=params.get("numero_calle_secundario"),
                label="Número de calle del tutor secundario",
            )
        )
        if params.get("piso_secundario", "") != "":
            message.extend(
                check_number(
                    field=params.get("piso_secundario"),
                    label="Piso del tutor secundario",
                    min_n=0,
                )
            )

        message.extend(
            validate_string(
                s=params.get("departamento_secundario"),
                label="Departamento del tutor secundario",
                maxlength=3,
                numbers_permitted=True,
                allowed_special_chars=("°",),
                spaced=False,
                required=False,
                only_numbers_accepted=True,
            )
        )

        message.extend(
            check_phone(
                phone=params.get("celular_secundario"),
                label="Celular del tutor secundario",
            )
        )

        message.extend(
            check_email(
                field=params.get("email_secundario"), label="Email del tutor secundario"
            )
        )

        message.extend(
            check_select(
                field=params.get("escolaridad_secundario"),
                label="Nivel de escolaridad del tutor secundario",
                permitted_values=niveles_de_escolaridad,
            )
        )

        message.extend(
            validate_string(
                s=params.get("ocupacion_secundario"),
                label="Ocupación del tutor secundario",
                maxlength=100,
                numbers_permitted=False,
                allowed_special_chars=("'", ".", "-"),
                spaced=True,
                required=True,
            )
        )

    return message
