from typing import Dict, List

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.core import charges, riders
from src.core.charges import order_and_filter_charges, validate_filter_params
from src.core.riders.rider import Rider
from src.core.team import get_active_employees, get_employee
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.exceptions import ChargeNotFoundException
from src.web.validators.charges_validations import validate_charge_params
from src.core.charges.charge import Charge


bp = Blueprint("charges", __name__, url_prefix="/cobros")


@bp.get("/index")
@bp.get("/index/<int:page>")
@login_required
@permission_required("charge_index")
def index_charges(page: int = 1):
    """
    Muestra la página principal de cobros con filtros y paginación.
    """
    params = request.args
    messages: List[str] = validate_filter_params(params)
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("charges.index_charges", _external=True))

    order = params.get("order", "desc")
    payment_method = params.get("payment_method", "")
    start_date = params.get("start_date", "")
    end_date = params.get("end_date", "")
    receiver_first_name = params.get("receiver_name", "")
    receiver_last_name = params.get("receiver_last_name", "")
    rider_id = params.get("rider_id", "")

    charges_list, pagination = order_and_filter_charges(
        page=page,
        order=order,
        payment_method=payment_method.upper() if payment_method else None,
        start_date=start_date,
        end_date=end_date,
        receiver_first_name=receiver_first_name if receiver_first_name else "",
        receiver_last_name=receiver_last_name if receiver_last_name else "",
        rider_id=rider_id if rider_id else None,
    )

    next_page = (
        url_for("charges.index_charges", page=pagination.next_num, **params)
        if pagination.has_next
        else None
    )

    prev_page = (
        url_for("charges.index_charges", page=pagination.prev_num, **params)
        if pagination.has_prev
        else None
    )
    riders_list = riders.get_riders_in_list()

    return render_template(
        "charges/index.html",
        charges=charges_list,
        pagination=pagination,
        order=order,
        start_date=start_date,
        end_date=end_date,
        payment_method=payment_method,
        receiver_name=receiver_first_name,
        receiver_last_name=receiver_last_name,
        rider_id=rider_id,
        riders=riders_list,
        next_page=next_page,
        prev_page=prev_page
    )


@bp.get("/create")
@login_required
@permission_required("charge_create")
def new_charge():
    """
    Muestra el formulario para crear un nuevo cobro.
    """
    employees = get_active_employees()
    riders_list = riders.get_riders_in_list()

    return render_template(
        "charges/create_edit.html",
        employees=employees,
        riders=riders_list,
        params=dict(),
    )


@bp.post("/create")
@login_required
@permission_required("charge_create")
def create_charge():
    """
    Crea un nuevo cobro en la base de datos.
    """
    params = request.form
    messages: List[str] = validate_charge_params(params)
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        employees = get_active_employees()
        riders_list = (
            riders.get_riders_in_list()
        )
        return render_template(
            "charges/create_edit.html",
            employees=employees,
            riders=riders_list,
            params=params,
        )

    charges.create_charge(params)
    flash("Cobro creado exitosamente", "success")

    return redirect(url_for("charges.index_charges"))


@bp.get("/cobro/<int:id>/edit")
@login_required
@permission_required("charge_update")
def edit_charge(id: int): 
    """
    Muestra el formulario para editar un cobro existente.
    """
    charge: Charge = charges.get_charge_by_id(id)
    employees = get_active_employees()
    riders_list = riders.get_riders_in_list()
    rider: Rider = riders.get_rider_by_id(int(charge.rider_id))
    debt = "yes" if rider.has_debt else "no"
    params: Dict[str, str] = {
        "rider_id": rider.id,
        "charge_date": charge.charge_date,
        "payment_method": charge.payment_method,
        "amount": charge.amount,
        "debt": debt,
        "receiver_id": charge.receiver_id,
        "observations": charge.observations,
    }
    return render_template(
        "charges/create_edit.html",
        cobro=charge,
        employees=employees,
        riders=riders_list,
        params=params,
    )


@bp.post("/cobro/<int:id>/edit")
@login_required
@permission_required("charge_update")
def update_charge(id):
    """
    Actualiza un cobro existente en la base de datos.
    """
    params = request.form

    params_copy = params.copy().to_dict()
    params_copy["payment_method"] = params.get("payment_method", "").upper()
    messages: List[str] = validate_charge_params(params_copy)
    if len(messages) > 0:
        for error in messages:
            flash(error, "error")
        return redirect(url_for("charges.index_charges"))

    charges.update_charge(id, params_copy)

    flash("Se actualizó el cobro correctamente", "success")

    return redirect(url_for("charges.index_charges"))


@bp.post("/charges/<int:id>/delete")
@login_required
@permission_required("charge_destroy")
def delete_charge(id):
    """
    Elimina un cobro existente de la base de datos.
    """
    try:
        charges.delete_charge_by_id(id)
    except ChargeNotFoundException:
        flash("No se pudo eliminar el cobro", "error")
        return redirect(url_for("auth.home"))

    flash("Cobro eliminado correctamente", "success")

    return redirect(url_for("charges.index_charges"))


@bp.get("/charges/<int:id>")
@login_required
@permission_required("charge_show")
def show_charge(id):
    """
    Muestra los detalles de un cobro específico.
    """
    try:
        charge = charges.get_charge_by_id(id)
        rider = riders.get_rider_by_id(charge.rider_id)
        receiver = get_employee(charge.receiver_id)
        return render_template(
            "charges/show.html", charge=charge, rider=rider, receiver=receiver
        )
    except ChargeNotFoundException:
        flash("Cobro no encontrado", "error")

        return redirect(url_for("charges.index_charges"))
