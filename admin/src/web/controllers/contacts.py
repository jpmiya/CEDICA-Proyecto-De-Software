from typing import Dict, List

from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
    redirect,
    url_for,
    request,
    flash,
)

from src.core.contacts import (
    count_contacts,
    get_consulta_by_id,
    paginar_consultas,
    modificar_consulta,
    eliminar_consulta,
    validate_filter_params,
)
from src.core.contacts.contacts import Contact
from src.web.handlers.auth import login_required, is_admin, permission_required
from src.web.validators.contact_validations import validate_update_contact


bp = Blueprint("contacts", __name__, url_prefix="/contacts")


@bp.get("/")
@bp.get("/<int:page>")
@login_required
@permission_required("contact_index")
def index(page: int = 1):
    """
    Muestra la lista de consultas paginadas.

    Args:
        page (int): Número de la página.

    Returns:
        str: Renderización de la plantilla 'contacts/index.html'.
    """
    if not isinstance(page, int):
        abort(400)

    if page == 0:
        flash("No existe esa página, reintente", "error")
        return redirect(url_for("contacts.index"))

    start_date: str = request.args.get("start_date", "")
    end_date: str = request.args.get("end_date", "")
    estado: str = request.args.get("estado", "")
    order: str = request.args.get("order", "")
    params: Dict[str, str] = {
        "start_date": start_date,
        "end_date": end_date,
        "estado": estado,
        "order": order,
    }

    messages: List[str] = validate_filter_params(params)
    if messages:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("contacts.index", _external=True))

    total_contacts = count_contacts(
        start_date=start_date, end_date=end_date, estado=estado.lower()
    )
    max_elements = current_app.config["MAX_ELEMENTS_ON_PAGE"]
    total_pages = (total_contacts + max_elements - 1) // max_elements

    if total_pages != 0 and page > total_pages:
        flash(f"La página {page} no existe. Mostrando la última página.", "error")
        return redirect(url_for("contacts.index", page=total_pages, **params))

    contacts_paginated = paginar_consultas(
        start_date=start_date,
        end_date=end_date,
        estado=estado.lower(),
        order=order,
        page=page,
    )
    next_page = (
        url_for("contacts.index", page=contacts_paginated.next_num, **params)
        if contacts_paginated.has_next
        else None
    )
    prev_page = (
        url_for("contacts.index", page=contacts_paginated.prev_num, **params)
        if contacts_paginated.has_prev
        else None
    )

    return render_template(
        "contacts/index.html",
        consultas=contacts_paginated,
        next_page=next_page,
        prev_page=prev_page,
        params=params,
    )


@bp.get("/show/<int:consulta_id>")
@login_required
@is_admin
def show(consulta_id: int):
    """
    Muestra el detalle de una consulta específica.

    Args:
        consulta_id (int): ID de la consulta.

    Returns:
        str: Renderización de la plantilla 'contacts/show.html'.
    """

    consulta = get_consulta_by_id(consulta_id)
    if consulta is not None:
        return render_template("contacts/show.html", consulta=consulta)

    flash("Consulta no encontrada", "error")
    return redirect(url_for("contacts.index"))


@bp.get("/actualizar/<int:consulta_id>")
@login_required
@permission_required("contact_update")
def show_update(consulta_id: int):
    """
    Muestra el formulario para actualizar una consulta.

    Args:
        consulta_id (int): ID de la consulta.

    Returns:
        str: Renderización de la plantilla 'contacts/create_edit.html'.
    """
    if not isinstance(consulta_id, int):
        abort(400)
    consulta: Contact = get_consulta_by_id(consulta_id)
    if consulta is None:
        flash("No se encontró la consulta", "error")
        return redirect(url_for("contacts.index"))
    params: Dict[str, str] = {
        "full_name": consulta.full_name,
        "email": consulta.email,
        "message": consulta.message,
        "state": consulta.state,
        "date": consulta.creation_date,
        "comment": consulta.comment if consulta.comment is not None else "",
    }

    return render_template(
        "contacts/create_edit.html", consulta_id=consulta_id, params=params
    )


@bp.post("/actualizar/<int:consulta_id>/update")
@login_required
@is_admin
def update(consulta_id: int):
    """
    Actualiza una consulta existente.

    Args:
        consulta_id (int): ID de la consulta.

    Returns:
        werkzeug.wrappers.Response: Redirección a la página principal de consultas.
    """
    if not isinstance(consulta_id, int):
        abort(400)
    consulta: Contact = get_consulta_by_id(consulta_id=consulta_id)
    if consulta is None:
        flash("No se encontró la consulta", "error")
        return redirect(url_for("contacts.index"))
    params = request.form.to_dict()
    estado = params.get("state")
    comentario = params.get("comment")
    new_params: Dict[str, str] = {
        "full_name": consulta.full_name,
        "email": consulta.email,
        "message": consulta.message,
        "state": consulta.state,
        "date": consulta.creation_date,
        "comment": comentario,
    }
    # Validaciones
    messages = validate_update_contact(params)
    if messages:
        for error in messages:
            flash(error, "error")
        return render_template(
            "contacts/create_edit.html", consulta_id=consulta_id, params=new_params
        )

    modificar_consulta(consulta_id, estado, comentario)
    flash("Consulta actualizada correctamente", "success")

    return redirect(url_for("contacts.index"))


@bp.post("/delete/")
@login_required
@is_admin
def delete():
    """
    Elimina una consulta.

    Returns:
        werkzeug.wrappers.Response: Redirección a la página principal de consultas.
    """
    params = request.form
    consulta_id: str = params.get("contact_id", "")

    if not isinstance(consulta_id, str):
        flash("No se proporcionó correctamente la información para eliminar.", "error")
        return redirect(url_for("contacts.index"))
    if not consulta_id.isdigit():
        flash("No se proporcionó correctamente la información para eliminar.", "error")
        return redirect(url_for("contacts.index"))
    id_consulta: int = int(consulta_id)
    try:
        eliminar_consulta(id_consulta)
        flash("Consulta eliminada correctamente", "success")
    except ValueError:
        flash("No se proporcionó correctamente la información para eliminar.", "error")

    return redirect(url_for("contacts.index"))
