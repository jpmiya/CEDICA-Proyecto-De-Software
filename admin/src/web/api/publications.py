from flask import Blueprint, request, current_app
from urllib3.exceptions import MaxRetryError

from src.core import publications, users
from src.web.schemas.publications import publication_schema, publications_schema


bp = Blueprint("publications_api", __name__, url_prefix="/api/publications")


@bp.get("/")
def get_publications():
    """
    Devuelve una lista paginada de publicaciones formateadas en JSON.
    """
    page = request.args.get("page", 1, type=int)
    author_alias = request.args.get("author", None)
    published_from = request.args.get("published_from", None)
    published_to = request.args.get("published_to", None)
    per_page = request.args.get(
        "per_page", 0, type=int
    )

    try:
        # Verificar los parámetros para la obtención de publicaciones
        publications.check_api_get_publications_params(
            page, author_alias, published_from, published_to, per_page
        )
    except ValueError as e:
        return str(e), 400

    # Obtener la lista paginada de publicaciones
    pagination, items = publications.get_publications_api(
        author_alias, published_from, published_to, page, per_page
    )
    data = publications_schema.dump(items)

    # Agregar el alias del autor a cada publicación
    if not author_alias:
        for item in data:
            item["author"] = users.find_user_by_id(item["author_id"]).alias
    else:
        for item in data:
            item["author"] = author_alias

    respuesta = {
        "data": data,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }

    return respuesta, 200


@bp.get("/<int:id>")
def get_publication(id):
    """
    Devuelve una publicación por su id, formateada en JSON.
    """
    try:
        publication = publications.get_publication_by_id(id)
        if publication:
            if publication.state != "Publicado":
                return "Publicación no encontrada", 404
            data = publication_schema.dump(publication)
            data["author"] = users.find_user_by_id(data["author_id"]).alias
            return data, 200
        else:
            return "Publicación no encontrada", 404
    except ValueError as ve:
        return {"error": f"Error de validación: {str(ve)}"}, 400
    except MaxRetryError:
        return {
            "error": "No se pudo hacer la conexión con la base de datos. Reintente"
        }, 500
    except:
        return "Error al buscar la publicación", 500
