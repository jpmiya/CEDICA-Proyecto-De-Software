from typing import List

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.core import ecuestre, team
from src.web.handlers.auth import permission_required, login_required


bp = Blueprint("equestrian", __name__, url_prefix="/form_equestrian")


@bp.get("/")
@login_required
@permission_required("horse_create")
def index():
    """Renderiza el formulario para crear un nuevo caballo."""
    entrenadores = team.get_employees_by_job_position("Entrenador de Caballos")
    conductores = team.get_employees_by_job_position("Conductor")

    return render_template(
        "equestrian/index.html", entrenadores=entrenadores, conductores=conductores
    )


@bp.post("/")
@login_required
@permission_required("horse_create")
def create():
    """Crea un nuevo caballo y gestiona archivos y enlaces asociados."""
    name = request.form.get("name")
    birth_date = request.form.get("birth_date")
    gender = request.form.get("gender")
    breed = request.form.get("breed")
    fur = request.form.get("fur")
    acquisition_type = request.form.get("acquisition_type")
    entry_date = request.form.get("entry_date")
    sede = request.form.get("sede")
    rider_type = request.form.get("rider_type")
    trainer_id = request.form.get("trainer")
    conductor_id = request.form.get("conductor")

    messages: List[str] = ecuestre.check_create_horse_params(
        name,
        birth_date,
        gender,
        breed,
        fur,
        acquisition_type,
        entry_date,
        sede,
        rider_type,
        trainer_id,
        conductor_id,
    )

    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("equestrian.index"))

    ecuestre.create_horse(
        name=name,
        birth_date=birth_date,
        gender=gender,
        breed=breed,
        fur=fur,
        acquisition_type=acquisition_type,
        entry_date=entry_date,
        sede=sede,
        rider_type=rider_type,
        trainer_id=trainer_id,
        conductor_id=conductor_id,
        active=True,
    )

    flash("Caballo creado exitosamente", "success")

    return redirect(url_for("equestrian_dashboard.index"))
