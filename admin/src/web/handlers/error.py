from dataclasses import dataclass
from flask import render_template


@dataclass
class Error:
    """Representa un error con su código, mensaje y descripción."""

    code: int
    message: str
    description: str


def not_found_error(error: Error):
    """
    Maneja el error 404 (No encontrado) y retorna una página de error personalizada.

    Args:
        error (Exception): Excepción que provoca el error 404.

    Returns:
        Tuple: Contenido de la página renderizada y el código de estado HTTP 404.
    """
    error = Error(404, "No encontrada", "La URL no fue encontrada en el servidor.")
    return render_template("error.html", error=error), error.code


def forbidden_error(error: Error):
    """
    Maneja el error 403 (Acceso prohibido) y retorna una página de error personalizada.

    Args:
        error (Exception): Excepción que provoca el error 403.

    Returns:
        Tuple: Contenido de la página renderizada y el código de estado HTTP 403.
    """
    error = Error(403, "Acceso prohibido", "No tiene permiso para acceder a este sitio")
    return render_template("error.html", error=error), error.code


def internal_server_error(error: Error):
    """
    Maneja el error 500 (Error interno del servidor) y retorna una página de error personalizada.

    Args:
        error (Exception): Excepción que provoca el error 500.

    Returns:
        Tuple: Contenido de la página renderizada y el código de estado HTTP 500.
    """
    error = Error(500, "Error interno", "Algo salió mal en el servidor, reintente")
    return render_template("error.html", error=error), error.code


def rider_not_found(error: Error):
    """
    Maneja un error personalizado para un jinete/amazona no encontrado.

    Args:
        error (Exception): Excepción que provoca el error personalizado.

    Returns:
        Tuple: Contenido de la página renderizada y el código de estado HTTP 1024.
    """
    error = Error(
        1024, "Amazona/Jinete no encontrado", "Algo salió mal, y no se pudo encontrar"
    )
    return render_template("error.html", error=error), error.code


def bad_request_error(error: Error):
    """
    Maneja el error 400 (Solicitud incorrecta) y retorna una página de error personalizada.

    Args:
        error (Exception): Excepción que provoca el error 400.

    Returns:
        Tuple: Contenido de la página renderizada y el código de estado HTTP 400.
    """
    error = Error(400, "Solicitud incorrecta", "Hubo un error en la carga")
    return render_template("error.html", error=error), error.code
