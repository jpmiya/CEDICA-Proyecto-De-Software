from flask import Blueprint, render_template, request, redirect, url_for, flash

from src.core import team
from src.core.team import list_and_search_employees
from src.core.users import find_user_by_id
from src.web.handlers.auth import is_admin, login_required


bp = Blueprint("team_dashboard", __name__, url_prefix="/team_dashboard")


@bp.get("/")
@login_required
@is_admin
def index():
    """
    Renderiza la página del panel de control del equipo.

    Se obtienen los empleados y se aplica paginación, ordenamiento y búsqueda según los parámetros
    proporcionados por la solicitud.

    Returns:
        str: El HTML renderizado de la plantilla 'team/dashboard.html'.
    """

    page = request.args.get("page", 1, type=int)
    order_by = request.args.get("order", "name")
    order_direction = request.args.get("order_direction", "asc")
    search_by = request.args.get("search_by", "", type=str)
    search_value = request.args.get("search_value", "")
    profession_value = request.args.get("profesion_value", "")

    team.check_order_params(page, order_by, order_direction, search_by, search_value)

    employees, pagination = list_and_search_employees(
        page, search_value, search_by, order_by, order_direction
    )

    # busco aquellos empleados que tengan usuario
    alias_dict = {}

    for employee in employees:
        if employee.user_id:
            alias = find_user_by_id(employee.user_id).alias
            alias_dict[employee.user_id] = alias

    return render_template(
        "team/dashboard.html",
        page=page,
        employees=employees,
        pagination=pagination,
        order=order_by,
        order_direction=order_direction,
        search_value=search_value,
        profession_value=profession_value,
        search_by=search_by,
        alias_dict=alias_dict,
    )


@bp.post("/")
@login_required
@is_admin
def order():
    """
    Redirige a la página de panel de control del equipo con los parámetros de orden y búsqueda.

    Obtiene los parámetros de orden y búsqueda de la solicitud y redirige a la función de
    index con esos parámetros.

    Returns:
        Response: Redirección a la vista del panel de control del equipo.
    """
    page = request.form.get("page", 1, type=int)
    order_employees = request.form.get("order")
    order_direction = request.form.get("order_direction")
    search_by = request.form.get("search_by", "")
    search_value = (
        request.form.get("search_value", "")
        if search_by != "profesion"
        else request.form.get("profesion_value", "")
    )

    return redirect(
        url_for(
            "team_dashboard.index",
            page=page,
            order=order_employees,
            order_direction=order_direction,
            search_by=search_by,
            search_value=search_value,
        )
    )


@bp.post("/delete_employee")
@login_required
@is_admin
def delete():
    """
    Elimina (o desactiva) un empleado.

    Obtiene el ID del empleado desde el formulario y lo desactiva.
    Luego, muestra un mensaje de éxito y redirige a la vista del panel de control del equipo.

    Returns:
        Response: Redirección a la vista del panel de control del equipo.
    """
    employee_id = request.form.get("employee_id")
    if employee_id.isdigit():
        employee = team.toggle_active(employee_id)
        if employee:
            op = request.form.get("op")
            flash(f"Empleado {op} correctamente", "success")
        else:
            flash("No se ha podido realizar la operación", "error")
    else:
        flash("ID de empleado no válido", "error")

    return redirect(url_for("team_dashboard.index"))
