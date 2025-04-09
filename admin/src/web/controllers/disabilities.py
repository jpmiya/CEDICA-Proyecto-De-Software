"""
Este módulo maneja las rutas relacionadas con los datos de discapacidad y beneficios de
los jinetes en una aplicación Flask.

Blueprint:
    bp: Instancia de Blueprint para las rutas relacionadas con discapacidad,
    con el prefijo de URL "/discapacidad".

Rutas:
    - GET /subir_datos_discapacidad/<int:user_id>: Renderiza un formulario para agregar
        datos de discapacidad de un jinete.
    - POST /subir_datos_discapacidad/<int:user_id>: Validar y guarda los datos de
        discapacidad de un jinete.
    - GET /datos_personales/<int:user_id>/discapacidad_y_pensiones: Renderiza un formulario
        para ver o editar los datos de discapacidad y pensiones.
    - POST /datos_personales/<int:user_id>/discapacidad_y_pensiones: Actualiza los datos de
    discapacidad y pensiones del jinete.

Requisitos:
    - Acceso basado en sesión y permisos para cada ruta.
    - Validación de sesión para el acceso basado en token en algunas rutas.
    - Importaciones y servicios para interactuar con los datos de los jinetes y
    manejar excepciones.

Excepciones:
    - RiderNotFoundException: Se lanza cuando un jinete con el ID especificado no existe.
"""

import secrets
from typing import List

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    session,
    abort,
)

from src.core import riders
from src.core.riders.rider import Rider
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.exceptions import RiderNotFoundException
from src.web.validators.disability_data_validations import (
    validate_disability_and_benefits_data,
)


bp = Blueprint("disabilities", __name__, url_prefix="/discapacidad")


@bp.get("/subir_datos_discapacidad/<int:user_id>")
@login_required
@permission_required("rider_create")
def show_new_disability_data(user_id: int):
    """Renderiza el formulario para cargar datos de discapacidad del jinete."""
    token = request.args.get("token")
    if token != session.get("disability_token"):
        abort(403)
    try:
        rider: Rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("No se pudo encontrar al jinete", "error")
        return render_template(url_for("home.html"))

    context = {"name": rider.name, "last_name": rider.last_name, "params": dict()}

    return render_template(
        "jinetes/registrar_discapacidad.html", user_id=user_id, **context
    )


@bp.post("/subir_datos_discapacidad/<int:user_id>")
@login_required
@permission_required("rider_create")
def new_disability_data(user_id: int):
    """Crea datos de discapacidad para el jinete."""
    params = request.form
    try:
        rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("Error: No se encontró al jinete en la base de datos", "error")
        return render_template(url_for("home.html"))

    # Validación
    message: List[str] = validate_disability_and_benefits_data(params)
    if message:
        context = {
            "name": rider.name,
            "last_name": rider.last_name,
            "params": get_params_for_form(request.form),
        }
        for error in message:
            flash(error, "error")
        return render_template(
            "jinetes/registrar_discapacidad.html", user_id=user_id, **context
        )

    riders.create_disability(params, rider)
    riders.create_benefits(params, rider)

    flash(
        f"""¡Bien! Seguiremos con los datos de situación previsional
        y escolares de {rider.name} {rider.last_name}""",
        "success",
    )

    session["insurance_and_school"] = secrets.token_urlsafe(16)

    return redirect(
        url_for(
            "insurance_and_schools.show_new_insurance_and_school",
            user_id=rider.id,
            token=session["insurance_and_school"],
        )
    )


@bp.get("/datos_personales/<int:user_id>/discapacidad_y_pensiones")
@login_required
@permission_required("rider_show")
def show_edit_disability_and_pension_data(user_id: int):
    """
    Renderiza el template con los datos cargados (si los hay) de la instancia
    de Disability y Benefits correspondiente.
    """
    rider = riders.get_rider_or_abort(user_id)

    disability = rider.disability
    benefits = rider.benefits
    if disability and benefits:
        params: dict[str, str] = {
            "has_disability": "yes" if disability.disability_certificate else "no",
            "diagnosis": disability.diagnosis,
            "other_diagnosis": disability.other_diagnosis,
            "mental": disability.disability_type.mental,
            "motora": disability.disability_type.motora,
            "sensorial": disability.disability_type.sensorial,
            "visceral": disability.disability_type.visceral,
            "asignacion_familiar": "yes" if benefits.asignacion_familiar else "no",
            "asignacion_por_hijo": benefits.asignacion_por_hijo,
            "asignacion_por_hijo_con_discapacidad": benefits.asignacion_por_hijo_con_discapacidad,
            "asignacion_por_ayuda_escolar": benefits.asignacion_por_ayuda_escolar,
            "has_pension": "yes" if benefits.beneficiario_de_pension else "no",
            "pension_type": (
                benefits.naturaleza_pension.value
                if benefits.beneficiario_de_pension
                else ""
            ),
        }
    else:
        params = dict()
    context = {
        "info_general": True,
        "discapacidad_y_pensiones": True,
        "rider": rider,
        "params": params,
    }

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.post("/datos_personales/<int:user_id>/discapacidad_y_pensiones")
@login_required
@permission_required("rider_create")
def edit_disability_and_pension_data(user_id: int):
    """
    Edita con los datos cargados (si los hay) la instancia de Disability y Benefits correspondiente.
    """
    rider = riders.get_rider_or_abort(user_id)
    disability = rider.disability
    benefits = rider.benefits
    params = request.form

    message: List[str] = validate_disability_and_benefits_data(params)

    context = {
        "info_general": True,
        "discapacidad_y_pensiones": True,
        "rider": rider,
        "params": get_params_for_form(request.form),
    }

    if message:
        for error in message:
            flash(error, "error")
        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    if rider.disability is None:
        riders.create_disability(params, rider)
    else:
        riders.update_disability(params, disability)

    if rider.benefits is None:
        riders.create_benefits(params, rider)
    else:
        riders.update_benefits(params, benefits)

    flash(
        "Datos de discapacidad y beneficios sociales actualizados exitosamente",
        "success",
    )

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


def get_params_for_form(params):
    """
    Obtener el diccionario de los parámetros ingresados para la renderización del template.
    """
    params = params.to_dict()
    params["mental"] = "Mental" in request.form.getlist("disability_type")
    params["motora"] = "Motora" in request.form.getlist("disability_type")
    params["sensorial"] = "Sensorial" in request.form.getlist("disability_type")
    params["visceral"] = "Visceral" in request.form.getlist("disability_type")

    params["asignacion_por_hijo"] = "asignacion_por_hijo" in request.form.getlist(
        "beneficios_sociales"
    )
    params["asignacion_por_hijo_con_discapacidad"] = (
        "asignacion_por_hijo_con_discapacidad"
        in request.form.getlist("beneficios_sociales")
    )
    params["asignacion_por_ayuda_escolar"] = (
        "asignacion_por_ayuda_escolar" in request.form.getlist("beneficios_sociales")
    )

    return params
