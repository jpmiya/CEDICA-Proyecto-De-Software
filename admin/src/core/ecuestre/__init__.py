import os
import ulid
from typing import List

from flask import current_app
from sqlalchemy import asc, desc
from sqlalchemy.sql import expression as expr

from src.core.database import db
from src.core.ecuestre.horse import Horse
from src.core.ecuestre.horse_document import HorseDocument
from src.core.functions import is_valid_url
from src.web.validators.general_validations import (
    check_radio_value,
    check_select,
    check_valid_birthday,
    validate_string,
)
from src.web.validators.institutional_work_validations import check_employee_role


def create_horse(**kwargs):
    """Crea un nuevo caballo en la base de datos.

    Args:
        **kwargs: Argumentos para inicializar los campos del modelo Horse.

    Returns:
        Horse: El objeto Horse recién creado.
    """
    horse = Horse(**kwargs)
    db.session.add(horse)
    db.session.commit()

    return horse


def get_horses():
    """Obtiene todos los caballos registrados en la base de datos.

    Returns:
        list: Una lista de objetos Horse.
    """
    return Horse.query.all()


search_map = {
    "name": Horse.name,
    "rider": Horse.rider_type,
}

order_map = {
    "name": Horse.name,
    "birth_date": Horse.birth_date,
    "entry_date": Horse.entry_date,
}


def search_horses(
    page,
    search_string="",
    search_by="name",
    order_by="name",
    order_direction="asc",
):
    """Busca caballos según criterios específicos y pagina los resultados.

    Args:
        page (int): Número de página de los resultados.
        search_string (str, opcional): Cadena de búsqueda para filtrar resultados.
            Por defecto, cadena vacía (sin filtro).
        search_by (str, opcional): Campo por el que se realizará la búsqueda
            (por ejemplo, 'name' o 'rider'). Por defecto, 'name'.
        order_by (str, opcional): Campo por el que se ordenarán los resultados
            (por ejemplo, 'name', 'birth_date' o 'entry_date'). Por defecto, 'name'.
        order_direction (str, opcional): Dirección del orden ('asc' para ascendente
            o 'desc' para descendente). Por defecto, 'asc'.

    Returns:
        tuple: Una tupla que contiene:
            - list: Lista de objetos Horse en la página actual.
            - Pagination: Objeto de paginación con información de la consulta.
    """
    # Obtener la columna para ordenar desde el diccionario
    order_column = order_map.get(order_by)

    if order_direction == "desc":
        order_column = desc(order_column)

    # Obtener la columna para la búsqueda
    search_column = search_map.get(search_by)

    if search_string:
        # Aplicar filtro de búsqueda
        search_string = search_string.strip().lower()
        pagination = (
            Horse.query.order_by(order_column)
            .filter(expr.func.lower(search_column).like(f"%{search_string}%"))
            .paginate(
                page=page,
                per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
                error_out=False,
            )
        )
    else:
        # Sin filtro de búsqueda
        pagination = Horse.query.order_by(order_column).paginate(
            page=page,
            per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
            error_out=False,
        )

    horses = pagination.items

    return horses, pagination


def create_document(title, doc_type, format, source, horse_id):
    """Crea un nuevo documento asociado a un caballo específico.

    Args:
        title (str): Título del documento.
        doc_type (str): Tipo del documento (por ejemplo, 'certificado', 'informe').
        format (str): Formato del documento ('file' o 'link').
        source (FileStorage o str): Fuente del documento, que puede ser un archivo
            cargado o un enlace.
        horse_id (int): ID del caballo al que pertenece el documento.

    Returns:
        HorseDocument: El objeto del documento recién creado.

    Raises:
        ValueError: Si el formato del archivo no está permitido.
    """
    _, file_extension = os.path.splitext(source.filename)
    if file_extension.lower() not in current_app.config["ACCEPTED_EXTENSIONS"]:
        msg = f"""Formato de archivo no permitido. Los formatos permitidos son:
            {', '.join(current_app.config['ACCEPTED_EXTENSIONS'])}"""
        raise ValueError(msg)

    if format == "file":
        client = current_app.storage.client
        bucket_name = "grupo13"
        source.seek(0, 2)  # Mueve el puntero al final del archivo
        length = source.tell()  # Calcula el tamaño del archivo
        source.seek(0)  # Regresa el puntero al inicio del archivo
        file_id = str(ulid.ulid())
        file_name = f"{file_id}-{source.filename}"
        client.put_object(
            bucket_name, file_name, source, length, content_type=source.content_type
        )
        source = file_name

    new_document = HorseDocument(
        title=title, type=doc_type, format=format, source=source, horse_id=horse_id
    )
    db.session.add(new_document)
    db.session.commit()

    return new_document


def find_horse_by_id(horse_id):
    """Busca un caballo por su ID.

    Args:
        horse_id (int): ID del caballo a buscar.

    Returns:
        Horse: El objeto Horse correspondiente al ID, o None si no se encuentra.
    """
    return Horse.query.filter_by(id=horse_id).first()


def modify_horse(horse, attributes):
    """Modifica los atributos de un caballo existente.

    Args:
        horse (Horse): Objeto Horse a modificar.
        attributes (dict): Diccionario con los atributos y sus nuevos valores.

    Returns:
        Horse: El objeto Horse actualizado.
    """
    for key, value in attributes.items():
        setattr(horse, key, value)
    db.session.add(horse)
    db.session.commit()

    return horse


def toggle_active(horse):
    """Alterna el estado activo de un caballo.

    Args:
        horse (Horse): Objeto Horse cuyo estado se alternará.

    Returns:
        Horse: El objeto Horse con su estado activo actualizado.
    """
    horse.active = not horse.active
    db.session.add(horse)
    db.session.commit()

    return horse


order_map_file = {
    "title": HorseDocument.title,
    "date": HorseDocument.created_at,
}

search_map_file = {
    "title": HorseDocument.title,
}


def get_documents_by_horse_id(
    page,
    horse_id,
    document_type,
    order="newer",
    search_value="",
):
    """
    Obtiene documentos asociados a un caballo específico, con soporte para filtros,
    ordenamiento y paginación.

    Parámetros:
        page (int): Número de página para la paginación de los resultados.
        horse_id (int): ID del caballo cuyos documentos se desean obtener.
        document_type (str, opcional): Tipo de documento para filtrar los resultados.
        order (str, opcional): Criterio de ordenamiento. Puede ser:
            - "newer" (por defecto): Ordenar por fecha de creación, más reciente primero.
            - "older": Ordenar por fecha de creación, más antiguo primero.
            - "titleA-Z": Ordenar por título de documento en orden ascendente.
            - "titleZ-A": Ordenar por título de documento en orden descendente.
        search_value (str, opcional): Cadena de búsqueda para filtrar documentos por título.

    Retorna:
        tuple: Un objeto de paginación y una lista de documentos en la página actual:
            - pagination: Objeto de paginación que contiene metadatos
            (como total de páginas y elementos).
            - items: Lista de documentos correspondientes a la página actual.

    Nota:
        - La función utiliza la configuración `MAX_ELEMENTS_ON_PAGE` de la aplicación
        para determinar la cantidad
          máxima de elementos por página.
        - Si no se especifican filtros, devuelve todos los documentos
        asociados al caballo indicado.

    """

    query = HorseDocument.query.filter_by(horse_id=horse_id)

    # Filtrar por tipo de documento
    if document_type:
        query = query.filter_by(type=document_type)

    # Filtrar por búsqueda en el título
    if search_value:
        query = query.filter(HorseDocument.title.ilike(f"%{search_value}%"))

    # Ordenar según el parámetro "order"
    if order == "newer":
        query = query.order_by(desc(HorseDocument.created_at))
    elif order == "older":
        query = query.order_by(asc(HorseDocument.created_at))
    elif order == "titleA-Z":
        query = query.order_by(asc(HorseDocument.title))
    elif order == "titleZ-A":
        query = query.order_by(desc(HorseDocument.title))

    # Paginar los resultados
    pagination = query.paginate(
        page=page, per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"]
    )

    # Retornar el objeto de paginación y los items
    return pagination, pagination.items


def download_document(document_id):
    """Descarga un documento específico.

    Args:
        document_id (int): ID del documento a descargar.

    Returns:
        tuple: El contenido del archivo descargado y el objeto del documento.

    Raises:
        ValueError: Si el documento no existe.
    """
    document = HorseDocument.query.filter_by(id=document_id).first()
    if not document:
        raise ValueError("Documento no encontrado")
    client = current_app.storage.client
    bucket_name = "grupo13"
    response = client.get_object(bucket_name, document.source)

    return response, document


def get_document_by_id(document_id):
    """Obtiene un documento por su ID.

    Args:
        document_id (int): ID del documento.

    Returns:
        HorseDocument: El documento encontrado o None si no existe.
    """
    return HorseDocument.query.filter_by(id=document_id).first()


def add_link(title, link, horse_id, document_type):
    """Agrega un enlace como documento asociado a un caballo.

    Args:
        title (str): Título del enlace.
        link (str): URL del enlace.
        horse_id (int): ID del caballo.
        document_type: Tipo de archivo eferente al caballo.

    Returns:
        HorseDocument: El objeto del documento recién creado.

    Raises:
        ValueError: Si el enlace no es válido.
    """
    try:
        if not is_valid_url(link):
            raise ValueError("URL inválida")
        new_link = HorseDocument(
            title=title,
            type=document_type,
            format="link",
            source=link,
            horse_id=horse_id,
        )
        db.session.add(new_link)
        db.session.commit()
        return new_link
    except ValueError as e:
        raise e


def check_order_params(page, order, order_direction, search_by, search_value):
    """Validar los parámetros de ordenamiento y búsqueda.

    Args:
        page (int): Número de página.
        order (str): Columna de ordenamiento.
        order_direction (str): Dirección de orden, "asc" o "desc".
        search_by (str): Columna para búsqueda.
        search_value (str): Valor para buscar en la columna.

    Returns:
        bool: True si los parámetros son válidos, False en caso contrario.
    """
    if order not in order_map:
        return False
    if order_direction not in ["asc", "desc"]:
        return False
    if search_by not in search_map:
        return False
    if search_by == "rider" and search_value not in [
        "Hipoterapia",
        "Monta Terapeutica",
        "Deporte Ecuestre Adaptado",
        "Actividades Recreativas",
        "Equitacion",
    ]:
        return False
    if not isinstance(page, int) or page < 1 or page > 1000:
        return False

    return True


def check_create_horse_params(
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
):
    """Validar los parámetros para crear un caballo.

    Args:
        name (str): Nombre del caballo.
        birth_date (str): Fecha de nacimiento en formato válido.
        gender (str): Género del caballo ("Macho" o "Hembra").
        breed (str): Raza del caballo.
        fur (str): Pelaje del caballo.
        acquisition_type (str): Tipo de adquisición ("Compra" o "Donación").
        entry_date (str): Fecha de ingreso en formato válido.
        sede (str): Sede a la que pertenece el caballo.
        rider_type (str): Tipo de jinete asignado.
        trainer_id (str): ID del entrenador.
        conductor_id (str): ID del conductor.

    Returns:
        bool: True si los parámetros son válidos.

    Raises:
        ValueError: Si algún parámetro no cumple con los requisitos.
    """
    messages: List[str] = []

    # Nombre
    messages.extend(
        validate_string(
            s=name,
            label="Nombre del caballo",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    messages.extend(
        check_select(
            field=gender,
            label="Género del caballo",
            permitted_values=("Macho", "Hembra"),
        )
    )

    messages.extend(
        validate_string(
            s=breed,
            label="Raza del caballo",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=tuple(),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    messages.extend(
        validate_string(
            s=fur,
            label="Pelaje del caballo",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=tuple(),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    messages.extend(
        check_radio_value(
            field=acquisition_type,
            label="Tipo de adquisición",
            permitted_values=("Compra", "Donacion"),
        )
    )

    lista_aux: List[str] = []
    lista_aux.extend(check_valid_birthday(date=entry_date, label="Fecha de ingreso"))
    lista_aux.extend(
        check_valid_birthday(date=birth_date, label="Fecha de nacimiento del caballo")
    )
    if len(lista_aux) == 0:
        if birth_date > entry_date:
            lista_aux.append(
                "La fecha de ingreso no puede ser menor a la fecha de nacimiento."
            )

    messages.extend(lista_aux)

    messages.extend(
        check_select(field=sede, label="Sede", permitted_values=("CASJ", "HLP", "OTRO"))
    )
    permitted_rider_types = (
        "Hipoterapia",
        "Monta Terapeutica",
        "Deporte Ecuestre Adaptado",
        "Actividades Recreativas",
        "Equitacion",
    )
    messages.extend(
        check_select(
            field=rider_type,
            label="Tipo de J&A asignado",
            permitted_values=permitted_rider_types,
        )
    )

    messages.extend(
        check_employee_role(
            employee_id=trainer_id,
            expected_profession=None,
            expected_job_position="Entrenador de Caballos",
            role_name="Entrenador",
        )
    )

    messages.extend(
        check_employee_role(
            employee_id=conductor_id,
            expected_job_position="Conductor",
            role_name="Conductor del caballo",
        )
    )

    return messages


def check_action_file_params(document_id, horse_id):
    """Verifica si los parámetros de acción para el archivo son válidos.

    Args:
        document_id (str): ID del documento.
        horse_id (str): ID del caballo.

    Returns:
        bool: True si ambos parámetros son válidos, False en caso contrario.
    """
    if not document_id.isdigit():
        return False
    if not horse_id.isdigit():
        return False
    if not Horse.query.filter_by(id=horse_id).first():
        return False
    if not HorseDocument.query.filter_by(id=document_id).first():
        return False

    return True


def get_horses_by_headquarters_and_proposal(
    headquarters: str, proposal: str
) -> List[Horse]:
    """Obtiene una lista de caballos según la sede y la propuesta.

    Args:
        headquarters (str): Sede en la que se encuentran los caballos.
        proposal (str): Tipo de propuesta asignada a los caballos.

    Returns:
        List[Horse]: Lista de objetos Horse que coinciden con los criterios especificados.
    """
    query = Horse.query
    if headquarters and headquarters != "":
        query = query.filter(Horse.sede == headquarters)

    if proposal and proposal != "":
        query = query.filter(Horse.rider_type == proposal)

    return query.all()


def delete_document_by_id(document_id):
    """Elimina un documento según su ID.

    Args:
        document_id (int): ID del documento a eliminar.

    Returns:
        HorseDocument: El objeto del documento eliminado.

    Raises:
        ValueError: Si el documento no existe en la base de datos.
    """
    document = HorseDocument.query.filter_by(id=document_id).first()
    if not document:
        raise ValueError("Documento no encontrado")
    db.session.delete(document)
    db.session.commit()

    return document
