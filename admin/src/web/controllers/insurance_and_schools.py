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
from src.core.database import db
from src.core.riders.rider import Rider
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.exceptions import RiderNotFoundException
from src.web.validators.insurance_and_school_validations import (
    validate_insurance_and_school_data,
)


bp = Blueprint("insurance_and_schools", __name__, url_prefix="/obra_social_y_escuela")


@bp.get("/subir_datos_obra_social_escuela/<int:user_id>")  # type: ignore
@login_required
@permission_required("rider_create")
def show_new_insurance_and_school(user_id: int):
    """Renderiza el formulario para cargar datos de obra social y escolar del jinete."""
    token = request.args.get("token")
    if token != session.get("insurance_and_school"):
        abort(403)

    try:
        rider: Rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("No se pudo encontrar al jinete", "error")
        return render_template(url_for("home.html"))

    context = {
        "params": dict(),
        "name": rider.name,
        "last_name": rider.last_name,
        "rider": rider,
    }

    return render_template(
        "jinetes/registrar_obra_social_y_escolar.html", user_id=user_id, **context
    )


@bp.post("/subir_datos_obra_social_escuela/<int:user_id>")
@login_required
@permission_required("rider_create")
def new_insurance_and_school(user_id: int):
    """Crea datos de obra social y escolar para el jinete."""
    params = request.form
    try:
        rider: Rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        return render_template(url_for("home.html"))

    # ----------------Validación ----------------
    message: List[str] = validate_insurance_and_school_data(params)

    if len(message) > 0:
        context = {"name": rider.name, "last_name": rider.last_name, "params": params}
        for error in message:
            flash(error, "error")

        return render_template(
            "jinetes/registrar_obra_social_y_escolar.html", user_id=user_id, **context
        )

    riders.create_insurance(params, rider)
    riders.create_school(params, rider)

    session["tutors"] = secrets.token_urlsafe(16)
    flash(
        f"""¡Muy bien! Seguiremos con los datos de obra social y escolares de {
          rider.name} {rider.last_name}""",
        "success",
    )

    return redirect(
        url_for("tutors.show_new_tutor", user_id=rider.id, token=session["tutors"])
    )


@bp.get("/datos_personales/<int:user_id>/obra_social_y_datos_escolares")
@login_required
@permission_required("rider_show")
def show_edit_social_and_school_data(user_id: int):
    """
    Muestra los datos de obra social y escolares de un jinete para su edición.

    Esta vista recupera los datos de obra social y escolares del jinete especificado
    y prepara el contexto para renderizar la plantilla donde se mostrarán dichos datos.
    Si los datos de obra social y escolares existen, se formatea un diccionario con los
    datos relevantes; de lo contrario, se prepara un contexto vacío para los campos.

    Args:
        user_id (int): ID del jinete cuyos datos se están mostrando.

    Returns:
        Un objeto `Response` que renderiza la plantilla "jinetes/jinete_show.html" con
        un contexto que incluye la información general del jinete, los datos de obra social
        y escolares (si están disponibles) y los parámetros necesarios para la edición.
    """
    rider = riders.get_rider_or_abort(user_id)

    insurance = rider.insurance
    school = rider.school
    if insurance is not None and school is not None:
        params: dict[str, str] = {
            "insurance_name": insurance.insurance_name,
            "affiliate_number": insurance.affiliate_number,
            "has_guardianship": "yes" if insurance.has_guardianship else "no",
            "guardianship_observations": insurance.guardianship_observations,
            "school_name": school.name,
            "school_address": school.address,
            "school_telephone": school.phone_number,
            "rider_school_grade": school.grade,
            "school_observations": school.school_observations,
            "professionals": school.professionals,
        }
    else:
        params = dict()

    context: dict[str, str] = {
        "info_general": True,
        "obra_social_y_datos_escolares": True,
        "params": params,
        "rider": rider,
    }

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.post("/datos_personales/<int:user_id>/obra_social_y_datos_escolares")
@login_required
@permission_required("rider_create")
def edit_social_and_school_data(user_id: int):
    """
    Maneja la solicitud para editar los datos de obra social y datos escolares de un jinete.

    Esta vista permite actualizar o crear los registros de obra social y datos escolares
    asociados a un jinete específico. La función valida los datos proporcionados,
    maneja la creación o actualización de los registros de seguro y escolaridad, y
    actualiza la sesión de la base de datos.

    Args:
        user_id (int): ID del jinete cuyos datos se están modificando.

    Returns:
        Un objeto `Response` que renderiza la plantilla "jinetes/jinete_show.html" con
        un contexto actualizado que contiene la información del jinete, los datos de
        obra social y datos escolares, así como los mensajes flash de éxito o error.
    """

    rider: Rider = riders.get_rider_or_abort(user_id)

    params = request.form
    # Validaciones
    message: List[str] = validate_insurance_and_school_data(params)

    context = {
        "info_general": True,
        "obra_social_y_datos_escolares": True,
        "rider": rider,
        "params": params,
    }

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    if rider.insurance is not None:
        riders.update_insurance(params, rider.insurance)
    else:
        riders.create_insurance(params, rider)

    if rider.school is not None:
        riders.update_school(params, rider.school)

    else:
        riders.create_school(params, rider)

    db.session.refresh(rider)

    flash("Datos de obra social y escolares actualizados exitosamente", "success")

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)
