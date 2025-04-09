from typing import List, Optional

from src.core import team, ecuestre
from src.core.ecuestre.horse import Horse
from src.core.team.employee import Employee
from src.web.validators.general_validations import (
    check_checkbox_selection,
    check_radio_value,
    check_select,
)


def check_employee_role(
    employee_id: str,
    expected_profession: Optional[str] = None,
    expected_job_position: Optional[str] = None,
    role_name: str = "Empleado",
) -> List[str]:
    """
    Verifica que un empleado cumpla con los criterios de identificación, actividad,
    y posición o profesión dados.
    Parámetros:
        employee_id (str): ID del empleado en formato de cadena.
        expected_profession (str): Profesión esperada del empleado (opcional).
        expected_job_position (str): Puesto de trabajo esperado del empleado (opcional).
        role_name (str): Nombre descriptivo del rol para los
        mensajes de error (por defecto "Empleado").
    Retorna:
        list: Lista de mensajes de errores
    """
    error_messages: List[str] = []

    if not isinstance(employee_id, str):
        error_messages.append(f"El campo de {role_name} recibió un formato no válido.")
        return error_messages

    if not employee_id.isdigit():
        error_messages.append(f"El campo de {role_name} no recibió lo esperado.")
        return error_messages

    id_empleado: int = int(employee_id)
    employee: Employee = team.get_employee(id_empleado)

    if employee is None:
        error_messages.append(f"No se seleccionó un {role_name} real.")
        return error_messages
    if not employee.active:
        error_messages.append(f"Se seleccionó un {role_name} no activo.")

    if expected_profession and expected_job_position:
        if not (
            employee.profession == expected_profession
            or employee.job_position == expected_job_position
        ):
            error_messages.append(
                f"""El {role_name} seleccionado no trabaja como
                {expected_profession} ni como {expected_job_position}."""
            )
    elif expected_job_position and employee.job_position != expected_job_position:
        error_messages.append(
            f"El {role_name} seleccionado no trabaja como {expected_job_position}."
        )

    return error_messages


def check_horse(horse_id: str, headquarters: str, proposal: str) -> List[str]:
    """
    Verifica que un caballo cumpla con los criterios de identificación, actividad y
    sede especificados.

    Parámetros:
        horse_id (str): ID del caballo en formato de cadena.
        headquarters (str): Sede esperada en la que se encuentra el caballo.
        proposal (str): Tipo de actividad en la que debe participar el caballo.

    Retorna:
        List[str]: Una lista de mensajes de error si el caballo no cumple con los criterios.
    """
    error_messages: List[str] = []

    if not isinstance(horse_id, str):
        error_messages.append("El campo de Caballo recibió un formato no válido.")
        return error_messages
    if not horse_id.isdigit():
        error_messages.append("El campo de Caballo no recibió lo esperado")
        return error_messages

    id_caballo = int(horse_id)
    caballo: Optional[Horse] = ecuestre.find_horse_by_id(id_caballo)  # type: ignore

    if caballo is None:
        error_messages.append(
            "El caballo seleccionado no corresponde a un caballo del sistema."
        )
        return error_messages

    if not caballo.active:
        error_messages.append("El caballo seleccionado no está activo")
    if caballo.sede != headquarters:
        error_messages.append(
            f"El caballo seleccionado no está en la sede {headquarters}"
        )
    if caballo.rider_type != proposal:
        error_messages.append(
            "El caballo seleccionado no participa de la actividad seleccionada"
        )

    return error_messages


def validate_institutional_work(params) -> List[str]:
    """
    Validar los parámetros para el registro de trabajo institucional, incluyendo empleados,
    caballo y otros datos de configuración.

    Parámetros:
        params (dict): Diccionario con los parámetros de entrada que incluyen ID de empleados,
        caballo, sede, propuesta de trabajo,
                       y días de la semana.

    Retorna:
        tuple: (error, message) donde `error` es un booleano que indica si hubo un error,
        y `message` es un mensaje descriptivo del error (si existe).

    Raises:
        ValueError: Si algún campo no cumple con las condiciones establecidas, el mensaje describe
        el problema específico.
    """
    message: List[str] = []

    proposals = (
        "Hipoterapia",
        "Monta Terapeutica",
        "Deporte Ecuestre Adaptado",
        "Actividades Recreativas",
        "Equitacion",
    )
    message.extend(
        check_select(
            field=params.get("proposal"),
            label="Propuesta de trabajo",
            permitted_values=proposals,
        )
    )

    sedes = ("CASJ", "HLP", "OTRO")
    message.extend(
        check_radio_value(
            field=params.get("headquarters"), label="Sede", permitted_values=sedes
        )
    )

    selected_days = params.getlist("days_of_the_week")
    valid_days = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    message.extend(
        check_checkbox_selection(
            selected_values=selected_days,
            label="Dias de la semana de trabajo",
            permitted_values=valid_days,
            min_options=1,
            max_options=7,
        )
    )

    message.extend(
        check_employee_role(
            employee_id=params.get("teacher_therapist"),
            expected_profession="Profesor/a",
            expected_job_position="Terapeuta",
            role_name="Profesor/a o Terapeuta",
        )
    )

    message.extend(
        check_employee_role(
            employee_id=params.get("horse_riders"),
            expected_job_position="Conductor",
            role_name="Conductor/a del caballo",
        )
    )

    message.extend(
        check_horse(
            horse_id=params.get("horse"),
            headquarters=params.get("headquarters"),
            proposal=params.get("proposal"),
        )
    )

    message.extend(
        check_employee_role(
            employee_id=params.get("track_assistant"),
            expected_job_position="Auxiliar de pista",
            role_name="Auxiliar de pista",
        )
    )

    return message
