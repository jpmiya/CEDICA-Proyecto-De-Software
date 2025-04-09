from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.core import ecuestre
from src.core.database import db
from src.web.handlers.auth import permission_required, login_required


bp = Blueprint("equestrian_dashboard", __name__, url_prefix="/equestrian_dashboard")


@bp.get("/")
@login_required
@permission_required("horse_index")
def index():
    """Renderiza la página principal del tablero ecuestre con paginación y búsqueda."""
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", "name")
    order_direction = request.args.get("order_direction", "asc")
    search_by = request.args.get("search_by", "name", type=str)
    search_value = request.args.get("search_value", "")
    if ecuestre.check_order_params(
        page, order, order_direction, search_by, search_value
    ):
        horses, pagination = ecuestre.search_horses(
            page, search_value, search_by, order, order_direction
        )
        return render_template(
            "equestrian/dashboard.html",
            page=page,
            horses=horses,
            pagination=pagination,
            order=order,
            order_direction=order_direction,
            search_value=search_value,
            search_by=search_by,
        )
    else:
        flash("Parámetros de ordenación no válidos", "error")

        return redirect(
            url_for(
                "equestrian_dashboard.index",
                page=1,
                order="name",
                order_direction="asc",
                search_by="name",
                search_value="",
            )
        )


@bp.post("/")
@login_required
@permission_required("horse_index")
def order_horses():
    """Ordena los caballos según los parámetros proporcionados en la solicitud."""
    page = request.form.get("page", 1, type=int)
    order = request.form.get("order")
    order_direction = request.form.get("order_direction")
    search_by = request.form.get("search_by", "")

    if search_by == "name":
        search_value = request.form.get("search_value", "")
    else:
        search_value = request.form.get("rider_value", "")

    if ecuestre.check_order_params(
        page, order, order_direction, search_by, search_value
    ):
        return redirect(
            url_for(
                "equestrian_dashboard.index",
                page=page,
                order=order,
                order_direction=order_direction,
                search_by=search_by,
                search_value=search_value,
            )
        )
    else:
        flash("Parámetros de ordenación no válidos", "error")

        return redirect(url_for("equestrian_dashboard.index"))


@bp.post("details")
@login_required
@permission_required("horse_show")
def details():
    """Redirige a la página de detalles de un caballo específico."""
    horse_id = request.form.get("horse_id")
    if not horse_id.isdigit():
        flash("ID de caballo no válido", "error")
        return redirect(url_for("equestrian_dashboard.index", horse_id=horse_id))

    return redirect(url_for("equestrian_details.details", horse_id=horse_id))


@bp.post("delete_horse")
@login_required
@permission_required("horse_destroy")
def delete():
    """Elimina un caballo y muestra un mensaje de éxito."""
    horse_id = request.form.get("horse_id")
    if not horse_id.isdigit():
        flash("ID de caballo no válido", "error")
        return redirect(url_for("equestrian_dashboard.index", horse_id=horse_id))
    horse = ecuestre.find_horse_by_id(horse_id)
    if horse:
        ecuestre.toggle_active(horse)
        db.session.commit()

        flash("Caballo eliminado exitosamente", "success")
    else:
        flash("No existe el caballo", "error")

    return redirect(url_for("equestrian_dashboard.index"))
