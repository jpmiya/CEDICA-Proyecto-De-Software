import re
from datetime import datetime

from flask import current_app
from sqlalchemy import desc
from sqlalchemy.sql import expression as expr

from src.core import users
from src.core.database import db
from src.core.publications.publication import Publication
from src.core.users.user import User


def create_publication(**kwargs):
    """
    Crea una nueva publicación con los datos proporcionados.

    Args:
        **kwargs: Diccionario con los datos necesarios para crear la publicación.
    """
    publication = Publication(**kwargs)
    if publication.state == "Publicado":
        publication.publication_date = datetime.now()
    db.session.add(publication)
    db.session.commit()


def update_publication(publication, **kwargs):
    """
    Actualiza los datos de una publicación existente.

    Args:
        publication (Publication): Objeto de la publicación a actualizar.
        **kwargs: Diccionario con los nuevos datos para actualizar.
    """
    if kwargs.get("state") == "Publicado" and publication.state != "Publicado":
        publication.publication_date = datetime.now()
    elif kwargs.get("state") != "Publicado" and publication.state == "Publicado":
        publication.publication_date = None
    for key, value in kwargs.items():
        setattr(publication, key, value)
    db.session.add(publication)
    db.session.commit()


def get_publication_by_id(publication_id):
    """
    Recupera una publicación por su ID.

    Args:
        publication_id (int): ID de la publicación.

    Returns:
        Publication: Objeto de la publicación encontrada o None.
    """
    return Publication.query.filter_by(id=publication_id).first()


search_map = {
    "title": Publication.title,
    "author_alias": User.alias,
    "creation_date": Publication.creation_date,
    "publication_date": Publication.publication_date,
}

order_map = {
    "creation_date": Publication.creation_date,
    "publication_date": Publication.publication_date,
    "title": Publication.title,
}


def search_and_order_publications(
    page,
    order="asc",
    order_by="creation_date",
    search_by="",
    search_value="",
    end_date=None,
    start_date=None,
):
    """
    Busca, ordena y pagina las publicaciones según los criterios especificados.

    Args:
        page (int): Número de la página a devolver.
        order (str): Dirección del orden ("asc" o "desc").
        order_by (str): Columna para ordenar.
        search_by (str): Columna para buscar.
        search_value (str): Valor a buscar.
        start_date (str): Fecha de inicio del rango de búsqueda (YYYY-MM-DD).
        end_date (str): Fecha de fin del rango de búsqueda (YYYY-MM-DD).

    Returns:
        tuple: Paginación y lista de publicaciones.
    """
    order_column = order_map.get(order_by)

    if order == "desc":
        order_column = desc(order_column)

    if search_by == "author_alias":
        query = Publication.query.join(User, Publication.author_id == User.id).order_by(
            order_column
        )

    else:
        query = Publication.query.order_by(order_column)
    if search_by != "":
        search_column = search_map.get(search_by)

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(search_column >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(search_column <= end_date)

    if search_value != "":
        search_value = search_value.lower()
        query = query.filter(expr.func.lower(search_column).like(f"%{search_value}%"))

    pagination = query.paginate(
        page=page, per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"], error_out=False
    )
    publications = pagination.items

    return pagination, publications


def check_order_params(page, order, order_by, search_by, start_date, end_date):
    """
    Validar los parámetros para búsqueda y orden de publicaciones.

    Args:
        page (int): Número de página.
        order (str): Dirección del orden ("asc" o "desc").
        order_by (str): Columna para ordenar.
        search_by (str): Columna para buscar.
        start_date (str): Fecha de inicio (YYYY-MM-DD).
        end_date (str): Fecha de fin (YYYY-MM-DD).

    Returns:
        bool: True si los parámetros son válidos.

    Raises:
        ValueError: Si algún parámetro no es válido.
    """
    if order not in ["asc", "desc"]:
        raise ValueError("Dirección de orden inválida")
    if order_by not in ["title", "creation_date", "publication_date"]:
        raise ValueError("Parámetro de orden inválido")
    list_search_by = [
        "",
        "title",
        "author_id",
        "creation_date",
        "publication_date",
        "author_alias",
    ]
    if search_by not in list_search_by:
        raise ValueError("Parámetro de búsqueda inválido")
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Fecha de inicio inválida")
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                if end_date < start_date:
                    raise ValueError
            except ValueError:
                raise ValueError("Fecha de fin inválida")
    if page < 1:
        raise ValueError("Número de página inválido")
    return True


def delete_publication_by_id(publication_id):
    """
    Elimina una publicación por su ID.

    Args:
        publication_id (int): ID de la publicación.

    Raises:
        ValueError: Sí ocurre un error durante la eliminación.
    """

    publication = Publication.query.filter_by(id=publication_id).first()
    if publication is None:
        raise ValueError("No se encontró la publicación")
    db.session.delete(publication)
    db.session.commit()


def check_create_params(title, summary, state, author_id, content):
    """
    Validar los parámetros para crear una publicación.

    Args:
        title (str): Título de la publicación.
        summary (str): Resumen de la publicación.
        state (str): Estado de la publicación.
        author_id (str): ID del autor.
        content (str): Contenido de la publicación.

    Returns:
        bool: True si los parámetros son válidos.

    Raises:
        ValueError: Si algún parámetro no es válido.
    """
    if len(title.strip()) == 0:
        raise ValueError("El título no puede estar vacío")
    if len(title) > 30:
        raise ValueError("El título no puede tener más de 30 caracteres")
    if len(summary) > 500:
        raise ValueError("El copete no puede tener más de 500 caracteres")
    if len(summary.strip()) == 0:
        raise ValueError("El copete no puede estar vacío")
    if len(re.sub(r"<[^>]*>", "", content).strip()) == 0:
        raise ValueError("El contenido no puede estar vacío")
    if state not in ["Borrador", "Publicado", "Archivado"]:
        raise ValueError("El estado de la publicación no es válido")
    if not author_id.isdigit() or not users.find_user_by_id(author_id):
        raise ValueError("El autor no existe")
    if not "Editor" in users.get_roles(users.find_user_by_id(author_id)):
        raise ValueError("El autor no es un editor")

    return True


def get_publications_api(author, published_from, published_to, page, per_page):
    """
    Recupera una lista paginada de publicaciones publicadas.

    Args:
        author (str): Alias del autor.
        published_from (str): Fecha de inicio (YYYY-MM-DD).
        published_to (str): Fecha de fin (YYYY-MM-DD).
        page (int): Número de página.
        per_page (int): Número de publicaciones por página.

    Returns:
        tuple: Paginación y lista de publicaciones.
    """
    query = Publication.query.filter(Publication.state == "Publicado").order_by(
        desc(Publication.publication_date)
    )
    if author:
        users_id = [user.id for user in users.find_users_by_alias(author)]
        query = query.filter(Publication.author_id.in_(users_id))
    if published_from:
        query = query.filter(Publication.publication_date >= published_from)
    if published_to:
        query = query.filter(Publication.publication_date <= published_to)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    publications = pagination.items

    return pagination, publications


def check_api_get_publications_params(
    page, author_alias, published_from, published_to, per_page
):
    """
    Validar los parámetros para la API de publicaciones.

    Args:
        page (int): Número de página.
        author_alias (str): Alias del autor.
        published_from (str): Fecha de inicio (YYYY-MM-DD).
        published_to (str): Fecha de fin (YYYY-MM-DD).
        per_page (int): Número de elementos por página.

    Returns:
        bool: True si los parámetros son válidos.

    Raises:
        ValueError: Si algún parámetro no es válido.
    """
    if not isinstance(page, int):
        raise ValueError("Número de página inválido")

    if author_alias and not users.find_users_by_alias(author_alias):
        raise ValueError("El autor no existe")

    if published_from:
        try:
            datetime.strptime(published_from, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Fecha de inicio inválida")

    if published_to:
        try:
            datetime.strptime(published_to, "%Y-%m-%d")
            if published_from and published_to < published_from:
                raise ValueError
        except ValueError:
            raise ValueError("Fecha de fin inválida")

    if not isinstance(per_page, int) or per_page <= 0:
        raise Exception("Número de elementos por página inválido")

    return True
