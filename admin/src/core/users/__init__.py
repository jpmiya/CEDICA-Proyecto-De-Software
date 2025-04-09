from typing import List, Optional

from flask import current_app, flash, session
from sqlalchemy import desc, func
from sqlalchemy.sql import expression as expr

from src.core.database import db
from src.core.bcrypt import bcrypt
from src.core.functions import check_alias, check_password, check_roles
from src.core.users.user import User
from src.core.users.role import Role
from src.core.users.permission import Permission
from src.core import team, pending_users
from src.web.validators.general_validations import check_email


order_map = {"email": User.email, "inserted_at": User.inserted_at}

search_map = {"email": User.email, "active": User.active, "rol": Role.name}


def list_and_search_users(
    page, search_string="", search_by="name", order_by="name", order_direction="asc"
):
    """
    Lista y busca usuarios según los filtros y el orden dados.

    :param page: Número de la página actual
    :param search_string: Cadena de búsqueda para filtrar
    :param search_by: Campo por el cual buscar (por ejemplo, 'email', 'active', 'rol')
    :param order_by: Campo por el cual ordenar (por ejemplo, 'email', 'inserted_at')
    :param order_direction: 'asc' para ascendente o 'desc' para descendente
    :return: Lista de usuarios y objeto de paginación
    """
    order_column = order_map.get(order_by)
    if order_direction == "desc":
        order_column = desc(order_column)

    search_column = search_map.get(search_by)
    if search_string:
        if search_by == "active":
            search_value = search_string.lower() == "si"
            pagination = (
                User.query.order_by(order_column)
                .filter(User.active == search_value)
                .paginate(
                    page=page,
                    per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
                    error_out=False,
                )
            )
        elif search_by == "rol":
            pagination = (
                User.query.join(User.roles)
                .order_by(order_column)
                .filter(func.lower(Role.name).like(f"%{search_string.lower()}%"))
                .paginate(
                    page=page,
                    per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
                    error_out=False,
                )
            )
        else:
            search_string = search_string.strip().lower()
            pagination = (
                User.query.order_by(order_column)
                .filter(func.lower(search_column).like(f"%{search_string}%"))
                .paginate(
                    page=page,
                    per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
                    error_out=False,
                )
            )
    else:
        pagination = User.query.order_by(order_column).paginate(
            page=page,
            per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
            error_out=False,
        )

    return pagination.items, pagination


def create_user(system_admin=False, **kwargs):
    """
    Crea un nuevo usuario.

    :param system_admin: Indica si el usuario es administrador del sistema
    :param kwargs: Atributos y roles del usuario
    :return: El objeto usuario creado
    :raises: EmailExistsException, AliasExistsException
    """
    roles = kwargs.pop("roles", [])
    kwargs["password"] = bcrypt.generate_password_hash(
        kwargs["password"].encode("utf-8")
    ).decode("utf-8")

    user = User(**kwargs, system_admin=system_admin)
    db.session.add(user)

    for role in roles:
        user.roles.append(Role.query.filter_by(name=role).first())

    db.session.commit()

    return user


def create_permissions():
    """
    Crea los permisos necesarios para varios módulos.
    """
    permissions = [
        "user_index",
        "user_create",
        "user_destroy",
        "user_update",
        "user_show",
        "team_index",
        "team_create",
        "team_destroy",
        "team_update",
        "team_show",
        "rider_index",
        "rider_show",
        "rider_update",
        "rider_create",
        "rider_destroy",
        "payment_index",
        "payment_show",
        "payment_update",
        "payment_create",
        "payment_destroy",
        "charge_index",
        "charge_show",
        "charge_update",
        "charge_create",
        "charge_destroy",
        "horse_index",
        "horse_show",
        "horse_update",
        "horse_create",
        "horse_destroy",
        "accept",
        "report_index",
        "report_show",
        "publication_index",
        "publication_create",
        "publication_destroy",
        "publication_update",
        "publication_show",
    ]

    for perm in permissions:
        existe_perm = Permission.query.filter_by(name=perm).first()
        if not existe_perm:
            new_perm = Permission(name=perm)
            db.session.add(new_perm)


def create_roles():
    """
    Crea roles para la institución y asigna permisos.
    """
    print("Creando roles...")
    rol_tecnica = Role(name="Tecnica", description="Rol para el area tecnica")
    rol_administracion = Role(
        name="Administracion", description="Rol para el area administrativa"
    )
    rol_voluntariado = Role(
        name="Voluntariado", description="Rol para el area de voluntariado"
    )
    rol_ecuestre = Role(name="Ecuestre", description="Rol para el area ecuestre")
    rol_editor = Role(
        name="Editor", description="Rol para el area de edición de publicaciones"
    )

    db.session.add(rol_tecnica)
    db.session.add(rol_administracion)
    db.session.add(rol_voluntariado)
    db.session.add(rol_ecuestre)
    db.session.add(rol_editor)
    print("Asignando permisos...")
    assign_permissions(
        rol_administracion=rol_administracion,
        rol_tecnica=rol_tecnica,
        rol_voluntariado=rol_voluntariado,
        rol_ecuestre=rol_ecuestre,
        rol_editor=rol_editor,
    )


def assign_permissions(
    rol_administracion: Role,
    rol_tecnica: Role,
    rol_voluntariado: Role,
    rol_ecuestre: Role,
    rol_editor: Role,
):
    """
    Asigna permisos específicos a los roles de administración, técnica, y
    ecuestre en la aplicación.

    :param rol_administracion: El rol asociado a la administración.
    :param rol_tecnica: El rol asociado al equipo técnico.
    :param rol_voluntariado: El rol asociado al voluntariado.
    :param rol_ecuestre: El rol asociado al equipo ecuestre.
    :param rol_editor: El rol asociado al área de edición de publicaciones.
    """
    permisos_administracion = [
        "team_index",
        "team_show",
        "team_create",
        "team_update",
        "team_destroy",
        "rider_index",
        "rider_show",
        "rider_update",
        "rider_create",
        "rider_destroy",
        "payment_index",
        "payment_show",
        "payment_update",
        "payment_create",
        "payment_destroy",
        "charge_index",
        "charge_show",
        "charge_update",
        "charge_create",
        "charge_destroy",
        "accept",
        "report_index",
        "report_show",
        "horse_index",
        "horse_show",
        "publication_index",
        "publication_show",
        "publication_update",
        "publication_create",
        "publication_destroy",
    ]

    permisos_tecnica = [
        "rider_index",
        "rider_show",
        "rider_update",
        "rider_create",
        "rider_destroy",
        "charge_index",
        "charge_show",
        "horse_index",
        "horse_show",
        "report_index",
        "report_show",
    ]

    permisos_voluntariado = list()

    permisos_ecuestre = [
        "rider_index",
        "rider_show",
        "horse_index",
        "horse_show",
        "horse_update",
        "horse_create",
        "horse_destroy",
    ]

    permisos_editor = [
        "publication_index",
        "publication_show",
        "publication_update",
        "publication_create",
    ]

    add_permissions_to_role(rol_administracion, permisos_administracion)
    add_permissions_to_role(rol_tecnica, permisos_tecnica)
    add_permissions_to_role(rol_voluntariado, permisos_voluntariado)
    add_permissions_to_role(rol_ecuestre, permisos_ecuestre)
    add_permissions_to_role(rol_editor, permisos_editor)


def add_permissions_to_role(role, permissions):
    """
    Añade permisos a un rol.

    :param role: Objeto Role
    :param permissions: Lista de nombres de permisos
    """
    for perm in permissions:
        role.permissions.append(Permission.query.filter_by(name=perm).first())


def find_user_by_id(user_id):
    """
    Encuentra un usuario por su ID.

    :param user_id: ID del usuario
    :return: Objeto User o None
    """
    return User.query.filter_by(id=user_id).first()


def find_user_by_email(email: str) -> User:
    """
    Encuentra un usuario por su correo electrónico, sin distinguir mayúsculas de minúsculas.

    :param email: Correo electrónico a buscar
    :return: Objeto User o None
    """
    email = email.lower()

    return User.query.filter(func.lower(User.email) == email).first()


def update_user(user: User, **kwargs):
    """
    Actualiza un usuario existente.

    :param user: Objeto User a actualizar
    :param kwargs: Atributos y roles del usuario a actualizar
    :return: Objeto User actualizado
    :raises: EmailExistsException, AliasExistsException
    """
    roles = kwargs.pop("roles", [])
    password = kwargs.get("password")
    email = kwargs.get("email")
    alias = kwargs.get("alias")
    messages: List[str] = []
    messages.extend(check_email(field=email, label="Correo electrónico del usuario"))
    messages.extend(check_alias(alias))
    messages.extend(check_roles(roles, kwargs["system_admin"]))
    if find_user_by_alias(alias) and user.alias != alias:
        messages.append("Ya existe un usuario en el sistema con ese alias")

    if find_user_by_email(email) and user.email != email:
        messages.append("El correo electrónico ingresado ya está en uso")
    if password != "":
        aux_lista: List[str] = check_password(password)
        if len(aux_lista) == 0:
            kwargs["password"] = bcrypt.generate_password_hash(
                kwargs["password"].encode("utf-8")
            ).decode("utf-8")
        else:
            messages.extend(aux_lista)
    else:
        kwargs.pop("password", None)

    if len(messages) > 0:
        return messages

    user.roles.clear()
    for role in roles:
        role_instance = Role.query.filter_by(name=role).first()
        if role_instance:
            user.roles.append(role_instance)
    if kwargs["system_admin"]:
        user.active = True

    if user.email != email:
        msg = ""
        associated = team.find_employee_by_email(user.email)
        if associated:
            associated.user_id = None
            db.session.add(associated)
            msg = f"El usuario asociado al empleado {associated.name} ha sido desvinculado"
        new_associated = team.find_employee_by_email(email)
        if new_associated and new_associated.active:
            if new_associated.active:
                new_associated.user_id = user.id
                db.session.add(new_associated)
                msg += (
                    f""". El empleado {new_associated.name} {new_associated.last_name}
                        ha sido vinculado al usuario """
                    f"{user.alias}"
                )
            else:
                msg += f""". El empleado {new_associated.name} {new_associated.last_name}
                        no ha sido vinculado al usuario 
                        porque está inactivo"""
                return messages
        if msg != "":
            flash(msg, "info")

    for key, value in kwargs.items():
        setattr(user, key, value)

    db.session.add(user)
    db.session.commit()

    return messages


def update_my_user(user_id, **kwargs):
    """
    Actualiza la información del usuario actual.

    :param user_id: ID del usuario a actualizar
    :param kwargs: Atributos del usuario a actualizar
    :return: Objeto User actualizado
    """
    user = User.query.get(user_id)

    password = kwargs.get("password")

    if password:
        kwargs["password"] = bcrypt.generate_password_hash(
            kwargs["password"].encode("utf-8")
        ).decode("utf-8")
    else:
        kwargs.pop("password", None)

    for key, value in kwargs.items():
        setattr(user, key, value)

    db.session.add(user)
    db.session.commit()

    return user


def check_update_params(user_id, email, alias, password):
    """Validar los parametros de actualización de un usuario

    Args:
        user_id (str): El id del usuario a modificar. Este debe referenciar a una entrada de la
            base de datos de los usuarios.
        email (str): El email del usuario a modificar. Se confirma si es único entre los usuarios.
        alias (str): El alias del usuario a modificar. Se confirma si es único entre los usuarios
        password (str): Si se suministra una nueva contraseña, se verifica que cumpla con las normas
            de seguridad establecidas
                - Longitud de al menos 6 caracteres
                - Al menos una letra mayúscula
                - Al menos una letra minúscula
                - Al menos un número

    Returns
        List[str] : Retorna una lista con todos los mensajes de error que se encuentra. Si no se
            encuentra ninguno se devuelve una lista vacía
    """
    errors: List[str] = []
    if not isinstance(user_id, str) or not user_id.isdigit():
        errors.append("Se suministró al usuario de una manera no válida")
        return errors

    user = find_user_by_id(user_id=user_id)
    if user is None:
        errors.append("El usuario modificado no existe. Reintente")
        return errors

    if User.query.filter(User.email == email, User.id != user_id).first():
        errors.append("El correo electrónico ya está en uso")
    if User.query.filter(User.alias == alias, User.id != user_id).first():
        errors.append("El alias ya está en uso")

    errors.extend(check_email(email, "usuario"))
    errors.extend(check_alias(alias))

    if password:
        errors.extend(check_password(password))

    return errors


def toggle_active(user_id):
    """
    Alterna el estado activo de un usuario.

    :param user_id: ID del usuario
    """
    if not user_id.isdigit():
        raise ValueError("ID de usuario no válido")
    user = User.query.get(user_id)
    if user:
        if user.system_admin:
            raise ValueError("No se puede desactivar un administrador del sistema")
        user.active = not user.active
        db.session.add(user)
        db.session.commit()
    else:
        raise ValueError("Usuario no encontrado")


def check_user(email: str, password: str) -> Optional[User]:
    """
    Verifica si el usuario existe y la contraseña es correcta.

    :param email: Correo electrónico del usuario
    :param password: Contraseña del usuario
    :return: Objeto User si las credenciales coinciden, de lo contrario None
    """
    user = find_user_by_email(email)

    if (
        user
        and not user.google_logged
        and bcrypt.check_password_hash(user.password, password)
    ):
        return user

    return None


def find_user_by_alias(alias: str) -> Optional[User]:
    """
    Encuentra un usuario por su alias.

    :param alias: Alias a buscar
    :return: Objeto User o None
    """
    return User.query.filter(User.alias.ilike(alias)).first()


def find_users_by_alias(alias):
    """Devuelve los usuarios con el alias proporcionado."""
    return User.query.filter(expr.func.lower(User.alias).like(f"%{alias.lower()}%"))


def get_permissions(user: User):
    """
    Devuelve la lista de permisos asignados a un usuario.

    :param user: Objeto User
    :return: Lista de nombres de permisos
    """
    return [perm.name for role in user.roles for perm in role.permissions]


def get_roles(user: User) -> List[Role]:
    """
    Devuelve la lista de roles asignados a un usuario.

    :param user: Objeto User
    :return: Lista de nombres de roles
    """
    return [role.name for role in user.roles]


def get_users():
    """
    Devuelve todos los usuarios.
    """
    return User.query.all()


def is_sys_admin():
    """
    Verifica si el usuario actual es administrador del sistema.

    :return: True si es administrador del sistema, de lo contrario False
    """
    return session["sysAdm"]


def check_permission(permission):
    """
    Verifica si el usuario actual tiene un permiso específico.

    :param permission: Nombre del permiso
    :return: True si tiene el permiso, de lo contrario False
    """
    return permission in session["permissions"] or is_sys_admin()


def get_rol(user):
    """
    Devuelve el primer rol de un usuario.

    :param user: Objeto User
    :return: Nombre del primer rol
    """
    return user.roles[0].name if user.roles else "Sin rol"


def get_id_user_or_null(email):
    """
    Devuelve el ID de un usuario por su correo electrónico o None si no existe.

    :param email: Correo electrónico del usuario
    :return: ID del usuario o None
    """
    user_id = User.query.filter_by(email=email).first()
    if user_id:
        return user_id.id
    else:
        return None


def has_permission(user, permission):
    """
    Verifica si un usuario tiene un permiso específico.

    :param user: Objeto User
    :param permission: Nombre del permiso
    :return: True si tiene el permiso, de lo contrario False
    """
    for role in user.roles:
        for perm in role.permissions:
            if perm.name == permission:
                return True
    return False


def check_create_params(email, alias, password, roles, system_admin):
    """
    Verifica que los parámetros de creación de usuario sean válidos.

    :param email: Correo del usuario
    :param alias: Alias del usuario
    :param password: Contraseña del usuario
    :param roles: Roles del usuario
    :param system_admin: Booleano que indica si es un administrador del sistema
    """
    messages: List[str] = []
    # Email válido
    messages.extend(check_email(field=email, label="Correo electrónico del usuario"))
    # Email único
    if find_user_by_email(email=email):
        messages.append(
            "Este correo electrónico ya le pertenece a un usuario del sistema"
        )
    if pending_users.find_pending_user_by_email(email):
        messages.append(
            """Este correo pertenece a un usuario 
                                   pendiente de aceptación. Reintente"""
        )
    messages.extend(check_alias(alias))
    messages.extend(check_roles(roles, system_admin))
    messages.extend(check_password(password))

    return messages


def get_publicators():
    """
    Devuelve los usuarios que tienen el rol de administración o editor.
    """
    return (
        User.query.filter_by(active=True)
        .join(User.roles)
        .filter(Role.name == "Editor")
        .all()
    )


def is_admin():
    """
    Verifica si el usuario actual es administrador.

    :return: True si es administrador, de lo contrario False
    """
    if "Administracion" in session["roles"] or is_sys_admin():
        return True

    return False
