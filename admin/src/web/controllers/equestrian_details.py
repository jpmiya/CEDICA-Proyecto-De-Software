import io
import os
from typing import Dict, List

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from urllib3.exceptions import MaxRetryError
from werkzeug.datastructures import FileStorage

from src.core import ecuestre, functions, team, users
from src.core.database import db
from src.core.ecuestre.horse import Horse
from src.core.ecuestre.horse_document import HorseDocument
from src.web.handlers.auth import login_required, permission_required
from src.web.validators.document_horse_validators import check_upload_link


bp = Blueprint("equestrian_details", __name__, url_prefix="/equestrian_details")


@bp.get("/")
@login_required
@permission_required("horse_show")
def details():
    """Renderiza los detalles de un caballo específico."""
    id = request.args.get("horse_id")
    if id.isdigit():
        horse = ecuestre.find_horse_by_id(id)
    else:
        horse = None

    if horse:
        entrenadores = team.get_employees_by_job_position("Entrenador de Caballos")
        conductores = team.get_employees_by_job_position("Conductor")
        if users.check_permission("horse_update"):
            return render_template(
                "equestrian/horse_details.html",
                horse=horse,
                entrenadores=entrenadores,
                conductores=conductores,
            )
        else:
            return render_template(
                "equestrian/horse_details_nomods.html",
                horse=horse,
                entrenadores=entrenadores,
                conductores=conductores,
            )
    else:
        flash("No existe el caballo", "error")

        return redirect(url_for("equestrian_dashboard.index"))


@bp.post("/edit_horse")
@login_required
@permission_required("horse_update")
def update_horse():
    """Modifica los atributos de un caballo y gestiona archivos adjuntos."""
    id = request.form.get("horse_id")
    if not id.isdigit():
        flash("ID invalida", "error")
        return redirect(url_for("equestrian_dashboard.index"))
    horse = ecuestre.find_horse_by_id(id)
    if not horse:
        flash("No existe el caballo", "error")
        return redirect(url_for("equestrian_dashboard.index"))
    attributes = {
        key: value
        for key, value in request.form.items()
        if key != "horse_id" and key != "files" and key != "file_titles"
    }

    messages: List[str] = ecuestre.check_create_horse_params(
        attributes["name"],
        attributes["birth_date"],
        attributes["gender"],
        attributes["breed"],
        attributes["fur"],
        attributes["acquisition_type"],
        attributes["entry_date"],
        attributes["sede"],
        attributes["rider_type"],
        attributes["trainer"],
        attributes["conductor"],
    )
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("equestrian_details.details", horse_id=id))

    ecuestre.modify_horse(horse, attributes)

    flash("Caballo modificado exitosamente", "success")

    return redirect(url_for("equestrian_dashboard.index"))


@bp.get("<int:horse_id>/horse_files")
@bp.get("<int:horse_id>/horse_files/<int:page>")
@login_required
@permission_required("horse_show")
def horse_files(horse_id: int, page: int = 1):
    """Renderiza los archivos asociados a un caballo específico."""
    if not isinstance(horse_id, int):
        flash("Parametros invalidos", "error")
        return redirect(url_for("equestrian_dashboard.index"))
    
    horse = ecuestre.find_horse_by_id(horse_id)
    if horse is None:
        flash("No existe el caballo", "error")
        return redirect(url_for("equestrian_dashboard.index"))

    search_value = request.args.get("search_value", "")
    document_type = request.args.get("document_type", "")
    order = request.args.get("order", "newer")

    pagination, documents = ecuestre.get_documents_by_horse_id(
        page=page,
        horse_id=horse_id,
        order=order,
        document_type=document_type,
        search_value=search_value,
    )
    params: Dict[str, str] = {
        "search_value": search_value,
        "document_type": document_type,
        "order": order,
    }
    next_page = (
        url_for(
            "equestrian_details.horse_files",
            page=pagination.next_num,
            horse_id=horse_id,
            **params,
        )
        if pagination.has_next
        else None
    )
    prev_page = (
        url_for(
            "equestrian_details.horse_files",
            page=pagination.prev_num,
            horse_id=horse_id,
            **params,
        )
        if pagination.has_prev
        else None
    )

    return render_template(
        "equestrian/files.html",
        horse=horse,
        params=params,
        documents=documents,
        pagination=pagination,
        prev_page=prev_page,
        next_page=next_page,
        page=page,
    )


@bp.get("/horse_files/upload_document/<int:horse_id>")
@login_required
@permission_required("horse_update")
def show_upload_document(horse_id: int):
    """Muestra el formulario para subir un documento."""
    horse: Horse = ecuestre.find_horse_by_id(horse_id=horse_id)
    if not horse:
        flash("Caballo no encontrado", "error")
        return redirect(url_for("equestrian_dashboard.index"))

    return render_template(
        "equestrian/upload_document.html", params=dict(), horse=horse
    )


@bp.post("/horse_files/upload_document/<int:horse_id>/upload")
@login_required
@permission_required("horse_update")
def upload_document(horse_id: int):
    """Sube un documento asociado a un caballo."""
    horse: Horse = ecuestre.find_horse_by_id(horse_id=horse_id)

    params = request.form
    file_uploaded = request.files.get("document", "")

    context = {"params": params, "horse": horse}

    if horse is None:
        flash("Hubo un error y no se pudo encontrar al caballo", "error")
        return redirect(url_for("equestrian_dashboard.index"))
    if (
        not file_uploaded
        or not isinstance(file_uploaded, FileStorage)
        or file_uploaded.filename == ""
    ):
        flash("No se seleccionó ningún archivo", "error")
        return render_template(
            "equestrian/upload_document.html", horse_id=horse_id, **context
        )
    if not functions.check_file_size(file_uploaded):
        flash("El archivo seleccionado excede el límite de 15 MB", "error")
        return render_template(
            "equestrian/upload_document.html", horse_id=horse_id, **context
        )

    if not functions.check_valid_format(file_uploaded):
        flash(
            """No aceptamos archivos de esa extensión.
            Sólamente aceptamos: PDF, DOC, DOCX, XLS, XLSX, JPEG.""",
            "error",
        )
        return render_template(
            "equestrian/upload_document.html", horse_id=horse_id, **context
        )
    title = params.get("title", "")
    if title == "" or len(title.strip()) == 0:
        flash("Ingrese un título para el archivo", "error")
        return render_template(
            "equestrian/upload_document.html", horse_id=horse_id, **context
        )

    document_types_valid = [
        "ficha_general",
        "planificacion",
        "informe_de_evaluacion",
        "carga_de_imagenes",
        "registro_veterinario",
    ]
    if params.get("document_type") not in document_types_valid:
        flash("Ingrese un tipo válido para el documento", "error")
        return render_template(
            "equestrian/upload_document.html", horse_id=horse_id, **context
        )

    try:
        ecuestre.create_document(
            title=params.get("title"),
            doc_type=params.get("document_type"),
            format="file",
            source=file_uploaded,
            horse_id=horse_id,
        )
        flash(
            f"""Se subio correctamente el archivo {
              params.get('title')}""",
            "success",
        )
    except MaxRetryError:
        flash("No se pudo establecer una conexión con nuestra base de datos", "error")

    return redirect(url_for("equestrian_details.horse_files", horse_id=horse_id))


@bp.get("/horse_files/upload_link/<int:horse_id>")
@login_required
@permission_required("horse_update")
def show_upload_link(horse_id: int):
    """Muestra el formulario para subir un enlace."""
    horse: Horse = ecuestre.find_horse_by_id(horse_id=horse_id)

    return render_template("equestrian/upload_link.html", horse=horse, params=dict())


@bp.post("/horse_files/upload_link/<int:horse_id>/upload")
@login_required
@permission_required("horse_update")
def upload_link(horse_id: int):
    """Sube un enlace asociado a un caballo."""
    horse: Horse = ecuestre.find_horse_by_id(horse_id=horse_id)
    params = request.form

    title = params.get("title", "")
    link = params.get("link", "")
    document_type = params.get("document_type", "")

    context = {"params": params, "horse": horse}

    messages: List[str] = check_upload_link(
        horse=horse, title=title, link=link, document_type=document_type
    )

    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return render_template(
            "equestrian/upload_link.html", horse_id=horse.id, **context
        )

    ecuestre.add_link(
        title=title, link=link, document_type=document_type, horse_id=horse_id
    )

    flash("Se ha subido el enlace correctamente", "success")

    return redirect(url_for("equestrian_details.horse_files", horse_id=horse_id))


@bp.post("download_horse_files")
@login_required
@permission_required("horse_show")
def download_horse_files():
    """Descarga un archivo asociado a un caballo específico."""
    document_id = request.form.get("document_id")
    horse_id = request.form.get("horse_id")
    if ecuestre.check_action_file_params(document_id, horse_id):

        try:
            response, document = ecuestre.download_document(document_id)
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
                    "Content-type": "application/octet-stream",
                },
            )
        except ValueError as e:
            flash(f"Error al descargar el archivo {e}", "error")

            return redirect(
                url_for("equestrian_details.horse_files", horse_id=horse_id)
            )
        except MaxRetryError:
            flash(f"No se pudo conectar a la base de datos. Reintente", "error")
            return redirect(
                url_for("equestrian_details.horse_files", horse_id=horse_id)
            )
    else:
        flash("Parametros invalidos", "error")

        return redirect(url_for("equestrian_details.horse_files", horse_id=horse_id))


@bp.post("/modify_document")
@login_required
@permission_required("horse_update")
def modify_document():
    """Modifica el título de un documento asociado a un caballo."""
    document_id = request.form.get("document_id")
    horse_id = request.form.get("horse_id")
    if document_id.isdigit() and horse_id.isdigit():
        page = request.form.get("page")
        title = request.form.get("title")
        document_type = request.form.get("document_type", "")
        document: HorseDocument = ecuestre.get_document_by_id(document_id)
        list_document_types: List[str] = [
            "ficha_general",
            "planificacion",
            "informe_de_evaluacion",
            "carga_de_imagenes",
            "registro_veterinario",
        ]
        if document_type not in list_document_types:
            flash("Debe seleccionar un tipo de archivo válido", "error")
        if len(title.strip()) == 0:
            flash("El título no puede estar vacío", "error")
            return redirect(
                url_for("equestrian_details.horse_files", horse_id=horse_id, page=page)
            )
        if len(title) <= 30:
            document.title = title
            document.type = document_type
            db.session.add(document)
            db.session.commit()
            flash("Título modificado exitosamente", "success")
        else:
            flash("El título no puede tener más de 30 caracteres", "error")

        return redirect(
            url_for("equestrian_details.horse_files", horse_id=horse_id, page=page)
        )
    else:
        flash("Parametros invalidos", "error")

        return redirect(url_for("equestrian_dashboard.index"))


@bp.post("delete_document")
@login_required
@permission_required("horse_update")
def delete_document():
    """Elimina un documento asociado a un caballo."""
    document_id = int(request.form.get("document_id"))
    horse_id = request.form.get("horse_id")
    page = request.form.get("page")
    
    caballo = ecuestre.find_horse_by_id(horse_id)
    if not caballo:
        flash("No existe el caballo", "error")
        return redirect(url_for("equestrian_dashboard.index"))
    document = ecuestre.get_document_by_id(document_id)
    if document is None:
        flash("No existe el documento", "error")
        return redirect(
            url_for("equestrian_details.horse_files", horse_id=horse_id, page=page)
        )
    if document.format == "file":
        # si es un "file" lo borro de MinIO
        try:
            functions.delete_document(document.source)
        except MaxRetryError:
            flash("No se pudo hacer la conexión con la base de datos. Reintente", "error")
            return redirect(
                url_for("equestrian_details.horse_files", horse_id=horse_id, page=page)
            )
    ecuestre.delete_document_by_id(document_id)
    if document.format == "file":
        flash("Documento eliminado exitosamente", "success")
    else:
        flash("Enlace eliminado exitosamente", "success")

    return redirect(
        url_for("equestrian_details.horse_files", horse_id=horse_id, page=page)
    )
