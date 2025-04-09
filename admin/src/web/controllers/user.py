from typing import List
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from src.core import users
from src.core.users import create_user, find_user_by_id
from src.web.handlers.auth import is_sys_admin, login_required


bp = Blueprint("user", __name__, url_prefix="/users")


@bp.get("/")
@login_required
@is_sys_admin
def index():
    """Renderiza la página principal de gestión de usuarios.

    Returns:
        La plantilla renderizada de la página de usuarios.
    """
    return render_template("user/create_user.html", params=dict())


@bp.post("/")
@login_required
@is_sys_admin
def new():
    """Crea un nuevo usuario con los datos proporcionados en el formulario.

    Obtiene el correo electrónico, alias, contraseña y roles del formulario.
    Muestra un mensaje de éxito si el usuario se crea correctamente,
    o un mensaje de error en caso de que se lance una excepción.

    Returns:
        Redirige a la página de usuarios.
    """
    email = request.form.get("email")
    alias = request.form.get("alias")
    password = request.form.get("password")
    roles = request.form.getlist("roles")
    system_admin = True if request.form.get("sys_adm") else False

    params = {
        "email": email,
        "alias": alias,
        "password": password,
        "roles": roles,
        "sys_adm": system_admin,
    }

    # Validación de parámetros
    messages: List[str] = users.check_create_params(
        email, alias, password, roles, system_admin
    )

    if len(messages) > 0:
        for error in messages:
            flash(error, "error")

        return render_template("user/create_user.html", params=params)

    create_user(system_admin, email=email, alias=alias, password=password, roles=roles)
    flash("Usuario creado correctamente", "success")

    return redirect(url_for("user_dashboard.index"))


@bp.get("/edit_profile/<int:user_id>")
@login_required
def modificar(user_id):
    """
    Navega a la página de modificación del perfil.
    Permite el acceso solo si el usuario autenticado coincide con el perfil.

    Args:
        user_id (int): ID del usuario cuyo perfil se va a modificar.

    Returns:
        Renderiza la plantilla de modificación de perfil si se tienen los permisos adecuados,
        o redirige a la página de inicio con un mensaje de error si no se tienen permisos.
    """
    user = find_user_by_id(user_id)

    if user_id == session.get("id") or session.get("sysAdm"):
        return render_template("user/modificar_perfil.html", user=user)
    else:
        if user:
            flash(
                "No tienes permiso para modificar el perfil de otro usuario.", "error"
            )
        else:
            flash("El usuario no existe.", "error")

        return redirect(url_for("user_dashboard.index"))


@bp.post("/update_user")
@login_required
def update_user():
    """
    Vista para actualizar los datos de un usuario.

    Obtiene el `id`, `email`, `alias` y `password` del formulario,
    luego intenta actualizar la información del usuario a través de la
    función `update_my_user`. Si la actualización es exitosa,
    se muestra un mensaje de éxito, de lo contrario, se captura cualquier excepción,
    se muestra un mensaje de error y se redirige al formulario de modificación del usuario.

    Returns:
        Redirige a la página de inicio si la actualización es exitosa,
        o a la página de modificación del usuario en caso de error.
    """
    user_id = request.form.get("id")
    email = request.form.get("email")
    alias = request.form.get("alias")
    password = request.form.get("password", None)

    messages: List[str] = users.check_update_params(
        user_id=user_id, email=email, alias=alias, password=password
    )
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("user.modificar", user_id=user_id))

    users.update_my_user(user_id, email=email, alias=alias, password=password)
    flash("Usuario actualizado exitosamente", "success")

    if session["id"] == int(user_id):
        session["alias"] = alias

    return redirect(url_for("auth.home"))


@bp.get("/profile/<int:user_id>")
@login_required
def profile(user_id):
    """
    Vista para mostrar el perfil de un usuario.

    Verifica si el usuario existe y si el `user_id` coincide con el
    usuario actual o si el usuario tiene privilegios de administrador.
    Si es así, se renderiza la página de perfil del usuario. Si no,
    se muestra un mensaje de error y se redirige a la página de inicio.

    Args:
        user_id (int): ID del usuario cuyo perfil se va a mostrar.

    Returns:
        Renderiza la plantilla "user/ver_perfil.html" si el usuario tiene
        los permisos apropiados, o redirige a la página de inicio con un mensaje de error
        si no se tienen permisos.
    """
    user = find_user_by_id(user_id)
    if user:
        if (user_id == session.get("id")) or session.get("sysAdm"):
            return render_template(
                "user/ver_perfil.html", user=user, current_user_id=user_id
            )
        else:
            if user:
                flash(
                    "No tienes permiso para modificar el perfil de otro usuario.",
                    "error",
                )
    else:
        flash("El usuario no existe.", "error")

    return redirect(url_for("auth.home"))
