from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from src.core import publications
from src.core.publications import search_and_order_publications, check_order_params
from src.core.users import find_user_by_id
from src.web.handlers.auth import is_admin, login_required, permission_required


bp = Blueprint("publication_dashboard", __name__, url_prefix="/publication_dashboard")


@bp.get("/")
@login_required
@permission_required("publication_index")
def index():
    """Renderiza la página principal del tablero de publicaciones."""
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order_direction", "asc")
    order_by = request.args.get("order", "creation_date")
    search_by = request.args.get("search_by", "")
    start_date = (
        request.args.get("start_date", None)
        if (search_by == "creation_date") or (search_by == "publication_date")
        else None
    )
    end_date = (
        request.args.get("end_date", None)
        if (search_by == "creation_date") or (search_by == "publication_date")
        else None
    )
    search_value = (
        request.args.get("search_value", "")
        if search_by in ["title", "author_alias"]
        else ""
    )
    try:
        check_order_params(page, order, order_by, search_by, start_date, end_date)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("publication_dashboard.index"))

    pagination, publications = search_and_order_publications(
        page, order, order_by, search_by, search_value, end_date, start_date
    )

    alias_dict = {}
    for publication in publications:
        if publication.author_id:
            alias = find_user_by_id(publication.author_id).alias
            alias_dict[publication.author_id] = alias

    return render_template(
        "publication/dashboard.html",
        page=page,
        order_direction=order,
        pagination=pagination,
        publications=publications,
        alias_dict=alias_dict,
        search_value=search_value,
        search_by=search_by,
        start_date=start_date,
        end_date=end_date,
        order=order_by,
        id_user=session.get("id"),
    )


@bp.post("/delete")
@login_required
@is_admin
def delete_publication():
    """Elimina la publicación cuyo formulario fue enviado para su eliminación."""
    publication_id = request.form.get("publication_id")
    try:
        publications.delete_publication_by_id(publication_id)
        flash("Publicación eliminada correctamente", "success")
    except ValueError as e:
        flash(e, "error")

    return redirect(url_for("publication_dashboard.index"))
