from datetime import datetime
from typing import List
from flask import current_app
import sqlalchemy as sa

from src.core import functions
from src.core.contacts.contacts import Contact
from src.core.database import db
from src.web.validators.general_validations import check_email, check_select, validate_string


def count_contacts(start_date=None, end_date=None, estado=None):
    """
    Cuenta la cantidad de contactos en la base de datos según los criterios proporcionados.

    Parámetros:
        start_date (datetime, opcional): Fecha inicial para filtrar los
        contactos por su fecha de creación.
        end_date (datetime, opcional): Fecha final para filtrar los contactos por
        su fecha de creación.
        estado (str, opcional): Estado del contacto para filtrar los resultados.

    Retorna:
        int: La cantidad de contactos que cumplen con los filtros especificados.

    Nota:
        - Si no se proporcionan filtros, devuelve la cantidad total de
        contactos en la base de datos.
        - Utiliza una sesión de la base de datos para ejecutar la consulta de manera segura.
    """
    query = sa.select(sa.func.count(Contact.id))
    if start_date:
        query = query.where(Contact.creation_date >= start_date)
    if end_date:
        query = query.where(Contact.creation_date <= end_date)
    if estado:
        query = query.where(Contact.state == estado)

    with db.session() as session:
        return session.execute(query).scalar()


def paginar_consultas(start_date=None, end_date=None, estado=None, order=None, page=1):
    """
    Lista todas las consultas, con opción de ordenar por fecha y
    filtrar por estado y rango de fechas.

    Args:
        start_date (str): Fecha de inicio para filtrar.
        end_date (str): Fecha de fin para filtrar.
        estado (str): Estado por el cual filtrar las consultas.
        order (str): Ordenar por fecha, "asc" o "desc".
        page (int): Página que se quiere mostrar del resultado del filtro

    Returns:
        list: Lista de consultas.
    """
    query = sa.select(Contact)
    if start_date:
        query = query.where(Contact.creation_date >= start_date)
    if end_date:
        query = query.where(Contact.creation_date <= end_date)

    if estado:
        query = query.where(Contact.state == estado)

    if order == "older":
        query = query.order_by(Contact.creation_date.asc())

    else:
        query = query.order_by(Contact.creation_date.desc())

    contacts_paginated = db.paginate(
        query,
        page=page,
        per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
        error_out=False,
    )

    return contacts_paginated


def modificar_consulta(consulta_id, estado=None, comentario=None):
    """
    Modifica el estado y/o comentario de una consulta.

    Args:
        consulta_id (int): ID de la consulta.
        estado (str): Nuevo estado de la consulta.
        comentario (str): Nuevo comentario de la consulta.

    Returns:
        Contact: Consulta modificada.
    """
    consulta: Contact = get_consulta_by_id(consulta_id=consulta_id)
    if consulta:
        if estado:
            consulta.state = estado
        if comentario:
            consulta.comment = comentario
        db.session.commit()

    return consulta


def crear_consulta(**kwargs):
    """Crea una nueva consulta."""
    nueva_consulta = Contact(**kwargs)
    nueva_consulta.state = "pendiente"
    db.session.add(nueva_consulta)
    db.session.commit()

    return nueva_consulta


def eliminar_consulta(consulta_id):
    """
    Elimina una consulta.

    Args:
        consulta_id (int): ID de la consulta.

    Returns:
        Contact: Consulta eliminada.
    """

    consulta: Contact = get_consulta_by_id(consulta_id=consulta_id)
    if consulta:
        db.session.delete(consulta)
        db.session.commit()
    else:
        raise ValueError("No se encontró la consulta")

    return consulta


def get_consulta_by_id(consulta_id: int):
    """
    Obtiene una instancia del modelo `Contact` basada en su ID.

    Args:
        consulta_id (int): ID único de la consulta a buscar.

    Returns:
        Contact: La instancia del modelo `Contact` sí se encuentra en la base de datos.
        None: Si el `consulta_id` no es un entero válido o si no existe una
        consulta con ese ID.
    """
    if not isinstance(consulta_id, int):
        return None

    consulta: Contact = Contact.query.filter_by(id=consulta_id).first()

    return consulta


def validate_filter_params(params):
    """Valida los parámetros de filtro en el listado de consultas."""
    messages: List[str] = []
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    estado = params.get("estado")
    order = params.get("order", "")

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            messages.append("Fecha de inicio no válida.")

    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messages.append("Fecha de fin no válida.")

    if len(messages) > 0:
        return messages

    if (start_date and end_date) and (start_date > end_date):
        messages.append("La fecha de inicio no puede ser mayor a la fecha de fin")

    if order not in ["older", "newer", ""]:
        messages.append("Orden no válido.")

    if estado not in ["PENDIENTE", "TERMINADO", "EN PROCESO", ""]:
        messages.append("Estado no válido")

    return messages


def check_api_get_contacts_params(state="pendiente", **kwargs):
    """
    Validar los parámetros para la API de obtener contactos.
    Retorna una lista con todos los errores que encontró
    """
    title = kwargs.get("title")
    name = kwargs.get("full_name")
    email = kwargs.get("email")
    message = kwargs.get("message")
    errors : List[str] = []
    caracteres_especiales = ("&", "-", "_", "/", ":", "(", ")", ".", ",", "#", "@", "+")
    errors.extend(validate_string(
        s=title,
        label="Título",
        maxlength=100,
        numbers_permitted=True,
        allowed_special_chars=caracteres_especiales,
        spaced=True,
        required=True,
        only_numbers_accepted=True
    ))
    errors.extend(functions.check_name(name))

    errors.extend(check_email(field=email, label="Formulario de contacto"))

    errors.extend(validate_string(
        s=message,
        label="Cuerpo del mensaje",
        maxlength=500,
        numbers_permitted=True,
        allowed_special_chars=caracteres_especiales,
        spaced=True,
        only_numbers_accepted=False
    ))
    if state:
        errors.extend(check_select(
            field=state,
            label="Estado de la consulta",
            permitted_values=("pendiente", "en proceso", "terminado")
        ))

    return errors


def order_and_filter_contacts(page, order, start_date=None, end_date=None, estado=None):
    """
    Lista todas las consultas con paginación, opción de ordenar por fecha y
    filtrar por estado y rango de fechas.

    Args:
        page (int): Número de página.
        order (str): Ordenar por fecha, "asc" o "desc".
        start_date (str): Fecha de inicio para filtrar.
        end_date (str): Fecha de fin para filtrar.
        estado (str): Estado por el cual filtrar las consultas.

    Returns:
        tuple: Lista de consultas y objeto de paginación.
    """
    consultas = Contact.query
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        consultas = consultas.filter(Contact.creation_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        consultas = consultas.filter(Contact.creation_date <= end_date)
    if estado:
        consultas = consultas.filter_by(state=estado)
    if order == "asc":
        consultas = consultas.order_by(Contact.creation_date.asc())
    else:
        consultas = consultas.order_by(Contact.creation_date.desc())

    total = consultas.count()
    consultas = (
        consultas.offset((page - 1) * current_app.config["MAX_ELEMENTS_ON_PAGE"])
        .limit(current_app.config["MAX_ELEMENTS_ON_PAGE"])
        .all()
    )
    pagination = {
        "page": page,
        "pages": (total + current_app.config["MAX_ELEMENTS_ON_PAGE"] - 1)
        // current_app.config["MAX_ELEMENTS_ON_PAGE"],
        "has_prev": page > 1,
        "has_next": page * current_app.config["MAX_ELEMENTS_ON_PAGE"] < total,
        "prev_num": page - 1,
        "next_num": page + 1,
    }

    return consultas, pagination
