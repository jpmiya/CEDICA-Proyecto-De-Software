from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from src.core import publications, users
from src.web.handlers.auth import login_required, permission_required


bp = Blueprint("publication", __name__, url_prefix="/publication")


@bp.get("/")
@login_required
@permission_required("publication_create")
def index():
    """Renderiza la página principal del índice de publicaciones."""
    if session["sysAdm"]:
        publicators = users.get_publicators()
        return render_template("publication/create_publication.html", users=publicators)
    else:
        return render_template("publication/create_publication.html")


@bp.post("/create")
@login_required
@permission_required("publication_create")
def create():
    """Crea una nueva publicación."""
    title = request.form.get("title")
    summary = request.form.get("summary")
    author_id = (
        request.form.get("author")
        if request.form.get("author")
        else str(users.find_user_by_email(session["user"]).id)
    )
    content = request.form.get("content")
    state = request.form.get("state")

    try:
        publications.check_create_params(title, summary, state, author_id, content)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("publication.index"))

    publications.create_publication(
        title=title, summary=summary, content=content, state=state, author_id=author_id
    )
    flash("Publicación creada exitosamente", "success")

    return redirect(url_for("publication_dashboard.index"))
