from functools import wraps

from flask import abort, session

from src.core.users import is_sys_admin as is_sys_admin_core


def is_authenticated(session):
    """Verifica si el usuario está autenticado.

    Args:
        session: La sesión actual del usuario.

    Returns:
        True si el usuario está autenticado, False en caso contrario.
    """
    return session.get("user") is not None


def login_required(f) -> bool:
    """Decorator que restringe el acceso a usuarios autenticados.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica autenticación antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated(session):
            return abort(403)

        return f(*args, **kwargs)

    return wrapper


def login_current(f):
    """Decorador que verifica el usuario logueado."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "id" not in session:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_sys_admin(f):
    """Decorator que restringe el acceso a usuarios con permisos de administrador del sistema.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica rol de administrador antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if is_sys_admin_core():
            return f(*args, **kwargs)
        return abort(403)

    return wrapper


def is_admin(f):
    """Decorator que restringe el acceso a usuarios con rol de Administración o
    administrador del sistema.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica el rol antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "Administracion" in session["roles"] or is_sys_admin_core():
            return f(*args, **kwargs)
        return abort(403)

    return wrapper


def is_volunteer(f):
    """Decorator que restringe el acceso a usuarios con rol de Voluntariado o
    administrador del sistema.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica el rol antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "Voluntariado" in session["roles"] or is_sys_admin_core():
            return f(*args, **kwargs)
        return abort(403)

    return wrapper


def is_equestrian(f):
    """Decorator que restringe el acceso a usuarios con rol de Ecuestre o administrador del sistema.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica el rol antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "Ecuestre" in session["roles"] or is_sys_admin_core():
            return f(*args, **kwargs)
        return abort(403)

    return wrapper


def is_technical(f):
    """Decorator que restringe el acceso a usuarios con rol de Técnica o administrador del sistema.

    Args:
        f: La función que se decorará.

    Returns:
        La función decorada que verifica el rol antes de ejecutarse.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "Tecnica" in session["roles"] or is_sys_admin_core():
            return f(*args, **kwargs)
        return abort(403)

    return wrapper


def permission_required(permission):
    """Decorator que restringe el acceso a usuarios con permisos específicos o
    administrador del sistema.

    Args:
        permission: El permiso requerido para acceder a la función.
        f: La función que se decorará.

    Returns:
        La función decorada que verifica el permiso antes de ejecutarse.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if permission in session["permissions"] or is_sys_admin_core():
                return f(*args, **kwargs)
            return abort(403)

        return wrapper

    return decorator
