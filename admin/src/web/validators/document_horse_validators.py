from typing import List

from src.core.ecuestre.horse import Horse
from src.core.functions import is_valid_url


def check_upload_link(horse: Horse, title: str, link: str, document_type: str):
    """
    Verifica los parámetros relacionados con la subida de un enlace y devuelve
    una lista de mensajes de error si alguno de ellos no es válido.

    Args:
        horse (Horse): El objeto Horse asociado al enlace. Puede ser None si no se encuentra.
        title (str): El título del enlace. Debe ser un texto no vacío con un máximo de 30
            caracteres.
        link (str): El enlace a validar. Debe ser una URL válida.
        document_type (str): El tipo de documento asociado al enlace. Debe pertenecer a un conjunto
                             específico de tipos válidos.

    Returns:
        List[str]: Una lista de mensajes de error en caso de que se detecten problemas
        con los parámetros. Si no hay errores, la lista estará vacía.
    """
    messages: List[str] = []
    # Chequeo de jinete/amazona
    if horse is None:
        messages.append("Hubo un error y no se pudo encontrar al usuario")
    # Chequeo de título
    if title is None or title == "" or len(title.strip()) == 0:
        messages.append("Ingrese un título para el enlace")
        return messages

    if len(title) > 30:
        messages.append("El título tiene un límite de 30 caracteres")

    # Chequeo de link vacío
    if link is None or link == "":
        messages.append("Ingrese un enlace")

    # Chequeo de tipo
    document_types_valid = [
        "ficha_general",
        "planificacion",
        "informe_de_evaluacion",
        "carga_de_imagenes",
        "registro_veterinario",
    ]

    if document_type not in document_types_valid:
        messages.append("Ingrese un tipo válido de documento")

    # Chequeo de link
    if not is_valid_url(link):
        messages.append("Por favor ingrese un enlace a un archivo real")

    return messages
