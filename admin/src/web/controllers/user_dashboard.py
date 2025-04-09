from typing import List

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.core import users
from src.core.users import find_user_by_id, list_and_search_users, User
from src.web.handlers.auth import login_required, is_sys_admin


bp = Blueprint("user_dashboard", __name__, url_prefix="/user_dashboard")


@bp.get("/")
@login_required
@is_sys_admin
def index():
    """Renderiza la página de inicio del panel de usuario con la lista de usuarios y paginación.

    Recupera la lista de usuarios basada en los parámetros de búsqueda y orden especificados.

    Returns:
        Plantilla del panel de usuarios renderizada con los datos de los usuarios.
    """
    page = request.args.get("page", 1, type=int)
    order_by = request.args.get("order", "email")
    order_direction = request.args.get("order_direction", "asc")
    search_by = request.args.get("search_by", "", type=str)
    search_value = request.args.get("search_value", "")
    users_list, pagination = list_and_search_users(
        page,
        search_value,
        search_by,
        order_by,
        order_direction,
    )

    return render_template(
        "user/dashboard.html",
        page=page,
        users=users_list,
        pagination=pagination,
        order=order_by,
        order_direction=order_direction,
        search_value=search_value,
        search_by=search_by,
    )


@bp.post("/")
@login_required
@is_sys_admin
def order():
    """Gestiona el orden de los usuarios según los criterios especificados.

    Recupera los parámetros de orden, dirección y búsqueda, y redirige
    al panel de usuarios con los filtros actualizados.

    Returns:
        Redirección al panel de usuarios con los parámetros de orden.
    """
    page = request.form.get("page", 1, type=int)
    order_by = request.form.get("order")
    order_direction = request.form.get("order_direction")
    search_by = request.form.get("search_by", "")

    if search_by == "rol":
        search_value = request.form.get("role_value", "")
    elif search_by == "email":
        search_value = request.form.get("search_value", "")
    else:
        search_value = request.form.get("activo", "")

    return redirect(
        url_for(
            "user_dashboard.index",
            page=page,
            order=order_by,
            order_direction=order_direction,
            search_by=search_by,
            search_value=search_value,
        )
    )


@bp.get("details")
@login_required
@is_sys_admin
def details():
    """Renderiza la página de detalles de un usuario específico.

    Recupera los detalles del usuario según el ID proporcionado.

    Returns:
        Plantilla de detalles de usuario renderizada.
    """
    user_id = request.args.get("user_id")

    user = find_user_by_id(user_id)

    if user is None:
        flash("Usuario no encontrado", "error")
        return redirect(url_for("user_dashboard.index"))

    roles = users.get_roles(user)

    return render_template("user/user_details.html", user=user, roles=roles)


@bp.post("delete_user")
@login_required
@is_sys_admin
def delete():
    """Alterna el estado activo de un usuario para marcarlo como 'bloqueado'.

    Recupera el ID del usuario desde el formulario, alterna el estado activo del usuario
    y muestra un mensaje de éxito.

    Returns:
        Redirección al panel de usuarios.
    """
    user_id = request.form.get("user_id")
    user: User = users.find_user_by_id(user_id)
    if user and user.system_admin:
        flash("No se puede bloquear a un administrador del sistema", "error")
        return redirect(url_for("user_dashboard.index"))
    try:
        users.toggle_active(user_id)
        flash("Usuario bloqueado correctamente", "success")

        return redirect(url_for("user_dashboard.index"))
    except ValueError as e:
        flash(str(e), "error")

        return redirect(url_for("user_dashboard.index"))


@bp.post("activate_user")
@login_required
@is_sys_admin
def activate():
    """Activa a un usuario alternando su estado activo.

    Recupera el ID del usuario desde el formulario, alterna el estado activo del usuario
    y muestra un mensaje de éxito.

    Returns:
        Redirección al panel de usuarios.
    """
    user_id = request.form.get("user_id")
    try:
        users.toggle_active(user_id)
        flash("Usuario desbloqueado correctamente", "success")
    except ValueError as e:
        flash(str(e), "error")

        return redirect(url_for("user_dashboard.index"))

    return redirect(url_for("user_dashboard.index"))


@bp.post("update_user")
@login_required
@is_sys_admin
def update():
    """Actualiza la información del usuario según los datos proporcionados.

    Recupera los datos del usuario desde el formulario, actualiza el usuario en la base de datos
    y muestra un mensaje de éxito.

    Returns:
        Redirección al panel de usuarios.
    """
    id = request.form.get("id")
    email = request.form.get("email")
    alias = request.form.get("alias")
    roles = request.form.getlist("roles")
    password = request.form.get("password", None)
    system_admin = bool(request.form.get("sys_adm"))
    if not id.isdigit():
        flash("ID de usuario no válido", "error")
        return redirect(url_for("user_dashboard.index"))
    user: User = find_user_by_id(id)
    if user:
        messages: List[str] = users.update_user(
            user,
            email=email,
            alias=alias,
            roles=roles,
            system_admin=system_admin,
            password=password,
        )
        if len(messages) > 0:
            for error in messages:
                flash(error, "error")
            return redirect(url_for("user_dashboard.details", user_id=id))

        flash("Usuario actualizado correctamente", "success")

        return redirect(url_for("user_dashboard.index"))
    else:
        flash("Usuario no encontrado", "error")

        return redirect(url_for("user_dashboard.index"))
