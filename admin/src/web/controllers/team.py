from datetime import datetime
from typing import List

from flask import Blueprint, flash, redirect, render_template, request, url_for, abort

from src.core import team, users

from src.web.handlers.auth import is_admin, login_required
from src.web.handlers.exceptions import (
    DniExistsException,
    DniLengthException,
    DniNotNumberException,
    EmailNotValidException,
    EmailExistsException,
    StartDateNullException,
    NameNotValidException,
)


bp = Blueprint("team", __name__, url_prefix="/form_equipo")


@bp.get("/")
@login_required
@is_admin
def index():
    """Renderiza la página principal del índice de equipo."""
    return render_template("team/create_employee.html")


@bp.post("/")
@login_required
@is_admin
def create():
    """Crea un nuevo empleado con los datos del formulario proporcionados.

    Analiza los datos recibidos, incluyendo los títulos de los archivos JSON y los archivos
    cargados, y crea un nuevo empleado y los documentos asociados.

    Returns:
        Redirige a la página de índice del equipo con un mensaje de éxito o error.
    """
    dni = request.form.get("dni")
    name = request.form.get("name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    telephone = request.form.get("telephone")
    profession = request.form.get("profession")
    locality = request.form.get("locality")
    address = request.form.get("address")
    job_position = request.form.get("job_position")
    start_date = request.form.get("start_date")
    if start_date == "":
        start_date = str(datetime.date(datetime.now()))
    end_date = request.form.get("end_date")
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
        return redirect(url_for("team.index"))

    user_id = users.get_id_user_or_null(email)
    if user_id:
        user = users.find_user_by_email(email)
        if not user.active:
            flash(
                f"""El usuario con el mail {email} esta bloqueado,
                  desbloquéelo para poder crear el empleado""",
                "error",
            )
            return redirect(url_for("user_dashboard.index"))
    try:
        team.create_employee(
            dni=dni,
            name=name,
            last_name=last_name,
            email=email,
            telephone=telephone,
            profession=profession,
            locality=locality,
            address=address,
            job_position=job_position,
            start_date=start_date,
            end_date=end_date,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_num=emergency_contact_num,
            social_insurance=social_insurance,
            affiliate_num=affiliate_num,
            condition=condition,
            user_id=user_id,
            active=active,
        )
        flash("Empleado registrado exitosamente", "success")
        if user_id:
            flash(f"El empleado fue asociado al usuario con alias {user.alias}", "info")

        return redirect(url_for("team_dashboard.index"))

    except (
        DniExistsException,
        DniLengthException,
        DniNotNumberException,
        EmailNotValidException,
        EmailExistsException,
        StartDateNullException,
        NameNotValidException,
    ) as e:
        error = e.message
        flash(error, "error")

        return redirect(url_for("team.index"))


@bp.get("/documentacion/<int:employee_id>", defaults={"page": 1})
@bp.get("/documentacion/<int:employee_id>/<int:page>")
@login_required
@is_admin
def show_documentation(employee_id: int, page: int = 1):
    """Muestra la documentación asociada a un empleado específico.

    Verifica la existencia del empleado y la validez de la página, y recupera los documentos
    asociados con paginación. Redirige a la página de índice del equipo si el empleado no se
    encuentra.

    Args:
        employee_id (int): ID del empleado.
        page (int): Número de página para la paginación.

    Returns:
        Renderiza la plantilla de la documentación de los empleados.
    """
    if not isinstance(employee_id, int) or not isinstance(page, int):
        abort(400)

    employee = team.get_employee(employee_id=employee_id)

    if not employee:
        flash("Empleado no encontrado", "error")
        return redirect(url_for("team_dashboard.index"))
    documents, pagination = team.get_documents_by_employee_id(
        employee_id=employee_id, page=page
    )
    next_page = (
        url_for("riders.index", page=pagination.next_num)
        if pagination.has_next
        else None
    )
    prev_page = (
        url_for("riders.index", page=pagination.prev_num)
        if pagination.has_prev
        else None
    )

    return render_template(
        "team/files.html",
        documents=documents,
        next_page=next_page,
        prev_page=prev_page,
        employee=employee,
        pagination=pagination,
    )
