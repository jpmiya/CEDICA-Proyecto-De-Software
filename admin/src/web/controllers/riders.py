import io
import os
import secrets
from typing import Dict, List

from flask import (
    Blueprint,
    current_app,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.datastructures import FileStorage
from urllib3.exceptions import MaxRetryError

from src.core import riders
from src.core.database import db
from src.core.functions import check_file_size, check_valid_format
from src.core.riders.rider import Rider
from src.core.riders.rider_document import RiderDocument
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.exceptions import RiderNotFoundException
from src.web.validators.document_rider_validations import (
    check_modify_document,
    check_upload_link,
)
from src.web.validators.personal_data_validations import validate_personal_data
from src.web.validators.riders_listing import check_search_rider_params


bp = Blueprint("riders", __name__, url_prefix="/jinetes_amazonas")


@bp.get("/")
@bp.get("/index/<int:page>")
@login_required
@permission_required("rider_index")
def index(page: int = 1) -> str:
    """
    Muestra la lista de jinetes o amazonas paginada con filtros de búsqueda.

    Esta vista permite ver la lista de jinetes o amazonas, con la opción de
    filtrarlos por nombre, apellido, DNI, profesionales o empleados, y de
    ordenarlos por diferentes criterios. La paginación es aplicada a los resultados
    y se permite la navegación entre páginas.

    Parámetros:
        - page: Página actual para la paginación (valor por defecto: 1).

    Si alguno de los parámetros de búsqueda no es válido, se redirige al usuario
    a la página de inicio con un mensaje de error.
    """
    if not isinstance(page, int):
        abort(400)

    if page == 0:
        flash("No existe esa página, reintente", "error")
        return redirect(url_for("riders.index"))

    params = {
        "name": request.args.get("name", ""),
        "last_name": request.args.get("last_name", ""),
        "dni": request.args.get("dni", ""),
        "employee": request.args.get("employee", ""),
        "order": request.args.get("order", "apellidoA-Z"),
    }
    # Validamos los parámetros
    message: List[str] = check_search_rider_params(params)

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return redirect(url_for("riders.index", _external=True))

    if params["order"] == "nombreA-Z":
        query = riders.get_riders_ordered_by_name(ascendent=True)
    elif params["order"] == "nombreZ-A":
        query = riders.get_riders_ordered_by_name(ascendent=False)
    elif params["order"] == "apellidoA-Z":
        query = riders.get_riders_ordered_by_last_name(ascendent=True)
    elif params["order"] == "apellidoZ-A":
        query = riders.get_riders_ordered_by_last_name(ascendent=False)
    else:
        query = riders.get_riders()
    if params["dni"] != "":
        query = query.filter(Rider.dni == params["dni"])
    if params["name"] != "":
        query = query.filter(Rider.name.ilike(f'%{params["name"]}%'))

    if params["last_name"]:
        query = query.filter(Rider.last_name.ilike(f'%{params["last_name"]}%'))
    if params["employee"]:
        query = riders.filter_by_professionals(query, params["employee"])

    riders_paginated = db.paginate(
        query,
        page=page,
        per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
        error_out=False,
    )
    cantidad_de_pages = riders_paginated.pages
    if cantidad_de_pages != 0 and cantidad_de_pages < page:
        flash(f"No existe la página {page}, redirigiendo a la última página", "error")
        riders_paginated = db.paginate(
            query,
            page=cantidad_de_pages,
            per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
            error_out=False,
        )

    next_page = (
        url_for("riders.index", page=riders_paginated.next_num, **params)
        if riders_paginated.has_next
        else None
    )
    prev_page = (
        url_for("riders.index", page=riders_paginated.prev_num, **params)
        if riders_paginated.has_prev
        else None
    )

    return render_template(
        "jinetes/listado.html",
        riders_paginated=riders_paginated,
        next_page=next_page,
        prev_page=prev_page,
        params=params,
    )


@bp.post("/eliminar_jinete")
@login_required
@permission_required("rider_delete")
def delete_rider():
    """
    Elimina un jinete o amazona de la base de datos.

    Esta vista permite eliminar un jinete o amazona de la base de datos
    después de verificar su existencia. También elimina los documentos o enlaces
    asociados con el jinete de los sistemas remotos.

    Si el jinete no se encuentra o los datos proporcionados no son válidos,
    se muestra un mensaje de error. Si el proceso es exitoso, se muestra un mensaje
    de confirmación.
    """
    id_received: str = request.form.get("rider_id")
    if not isinstance(id_received, str) or not id_received.isdigit():
        flash(
            "Hubo un error, no se pasó correctamente al jinete/amazona a eliminar. Reintente",
            "error",
        )
        return redirect(url_for("riders.index"))
    rider_id = int(id_received)
    rider: Rider = riders.get_rider_by_id(rider_id)
    if rider is None:
        flash("No se encontró el jinete a eliminar, reintente", "error")
        return redirect(url_for("riders.index"))
    # Borrar todos los documentos / enlaces del jinete
    if rider.charges:
        flash(
            """No se puede eliminar al jinete porque tiene cobros asociados. 
            Elimine los cobros primero.""",
            "error",
        )
        return redirect(url_for("riders.index"))

    riders.drop_documents_from_remote(rider_id)
    riders.delete_rider(rider_id)

    flash("El jinete ha sido eliminado correctamente", "info")

    return redirect(url_for("riders.index"))


@bp.get("/registrar_jinetes_amazonas")
@login_required
@permission_required("rider_create")
def show_new_rider():
    """
    Renderiza el formulario para registrar un nuevo jinete o amazona.

    Esta vista muestra el formulario necesario para registrar un nuevo jinete o amazona
    en el sistema. El formulario permite capturar los datos correspondientes del jinete
    y, si se completa correctamente, crear una nueva entrada en la base de datos.

    Requiere que el usuario esté autenticado y tenga el permiso 'rider_create'.
    """
    context = {"params": dict()}

    return render_template("jinetes/registrar_jinete_amazona.html", **context)


@bp.post("/registrar_jinetes_amazonas")
@login_required
@permission_required("rider_create")
def new_rider():
    """Crea un nuevo jinete o amazona y redirige a la carga de datos de discapacidad."""

    params = request.form
    # Validar datos
    message: List[str] = validate_personal_data(params)
    if len(message) > 0:
        for error in message:
            flash(error, "error")

        context = {"params": params}
        return render_template("jinetes/registrar_jinete_amazona.html", **context)

    # ..........................
    rider = riders.create_rider(params)

    session["disability_token"] = secrets.token_urlsafe(16)

    mensaje = f"""¡ Se ha añadido a {
        rider.name} !. Ahora carguemos sus datos de discapacidad y beneficios gubernamentales"""

    flash(mensaje, "success")

    return redirect(
        url_for(
            "disabilities.show_new_disability_data",
            user_id=rider.id,
            token=session["disability_token"],
        )
    )


@bp.get("/datos_personales/<int:user_id>")  # type: ignore
@login_required
@permission_required("rider_show")
def show_rider(user_id):
    """
    Muestra los datos personales de un jinete o amazona.

    Esta función obtiene los datos del jinete utilizando su ID y los muestra en la
    plantilla correspondiente. Los datos incluyen información como DNI, nombre,
    dirección, contacto de emergencia, etc.

    Args:
        user_id (int): El ID del jinete cuya información se desea mostrar.

    Returns:
        str: La plantilla que muestra los datos del jinete.
    """
    rider = riders.get_rider_or_abort(user_id)
    params: dict = get_personal_data_params(rider=rider)

    context = {
        "info_general": True,
        "rider": rider,
        "datos_personales": True,
        "params": params,
    }

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.get("/datos_personales/<int:user_id>/datos_personales")
@login_required
@permission_required("rider_show")
def show_edit_personal_data(user_id):
    """
    Muestra el formulario para editar los datos personales de un jinete o amazona.

    Esta función permite a los usuarios editar los datos personales de un jinete,
    como el nombre, apellido, teléfono, etc., y mostrar los datos actuales para su modificación.

    Args:
        user_id (int): El ID del jinete cuyo formulario se desea mostrar.

    Returns:
        str: La plantilla que muestra el formulario de edición de datos del jinete.
    """
    rider = riders.get_rider_or_abort(user_id)
    params = get_personal_data_params(rider=rider)
    context: dict = {
        "info_general": True,
        "datos_personales": True,
        "rider": rider,
        "params": params,
    }

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


@bp.post("/datos_personales/<int:user_id>/datos_personales")
@login_required
@permission_required("rider_create")
def edit_personal_data(user_id):
    """
    Edita los datos personales de un jinete o amazona.

    Esta función recibe los datos modificados de un jinete y actualiza la información
    en la base de datos. En caso de error de validación, muestra un mensaje de error.

    Args:
        user_id (int): El ID del jinete cuyos datos se desean editar.

    Returns:
        str: La plantilla actualizada con los nuevos datos del jinete.
    """
    rider = riders.get_rider_or_abort(user_id)
    params = request.form
    context = {
        "info_general": True,
        "datos_personales": True,
        "rider": rider,
        "params": params,
    }
    message: List[str] = validate_personal_data(params, rider=rider, updating=True)
    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return render_template("jinetes/jinete_show.html", user_id=user_id, **context)

    rider = riders.update_rider(rider, params)
    context["params"] = get_personal_data_params(rider=rider)

    flash("Datos cambiados exitosamente", "success")

    return render_template("jinetes/jinete_show.html", user_id=user_id, **context)


def get_personal_data_params(rider: Rider) -> Dict[str, str]:
    """Obtener los datos del jinete en un diccionario para el cargado de un formulario"""
    params: dict = {  # type: ignore
        "dni": rider.dni,
        "name": rider.name,
        "last_name": rider.last_name,
        "birthday": rider.birthday,
        "province": rider.province,
        "locality": rider.locality,
        "province_address": rider.province_address,
        "locality_address": rider.locality_address,
        "street": rider.street,
        "house_num": rider.house_num,
        "dpto": rider.dpto if rider.dpto is not None else "",
        "actual_tel": rider.actual_tel,
        "emergency_contact_name": rider.emergency_contact_name,
        "emergency_contact_tel": rider.emergency_contact_tel,
        "scholarship_holder": "yes" if rider.scholarship_holder else "no",
        "rider_observations": rider.rider_observations,
    }

    return params


@bp.get("/datos_personales/<int:user_id>/documentos")
@bp.get("/datos_personales/<int:user_id>/documentos/<int:page>")
@login_required
@permission_required("rider_show")
def show_documentation(user_id: int, page: int = 1):
    """
    Muestra la documentación asociada a un jinete o amazona.

    Esta función permite visualizar los documentos de un jinete. Los documentos
    se pueden filtrar por título, tipo y orden (ascendente/descendente) según
    los parámetros proporcionados en la URL. También se implementa paginación
    para los resultados.

    Args:
        user_id (int): El ID del jinete cuyas documentos se desean mostrar.
        page (int): El número de página para la paginación de los resultados
        (opcional, por defecto es 1).

    Returns:
        str: La plantilla que muestra la documentación del jinete.
    """
    try:
        rider = riders.get_rider_by_id(user_id)
    except RiderNotFoundException:
        flash("No se puede acceder al jinete solicitado, reintente", "error")
        abort(403)

    sort = request.args.get("sort", "mas_recientes")
    title = request.args.get("title", "")
    document_type = request.args.get("type", "")

    params = {"sort": sort, "title": title, "type": document_type}

    # Validaciones
    if sort not in ["nombre_asc", "nombre_desc", "mas_recientes", "mas_viejos", ""]:
        flash("Seleccionó un orden inválido", "error")
        return redirect(url_for("riders.show_edit_personal_data", user_id=user_id))

    document_types_valid = [
        "",
        "entrevista",
        "evaluacion",
        "planificaciones",
        "evolucion",
        "cronicas",
        "documental",
    ]

    if document_type not in document_types_valid:
        flash("Seleccionó un orden inválido", "error")
        return redirect(url_for("riders.show_edit_personal_data", user_id=user_id))

    query = riders.get_documents_by_rider_id(
        rider_id=user_id, title=title, doc_type=document_type, order_by=sort
    )

    docs_paginated = db.paginate(
        query,
        page=page,
        per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
        error_out=False,
    )

    if docs_paginated.pages != 0 and page > docs_paginated.pages:
        flash("Esta página no existe, reintente", "error")
        return redirect(url_for("riders.show_documentation", user_id=user_id, page=1))

    next_page = (
        url_for(
            "riders.show_documentation",
            page=docs_paginated.next_num,
            user_id=user_id,
            **params,
        )
        if docs_paginated.has_next
        else None
    )
    prev_page = (
        url_for(
            "riders.show_documentation",
            page=docs_paginated.prev_num,
            user_id=user_id,
            **params,
        )
        if docs_paginated.has_prev
        else None
    )

    return render_template(
        "jinetes/jinete_documentacion.html",
        user_id=user_id,
        name=rider.name,
        last_name=rider.last_name,
        docs_paginated=docs_paginated,
        next_page=next_page,
        prev_page=prev_page,
        params=params,
        page=page,
    )


@bp.get("/datos_personales/<int:user_id>/subir_enlace")
@login_required
@permission_required("rider_create")
def show_upload_link(user_id: int):
    """
    Muestra el formulario para subir un enlace asociado a un jinete o amazona.

    Esta función presenta el formulario donde el usuario puede subir un enlace
    relacionado con el jinete, proporcionando la posibilidad de agregar información adicional.

    Args:
        user_id (int): El ID del jinete al que se le va a asociar el enlace.

    Returns:
        str: La plantilla para subir un enlace para el jinete.
    """
    rider = riders.get_rider_or_abort(str(user_id))
    return render_template(
        "jinetes/subir_enlace.html", user_id=user_id, rider=rider, params=dict()
    )


@bp.get("/datos_personales/<int:user_id>/subir_doc")
@login_required
@permission_required("rider_create")
def show_upload_document(user_id: int):
    """
    Muestra el formulario para subir un documento asociado a un jinete o amazona.

    Esta función permite al usuario cargar un documento relacionado con el jinete
    proporcionando el formulario necesario para completar el proceso.

    Args:
        user_id (int): El ID del jinete al que se le va a asociar el documento.

    Returns:
        str: La plantilla para subir un documento para el jinete.
    """
    rider = riders.get_rider_or_abort(user_id=user_id)

    return render_template(
        "jinetes/subir_doc.html", user_id=user_id, params=dict(), rider=rider
    )


@bp.post("/datos_personales/<int:user_id>/subir_doc")
@login_required
@permission_required("rider_create")
def upload_document(user_id):
    """
    Permite subir un documento asociado a un jinete o amazona.

    Esta función gestiona la carga de un documento para un jinete. Verifica que el archivo
    cumpla con los requisitos de tamaño y formato, que el jinete exista y que se ingrese
    un título y tipo de documento válidos. Después, guarda el documento en la base de datos.

    Args:
        user_id (int): El ID del jinete al que se va a asociar el documento.

    Returns:
        str: La plantilla para subir el documento o una redirección a la vista de documentación
        del jinete.
    """
    rider = riders.get_rider_by_id(user_id)

    params = request.form
    file_uploaded = request.files.get("document", "")

    context = {"params": params, "rider": rider}

    # Chequeo de jinete/amazona
    if rider is None:
        flash("Hubo un error y no se pudo encontrar al usuario", "error")
        abort(403)

    # Chequeo de archivo seleccionado
    if (
        not file_uploaded
        or not isinstance(file_uploaded, FileStorage)
        or file_uploaded.filename == ""
    ):
        flash("No se seleccionó ningún archivo.", "error")
        return render_template("jinetes/subir_doc.html", user_id=user_id, **context)
    if not check_file_size(file_uploaded):
        flash("El archivo seleccionado excede el límite de 15 MB", "error")
        return render_template("jinetes/subir_doc.html", user_id=user_id, **context)

    # Chequeo de formato válido
    if not check_valid_format(file_uploaded):
        flash(
            """No aceptamos archivos de esa extensión.
            Sólamente aceptamos: PDF, DOC, DOCX, XLS, XLSX, JPEG.""",
            "error",
        )

        return render_template("jinetes/subir_doc.html", user_id=user_id, **context)

    # Chequeo de titulo
    if params.get("title") == "":
        flash("Ingrese un título para el archivo", "error")
        return render_template("jinetes/subir_doc.html", user_id=user_id, **context)

    # Chequeo de tipo de documento
    document_types_valid = [
        "entrevista",
        "evaluacion",
        "planificaciones",
        "evolucion",
        "cronicas",
        "documental",
    ]
    if params.get("document_type") not in document_types_valid:
        flash("Ingrese un tipo válido para el documento", "error")
        return render_template("jinetes/subir_doc.html", user_id=user_id, **context)

    try:
        riders.create_document(
            title=params.get("title"),
            doc_type=params.get("document_type"),
            format="file",
            source=file_uploaded,
            rider_id=user_id,
        )
        flash(
            f"""Se subio correctamente el archivo {
              params.get('title')}""",
            "success",
        )
    except MaxRetryError:
        flash("No se pudo establecer una conexión con nuestra base de datos", "error")

    return redirect(url_for("riders.show_documentation", user_id=user_id))


@bp.post("/datos_personales/<int:user_id>/subir_link")
@login_required
@permission_required("rider_update")
def upload_link(user_id):
    """
    Permite subir un enlace asociado a un jinete o amazona.

    Esta función permite al usuario subir un enlace que apunte a un documento relacionado
    con el jinete. Se valida que el enlace no esté vacío, que sea un URL válido y que
    el tipo de documento seleccionado sea correcto.

    Args:
        user_id (int): El ID del jinete al que se le va a asociar el enlace.

    Returns:
        str: La plantilla para subir el enlace o una redirección a la vista de documentación
        del jinete.
    """
    rider = riders.get_rider_by_id(user_id)
    params = request.form

    title = params.get("title", "")
    link = params.get("link", "")
    document_type = params.get("document_type", "")

    context = {"params": params, "rider": rider}

    messages: List[str] = check_upload_link(
        rider=rider, title=title, link=link, document_type=document_type
    )

    if len(messages) > 0:
        for error in messages:
            flash(error, "error")

        return render_template("jinetes/subir_enlace.html", user_id=user_id, **context)

    riders.add_link(
        title=title, link=link, document_type=document_type, rider_id=user_id
    )

    flash("Se ha subido el enlace correctamente", "success")

    return redirect(url_for("riders.show_documentation", user_id=user_id))


@bp.post("/datos_personales/<int:user_id>/descargar_doc")
@login_required
@permission_required("rider_update")
def download_rider_file(user_id: int) -> Response:
    """
    Ruta para descargar un documento de un jinete desde MinIO.

    Esta ruta maneja la descarga de un documento específico del jinete,
    utilizando el ID del documento proporcionado. Si se encuentra el
    documento en MinIO, se prepara para la descarga y se responde con
    el archivo solicitado.

    Parámetros:
        user_id (int): ID del jinete del cual se quiere descargar el documento.

    Retorna:
        Response: Respuesta con el archivo listo para ser descargado.

    Si ocurre un error, se muestra un mensaje flash con el error y
    se redirige a la página de documentos del jinete.
    """
    params = request.form
    document_id = params.get("document_id")

    try:
        # Descargar el archivo desde MinIO
        response, document = riders.download_document(document_id)

        archivo = io.BytesIO(response.read())
        archivo.seek(0)

        extension: str = os.path.splitext(document.source)[1]  # Extrae la extensión
        if not extension.startswith("."):  # Asegurarse de que tenga un punto
            extension = f".{extension}"

        filename = f"{document.title}{extension}"

        return Response(
            archivo,
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/octet-stream",
            },
        )
    except ValueError as e:
        # Manejo de errores
        flash(f"Error al descargar el archivo: {e}", "error")

        return redirect(url_for("riders.show_documentation", user_id=user_id))


@bp.post("/datos_personales/<int:user_id>/modificar_doc")
@login_required
@permission_required("rider_update")
def modify_document(user_id: int) -> Response:
    """
    Ruta para modificar los detalles de un documento de un jinete.

    Esta ruta permite modificar el título y el tipo de un documento
    existente, especificado por el ID del documento.

    Parámetros:
        user_id (int): ID del jinete cuyo documento se va a modificar.

    Retorna:
        jsonify: Respuesta JSON indicando el éxito o error de la operación.

    Si ocurre un error, se muestra un mensaje flash con el error y
    se devuelve un código de estado 404.
    """
    data = request.get_json()
    if not data:
        flash("No se mandó la información necesaria", "error")
        return jsonify({"success": False, "message": "data"})

    message: List[str] = check_modify_document(
        user_id=user_id,
        document_id=data.get("document_id"),
        title=data.get("title"),
        doc_type=data.get("document_type"),
    )

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return jsonify({"success": False, "message": message})

    try:
        riders.edit_document(
            document_id=data.get("document_id"),
            title=data.get("title"),
            doc_type=data.get("document_type"),
        )
        flash("Se ha modificado el documento correctamente", "success")

        return jsonify({"success": True})
    except MaxRetryError:
        flash("No se pudo conectar a la base de datos", "error")

        return jsonify(
            {"success": False, "message": "No se pudo conectar a a base de datos"}
        )


@bp.post("/datos_personales/<int:user_id>/eliminar_doc")
@login_required
@permission_required("rider_update")
def delete_document(user_id: int):
    """
    Ruta para eliminar un documento de un jinete.

    Esta ruta permite eliminar un documento de un jinete usando el
    ID del documento. Si el documento no se encuentra u ocurre un
    error durante la eliminación, se devuelve un mensaje de error.

    Parámetros:
        user_id (int): ID del jinete cuyo documento se desea eliminar.

    Retorna:
        jsonify: Respuesta JSON indicando el éxito o error de la operación.

    Si ocurre un error, se realiza un rollback y se muestra un mensaje flash
    con el error.
    """
    # Obtener los parámetros del formulario
    params = request.form

    document_id = params.get("document_id")

    # Validar si el documento existe
    document: RiderDocument = riders.get_document_by_id(document_id)
    if not document:
        flash("No se pudo encontrar el documento solicitado", "error")

        return jsonify({"success": False})

    try:
        riders.delete_document(document=document)
        flash("Documento eliminado exitosamente", "success")

        return redirect(url_for("riders.show_documentation", user_id=user_id))

    except RiderNotFoundException:
        # En caso de error, realizar rollback y mostrar mensaje de error
        flash("Error al eliminar el documento", "error")

        return jsonify({"success": False})
