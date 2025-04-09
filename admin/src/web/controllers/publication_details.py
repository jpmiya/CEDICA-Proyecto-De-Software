from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from src.core import publications
from src.core.users import get_publicators, find_user_by_id
from src.web.handlers.auth import login_required, permission_required

bp = Blueprint("publication_details", __name__, url_prefix="/publication_details")


@bp.post("/")
@login_required
@permission_required("publication_show")
def index():
    """
    Renderiza la página principal de los detalles de una publicacion
    """

    publication_id = request.form.get("publication_id")
    publication = (
        publications.get_publication_by_id(publication_id) if publication_id else None
    )
    if publication:
        if (
            session["sysAdm"]
            or "Administracion" in session["roles"]
            or publication.author_id == session.get("id")
        ):
            users = get_publicators()
            return render_template(
                "publication/details.html", publication=publication, users=users
            )
        else:
            user = find_user_by_id(publication.author_id)

            return render_template(
                "publication/details_no_mods.html", publication=publication, author=user
            )
    else:
        flash("Publicación no encontrada", "error")

        return redirect(url_for("publication_dashboard.index"))


@bp.post("/update")
@login_required
@permission_required("publication_update")
def update_publication():
    """Actualiza la publicación cuya información fue enviada en el formulario."""

    publication_id = request.form.get("publication_id")
    publication = publications.get_publication_by_id(publication_id)
    if (
        publication.author_id == session.get("id")
        or session["sysAdm"]
        or "Administracion" in session["roles"]
    ):
        if not publication:
            flash("Ocurrió un error", "error")
            return redirect(url_for("publication_dashboard.index"))

        title = request.form.get("title")
        summary = request.form.get("summary")
        state = request.form.get("state")
        content = request.form.get("content")
        author_id = (
            request.form.get("author")
            if session["sysAdm"] or "Administracion" in session["roles"]
            else request.form.get("author_id")
        )

        try:
            publications.check_create_params(title, summary, state, author_id, content)
        except ValueError as e:
            flash(e, "error")
            return redirect(url_for("publication_dashboard.index"))

        publications.update_publication(
            publication,
            title=title,
            summary=summary,
            state=state,
            author_id=author_id,
            content=content,
        )
        flash("Publicación actualizada correctamente", "success")
    else:
        flash("No puedes modificar esta publicacion", "error")

    return redirect(url_for("publication_dashboard.index"))
