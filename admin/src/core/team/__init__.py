from typing import List
from datetime import datetime
import ulid

from flask import current_app

from sqlalchemy import desc, or_
from sqlalchemy.sql import expression as expr
from src.web.validators.general_validations import (
    check_email,
    check_number,
    check_phone,
    validate_string,
)
from src.core import functions
from src.core.database import db
from src.core.team.employee_document import EmployeeDocument
from src.core.team.employee import Employee

from src.web.handlers.exceptions import (
    DniExistsException,
    DniLengthException,
    DniNotNumberException,
    EmailNotValidException,
    EmailExistsException,
    NameNotValidException,
)


def existe_dni(dni):
    """
    Verifica si el DNI ya existe en la base de datos.

    Args:
        dni (str): DNI a verificar.

    Raises:
        DniExistsException: Si el DNI ya existe.

    Returns:
        bool: True si el DNI ya existe, False en caso contrario.
    """
    employee = Employee.query.filter_by(dni=dni).first()

    if employee is not None:
        raise DniExistsException()


def existe_email(email):
    """
    Verifica si el email ya existe en la base de datos.

    Args:
        email (str): Email a verificar.

    Raises:
        EmailExistsException: Si el email ya existe.

    Returns:
        bool: True si el email ya existe, False en caso contrario.
    """
    employee = Employee.query.filter_by(email=email).first()

    if employee is not None:
        raise EmailExistsException()


def get_employee(employee_id) -> Employee:
    """
    Retorna el empleado con el ID especificado.

    Args:
        employee_id (int): ID del empleado.

    Returns:
        Employee: Empleado con el ID especificado.
    """
    return Employee.query.filter_by(id=employee_id).first()


def modify_employee(employee_id, **kwargs):
    """
    Modifica los datos del empleado con el ID especificado.

    Args:
        employee_id (int): ID del empleado.
        kwargs: Campos del empleado a modificar.

    Returns:
        Employee: Empleado modificado.
    """
    employee = get_employee(employee_id)

    if kwargs["dni"] != employee.dni:
        try:
            existe_dni(kwargs["dni"])
        except DniExistsException as e:
            raise e
    else:
        kwargs.pop("dni")

    if kwargs["email"] != employee.email:
        try:
            existe_email(kwargs["email"])
        except EmailExistsException as e:
            raise e
    else:
        kwargs.pop("email")

    for key, value in kwargs.items():
        setattr(employee, key, value)

    db.session.add(employee)
    db.session.commit()

    return employee


def create_employee(**kwargs):
    """
    Crea un nuevo empleado en la base de datos.

    Lanza:
        DniExistsException: Si el DNI ya existe.
        DniLengthException: Si la longitud del DNI es inválida.
        DniNotNumberException: Si el DNI contiene caracteres no numéricos.
        EmailExistsException: Si el correo electrónico ya existe.
        EmailNotValidException: Si el formato del correo electrónico es inválido.
        NameNotValidException: Si el nombre o apellido es inválido.

    Retorna:
        Employee: El empleado creado.
    """
    dni = kwargs.get("dni")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")

    if start_date == "":
        start_date = datetime.today()
        kwargs["start_date"] = start_date

    if end_date == "":
        end_date = None
        kwargs["end_date"] = end_date

    if "email" in kwargs and kwargs["email"] is not None:
        kwargs["email"] = kwargs["email"].lower()

    try:
        existe_dni(dni)
        existe_email(kwargs.get("email"))
        functions.check_dni(dni)
        functions.check_email(kwargs.get("email"))
        functions.check_name(kwargs.get("name"))
        functions.check_name(kwargs.get("last_name"))

    except (
        DniExistsException,
        DniLengthException,
        DniNotNumberException,
        EmailNotValidException,
        NameNotValidException,
    ) as e:
        raise e

    employee = Employee(**kwargs)
    db.session.add(employee)
    db.session.commit()

    return employee


search_map = {
    "name": Employee.name,
    "last_name": Employee.last_name,
    "email": Employee.email,
    "dni": Employee.dni,
    "profesion": Employee.profession,
}

order_map = {
    "name": Employee.name,
    "last_name": Employee.last_name,
    "email": Employee.email,
    "start_date": Employee.start_date,
}


def list_and_search_employees(
    page, search_string="", search_by="name", order_by="name", order_direction="asc"
):
    """
    Busca empleados cuya columna especificada contiene la subcadena dada,
    aplica un orden y pagina los resultados.

    Args:
        page (int): Número de página a recuperar.
        search_string (str, opcional): Subcadena a buscar. Por defecto, es una cadena vacía.
        search_by (str, opcional): Columna para realizar la búsqueda. Por defecto, 'name'.
        order_by (str, opcional): Columna para ordenar los resultados. Por defecto, 'name'.
        order_direction (str, opcional): 'asc' para orden ascendente o 'desc' para orden
        descendente.

    Retorna:
        list: Una lista paginada de empleados que coinciden con los criterios de búsqueda.
        Pagination: Objeto de paginación con detalles de la paginación.
    """
    order_column = order_map.get(order_by)

    if order_direction == "desc":
        order_column = desc(order_column)

    search_column = search_map.get(search_by)

    if search_string:
        search_string = search_string.strip().lower()
        pagination = (
            Employee.query.order_by(order_column)
            .filter(expr.func.lower(search_column).like(f"%{search_string}%"))
            .paginate(
                page=page,
                per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
                error_out=False,
            )
        )
    else:
        pagination = Employee.query.order_by(order_column).paginate(
            page=page,
            per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
            error_out=False,
        )

    employees = pagination.items

    return employees, pagination


def get_employees_by_job_position(job_position):
    """
    Obtiene una lista de empleados basada en su posición laboral.

    Args:
        job_position (str): Posición laboral de los empleados a recuperar.

    Retorna:
        list: Una lista de objetos Employee que coinciden con la posición laboral
        y estado activo especificados.

    Ejemplo:
        employees = get_employees_by_job_position("Manager")
    """
    return (
        db.session.query(Employee)
        .filter(Employee.active, Employee.job_position == job_position)
        .all()
    )


def toggle_active(employee_id):
    """
    Cambia el estado activo del empleado con el ID especificado.

    Args:
        employee_id (int): ID del empleado.

    Retorna:
        Employee: El empleado modificado.
    """
    employee = get_employee(employee_id)
    if employee:
        activo = employee.active
        if activo:
            employee.end_date = datetime.today()
        else:
            employee.end_date = None
        employee.active = not employee.active
        db.session.add(employee)
        db.session.commit()
        return employee
    else:
        return None


def get_teachers_and_therapists():
    """
    Retorna todos los empleados que son profesores o terapeutas.

    Retorna:
        list: Lista de empleados que cumplen con los criterios.
    """
    result = (
        Employee.query.filter(
            or_(
                Employee.profession == "Profesor/a",
                Employee.job_position == "Terapeuta",
            )
        )
        .distinct()
        .all()
    )

    return result


def create_document(title, format, source, employee_id):
    """
    Crea un nuevo documento para el empleado con el ID especificado.

    Args:
        title (str): Título del documento.
        format (str): Formato del documento (por ejemplo, "file" o "link").
        source (minio.storage.StorageClass): Fuente del documento (archivo o enlace).
        employee_id (int): ID del empleado.

    Retorna:
        EmployeeDocument: El documento creado.
    """
    if format == "file":
        client = current_app.storage.client
        bucket_name = "grupo13"
        source.seek(0, 2)
        length = source.tell()
        source.seek(0)
        file_id = str(ulid.ulid())
        file_name = f"{file_id}-{source.filename}"
        client.put_object(
            bucket_name, file_name, source, length, content_type=source.content_type
        )

        source = file_name

        new_document = EmployeeDocument(
            title=title,
            type="Archivo",
            format=format,
            source=source,
            employee_id=employee_id,
        )

        db.session.add(new_document)
        db.session.commit()

        return new_document


def add_link(title, link, document_type, employee_id):
    """
    Agrega un enlace a un empleado con el ID especificado.

    Crea un nuevo documento con un enlace (no un archivo) y lo asocia al empleado.

    Args:
        title (str): Título del enlace.
        link (str): URL del enlace.
        document_type (str): Tipo de documento.
        employee_id (int): ID del empleado al que se le asociará el enlace.

    Retorna:
        EmployeeDocument: El nuevo documento creado con el enlace.
    """
    new_link = EmployeeDocument(
        title=title,
        type=document_type,
        format="link",
        source=link,
        employee_id=employee_id,
    )
    db.session.add(new_link)
    db.session.commit()

    return new_link


def get_document_by_id(document_id):
    """
    Retorna el documento con el ID especificado.

    Args:
        document_id (int): ID del documento.

    Retorna:
        EmployeeDocument: Documento con el ID especificado.
    """
    return EmployeeDocument.query.filter_by(id=document_id).first()


def get_documents_by_employee_id(page, employee_id):
    """
    Devuelve los documentos del empleado con el ID especificado.

    Args:
        page (int): Número de página para la paginación.
        employee_id (int): ID del empleado.

    Retorna:
        tuple: Una tupla con la lista de documentos del empleado y el objeto de paginación.
    """
    pagination = (
        EmployeeDocument.query.filter_by(employee_id=employee_id)
        .order_by(EmployeeDocument.created_at.desc())
        .paginate(
            page=page,
            per_page=current_app.config["MAX_ELEMENTS_ON_PAGE"],
            error_out=False,
        )
    )

    documents = pagination.items

    return documents, pagination


def download_document(document_id):
    """
    Descarga el documento con el ID especificado.

    Args:
        document_id (int): ID del documento.

    Retorna:
        Response: Objeto de respuesta Flask.
        EmployeeDocument: Documento descargado.
    """
    document = EmployeeDocument.query.filter_by(id=document_id).first()
    if not document:
        raise ValueError("Documento no encontrado")
    client = current_app.storage.client
    bucket_name = "grupo13"
    response = client.get_object(bucket_name, document.source)

    return response, document


def check_order_params(page, order, order_direction, search_by, search_value):
    """
    Verifica si los parámetros de ordenamiento son válidos.

    Args:
        page (int): Número de página.
        order (str): Columna por la que se ordenará.
        order_direction (str): Dirección del orden ('asc' o 'desc').
        search_by (str): Columna por la que se buscará.
        search_value (str): Valor para la búsqueda.

    Lanza:
        ValueError: Si alguno de los parámetros de ordenamiento es inválido.
    """
    try:
        if order not in order_map.keys():
            raise ValueError("Columna de orden inválida")
        if order_direction not in ["asc", "desc"]:
            raise ValueError("Dirección de orden inválida")
        if search_by != "" and search_by not in search_map.keys():
            raise ValueError("Columna de búsqueda inválida")
        if (not isinstance(page, int)) or page < 1 or page > 1000:
            raise ValueError("Número de página inválido")
        if not isinstance(search_value, str):
            raise ValueError("Valor de búsqueda inválido")
    except ValueError as e:
        raise ValueError(str(e))


def check_create_params(
    dni,
    name,
    last_name,
    email,
    telephone,
    profession,
    locality,
    address,
    job_position,
    start_date,
    end_date,
    emergency_contact_name,
    emergency_contact_num,
    social_insurance,
    affiliate_num,
    condition,
    active,
):
    """
    Validar los parámetros proporcionados para crear un empleado.

    Args:
        dni (str): DNI (número de identificación) del empleado.
        name (str): Nombre del empleado.
        last_name (str): Apellido del empleado.
        email (str): Correo electrónico del empleado.
        telephone (str): Teléfono del empleado.
        profession (str): Profesión del empleado.
        locality (str): Localidad donde reside el empleado.
        address (str): Dirección del empleado.
        job_position (str): Posición laboral del empleado.
        start_date (str): Fecha de inicio del empleo.
        end_date (str, opcional): Fecha de fin del empleo, si aplica.
        emergency_contact_name (str): Nombre de la persona de contacto de emergencia.
        emergency_contact_num (str): Teléfono del contacto de emergencia.
        social_insurance (str): Número de seguro social del empleado.
        affiliate_num (int): Número de afiliación del empleado al seguro social.
        condition (str): Condición o estado del empleado.

    Lanza:
        ValueError: Si algún valor de entrada no es válido o no cumple las condiciones requeridas.
    """
    message: List[str] = []
    # DNI
    message.extend(functions.check_dni(dni))

    # Nombre
    message.extend(
        validate_string(
            s=name,
            label="Nombre del empleado",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    # Apellido
    message.extend(
        validate_string(
            s=last_name,
            label="Apellido del empleado",
            maxlength=50,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    # Correo
    message.extend(check_email(field=email, label="Correo electrónico del empleado"))

    # Teléfono
    message.extend(
        check_phone(phone=telephone, label="Número de teléfono del empleado")
    )

    # Localidad
    message.extend(
        validate_string(
            s=locality,
            label="Localidad del empleado",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("'", "."),
            spaced=True,
        )
    )

    # Dirección
    message.extend(
        validate_string(
            s=address,
            label="Dirección del empleado",
            maxlength=100,
            numbers_permitted=True,
            allowed_special_chars=("&", ".", "'"),
            spaced=True,
            required=True,
            only_numbers_accepted=True,
        )
    )

    # Profesión
    message.extend(functions.check_profession(profession))

    # Puesto de trabajo
    message.extend(functions.check_job_position(job_position=job_position))

    # Fecha de inicio
    message.extend(functions.check_is_valid_date(start_date, label="Fecha de inicio"))
    if start_date > str(datetime.today()):
        message.append("La fecha de inicio no puede ser mayor a la fecha actual")
    # Fecha de finalización
    if end_date:
        lista_aux: List[str] = functions.check_is_valid_date(
            end_date, label="Fecha de finalización"
        )
        if len(lista_aux) == 0:
            if start_date > end_date:
                message.append(
                    "La fecha de inicio no puede ser mayor a la fecha de finalización"
                )
            if start_date > str(datetime.now()):
                message.append(
                    "La fecha de inicio no puede ser mayor a la fecha actual"
                )

    # Nombre de contacto de emergencia
    message.extend(
        validate_string(
            s=emergency_contact_name,
            label="Nombre del contacto de emergencia del empleado",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=("'",),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    # Número de teléfono de emergencia
    message.extend(
        check_phone(
            phone=emergency_contact_num,
            label="Número de teléfono de contacto de emergencia del empleado",
        )
    )

    # Obra social
    message.extend(
        validate_string(
            s=social_insurance,
            label="Obra social del empleado",
            maxlength=100,
            numbers_permitted=False,
            allowed_special_chars=(".", "&"),
            spaced=True,
            required=True,
            only_numbers_accepted=False,
        )
    )

    # Número de afiliado
    message.extend(
        check_number(field=affiliate_num, label="Número de afiliado", min_n=1)
    )

    # Condición
    message.extend(functions.check_condition(condition=condition))

    if not active in ["true", "false"]:
        message.append("Error en el campo activo.")

    return message


def delete_document(document_id):
    """
    Borra el documento cuya ID es igual a document_id

    Args:
        document_id (EmployeeDocument): ID del documento a borrar
    """

    document = get_document_by_id(document_id)
    db.session.delete(document)
    db.session.commit()


def get_employees():
    """
    Retorna a TODOS los empleados.

    Returns:
        list[Employee].
    """
    return Employee.query.order_by(Employee.last_name).all()


def get_employees_that_work_with_riders() -> List[Employee]:
    """
    Devuelve una lista de empleados que cumplan al menos una de las siguientes condiciones:
    - `job_position` sea "Terapeuta", "Conductor" o "Auxiliar de pista".
    - `profession` sea "Profesor/a".
    No se repiten
    """
    filters = or_(
        Employee.job_position.in_(["Terapeuta", "Conductor", "Auxiliar de pista"]),
        Employee.profession == "Profesor/a",
        Employee.active,
    )

    employees = db.session.query(Employee).filter(filters).distinct().all()

    sorted_employees = sorted(employees, key=lambda e: (e.last_name, e.name, e.dni))

    return sorted_employees


def find_employee_by_email(email):
    """
    Busca un empleado por su email.

    Args:
        email (str): Email del empleado.

    Returns:
        Employee: Empleado con el email especificado.
    """
    return Employee.query.filter_by(email=email).first()


def get_active_employees():
    """
    Retorna una lista con los empleados en estado activo
    Returns:
        List[Employee]: Listado de empleados activos
    """
    employees = (
        db.session.query(Employee)
        .order_by(Employee.last_name, Employee.name)
        .filter_by(active=True)
        .all()
    )

    return employees
