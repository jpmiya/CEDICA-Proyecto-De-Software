import io
import os
from datetime import datetime
from typing import List

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from urllib3.exceptions import MaxRetryError
from werkzeug.datastructures import FileStorage

from src.core import functions, team, users
from src.core.database import db
from src.web.handlers.auth import is_admin, login_required
from src.web.handlers.exceptions import DniExistsException, EmailExistsException
from src.web.validators.general_validations import validate_string


bp = Blueprint("team_details", __name__, url_prefix="/team_details")


@bp.get("/")
@login_required
@is_admin
def index():
    """
    Renderiza la página de detalles de un empleado.

    Returns:
        str: HTML de la plantilla 'team/employee_details.html' si el empleado no es None.
    """

    id_employee = request.args.get("employee_id")
    if id_employee and id_employee.isdigit():

        employee = team.get_employee(id_employee)

        if employee:
            end_date = employee.end_date if employee.end_date else None
            return render_template(
                "team/employee_details.html", employee=employee, end_date=end_date
            )
        else:
            flash("Empleado no encontrado", "error")
            return redirect(url_for("team_dashboard.index"))
    else:
        flash("Empleado no encontrado", "error")
        return redirect(url_for("team_dashboard.index"))


@bp.post("/")
@login_required
@is_admin
def details():
    """
    Renderiza los detalles de un empleado.

    Obtiene el ID del empleado desde el formulario y lo busca. Luego, genera un nuevo
    token para el empleado en la sesión.

    Returns:
        str: HTML de la plantilla 'team/employee_details.html' con los datos del empleado.
    """
    employee_id = request.form.get("employee_id")
    if employee_id.isdigit():
        employee = team.get_employee(employee_id)
        if employee:
            end_date = employee.end_date if employee.end_date else None
            return render_template(
                "team/employee_details.html", employee=employee, end_date=end_date
            )
        else:
            flash("Empleado no encontrado", "error")
            return redirect(url_for("team_dashboard.index"))
    else:
        flash("Empleado no encontrado", "error")
        return redirect(url_for("team_dashboard.index"))


@bp.post("update_employee")
@login_required
@is_admin
def update_employee():
    """
    Actualiza la información de un empleado.

    Obtiene los datos del formulario y actualiza el empleado en la base de datos.
    Maneja la excepción DniExistsException si el DNI ya existe.

    Returns:
        str: HTML de la plantilla 'team/employee_details.html' con el empleado actualizado
              o con un mensaje de error si ocurre una excepción.
    """
    employee_id = request.form.get("id")
    if not employee_id.isdigit():
        flash("Empleado no encontrado", "error")
        return redirect(url_for("team_dashboard.index"))
    else:
        employee = team.get_employee(employee_id)
        if not employee:
            flash("Empleado no encontrado", "error")
            return redirect(url_for("team_dashboard.index"))
    dni = request.form.get("dni")
    name = request.form.get("name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    profession = request.form.get("profession")
    locality = request.form.get("locality")
    address = request.form.get("address")
    telephone = request.form.get("telephone")
    job_position = request.form.get("job_position")
    start_date = request.form.get("start_date")
    if start_date == "":
        start_date = str(datetime.date(datetime.now()))
    end_date = request.form.get("end_date")
    if end_date == "":
        end_date = None
    emergency_contact_name = request.form.get("emergency_contact_name")
    emergency_contact_num = request.form.get("emergency_contact_num")
    social_insurance = request.form.get("social_insurance")
    affiliate_num = request.form.get("affiliate_num")
    condition = request.form.get("condition")
    active = request.form.get("active")

    messages: List[str] = team.check_create_params(
        dni,
        name,
        last_name,
        email,
        telephone,
        profession,
        locality,
        address,
        job_position,
        start_date,
        end_date,
        emergency_contact_name,
        emergency_contact_num,
        social_insurance,
        affiliate_num,
        condition,
        active,
    )
    if active in ["true", "false"]:
        active = True if active == "true" else False
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("team_details.index", employee_id=employee_id))
    if email != employee.email:
        user_id = users.get_id_user_or_null(email)
        if user_id:
            user = users.find_user_by_email(email)
            if not user.active:
                flash(
                    f"""El usuario con el mail {email} esta bloqueado,
                      desbloquéelo para poder modificar el empleado""",
                    "error",
                )
                return redirect(url_for("user_dashboard.index"))
    try:
        user_id = users.get_id_user_or_null(email)
        user = users.find_user_by_email(email)
        team.modify_employee(
            employee_id,
            name=name,
            last_name=last_name,
            email=email,
            profession=profession,
            locality=locality,
            dni=dni,
            address=address,
            telephone=telephone,
            job_position=job_position,
            start_date=start_date,
            end_date=end_date,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_num=emergency_contact_num,
            social_insurance=social_insurance,
            affiliate_num=affiliate_num,
            condition=condition,
            user_id=user_id if user_id else None,
            active=active,
        )
        flash("Empleado modificado exitosamente", "success")
        if user:
            flash(
                f"El empleado fue asociado con el usuario con alias {user.alias}",
                "info",
            )
        return redirect(url_for("team_details.index", employee_id=employee_id))
    except (DniExistsException, EmailExistsException) as e:
        flash(e, "error")
        return redirect(url_for("team_details.index", employee_id=employee_id))


@bp.post("download_employee_files")
@login_required
@is_admin
def download_employee_files():
    """
    Descarga un archivo asociado a un empleado.

    Obtiene el ID del documento y del empleado, y prepara la respuesta para la descarga
    del documento correspondiente.

    Returns:
        Response: Respuesta con el archivo para descargar.
    """
    document_id = request.form.get("document_id")
    employee_id = request.form.get("employee_id")

    if not isinstance(document_id, str) and not isinstance(employee_id, str):
        flash("Hubo un error en la solicitud de descarga. Reintente", "error")
        return redirect(url_for("team_dashboard.index"))

    if not document_id.isdigit() and not employee_id.isdigit():
        flash("Hubo un error en la solicitud de descarga. Reintente", "error")
        return redirect(url_for("team_dashboard.index"))

    try:
        response, document = team.download_document(document_id)
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
        return redirect(url_for("team_dashboard.index"))


@bp.post("modify_title")
@login_required
@is_admin
def modify_title():
    """
    Modifica el título de un documento.

    Obtiene el ID del documento y el nuevo título, lo actualiza en la base de datos,
    y redirige a la página de archivos del empleado.

    Returns:
        Response: Redirección a la página de archivos del empleado.
    """
    document_id = request.form.get("document_id")
    employee_id = request.form.get("id")
    if not employee_id.isdigit() or not document_id.isdigit():
        flash("Parámetros inválidos", "error")
        return redirect(url_for("team_dashboard.index"))
    page = request.form.get("page")
    title = request.form.get("title")
    if len(title) > 30:
        flash("El título no puede tener más de 30 caracteres", "error")
        return redirect(
            url_for("team.show_documentation", employee_id=employee_id, page=page)
        )
    document = team.get_document_by_id(document_id)
    if document:
        document.title = title
        db.session.add(document)
        db.session.commit()
        flash("Título modificado exitosamente", "success")
    else:
        flash("Documento no encontrado", "error")
    return redirect(
        url_for("team.show_documentation", employee_id=employee_id, page=page)
    )


@bp.post("delete_document")
@login_required
@is_admin
def delete_document():
    """
    Elimina un documento asociado a un empleado.

    Obtiene el ID del documento y lo elimina de la base de datos. Luego, redirige
    a la página de archivos del empleado.

    Returns:
        Response: Redirección a la página de archivos del empleado.
    """
    document_id = request.form.get("document_id")
    employee_id = request.form.get("id")
    if employee_id.isdigit() and document_id.isdigit():
        page = request.form.get("page")
        document = team.get_document_by_id(document_id)
        if document:
            if document.format == "file":
                try:
                    functions.delete_document(document.source)
                except MaxRetryError:
                    flash("No se pudo hacer conexión con la base de datos.", "error")
            team.delete_document(document_id)
            flash("Documento eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el documento. No se encontró", "error")
        return redirect(
            url_for("team.show_documentation", employee_id=employee_id, page=page)
        )
    else:
        flash("Parámetros inválidos", "error")
        return redirect(url_for("team_dashboard.index"))


@bp.get("/upload_document/<int:employee_id>")
@login_required
@is_admin
def show_upload_document(employee_id: int):
    """Muestra la página para subir un documento.

    Args:
        employee_id (int): ID del empleado.

    Returns:
        Renderización de la plantilla para subir documentos o redirección en caso de error.
    """
    if not isinstance(employee_id, int):
        abort(400)

    employee = team.get_employee(employee_id=employee_id)

    if employee is None:
        flash("No se encontró al empleado", "error")
        return redirect(url_for("auth.home"))

    return render_template(
        "team/upload_file.html",
        params=dict(),
        employee_id=employee_id,
        employee=employee,
    )


@bp.post("/upload_document/<int:employee_id>")
@login_required
@is_admin
def upload_document(employee_id: int):
    """Procesa la carga de un documento para un empleado.

    Args:
        employee_id (int): ID del empleado.

    Returns:
        Redirección a la documentación del empleado o renderización de la página en caso de error.
    """
    if not isinstance(employee_id, int):
        abort(400)

    employee = team.get_employee(employee_id=employee_id)
    params = request.form
    file_uploaded = request.files.get("document", "")
    context = {"params": params, "employee": employee}

    if employee is None:
        flash("Hubo un error y no se pudo encontrar al usuario")
        abort(403)

    if (
        not file_uploaded
        or not isinstance(file_uploaded, FileStorage)
        or file_uploaded.filename == ""
    ):
        flash("No se seleccionó ningún archivo.", "error")
        return render_template(
            "team/upload_file.html", employee_id=employee_id, **context
        )

    if not functions.check_file_size(file_uploaded):
        flash("El archivo seleccionado excede el límite de 15 MB", "error")
        return render_template(
            "team/upload_file.html", employee_id=employee_id, **context
        )

    if not functions.check_valid_format(file_uploaded):
        flash(
            """No aceptamos archivos de esa extensión.
            Solamente aceptamos: PDF, DOC, DOCX, XLS, XLSX, JPEG.""",
            "error",
        )
        return render_template(
            "team/upload_file.html", employee_id=employee_id, **context
        )

    if params.get("title") == "":
        flash("Ingrese un título para el archivo")
        return render_template(
            "team/upload_file.html", employee_id=employee_id, **context
        )

    if len(params.get("title")) > 30:
        flash("El campo título tiene una extensión máxima de 30 caracteres", "error")
        return render_template(
            "team/upload_file.html", employee_id=employee_id, **context
        )

    try:
        team.create_document(
            title=params.get("title"),
            format="file",
            source=file_uploaded,
            employee_id=employee_id,
        )
        flash(f"Se subió correctamente el archivo {params.get('title')}", "success")
    except MaxRetryError:
        flash("No se pudo establecer una conexión con nuestra base de datos", "error")

    return redirect(url_for("team.show_documentation", employee_id=employee_id))


@bp.get("/upload_link/<int:employee_id>")
@login_required
@is_admin
def show_upload_link(employee_id: int):
    """Muestra la página para subir un enlace.

    Args:
        employee_id (int): ID del empleado.

    Returns:
        Renderización de la plantilla para subir enlaces o redirección en caso de error.
    """
    if not isinstance(employee_id, int):
        abort(400)

    employee = team.get_employee(employee_id=employee_id)

    if employee is None:
        flash("No se encontró al empleado", "error")
        return redirect(url_for("team_dashboard.index"))

    return render_template(
        "team/upload_link.html",
        params=dict(),
        employee_id=employee_id,
        employee=employee,
    )


@bp.post("/upload_link/<int:employee_id>")
@login_required
@is_admin
def upload_link(employee_id: int):
    """Procesa la carga de un enlace para un empleado.

    Args:
        employee_id (int): ID del empleado.

    Returns:
        Redirección a la documentación del empleado o renderización de la página en caso de error.
    """
    if not isinstance(employee_id, int):
        abort(400)

    employee = team.get_employee(employee_id=employee_id)
    if employee is None:
        flash("No se encontró al empleado", "error")
        return redirect(url_for("team_dashboard.index"))

    params = request.form
    title = params.get("title", "")
    link = params.get("link", "")
    message: List[str] = list()

    if not functions.is_valid_url(link):
        message.append("Ingresó un link no válido")

    special_characters = (
        "&",
        "%",
        "$",
        "#",
        "@",
        "!",
        "*",
        "(",
        ")",
        "-",
        "_",
        "=",
        "+",
        "{",
        "}",
        "[",
        "]",
        "<",
        ">",
        "/",
        "?",
        ":",
        ";",
        '"',
        "'",
        "\\",
        "|",
        "^",
        "~",
        "`",
        ".",
        ",",
    )
    message.extend(
        validate_string(
            s=title,
            label="Título del enlace",
            maxlength=30,
            numbers_permitted=True,
            allowed_special_chars=special_characters,
            spaced=True,
            required=True,
            only_numbers_accepted=True,
        )
    )

    if len(message) != 0:
        for error in message:
            flash(error, "error")
        return render_template(
            "team/upload_link.html",
            params=params,
            employee_id=employee_id,
            employee=employee,
        )

    try:
        team.add_link(
            title=title, link=link, document_type="Link", employee_id=employee_id
        )
    except MaxRetryError:
        flash("No se pudo conectar a la base de datos", "error")
        return redirect(
            url_for("team.show_documentation", employee_id=employee_id, page=1)
        )

    flash("Enlace subido con éxito", "success")

    return redirect(url_for("team.show_documentation", employee_id=employee_id, page=1))
