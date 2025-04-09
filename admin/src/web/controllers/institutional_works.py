from typing import List

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.core import ecuestre, riders, team
from src.core.riders.institutional_work import InstitutionalWork
from src.web.handlers.auth import login_required, permission_required
from src.web.validators.institutional_work_validations import (
    validate_institutional_work,
)


bp = Blueprint("institutional_works", __name__, url_prefix="/trabajo_institucional")


@bp.get("/subir_datos_trabajo/<int:user_id>")
@login_required
@permission_required("rider_create")
def show_institutional_work(user_id):
    """
    Muestra el formulario para cargar los datos de trabajo institucional de un jinete.

    Esta función verifica si el usuario tiene los permisos necesarios y si
    se encuentran cargados los datos requeridos (profesores/terapeutas,
    conductores de caballos, auxiliares de pista, y caballos). Si falta
    alguno de estos elementos, se muestra un mensaje de error.

    Args:
        user_id (int): El ID del jinete para el cual se cargarán los datos de trabajo.

    Returns:
        render_template: Renderiza la plantilla 'registrar_trabajo.html' con el formulario
                         para completar los datos de trabajo institucional.
        flash: Muestra un mensaje de error si faltan datos en el sistema.
        redirect: Redirige a la página de inicio si los datos faltantes impiden
        completar el registro.
    """
    if not session.get("institutional_work"):
        abort(403)

    rider = riders.get_rider_by_id(user_id)
    if rider is None:
        flash("No se encontró al jinete. Reintente")
        return redirect(url_for("riders.index"))

    teachers_therapists = team.get_teachers_and_therapists()
    horse_riders = team.get_employees_by_job_position("Conductor")
    track_assistants = team.get_employees_by_job_position("Auxiliar de pista")
    horses = ecuestre.get_horses()
    faltantes = ""
    if not teachers_therapists:
        faltantes += " Profesor/as y/o terapeutas "
    if not horse_riders:
        faltantes += " Conductor@s de caballos "
    if not track_assistants:
        faltantes += " Auxiliares de pista "
    if not horses:
        faltantes += " Caballos "
    if faltantes != "":
        mensaje = f"""No puede completar esta sección de trabajo institucional
        ya que aún no hay{faltantes}cargados en el sistema"""
        flash(mensaje, "error")
        return redirect(url_for("auth.home"))

    context = {
        "rider": rider,
        "name": rider.name,
        "last_name": rider.last_name,
        "teachers_therapists": teachers_therapists,
        "horse_riders": horse_riders,
        "track_assistants": track_assistants,
        "horses": horses,
        "params": dict(),
    }

    return render_template("jinetes/registrar_trabajo.html", user_id=user_id, **context)


@bp.post("/subir_datos_trabajo/<int:user_id>")
@login_required
@permission_required("rider_create")
def new_institutional_work(user_id):
    """
    Procesa y guarda los datos de trabajo institucional de un jinete.

    Esta función recibe los datos del formulario, realiza validaciones y,
    si son correctos, guarda la información del trabajo institucional para
    el jinete correspondiente. Si ocurre algún error durante el proceso de
    validación, muestra un mensaje de error.

    Args:
        user_id (int): El ID del jinete para el cual se guardarán los datos de trabajo.

    Returns:
        render_template: Renderiza la plantilla 'registrar_trabajo.html' con el formulario
                         de trabajo institucional, mostrando mensajes de error si es necesario.
        flash: Muestra un mensaje de éxito al completar el registro correctamente.
        redirect: Redirige a la página principal si se completa con éxito el registro.
    """
    if not isinstance(user_id, int):
        abort(500)

    params = request.form
    rider = riders.get_rider_or_abort(user_id)
    teachers_therapists = team.get_teachers_and_therapists()
    horse_riders = team.get_employees_by_job_position("Conductor")
    track_assistants = team.get_employees_by_job_position("Auxiliar de pista")
    horses = ecuestre.get_horses()
    # VALIDACION
    message: List[str] = validate_institutional_work(params)
    context = {
        "rider": rider,
        "name": rider.name,
        "last_name": rider.last_name,
        "teachers_therapists": teachers_therapists,
        "horse_riders": horse_riders,
        "track_assistants": track_assistants,
        "horses": horses,
        "params": get_params_for_form(params),
    }
    if len(message) != 0:
        for error in message:
            flash(error, "error")

        return render_template(
            "jinetes/registrar_trabajo.html", user_id=user_id, **context
        )

    riders.create_work(params, rider)

    flash("¡Espectacular! Se ha completado el registro", "success")

    return redirect(url_for("riders.index"))


@bp.get("/datos_personales/<int:user_id>/trabajo_institucional")
@login_required
@permission_required("rider_show")
def show_edit_institutional_work(user_id):
    """
    Muestra el formulario para editar los datos de trabajo institucional de un jinete.

    Esta función permite editar los datos de trabajo institucional del jinete
    correspondiente. Verifica que todos los datos necesarios estén disponibles
    (profesores/terapeutas, conductores de caballos, auxiliares de pista y caballos).
    Si falta algún dato, se muestra un mensaje de error y se redirige al perfil del jinete.

    Args:
        user_id (int): El ID del jinete cuyos datos de trabajo institucional se van a editar.

    Returns:
        render_template: Renderiza la plantilla 'jinete_show.html' con el formulario de trabajo
                         institucional y los datos cargados para editar. Si faltan datos en el
                         sistema, redirige al perfil del jinete con un mensaje de error.
        flash: Muestra un mensaje de error si faltan datos en el sistema para completar el registro.
        redirect: Redirige al perfil del jinete si hay datos faltantes.
    """
    rider = riders.get_rider_or_abort(user_id)
    teachers_therapists = team.get_teachers_and_therapists()
    horse_riders = team.get_employees_by_job_position("Conductor")
    track_assistants = team.get_employees_by_job_position("Auxiliar de pista")
    horses = ecuestre.get_horses()

    faltantes = ""
    if not teachers_therapists:
        faltantes += " <Profesor/as y/o terapeutas> "

    if not horse_riders:
        faltantes += " <Conductor@s de caballos> "

    if not track_assistants:
        faltantes += " <Auxiliares de pista> "

    if not horses:
        faltantes += " <Caballos> "

    if faltantes != "":
        mensaje = f"""No puede completar esta sección ya
            que aún no hay {faltantes} cargados en el sistema"""
        flash(mensaje, "error")
        return redirect(url_for("riders.show_rider", user_id=user_id))

    work: InstitutionalWork = rider.institutional_work
    if work is not None:
        params = {
            "proposal": work.proposal,
            "headquarters": work.headquarters,
            "monday": work.monday,
            "tuesday": work.tuesday,
            "wednesday": work.wednesday,
            "thursday": work.thursday,
            "friday": work.friday,
            "saturday": work.saturday,
            "sunday": work.sunday,
            "teacher_therapist_id": work.teacher_therapist_id,
            "horse_rider_id": work.horse_conductor_id,
            "horse_id": work.horse_id,
            "track_assistant_id": work.track_assistant_id,
        }
    else:
        params = dict()

    context = {
        "info_general": True,
        "trabajo_institucional": True,
        "rider": rider,
        "teachers_therapists": teachers_therapists,
        "horse_riders": horse_riders,
        "track_assistants": track_assistants,
        "horses": horses,
        "params": params,
    }

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.post("/datos_personales/<int:user_id>/trabajo_institucional")
@login_required
@permission_required("rider_create")
def edit_institutional_work(user_id):
    """
    Procesa y guarda los datos editados de trabajo institucional de un jinete.

    Esta función recibe los datos del formulario de trabajo institucional, valida los mismos,
    y los guarda en el sistema. Si los datos no son válidos, muestra un mensaje de error y
    vuelve a cargar el formulario. Si los datos son correctos, se actualiza o crea el registro
    de trabajo institucional del jinete.

    Args:
        user_id (int): El ID del jinete cuyos datos de trabajo institucional se van a
        guardar o actualizar.

    Returns:
        render_template: Renderiza la plantilla 'jinete_show.html' con los datos del formulario,
                         mostrando mensajes de error si es necesario.
        flash: Muestra un mensaje de éxito si los datos se han guardado correctamente.
        redirect: Redirige a la vista de detalle del jinete si la operación es exitosa.
    """
    rider = riders.get_rider_or_abort(user_id)
    teachers_therapists = team.get_teachers_and_therapists()
    horse_riders = team.get_employees_by_job_position("Conductor")
    track_assistants = team.get_employees_by_job_position("Auxiliar de pista")
    horses = ecuestre.get_horses()

    params = request.form
    message: List[str] = validate_institutional_work(params)
    context = {
        "info_general": True,
        "trabajo_institucional": True,
        "rider": rider,
        "teachers_therapists": teachers_therapists,
        "horse_riders": horse_riders,
        "track_assistants": track_assistants,
        "horses": horses,
        "params": get_params_for_form(request.form),
    }
    if len(message) != 0:
        for error in message:
            flash(error, "error")

        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    if rider.institutional_work is not None:
        riders.update_work(params, rider.institutional_work)
    else:
        riders.create_work(params, rider)

    flash("Datos de trabajo institucional actualizados exitosamente", "success")

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


def get_params_for_form(params):
    """Devuelve el diccionario hecho para la renderización del template"""
    params_dict = params.to_dict()
    params_dict["monday"] = "monday" in params.getlist("days_of_the_week")
    params_dict["tuesday"] = "tuesday" in params.getlist("days_of_the_week")
    params_dict["wednesday"] = "wednesday" in params.getlist("days_of_the_week")
    params_dict["thursday"] = "thursday" in params.getlist("days_of_the_week")
    params_dict["friday"] = "friday" in params.getlist("days_of_the_week")
    params_dict["saturday"] = "saturday" in params.getlist("days_of_the_week")
    params_dict["sunday"] = "sunday" in params.getlist("days_of_the_week")
    params_dict["teacher_therapist_id"] = params.get("teacher_therapist")
    params_dict["horse_rider_id"] = params.get("horse_riders")
    params_dict["horse_id"] = params.get("horse")
    params_dict["track_assistant_id"] = params.get("track_assistant")

    return params_dict


@bp.post("/get_caballos")
@login_required
@permission_required("rider_create")
def get_caballos():
    """
    Obtiene una lista de caballos filtrada por sede y tipo de jinete.

    Esta función maneja la solicitud POST que recibe parámetros para filtrar los caballos
    disponibles según la sede y el tipo de propuesta (rider_type). Si los parámetros son
    "undefined", se convierten a `None` para realizar una búsqueda sin filtrar esos valores.


    Returns:
        jsonify: Devuelve una respuesta en formato JSON con una lista de caballos que coinciden
                 con los filtros de sede y tipo de jinete, donde cada caballo tiene un ID,
                 nombre y sede.
    """
    sede = request.form.get("headquarters")
    if sede == "undefined":  # Verifica si sede es "undefined" y lo convierte a None
        sede = None

    rider_type = request.form.get("proposal")
    if (
        rider_type == "undefined"
    ):  # Verifica si rider_type es "undefined" y lo convierte a None
        rider_type = None

    horses = ecuestre.get_horses_by_headquarters_and_proposal(
        headquarters=sede, proposal=rider_type
    )

    # Convertir los resultados a JSON
    horses_data = [
        {"id": horse.id, "name": horse.name, "sede": horse.sede} for horse in horses
    ]

    return jsonify(horses_data)
