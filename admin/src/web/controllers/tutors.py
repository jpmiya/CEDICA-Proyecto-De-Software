import secrets
from typing import List

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.core import riders
from src.core.riders.rider import Rider
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.exceptions import (
    RiderNotFoundException,
    SameTutorException,
)
from src.web.validators.tutors_validations import validate_tutors


bp = Blueprint("tutors", __name__, url_prefix="/tutores")


def get_rider_or_abort(user_id):
    """Obtiene el jinete por ID o lanza un error 403 si no se encuentra."""
    try:
        rider: Rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("No se puede acceder al jinete solicitado, reintente", "error")
        abort(403)
    return rider


def manage_tutors_for_rider(params, rider):
    """
    Gestiona los tutores de un jinete, asignando o actualizando los tutores primarios y secundarios
    según los parámetros proporcionados.
    Si el jinete no tiene un tutor asignado, se crea uno nuevo;
    de lo contrario, se actualiza el tutor existente. Además, maneja la relación entre el jinete y
    sus tutores.

    Parameters:
        params (dict): Diccionario con los parámetros necesarios para gestionar los tutores.
        rider (Rider): Objeto jinete al que se le asignarán o actualizarán los tutores.

    Raises:
        SameTutorException: Sí se intenta asignar el mismo tutor como primario y secundario.
    """
    # Lo busco en la BD
    tutor_primario = riders.find_tutor_by_dni(int(params.get("dni_primario")))

    # Si el jinete no tiene un tutor asignado
    if not rider.primary_tutor:
        # Si existe la persona, lo actualizo
        if tutor_primario is not None:
            tutor_primario = riders.update_tutor(
                params=params, tutor=tutor_primario, primario=True
            )
        # Si no, lo creo
        else:
            tutor_primario = riders.create_tutor(params=params, primario=True)
        # Lo añado como tutor primario del jinete
        riders.create_kinship(
            rider=rider,
            tutor=tutor_primario,
            primario=True,
            kinship=params.get("parentesco_primario"),
        )
    else:
        vinculo = riders.find_connection_rider_tutor(rider.id, rider.primary_tutor.id)
        # Si es el mismo DNI
        if rider.primary_tutor.dni == int(params.get("dni_primario")):
            # Actualizo
            riders.update_tutor(params=params, tutor=tutor_primario, primario=True)
            # Renuevo vínculo
            riders.update_kinship(vinculo, params.get("parentesco_primario"))
        # Sino, si el DNI es diferente pero le pertenece al tutor secundario
        elif rider.secondary_tutor and rider.secondary_tutor.dni == int(
            params.get("dni_primario")
        ):
            raise SameTutorException()
        # Si no
        else:
            # Eliminar vínculo
            riders.delete_kinship(vinculo)
            # Sí existe en la BD
            tutor_primario = riders.find_tutor_by_dni(int(params.get("dni_primario")))
            if tutor_primario is not None:
                # Actualizar
                tutor_primario = riders.update_tutor(
                    params=params, tutor=tutor_primario, primario=True
                )
            # Si no existe
            else:
                tutor_primario = riders.create_tutor(params, primario=True)
            # Conectar
            riders.create_kinship(
                rider=rider,
                tutor=tutor_primario,
                primario=True,
                kinship=params.get("parentesco_primario"),
            )

    # -------------------------------- Segundo tutor --------------------------------------
    if params.get("second_tutor_enabled") == "yes":
        # Lo busco en la BD
        tutor_secundario = riders.find_tutor_by_dni(int(params.get("dni_secundario")))

        if not rider.secondary_tutor:
            # Si existe, lo actualizo
            if tutor_secundario is not None:
                tutor_secundario = riders.update_tutor(
                    params=params, tutor=tutor_secundario, primario=False
                )
            # Si no, lo creo
            else:
                tutor_secundario = riders.create_tutor(params=params, primario=False)
            # Lo añado como tutor secundario del jinete
            riders.create_kinship(
                rider=rider,
                tutor=tutor_secundario,
                primario=False,
                kinship=params.get("parentesco_secundario"),
            )
        else:
            vinculo = riders.find_connection_rider_tutor(
                rider.id, rider.secondary_tutor.id
            )
            # Si es el mismo DNI
            if rider.secondary_tutor.dni == int(params.get("dni_secundario")):
                # Actualizo
                riders.update_tutor(
                    params=params, tutor=tutor_secundario, primario=False
                )
                # Renuevo vínculo
                riders.update_kinship(vinculo, params.get("parentesco_secundario"))
            # Sino, si el DNI es diferente pero le pertenece al tutor primario
            elif rider.primary_tutor.dni == int(params.get("dni_secundario")):
                raise SameTutorException()
            # Si no
            else:
                # Eliminar vínculo
                riders.delete_kinship(vinculo)
                # Sí existe en la BD
                if tutor_secundario is not None:
                    # Actualizar
                    tutor_secundario = riders.update_tutor(
                        params=params, tutor=tutor_secundario, primario=False
                    )
                # Si no existe
                else:
                    tutor_secundario = riders.create_tutor(
                        params=params, primario=False
                    )
                # Conectar
                riders.create_kinship(
                    rider=rider,
                    tutor=tutor_secundario,
                    primario=False,
                    kinship=params.get("parentesco_secundario"),
                )


@bp.get("/subir_datos_tutores/<int:user_id>")
@login_required
@permission_required("rider_create")
def show_new_tutor(user_id):
    """
    Muestra el formulario para registrar los tutores de un jinete.

    Esta función chequea que el token proporcionado en la URL coincida con el token de sesión
    y luego carga la información del jinete. Si el jinete no se encuentra,
    se muestra un mensaje de error.

    Parameters:
        user_id (int): El ID del jinete al que se le van a registrar los tutores.

    Returns:
        Renderiza la plantilla 'registrar_tutores.html' con el formulario de los tutores y
        los datos del jinete.

    Raises:
        abort(403): Si el token no coincide con el de sesión, se prohíbe el acceso.
    """
    token = request.args.get("token")
    if token != session.get("tutors"):
        # Prohibir el acceso
        abort(403)
    try:
        rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("No se pudo encontrar al jinete", "error")
        return render_template(url_for("home.html"))

    context = {"rider": rider, "params": dict()}

    return render_template(
        "jinetes/registrar_tutores.html", user_id=user_id, token=token, **context
    )


@bp.post("/subir_datos_tutores/<int:user_id>")
@login_required
@permission_required("rider_create")
def new_tutor(user_id: int):
    """
    Registra un nuevo tutor para un jinete.

    Esta función valida los datos del tutor proporcionados en el formulario.
    Si los datos son correctos, se gestionan los tutores del jinete.
    En caso de que haya un error, se muestra un mensaje de error.
    Si el tutor es el mismo para el jinete primario y secundario, se lanza una excepción.

    Parameters:
        user_id (int): El ID del jinete al que se le va a registrar el nuevo tutor.

    Returns:
        Renderiza la plantilla 'registrar_tutores.html' con el formulario de los tutores
        y los datos del jinete si hay un error o después de registrar correctamente el tutor.
        Redirige a la página de trabajos institucionales si el proceso es exitoso.

    Raises:
        SameTutorException: Sí se intenta agregar el mismo tutor como primario y
        secundario para el mismo jinete.
    """
    params = request.form
    try:
        rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        abort(403)

    context = {
        "name": rider.name,
        "last_name": rider.last_name,
        "params": params,
        "rider": rider,
    }

    message: List[str] = validate_tutors(params)
    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return render_template(
            "jinetes/registrar_tutores.html", user_id=user_id, **context
        )
    try:
        manage_tutors_for_rider(params, rider)
    except SameTutorException:
        flash("No puede agregar dos veces el mismo tutor a un solo jinete", "error")
        return render_template(
            "jinetes/registrar_tutores.html", user_id=user_id, **context
        )

    flash(
        f"""¡Genial! Seguiremos con el trabajo en CEDICA de {
          rider.name} {rider.last_name}""",
        "success",
    )
    session["institutional_work"] = secrets.token_urlsafe(16)

    return redirect(
        url_for("institutional_works.show_institutional_work", user_id=user_id)
    )


@bp.get("/datos_personales/<int:user_id>/tutores")
@login_required
@permission_required("rider_show")
def show_edit_tutors(user_id):
    """
    Muestra los datos actuales de los tutores de un jinete y permite su edición.

    Esta función obtiene la información del jinete especificado por su ID y
    verifica si tiene un tutor primario
    y/o secundario. Si existen, muestra sus datos completos en el formulario
    de edición. Si no existen tutores,
    el formulario se muestra vacío.

    Parameters:
        user_id (int): El ID del jinete cuyos tutores se van a mostrar y editar.

    Returns:
        Renderiza la plantilla 'jinete_show.html' con la información actual de los tutores
        y el jinete.
    """
    rider = riders.get_rider_or_abort(user_id)
    tutor_primario = rider.primary_tutor
    parentesco_primario = (
        riders.find_connection_rider_tutor(rider.id, tutor_primario.id)
        if tutor_primario
        else None
    )

    tutor_secundario = rider.secondary_tutor

    parentesco_secundario = (
        riders.find_connection_rider_tutor(rider.id, tutor_secundario.id)
        if tutor_secundario
        else None
    )
    if tutor_primario:
        params = {
            "second_tutor_enabled": "yes" if tutor_secundario else "no",
            "dni_primario": tutor_primario.dni,
            "parentesco_primario": parentesco_primario.kinship,
            "nombre_primario": tutor_primario.name,
            "apellido_primario": tutor_primario.last_name,
            "provincia_primario": tutor_primario.province,
            "localidad_primario": tutor_primario.locality,
            "calle_primario": tutor_primario.street,
            "numero_calle_primario": tutor_primario.street_number,
            "piso_primario": tutor_primario.floor if tutor_primario.floor else "",
            "departamento_primario": (
                tutor_primario.department_number
                if tutor_primario.department_number
                else ""
            ),
            "celular_primario": tutor_primario.phone_number,
            "email_primario": tutor_primario.email,
            "escolaridad_primario": tutor_primario.scholarity_level,
            "ocupacion_primario": tutor_primario.occupation,
            # ---------------------------------
            "dni_secundario": tutor_secundario.dni if tutor_secundario else "",
            "parentesco_secundario": (
                parentesco_secundario.kinship if parentesco_secundario else ""
            ),
            "nombre_secundario": tutor_secundario.name if tutor_secundario else "",
            "apellido_secundario": (
                tutor_secundario.last_name if tutor_secundario else ""
            ),
            "provincia_secundario": (
                tutor_secundario.province if tutor_secundario else ""
            ),
            "localidad_secundario": (
                tutor_secundario.locality if tutor_secundario else ""
            ),
            "calle_secundario": tutor_secundario.street if tutor_secundario else "",
            "numero_calle_secundario": (
                tutor_secundario.street_number if tutor_secundario else ""
            ),
            "piso_secundario": (
                tutor_secundario.floor
                if tutor_secundario and tutor_secundario.floor
                else ""
            ),
            "departamento_secundario": (
                tutor_secundario.department_number
                if tutor_secundario and tutor_secundario.floor
                else ""
            ),
            "celular_secundario": (
                tutor_secundario.phone_number if tutor_secundario else ""
            ),
            "email_secundario": tutor_secundario.email if tutor_secundario else "",
            "escolaridad_secundario": (
                tutor_secundario.scholarity_level if tutor_secundario else ""
            ),
            "ocupacion_secundario": (
                tutor_secundario.occupation if tutor_secundario else ""
            ),
        }
    else:
        params = dict()

    context = {"info_general": True, "tutores": True, "rider": rider, "params": params}

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.post("/datos_personales/<int:user_id>/tutores")
@login_required
@permission_required("rider_create")
def edit_tutors(user_id: int):
    """
    Actualiza los datos de los tutores de un jinete.

    Esta función recibe los datos enviados por el formulario, chequea la información de los tutores
    y la actualiza en la base de datos. Si se encuentra un error, se muestra un mensaje de
    error al usuario.
    Si la actualización es exitosa, se muestra un mensaje de éxito.

    Parameters:
        user_id (int): El ID del jinete cuyos tutores se van a actualizar.

    Returns:
        Renderiza la plantilla 'jinete_show.html' con los datos actualizados o muestra
        un mensaje de error si
        hubo algún problema durante la actualización.
    """
    params = request.form
    rider = riders.get_rider_or_abort(user_id=user_id)
    context = {
        "info_general": True,
        "tutores": True,
        "name": rider.name,
        "last_name": rider.last_name,
        "params": params,
        "rider": rider,
    }
    message: List[str] = validate_tutors(params)

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    try:
        manage_tutors_for_rider(params, rider)
    except SameTutorException:
        flash("No puede agregar dos veces el mismo tutor a un solo jinete", "error")
        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    flash("Datos de tutores actualizados exitosamente", "success")

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)
