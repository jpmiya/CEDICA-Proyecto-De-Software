from typing import List

from src.core import riders
from src.core.functions import is_valid_url
from src.core.riders.rider import Rider
from src.core.riders.rider_document import RiderDocument
from src.web.validators.general_validations import (
    check_number,
    check_select,
    validate_string,
)


def check_modify_document(user_id: int, document_id: int, title: str, doc_type: str):
    """
    Validar los datos enviados para modificar un documento.

    Esta función realiza validaciones sobre los campos proporcionados para asegurar
    que cumplen con los requisitos esperados. Recopila los errores encontrados en
    una lista y los devuelve.

    Parámetros:
        document_id (int): ID del documento que se desea modificar. Debe ser un
        número válido.
        title (str): Título del documento, sujeto a restricciones de formato y
        longitud.
        doc_type (str): Tipo de documento, debe ser uno de los valores permitidos.

    Retorna:
        List[str]: Una lista con los mensajes de error encontrados durante la
        validación. Si no se encuentran errores, la lista estará vacía.

    Validaciones realizadas:
        - `document_id`:
            - Debe ser un número válido.
        - `title`:
            - Longitud máxima de 100 caracteres.
            - Puede incluir números y espacios.
            - Permite caracteres especiales como: '-', '_', '.', '(', ')', '[',
              ']', '{', '}', '!', '@', '#', '$', '%', '^', '&', '*', '=', '+',
              ',', ';', ':', "'", '"', '<', '>', '?', '~', '`' o un espacio
        - `doc_type`:
            - Debe coincidir con uno de los valores permitidos: "entrevista",
              "evaluacion", "planificaciones", "evolucion", "cronicas",
              "documental".
    """
    message: List[str] = []
    # Chequeo del ID del documento
    message.extend(check_number(str(document_id), label="Documento"))
    if len(message) == 0:
        rider: Rider = riders.get_rider_by_id(user_id)
        document: RiderDocument = riders.get_document_by_id(document_id=document_id)

        if rider is None:
            message.append("El jinete no fue encontrado")
        if document is None:
            message.append("El documento seleccionado no existe")
        if rider and document:
            if not any(document.id == int(document_id) for document in rider.documents):
                message.append("El documento seleccionado no existe")

    allowed_special_characters = (
        "-",
        "_",
        ".",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
        " ",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "=",
        "+",
        ",",
        ";",
        ":",
        "'",
        '"',
        "<",
        ">",
        "?",
        "~",
        "`",
    )

    # Validación del título
    message.extend(
        validate_string(
            s=title,
            label="Título del documento",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=allowed_special_characters,
            spaced=True,
            only_numbers_accepted=True,
        )
    )

    document_types_valid = (
        "entrevista",
        "evaluacion",
        "planificaciones",
        "evolucion",
        "cronicas",
        "documental",
    )
    # Validación del tipo de documento
    message.extend(
        check_select(
            field=doc_type,
            label="Tipo de documento",
            permitted_values=document_types_valid,
        )
    )

    return message


def check_upload_link(rider: Rider, title: str, link: str, document_type: str):
    """
    Validar los datos proporcionados para subir un enlace asociado a un jinete.

    Parámetros:
        rider (Rider): El jinete asociado al enlace.
        title (str): Título del enlace.
        link (str): URL del archivo a asociar.
        document_type (str): Tipo de documento.

    Retorna:
        List[str]: Una lista de mensajes de error si se encuentran problemas en los datos.
                   Si la lista está vacía, los datos son válidos.

    Validaciones realizadas:
        - Verifica que el jinete exista.
        - Validar que el título no esté vacío y no exceda los 30 caracteres.
        - Comprueba que el enlace no esté vacío.
        - Verifica que el tipo de documento sea uno de los valores válidos:
          ("entrevista", "evaluacion", "planificaciones", "evolucion", "cronicas", "documental").
        - Validar que el enlace sea una URL válida utilizando la función `is_valid_url`.
    """
    messages: List[str] = []
    # Chequeo de jinete/amazona
    if rider is None:
        messages.append("Hubo un error y no se pudo encontrar al usuario")
    # Chequeo de título
    if title is None or title == "":
        messages.append("Ingrese un título para el enlace")
        return messages

    if len(title) > 30:
        messages.append("El título tiene un límite de 30 caracteres")
    # Chequeo de link vacío
    if link is None or link == "":
        messages.append("Ingrese un enlace")

    # Chequeo de tipo
    document_types_valid = [
        "entrevista",
        "evaluacion",
        "planificaciones",
        "evolucion",
        "cronicas",
        "documental",
    ]

    if document_type not in document_types_valid:
        messages.append("Ingrese un tipo válido de documento")

    # Chequeo de link
    if not is_valid_url(link):
        messages.append("Por favor ingrese un enlace a un archivo real")

    return messages
