from typing import List

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    Blueprint,
    request,
    abort,
    url_for,
)

from src.core import users
from src.core import pending_users
from src.core.database import db
from src.core.functions import check_alias
from src.core.pending_users.pending_user import PendingUser
from src.web.handlers.auth import login_required, permission_required
from src.web.validators.pending_users_listing import (
    check_delete_pending_user,
    check_search_pending_user_params,
)


bp = Blueprint("pending_users", __name__, url_prefix="/usuarios_pendientes")


@bp.get("/index")
@bp.get("/index/<int:page>")
@login_required
@permission_required("accept")
def index(page: int = 1) -> str:
    """
    Muestra una lista de usuarios pendientes de aceptación, con opciones de ordenación
    por correo electrónico o fecha. Además, permite filtrar por correo electrónico.

    Parámetros:
    - `page`: Página de paginación (el valor por defecto es 1).

    Redirige:
    - Si se detecta un error en los parámetros de búsqueda: `auth.home`.
    """
    if not isinstance(page, int):
        abort(400)

    params: dict[str, str] = {
        "email": request.args.get("email", ""),
        "order": request.args.get("order", ""),
    }

    message: List[str] = check_search_pending_user_params(params)

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return redirect(url_for("pending_users.index", _external=True))

    order: str = params["order"]

    if order == "emailA-Z":
        query = pending_users.get_pending_users_ordered_by_email(ascendent=True)
    elif order == "emailZ-A":
        query = pending_users.get_pending_users_ordered_by_email(ascendent=False)
    elif order == "newer":
        query = pending_users.get_pending_users_ordered_by_time(newer_to_older=True)
    elif order == "older":
        query = pending_users.get_pending_users_ordered_by_time(newer_to_older=False)
    else:
        query = pending_users.get_pending_users()

    email_filtered: str = params["email"]

    if email_filtered and email_filtered != "":
        query = query.filter(PendingUser.email.like(f"%{email_filtered.lower()}%"))

    pending_user_paginated = db.paginate(
        query,
        page=page,
        per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
        error_out=False,
    )

    next_page = (
        url_for("pending_users.index", page=pending_user_paginated.next_num, **params)
        if pending_user_paginated.has_next
        else None
    )

    prev_page = (
        url_for("pending_users.index", page=pending_user_paginated.prev_num, **params)
        if pending_user_paginated.has_prev
        else None
    )

    return render_template(
        "pending_users/listado.html",
        pending_user_paginated=pending_user_paginated,
        next_page=next_page,
        prev_page=prev_page,
        params=params,
    )


@bp.post("/delete_pending_user")
@login_required
@permission_required("accept")
def delete_pending_user():
    """
    Elimina un usuario pendiente del sistema.

    Recibe los parámetros del formulario y verifica si la eliminación es válida.
    Si es válida, elimina al usuario pendiente especificado. Si el usuario no se encuentra
    o hay un error, se muestra un mensaje de error.

    Redirige:
    - Después de la eliminación o error, redirige de nuevo a la lista de usuarios pendientes.
    """
    params = request.form
    email = request.args.get("email", "")
    order = request.args.get("order", "")
    page = request.args.get("page", 1)
    message: List[str] = check_delete_pending_user(params)

    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return redirect(
            url_for("pending_users.index", page=page, order=order, email=email)
        )

    user = pending_users.find_pending_user_by_id(params["pending_user_id"])

    if user is None:
        flash("No se encontró el usuario pendiente de aceptación", "error")
        return redirect(
            url_for("pending_users.index", page=page, order=order, email=email)
        )

    pending_users.delete_pending_user(user)

    flash("Eliminado exitosamente", "info")

    return redirect(url_for("pending_users.index", page=page, order=order, email=email))


@bp.get("/accept_pending_user/<int:user_id>")
@login_required
@permission_required("accept")
def show_accept_user(user_id: int) -> str:
    """
    Muestra la página para aceptar a un usuario pendiente.

    Recibe el ID del usuario pendiente y muestra la interfaz para aceptar al usuario,
    donde se puede asignar un alias.

    Parámetros:
    - `user_id`: ID del usuario pendiente de aceptación.

    Redirige:
    - Si el usuario no existe: Redirige a `auth.home`.
    """
    if not isinstance(user_id, int):
        abort(400)

    new_user = pending_users.find_pending_user_by_id(user_id)
    if new_user is None:
        flash(
            "Algo salió mal, no se encontró al usuario pendiente de aceptación, reintente",
            "error",
        )
        redirect(url_for("auth.home"))

    params = {"email": new_user.email}

    return render_template(
        "pending_users/accept_user.html", user_id=new_user.id, params=params
    )


@bp.post("/accept_pending_user/<int:user_id>")
@login_required
@permission_required("accept")
def accept_user(user_id: int) -> str:
    """
    Acepta a un usuario pendiente y lo convierte en un usuario activo.

    Verifica el alias proporcionado y lo valida antes de aceptar al usuario. Si el alias
    no es válido, se muestra un mensaje de error. Si todo es correcto, acepta al usuario
    y lo añade al sistema.

    Parámetros:
    - `user_id`: ID del usuario pendiente de aceptación.

    Redirige:
    - Si el alias es inválido: Redirige a `pending_users.index`.
    - Si el usuario es aceptado exitosamente: Redirige a `pending_users.index`.
    """
    if not isinstance(user_id, int):
        abort(400)

    alias = request.form.get("alias", "")

    message: List[str] = check_alias(alias)
    if users.find_user_by_alias(alias):
        message.append("Ya existe un usuario en el sistema con ese alias")
    params = {
        "email": pending_users.find_pending_user_by_id(user_id).email,
        "alias": alias,
    }
    if len(message) > 0:
        for error in message:
            flash(error, "error")
        return render_template(
            "pending_users/accept_user.html", user_id=user_id, params=params
        )

    new_user = pending_users.find_pending_user_by_id(user_id)

    if new_user is None:
        flash("Hubo un error. El usuario aceptado no existe", "error")
        return redirect(url_for("pending_users.index"))

    pending_users.accept_pending_user(user_id=user_id, alias=alias)

    flash(f"Se aceptó al usuario {params.get('alias')}", "success")

    return redirect(url_for("pending_users.index"))
