from typing import List

from flask import current_app

from src.web.validators.general_validations import (
    check_checkbox_selection,
    check_radio_value,
    check_select,
    validate_string,
)


def check_all_required_data_submitted(params):
    """
    Verifica que se hayan enviado todos los datos requeridos.

    Args:
        params (MultiDict): Un diccionario que contiene los parámetros enviados.

    Returns:
        list: Una lista con los mensajes de error encontrados. Si está vacía, no hay errores.
    """
    required = {
        "has_disability": "¿Posee Certificado de Discapacidad?",
        "asignacion_familiar": "¿Percibe alguna Asignación Familiar?",
        "has_pension": "¿Es beneficiario de alguna pensión?",
    }

    error_messages = []

    # Encuentra claves faltantes
    missing_keys = [required[key] for key in required if key not in params]
    if missing_keys:
        missing_fields = ", ".join(missing_keys)
        error_messages.append(f"Faltan los siguientes campos: {missing_fields}")
        return error_messages

    # Check del certificado de discapacidad
    if "has_disability" in params:
        if params["has_disability"] == "yes":
            if "diagnosis" not in params:
                error_messages.append("El campo de diagnóstico es obligatorio.")

            if params["diagnosis"] == "OTRO" and "other_diagnosis" not in params:
                error_messages.append("Debe indicar qué otro diagnóstico recibió.")

        elif params["has_disability"] == "no":
            if "disability_type" not in params:
                error_messages.append(
                    """Debe indicar al menos un tipo de discapacidad 
                                          [Mental, Motora, Sensorial o Visceral]."""
                )
        else:
            error_messages.append(
                """Debe indicar 'sí' o 'no' en el campo 
                                     de certificado de discapacidad."""
            )

    # Check de la asignación familiar
    if "asignacion_familiar" in params:
        if params["asignacion_familiar"] == "yes":
            selected_options = params.getlist("beneficios_sociales")
            if not selected_options:
                error_messages.append(
                    "Debe seleccionar al menos una asignación familiar."
                )

        elif params["asignacion_familiar"] != "no":
            error_messages.append(
                """Debe indicar 'sí' o 'no' en el campo 
                                      de asignación familiar."""
            )

    # Check de pensión percibida
    if "has_pension" in params:
        if params["has_pension"] == "yes":
            if "pension_type" not in params:
                error_messages.append(
                    """Debe seleccionar al menos un tipo de pensión 
                                          (NACIONAL o PROVINCIAL)."""
                )
        elif params["has_pension"] != "no":
            error_messages.append(
                """Debe indicar 'sí' o 'no' en el campo 
                                      de pensión percibida."""
            )

    return error_messages


def validate_disability_and_benefits_data(params) -> List[str]:
    """
    Validar los datos de discapacidad y beneficios enviados.

    Args:
        params (InmutableDictKey): Un diccionario inmutable que contiene los parámetros enviados
                                  para la validación de datos de discapacidad y beneficios.

    Returns:
        List[str]: Una lista de mensajes de error que describen los problemas encontrados en los
                   datos enviados. La lista estará vacía si no se encontraron errores.
    """
    message: List[str] = []

    # Chequeo que haya mandado todos los datos
    message.extend(check_all_required_data_submitted(params))

    if len(message) != 0:
        return message

    message.extend(
        check_radio_value(
            field=params["has_disability"],
            label="¿Posee Certificado de Discapacidad?",
            permitted_values=("yes", "no"),
        )
    )

    if params["has_disability"] == "yes":
        # Chequeo que haya elegido una de las opciones

        message.extend(
            check_select(
                field=params["diagnosis"],
                label="¿Con qué diagnóstico?",
                permitted_values=current_app.config["DISABILITIES_IN_SYSTEM"],
            )
        )

        # Si eligió "OTRO"
        if params["diagnosis"] == "OTRO":
            # Chequeo que haya completado el campo "OTRO"
            message.extend(
                validate_string(
                    s=params["other_diagnosis"],
                    label="Si es OTRO, indicar cuál",
                    maxlength=100,
                    numbers_permitted=True,
                    allowed_special_chars=("'", ".", "&"),
                    spaced=True,
                )
            )

    # Si no
    else:
        # Chequeo que haya elegido una de las 4 opciones
        valid_options = ("Mental", "Motora", "Sensorial", "Visceral")
        selected_options = params.getlist("disability_type")

        message.extend(
            check_checkbox_selection(
                selected_values=selected_options,
                label="Tipo de Discapacidad",
                permitted_values=valid_options,
                min_options=1,
            )
        )

    message.extend(
        check_radio_value(
            field=params["asignacion_familiar"],
            label="¿Percibe alguna Asignación Familiar?",
            permitted_values=("yes", "no"),
        )
    )

    if params["asignacion_familiar"] == "yes":
        valid_options = (
            "asignacion_por_hijo",
            "asignacion_por_hijo_con_discapacidad",
            "asignacion_por_ayuda_escolar",
        )
        selected_options = params.getlist("beneficios_sociales")

        message.extend(
            check_checkbox_selection(
                selected_values=selected_options,
                label="¿Cuál asignación familiar percibe?",
                permitted_values=valid_options,
                min_options=1,
            )
        )

        message.extend(
            check_radio_value(
                field=params["has_pension"],
                label="¿Es beneficiario de alguna pensión?",
                permitted_values=("yes", "no"),
            )
        )

    if params["has_pension"] == "yes":

        valid_options = ("Nacional", "Provincial")

        message.extend(
            check_radio_value(
                field=params["pension_type"],
                label="¿Cuál pensión?",
                permitted_values=valid_options,
            )
        )

    return message
