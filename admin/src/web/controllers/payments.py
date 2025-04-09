from typing import List

from flask import render_template, Blueprint, redirect, url_for, request, flash

from src.core import payments
from src.core.payments import order_and_filter_payments, delete_payment_by_id
from src.core.payments.payments import Payment
from src.core.team import get_employee, get_employees, get_active_employees
from src.web.handlers.exceptions import PaymentNotFoundException
from src.web.handlers.auth import login_required, is_admin


bp = Blueprint("payments", __name__, url_prefix="/pagos")


@bp.post("/create_payment")
@login_required
@is_admin
def create_payment():
    """
    Crea un nuevo pago en el sistema.

    Esta función recibe los datos del formulario de creación de pago, validar que
    los parámetros sean correctos y, en caso de serlo, crea un nuevo pago en la
    base de datos. Si ocurre un error durante la validación o la creación del
    pago, se muestra un mensaje de error al usuario. Si el pago se genera correctamente,
    se redirige a la página de dashboard de pagos con un mensaje de éxito.

    Parámetros:
    - `beneficiary_id`: ID del beneficiario del pago.
    - `payment_type`: Tipo de pago (por ejemplo, 'Honorarios').
    - `payment_date`: Fecha del pago.
    - `amount`: Monto del pago.
    - `description`: Descripción del pago.

    Redirecciones:
    - Si el pago se crea correctamente: `payments.dashboard`.
    - Si ocurre un error: `payments.new_payment`.

    Mensajes de flash:
    - Si ocurre un error durante la validación o la creación: Muestra el error en pantalla.
    - Si el pago se crea con éxito: Muestra un mensaje de éxito.

    Excepciones:
    - Si alguno de los parámetros es incorrecto o no válido, se muestra un mensaje de error.
    """
    beneficiary_id = request.form.get("beneficiary_id")
    payment_type = request.form.get("payment_type")
    if beneficiary_id == "" or payment_type != "Honorarios":
        beneficiary_id = None
    payment_date = request.form.get("payment_date")
    amount = request.form.get("amount")
    description = request.form.get("description")
    messages: List[str] = []

    messages.extend(
        payments.check_create_params(
            beneficiary_id=beneficiary_id,
            payment_date=payment_date,
            amount=amount,
            description=description,
            payment_type=payment_type,
        )
    )
    if len(messages) > 0:
        for message in messages:
            flash(message, "error")
        return redirect(url_for("payments.new_payment"))

    payments.create_payment(
        beneficiary_id=beneficiary_id,
        payment_date=payment_date,
        payment_type=payment_type,
        amount=amount,
        description=description,
    )
    flash("Pago creado correctamente", "success")

    return redirect(url_for("payments.dashboard"))


@bp.get("/create")
@login_required
@is_admin
def new_payment():
    """Renderiza el formulario para crear un nuevo pago."""
    type_payment = request.args.get("type")
    employees = get_active_employees()

    return render_template("payments/form.html", employees=employees, type=type_payment)


@bp.get("/dashboard")
@login_required
@is_admin
def dashboard():
    """Renderiza la vista de pagos."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search_value = request.args.get("search_value")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    payments_list, pagination, beneficiarys = order_and_filter_payments(
        page, order, search_value, start_date, end_date
    )

    return render_template(
        "payments/index.html",
        payments=payments_list,
        beneficiarys=beneficiarys,
        pagination=pagination,
        search_value=search_value,
        order=order,
        start_date=start_date,
        end_date=end_date,
    )


@bp.get("/pago/<int:payment_id>")
@login_required
@is_admin
def show_payment(payment_id):
    """Renderiza la vista de un pago en específico."""
    payment = Payment.query.get_or_404(payment_id)
    if payment.payment_type == "Honorarios":
        employee = get_employee(payment.beneficiary_id)
        if employee:
            return render_template(
                "payments/show.html", payment=payment, employee=employee
            )
        else:
            flash("No se encontró al empleado del pago", "error")
            return redirect(url_for("payments.dashboard"))

    return render_template("payments/show.html", payment=payment)


@bp.post("/update")
@login_required
@is_admin
def update_payment():
    """Recibe los datos de un pago y los actualiza en la base de datos."""
    payment_id = request.form.get("payment_id")
    beneficiary_id = request.form.get("beneficiary_id")
    payment_date = request.form.get("payment_date")
    payment_type = request.form.get("payment_type")
    amount = request.form.get("amount")
    description = request.form.get("description")
    messages = []

    messages.extend(
        payments.update_payment(
            payment_id,
            beneficiary_id=beneficiary_id,
            payment_date=payment_date,
            payment_type=payment_type,
            amount=amount,
            description=description,
        )
    )

    if messages:
        for message in messages:
            flash(message, "error")
        return redirect(url_for("payments.dashboard"))

    flash("Pago actualizado correctamente", "success")

    return redirect(url_for("payments.dashboard"))


@bp.get("/pago/<int:payment_id>/edit")
@login_required
@is_admin
def edit_payment(payment_id):
    """Renderiza el formulario para editar un pago."""
    payment = payments.get_payment_by_id(payment_id)
    if payment is None:
        flash("No se encontró el pago", "error")
        return redirect(url_for("payments.dashboard"))
    type_payment = (
        request.args.get("type") if request.args.get("type") else payment.payment_type
    )
    employees = get_employees()
    if payment.payment_type == "Honorarios":
        employee_act = get_employee(payment.beneficiary_id)
        if employee_act not in employees:
            employees.append(employee_act)

    return render_template(
        "payments/form.html", payment=payment, employees=employees, type=type_payment
    )


@bp.post("/delete")
@login_required
@is_admin
def delete_payment():
    """Recibe el id de un pago y lo elimina de la base de datos."""
    payment_id = request.form.get("payment_id")
    try:
        delete_payment_by_id(payment_id)
        flash("Pago eliminado correctamente", "success")
    except PaymentNotFoundException:
        flash("No se pudo eliminar el pago", "error")

        return redirect(url_for("payments.dashboard"))

    return redirect(url_for("payments.dashboard"))
