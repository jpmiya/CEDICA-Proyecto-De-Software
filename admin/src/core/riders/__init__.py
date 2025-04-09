from datetime import datetime
from typing import List, Optional

import sqlalchemy as sa
import ulid
from sqlalchemy import or_, select

from flask import abort, current_app, flash

from src.core.database import db
from src.core.functions import format_name
from src.core.riders.benefits import Benefits, PensionType
from src.core.riders.disability import Disability, DisabilityType
from src.core.riders.insurance import Insurance
from src.core.riders.institutional_work import InstitutionalWork
from src.core.riders.rider import Rider
from src.core.riders.rider_document import RiderDocument
from src.core.riders.rider_tutor import RiderTutor
from src.core.riders.school import School
from src.core.riders.tutor import Tutor
from src.web.handlers.exceptions import RiderNotFoundException


def create_rider(params):
    """
    Crea una amazona o jinete en la base de datos tras validar los parámetros proporcionados.

    Args:
        params (dict): Un diccionario con los datos del jinete/amazona,
                       que incluye 'dni', 'name', 'last_name', 'birthday',
                       'locality', 'province', 'actual_tel', 'emergency_contact_name',
                       'emergency_contact_tel', 'scholarship_holder',
                       'rider_observations'.

    Returns:
        Rider: El objeto Rider creado y guardado en la base de datos.
    """

    rider = Rider(
        dni=params.get("dni"),
        name=format_name(params.get("name")),
        last_name=format_name(params.get("last_name")),
        birthday=params.get("birthday"),
        locality=params.get("locality"),
        province=params.get("province"),
        province_address=params.get("province_address"),
        locality_address=params.get("locality_address"),
        street=params.get("street"),
        house_num=params.get("house_num"),
        dpto=params.get("dpto"),
        actual_tel=params.get("actual_tel"),
        emergency_contact_name=format_name(params.get("emergency_contact_name")),
        emergency_contact_tel=params.get("emergency_contact_tel"),
        scholarship_holder=params.get("scholarship_holder") == "yes",
        rider_observations=params.get("rider_observations", ""),
        condition=True,
    )

    db.session.add(rider)
    db.session.commit()

    return rider


def unique_dni(dni: str) -> bool:
    """
    Verifica si el DNI proporcionado es único en la base de datos.

    Esta función consulta la base de datos para verificar si ya existe un jinete
    con el DNI proporcionado. Si no existe ningún jinete con ese DNI, la función
    devuelve True, lo que indica que el DNI es único. Si ya existe un jinete con
    el mismo DNI, devuelve False.

    Parámetros:
    dni (str): El DNI del jinete a comprobar.

    Retorna:
    bool: True si el DNI es único, False si ya existe un jinete con el mismo DNI.
    """
    rider = Rider.query.filter_by(dni=int(dni)).first()

    return rider is None


def delete_rider(user_id: int) -> None:
    """
    Elimina un jinete de la base de datos.

    Esta función recibe el ID de un usuario (jinete) y elimina el registro correspondiente
    de la base de datos. Si el jinete no existe, se invoca la función `get_rider_or_abort`
    para abortar la operación. Después de eliminar el jinete, se confirma la transacción
    en la base de datos.

    Parámetros:
    user_id (int): El ID del jinete que se desea eliminar.

    Retorna:
    None: La función no retorna ningún valor.
    """
    rider: Rider = get_rider_or_abort(user_id=str(user_id))
    for tutor in rider.tutors:
        connection: RiderTutor = find_connection_rider_tutor(
            rider_id=rider.id, tutor_id=tutor.tutor_id
        )
        delete_kinship(connection)

    db.session.delete(rider)
    db.session.commit()


def get_rider_or_abort(user_id: str) -> Rider:
    """Obtiene el jinete por ID o lanza un error 403 si no se encuentra."""
    try:
        rider = get_rider_by_id(int(user_id))
        return rider
    except RiderNotFoundException:
        flash("No se puede acceder al jinete solicitado, reintente", "error")
        abort(403)


def create_disability(params, rider):
    """
    Crea una entrada en la tabla de discapacidad para el jinete/amazona pasado como parámetro
    """

    disability_certificate = params["has_disability"] == "yes"

    if params.get("diagnosis") != "" and params.get("diagnosis") != "OTRO":
        diagnosis = params.get("diagnosis")
    elif params.get("diagnosis") != "OTRO":
        diagnosis = params.get("other_diagnosis")
    else:
        diagnosis = " "
    # Obtengo los tipos de discapacidad escogidos
    selected_disabilities = params.getlist("disability_type")

    # Inicializar el diccionario
    disability_types = {
        "mental": "Mental" in selected_disabilities,
        "motora": "Motora" in selected_disabilities,
        "sensorial": "Sensorial" in selected_disabilities,
        "visceral": "Visceral" in selected_disabilities,
    }

    # Creo el objeto DisablityType
    disability_type = DisabilityType(
        mental=disability_types["mental"],
        motora=disability_types["motora"],
        sensorial=disability_types["sensorial"],
        visceral=disability_types["visceral"],
    )

    disability = Disability(
        disability_certificate=disability_certificate,
        diagnosis=diagnosis,
        disability_type=disability_type,
    )

    rider.disability = disability

    db.session.add(disability)
    db.session.add(disability_type)
    db.session.add(rider)
    db.session.commit()

    return disability


def create_benefits(params, rider):
    """
    Crea un objeto Benefits y lo asocia a un Rider.

    Args:
        params (MultiDict): Un diccionario con los datos de los beneficios,
                       que incluye 'asignacion_familiar', 'asignacion_universal_por_hijo',
                       'asignacion_universal_por_hijo_con_discapacidad',
                       'asignacion_por_ayuda_escolar',
                       'has_pension', 'pensionType'.
        rider (Rider): El jinete o amazona al cual se le asocian los beneficios.

    Returns:
        Benefits: El objeto Benefits creado y asociado al jinete/amazona.
    """
    asignacion_familiar = params.get("asignacion_familiar") == "yes"
    asignacion_por_hijo = "asignacion_por_hijo" in params.getlist("beneficios_sociales")
    asignacion_por_hijo_con_discapacidad = (
        "asignacion_por_hijo_con_discapacidad" in params.getlist("beneficios_sociales")
    )
    asignacion_por_ayuda_escolar = "asignacion_por_ayuda_escolar" in params.getlist(
        "beneficios_sociales"
    )

    beneficiario_de_pension = params.get("has_pension") == "yes"

    naturaleza_pension = None
    if beneficiario_de_pension:
        pension_type_value = params.get("pension_type")
        if pension_type_value == "Nacional":
            naturaleza_pension = PensionType.NACIONAL
        elif pension_type_value == "Provincial":
            naturaleza_pension = PensionType.PROVINCIAL

    benefits = Benefits(
        asignacion_familiar=asignacion_familiar,
        asignacion_por_hijo=asignacion_por_hijo,
        asignacion_por_hijo_con_discapacidad=asignacion_por_hijo_con_discapacidad,
        asignacion_por_ayuda_escolar=asignacion_por_ayuda_escolar,
        beneficiario_de_pension=beneficiario_de_pension,
        naturaleza_pension=naturaleza_pension,
    )

    rider.benefits = benefits

    db.session.add(benefits)
    db.session.add(rider)
    db.session.commit()

    return benefits


def create_insurance(params, rider):
    """
    Crea un objeto Insurance y lo asocia a un Rider.

    Args:
        params (dict): Un diccionario con los datos del seguro,
                       que incluye 'insurance_name', 'affiliate_number',
                       'has_guardianship', 'guardianship_observations'.
        rider (Rider): El jinete o amazona al cual se le asocia el seguro.

    Returns:
        Insurance: El objeto Insurance creado y asociado al jinete/amazona.
    """
    insurance = Insurance(
        insurance_name=params.get("insurance_name").upper(),
        affiliate_number=params.get("affiliate_number"),
        has_guardianship=params.get("has_guardianship") == "yes",
        guardianship_observations=params.get("guardianship_observations"),
    )

    rider.insurance = insurance

    db.session.add(insurance)
    db.session.add(rider)
    db.session.commit()

    return insurance


def create_school(params, rider):
    """
    Crea un objeto School y lo asocia a un Rider.

    Args:
        params (dict): Un diccionario con los datos de la escuela,
                       que incluye 'school_name', 'school_address', 'school_telephone',
                       'rider_school_grade', 'school_observations', 'professionals'.
        rider (Rider): El jinete o amazona al cual se le asocia la escuela.

    Returns:
        School: El objeto School creado y asociado al jinete/amazona.
    """
    school = School(
        name=format_name(params.get("school_name")),
        address=params.get("school_address"),
        phone_number=params.get("school_telephone"),
        grade=params.get("rider_school_grade"),
        school_observations=params.get("school_observations"),
        professionals=params.get("professionals"),
    )

    rider.school = school

    db.session.add(school)
    db.session.add(rider)
    db.session.commit()

    return school


def create_tutor(params, primario):
    """
    Crea un tutor en la base de datos.

    Esta función recibe un diccionario de parámetros (`params`) con la información
    de un tutor (ya sea primario o secundario) y crea un registro en la base de datos
    con esos datos. Si el parámetro `primario` es `True`, se genere un tutor primario
    utilizando los datos correspondientes; de lo contrario, se genere un tutor secundario.
    Luego, se agrega el tutor a la sesión de la base de datos y se confirma la transacción.

    Parámetros:
    - params (dict): Un diccionario que contiene los datos del tutor.
    - primario (bool): Un valor booleano que indica si el tutor es primario o secundario.

    Retorna:
    - tutor (Tutor): El objeto `Tutor` creado y guardado en la base de datos.

    Ejemplo de uso:
    - create_tutor(params, True) # Generar tutor primario
    - create_tutor(params, False) # Generar tutor secundario
    """
    if primario:
        tutor = Tutor(
            dni=params.get("dni_primario"),
            name=format_name(params.get("nombre_primario")),
            last_name=format_name(params.get("apellido_primario")),
            province=params.get("provincia_primario"),
            locality=format_name(params.get("localidad_primario")),
            street=format_name(params.get("calle_primario")),
            street_number=params.get("numero_calle_primario"),
            floor=(
                params.get("piso_primario")
                if params.get("piso_primario") != ""
                else None
            ),
            department_number=(
                params.get("departamento_primario")
                if params.get("departamento_primario") != ""
                else None
            ),
            phone_number=params.get("celular_primario"),
            email=params.get("email_primario"),
            scholarity_level=params.get("escolaridad_primario"),
            occupation=format_name(params.get("ocupacion_primario")),
        )
        db.session.add(tutor)
        db.session.commit()
    else:
        tutor = Tutor(
            dni=params.get("dni_secundario"),
            name=format_name(params.get("nombre_secundario")),
            last_name=format_name(params.get("apellido_secundario")),
            province=params.get("provincia_secundario"),
            locality=format_name(params.get("localidad_secundario")),
            street=format_name(params.get("calle_secundario")),
            street_number=params.get("numero_calle_secundario"),
            floor=(
                params.get("piso_secundario")
                if params.get("piso_secundario") != ""
                else None
            ),
            department_number=(
                params.get("departamento_secundario")
                if params.get("departamento_secundario") != ""
                else None
            ),
            phone_number=params.get("celular_secundario"),
            email=params.get("email_secundario"),
            scholarity_level=params.get("escolaridad_secundario"),
            occupation=format_name(params.get("ocupacion_secundario")),
        )
        db.session.add(tutor)
        db.session.commit()
    return tutor


def create_kinship(rider, tutor, primario, kinship):
    """
    Crea una relación de parentesco entre un jinete y un tutor.

    Esta función crea un registro en la tabla `RiderTutor` que asocia un jinete
    con un tutor, incluyendo la relación de parentesco (kinship) y si el tutor es primario
    (valor de `primario`). Luego, guarda esta relación en la base de datos.

    Parámetros:
    - rider (Rider): El objeto `Rider` que representa al jinete.
    - tutor (Tutor): El objeto `Tutor` que representa al tutor.
    - primario (bool): Un valor booleano que indica si el tutor es primario.
    - kinship (str): El tipo de parentesco entre el jinete y el tutor.

    Retorna:
    - rider_tutor (RiderTutor): El objeto `RiderTutor` creado y guardado en la base de datos.

    Ejemplo de uso:
    - create_kinship(rider, tutor, True, "madre")
    """
    rider_tutor = RiderTutor(
        rider_id=rider.id,
        tutor_id=tutor.id,
        kinship=format_name(kinship),
        is_primary=primario,
    )
    db.session.add(rider_tutor)
    db.session.commit()

    return rider_tutor


def update_kinship(rider_tutor, kinship):
    """
    Actualiza la relación de parentesco de un jinete y su tutor.

    Esta función actualiza el campo `kinship` en el objeto `RiderTutor` proporcionado
    con el nuevo valor de parentesco y guarda los cambios en la base de datos.

    Parámetros:
    - rider_tutor (RiderTutor): El objeto `RiderTutor` que representa la relación entre el
    jinete y el tutor.
    - kinship (str): El nuevo tipo de parentesco entre el jinete y el tutor.

    Retorna:
    - None

    Ejemplo de uso:
    - update_kinship(rider_tutor, "madre")
    """
    rider_tutor.kinship = format_name(kinship)
    db.session.commit()


def delete_kinship(rider_tutor):
    """
    Elimina la relación de parentesco entre un jinete y su tutor.

    Esta función elimina el registro de la relación de parentesco (RiderTutor)
    de la base de datos y realiza el commit para guardar los cambios.

    Parámetros:
    - rider_tutor (RiderTutor): El objeto `RiderTutor` que representa la relación
    entre el jinete y el tutor.

    Retorna:
    - None

    Ejemplo de uso:
    - delete_kinship(rider_tutor)
    """
    db.session.delete(rider_tutor)
    db.session.commit()


def find_connection_rider_tutor(rider_id, tutor_id):
    """
    Busca una relación de parentesco entre un jinete y un tutor.

    Esta función consulta la base de datos para encontrar un registro en la tabla
    `RiderTutor` que asocie el jinete con el tutor, ambos
    especificados por sus identificadores.

    Parámetros:
    - rider_id (int): El ID del jinete.
    - tutor_id (int): El ID del tutor.

    Retorna:
    - connection (RiderTutor o None): Un objeto `RiderTutor` si se encuentra la relación,
      o `None` si no existe la relación.

    Ejemplo de uso:
    - find_connection_rider_tutor(1, 2)
    """
    connection = RiderTutor.query.filter_by(
        rider_id=rider_id, tutor_id=tutor_id
    ).first()

    return connection


def find_tutor_by_dni(dni):
    """
    Busca un Tutor por DNI.

    Args:
        dni (str): El número de DNI del tutor a buscar.

    Returns:
        Tutor: El objeto Tutor encontrado, o None si no se encuentra.
    """
    return Tutor.query.filter_by(dni=dni).first()


def get_rider_by_id(user_id) -> Optional[Rider]:
    """
    Busca un Rider por su ID.

    Args:
        user_id (int): El ID del jinete/amazona a buscar.

    Raises:
        RiderNotFoundException: Si no se encuentra un jinete/amazona con ese ID.

    Returns:
        Rider: El objeto Rider encontrado.
    """
    return Rider.query.filter(Rider.id == user_id).first()


def create_work(params, rider):
    """Crea una instancia y almacena una entrada en la tabla de Institutional Work"""
    proposal = params.get("proposal")
    headquarters = params.get("headquarters")
    selected_days = params.getlist("days_of_the_week")

    teacher_therapist_id = params.get("teacher_therapist")
    horse_conductor_id = params.get("horse_riders")
    track_assistant_id = params.get("track_assistant")
    horse_id = params.get("horse")

    work = InstitutionalWork(
        proposal=proposal,
        headquarters=headquarters,
        monday="monday" in selected_days,
        tuesday="tuesday" in selected_days,
        wednesday="wednesday" in selected_days,
        thursday="thursday" in selected_days,
        friday="friday" in selected_days,
        saturday="saturday" in selected_days,
        sunday="sunday" in selected_days,
        teacher_therapist_id=teacher_therapist_id,
        horse_conductor_id=horse_conductor_id,
        track_assistant_id=track_assistant_id,
        horse_id=horse_id,
    )

    # Add the new institutional work to the session and commit
    db.session.add(work)
    rider.institutional_work = work

    db.session.commit()

    return work


def get_riders_in_list():
    """
    Obtiene todos los jinetes ordenados por apellido y nombre.

    Esta función consulta la base de datos para obtener todos los jinetes y los
    ordena alfabéticamente primero por el apellido y luego por el nombre.

    Retorna:
    - Listado de objetos `Rider`: Todos los jinetes ordenados por apellido y nombre.

    Ejemplo de uso:
    - get_riders_in_list()
    """
    return Rider.query.order_by(Rider.last_name, Rider.name).all()


def get_riders_ordered_by_name(ascendent: bool = True):
    """
    Obtiene todos los jinetes ordenados por su nombre.

    Esta función consulta la base de datos para obtener todos los jinetes
    y los ordena por el campo `name`, ya sea de forma ascendente o descendente,
    según el parámetro `ascendent`.

    Parámetros:
    - ascendent (bool): Si es `True`, ordena los jinetes en orden ascendente
      por su nombre. Si es `False`, los ordena en orden descendente.
      El valor por defecto es `True`.

    Retorna:
    - Consulta de SQLAlchemy: Los jinetes ordenados por su nombre en el orden
      especificado.

    Ejemplo de uso:
    - get_riders_ordered_by_name(ascendent=True)
    """
    if ascendent:
        return sa.select(Rider).order_by(Rider.name.asc())
    else:
        return sa.select(Rider).order_by(Rider.name.desc())


def get_riders_ordered_by_last_name(ascendent: bool = True):
    """
    Obtiene todos los jinetes ordenados por su apellido.

    Esta función consulta la base de datos para obtener todos los jinetes
    y los ordena por el campo `last_name`, ya sea de forma ascendente o
    descendente, según el parámetro `ascendent`.

    Parámetros:
    - ascendent (bool): Si es `True`, ordena los jinetes en orden ascendente
      por su apellido. Si es `False`, los ordena en orden descendente.
      El valor por defecto es `True`.

    Retorna:
    - Consulta de SQLAlchemy: Los jinetes ordenados por su apellido en el orden
      especificado.

    Ejemplo de uso:
    - get_riders_ordered_by_last_name(ascendent=False)
    """
    if ascendent:
        return sa.select(Rider).order_by(Rider.last_name.asc())
    else:
        return sa.select(Rider).order_by(Rider.last_name.desc())


def filter_by_professionals(riders_query, professionals):
    """
    Filtra a los jinetes según el texto proporcionado en el campo `professionals`
    de la tabla School.

    Args:
        riders_query: Consulta inicial para obtener los jinetes.
        professionals (str): Texto a buscar en el campo `professionals` de la tabla School.

    Returns:
        Consulta de SQLAlchemy que filtra a los jinetes según el criterio.
    """
    if not professionals:  # Si el texto está vacío, no filtra nada
        return riders_query

    search_text = f"%{professionals}%"
    filtered_query = riders_query.join(Rider.school).filter(
        School.professionals.ilike(search_text)
    )

    return filtered_query


def update_rider(rider, params):
    """
    Actualiza la información de un jinete en la base de datos.

    Esta función actualiza los atributos de un jinete (`rider`) con los valores proporcionados
    en el diccionario `params`. Los campos como DNI, nombre, apellido, fecha de nacimiento,
    localidad, entre otros, son actualizados en la base de datos.

    Parámetros:
    - rider: Objeto `Rider` que se actualizará en la base de datos.
    - params (dict): Diccionario con los nuevos valores para los atributos del jinete.
      Las claves deben coincidir con los nombres de los campos del jinete en la base de datos.

    Retorna:
    - Rider: El objeto `Rider` actualizado.

    Ejemplo de uso:
    - update_rider(rider, params)
    """
    rider.dni = int(params.get("dni"))
    rider.name = format_name(params.get("name"))
    rider.last_name = format_name(params.get("last_name"))
    rider.birthday = params.get("birthday")
    rider.locality = params.get("locality")
    rider.province = params.get("province")
    rider.province_address = params.get("province_address")
    rider.locality_address = params.get("locality_address")
    rider.street = params.get("street")
    rider.house_num = params.get("house_num")
    rider.dpto = params.get("dpto")
    rider.actual_tel = params.get("actual_tel")
    rider.emergency_contact_name = format_name(params.get("emergency_contact_name"))
    rider.emergency_contact_tel = params.get("emergency_contact_tel")
    rider.scholarship_holder = (
        params.get("scholarship_holder") == "yes"
    )  # Convierte a booleano
    rider.rider_observations = params.get("rider_observations")

    db.session.commit()

    return rider


def update_disability(params, disability):
    """Actualiza la instancia/entrada en la tabla de Disability"""
    disability.disability_certificate = params.get("has_disability") == "yes"
    if params.get("diagnosis") != "" and params.get("diagnosis") != "OTRO":
        disability.diagnosis = params.get("diagnosis")
    elif params.get("diagnosis") != "OTRO":
        disability.diagnosis = params.get("other_diagnosis")

    selected_disabilities = params.getlist("disability_type")

    # Inicializar el diccionario
    disability_types = {
        "mental": "Mental" in selected_disabilities,
        "motora": "Motora" in selected_disabilities,
        "sensorial": "Sensorial" in selected_disabilities,
        "visceral": "Visceral" in selected_disabilities,
    }

    # Aca se crea un nuevo objeto, revisar previamente como se debería actualizar el objeto
    disability_type = DisabilityType(
        mental=disability_types["mental"],
        motora=disability_types["motora"],
        sensorial=disability_types["sensorial"],
        visceral=disability_types["visceral"],
    )

    disability.disability_type = disability_type

    db.session.add(disability_type)

    db.session.commit()

    return disability


def update_benefits(params, benefits):
    """Actualiza la instancia/entrada en la tabla de Benefits"""
    benefits.asignacion_familiar = params.get("asignacion_familiar") == "yes"

    benefits.asignacion_por_hijo = "asignacion_por_hijo" in params.getlist(
        "beneficios_sociales"
    )

    benefits.asignacion_por_hijo_con_discapacidad = (
        "asignacion_por_hijo_con_discapacidad" in params.getlist("beneficios_sociales")
    )
    benefits.asignacion_por_ayuda_escolar = (
        "asignacion_por_ayuda_escolar" in params.getlist("beneficios_sociales")
    )

    beneficiario_de_pension = params.get("has_pension") == "yes"
    benefits.beneficiario_de_pension = beneficiario_de_pension

    naturaleza_pension = None
    if beneficiario_de_pension:
        pension_type_value = params.get("pension_type")
        if pension_type_value == "Nacional":
            naturaleza_pension = PensionType.NACIONAL
        elif pension_type_value == "Provincial":
            naturaleza_pension = PensionType.PROVINCIAL

    benefits.naturaleza_pension = naturaleza_pension

    db.session.commit()

    return benefits


def update_insurance(params, insurance):
    """Actualiza la instancia/entrada en la tabla de Insurance"""
    insurance.insurance_name = params.get("insurance_name").upper()
    insurance.affiliate_number = params.get("affiliate_number")
    insurance.has_guardianship = params.get("has_guardianship") == "yes"
    insurance.guardianship_observations = params.get("guardianship_observations")

    db.session.commit()

    return insurance


def update_school(params, school):
    """Actualiza la instancia/entrada en la tabla de School"""
    school.name = format_name(params.get("school_name"))
    school.address = params.get("school_address")
    school.phone_number = params.get("school_telephone")
    school.grade = params.get("rider_school_grade")
    school.school_observations = params.get("school_observations")
    school.professionals = params.get("professionals")

    db.session.commit()

    return school


def update_tutor(params, tutor, primario):
    """Actualiza la instancia/entrada en la tabla de Tutores y Rider_Tutor"""
    # Sí es clasificado como el tutor primario
    if primario:
        # Actualizo todos sus datos
        tutor.dni = params.get("dni_primario")
        tutor.name = format_name(params.get("nombre_primario"))
        tutor.last_name = (format_name(params.get("apellido_primario")),)
        tutor.province = (params.get("provincia_primario"),)
        tutor.locality = (params.get("localidad_primario"),)
        tutor.street = (params.get("calle_primario"),)
        tutor.street_number = (params.get("numero_calle_primario"),)
        tutor.floor = (
            params.get("piso_primario") if params.get("piso_primario") != "" else None,
        )
        tutor.department_number = (
            (
                params.get("departamento_primario")
                if params.get("departamento_primario") != ""
                else None
            ),
        )
        tutor.phone_number = (params.get("celular_primario"),)
        tutor.email = (params.get("email_primario"),)
        tutor.scholarity_level = (params.get("escolaridad_primario"),)
        tutor.occupation = format_name(params.get("ocupacion_primario"))

    # Si es el tutor secundario
    else:
        # Actualizo sus datos
        tutor.dni = (params.get("dni_secundario"),)
        tutor.name = (format_name(params.get("nombre_secundario")),)
        tutor.last_name = (format_name(params.get("apellido_secundario")),)
        tutor.province = (params.get("provincia_secundario"),)
        tutor.locality = (params.get("localidad_secundario"),)
        tutor.street = (params.get("calle_secundario"),)
        tutor.street_number = (params.get("numero_calle_secundario"),)
        tutor.floor = (
            (
                params.get("piso_secundario", "")
                if params.get("piso_secundario") != ""
                else None
            ),
        )
        tutor.department_number = (
            (
                params.get("departamento_secundario")
                if params.get("departamento_secundario") != ""
                else None
            ),
        )
        tutor.phone_number = (params.get("celular_secundario"),)
        tutor.email = (params.get("email_secundario"),)
        tutor.scholarity_level = (params.get("escolaridad_secundario"),)
        tutor.occupation = format_name(params.get("ocupacion_secundario"))

    db.session.commit()

    return tutor


def update_work(params, work):
    """Actualiza la instancia/entrada en la tabla de Institutional Work"""
    work.proposal = params.get("proposal")
    work.headquarters = params.get("headquarters")

    selected_days = params.getlist("days_of_the_week")

    work.monday = "monday" in selected_days
    work.tuesday = "tuesday" in selected_days
    work.wednesday = "wednesday" in selected_days
    work.thursday = "thursday" in selected_days
    work.friday = "friday" in selected_days
    work.saturday = "saturday" in selected_days
    work.sunday = "sunday" in selected_days

    teacher_therapist_id = params.get("teacher_therapist")
    horse_conductor_id = params.get("horse_riders")
    track_assistant_id = params.get("track_assistant")
    horse_id = params.get("horse")

    work.teacher_therapist_id = teacher_therapist_id
    work.horse_conductor_id = horse_conductor_id
    work.track_assistant_id = track_assistant_id
    work.horse_id = horse_id

    db.session.commit()

    return work


def create_document(title, doc_type, format, source, rider_id):
    """
    crea nuevo documento

    Args:
    title (str): título del documento
    doc_type (str): tipo del doc
    format (str): formato del documento
    source (str): fuente del doc.
    rider_id (int): id del jinete/amazona asociado
    """

    rider = get_rider_by_id(rider_id)
    if rider is None:
        raise RiderNotFoundException()

    if format == "file":
        client = current_app.storage.client
        bucket_name = "grupo13"
        source.seek(
            0, 2
        )  # Indico dos punteros, uno en el comienzo del archivo, otro en el final
        length = source.tell()  # Calculo el largo del archivo
        source.seek(0)
        file_id = str(ulid.ulid())  # Creo un identificador unico para el archivo
        file_name = (
            f"{file_id}-{source.filename}"  # Guardo el nombre del archivo junto a su id
        )
        client.put_object(
            bucket_name, file_name, source, length, content_type=source.content_type
        )

        source = file_name

        new_document = RiderDocument(
            title=title,
            document_type=doc_type,
            format=format,
            source=source,
            rider_id=rider_id,
        )

        db.session.add(new_document)
        db.session.commit()

        return new_document


def get_document_by_id(document_id):
    """
    Obtiene un documento de jinete a partir de su ID.

    Esta función consulta la base de datos para encontrar un documento de jinete
    (`RiderDocument`) utilizando su ID. Retorna el primer documento encontrado o `None`
    si no existe un documento con el ID proporcionado.

    Parámetros:
    - document_id (int): El ID del documento a buscar.

    Retorna:
    - RiderDocument o None: El documento de jinete encontrado o `None` si no se encuentra.

    Ejemplo de uso:
    - get_document_by_id(document_id)
    """
    doc_id = int(document_id)
    return RiderDocument.query.filter_by(id=doc_id).first()


def get_documents_by_rider_id(
    rider_id, title=None, doc_type=None, order_by="mas_recientes"
):
    """
    Obtiene una lista de documentos de jinete filtrados por el ID del jinete.

    Esta función consulta la base de datos para obtener todos los documentos asociados
    a un jinete específico, con la opción de aplicar filtros por título, tipo de documento
    y ordenación.

    Parámetros:
    - rider_id (int): El ID del jinete cuyos documentos se deben recuperar.
    - title (str, opcional): Filtra los documentos que contienen el título especificado.
    - doc_type (str, opcional): Filtra los documentos por tipo de documento.
    - order_by (str, opcional): Define el orden de los resultados. Puede ser uno de los
    siguientes valores:
      - "nombre_asc": Ordena por título en orden ascendente.
      - "nombre_desc": Ordena por título en orden descendente.
      - "mas_recientes": Ordena por fecha de creación en orden descendente.
      - "mas_viejos": Ordena por fecha de creación en orden ascendente.

    Retorna:
    - Query: Consulta filtrada que se puede ejecutar para obtener los documentos.

    Ejemplo de uso:
    - get_documents_by_rider_id(rider_id, title="Certificado", order_by="mas_recientes")
    """
    query = RiderDocument.query.filter_by(rider_id=rider_id)

    if title:
        query = query.filter(RiderDocument.title.ilike(f"%{title}%"))

    if doc_type:
        query = query.filter(RiderDocument.document_type == doc_type)

    if order_by:
        if order_by == "nombre_asc":
            query = query.order_by(RiderDocument.title.asc())
        elif order_by == "nombre_desc":
            query = query.order_by(RiderDocument.title.desc())
        elif order_by == "mas_recientes":
            query = query.order_by(RiderDocument.created_at.desc())
        elif order_by == "mas_viejos":
            query = query.order_by(RiderDocument.created_at.asc())

    return query


def edit_document(document_id, title, doc_type):
    """
    Edita los detalles de un documento de jinete.

    Esta función busca un documento de jinete a partir de su ID, y si lo encuentra,
    actualiza su título, tipo de documento y la fecha de actualización. Si el documento
    no existe, se lanza una excepción.

    Parámetros:
    - document_id (int): El ID del documento que se desea editar.
    - title (str): El nuevo título del documento.
    - doc_type (str): El nuevo tipo de documento.

    Retorna:
    - RiderDocument: El documento editado.

    Lanza:
    - ValueError: Si no se encuentra el documento con el ID proporcionado.

    Ejemplo de uso:
    - edit_document(document_id=123, title="Nuevo Título", doc_type="PDF")
    """
    document = get_document_by_id(document_id)
    if not document:
        raise ValueError("Documento no encontrado")

    document.title = title
    document.document_type = doc_type
    document.updated_at = datetime.now()

    db.session.commit()

    return document


def delete_document(document):
    """
    Elimina un documento de jinete y su archivo asociado.

    Esta función elimina un documento de jinete de la base de datos y, si el documento
    tiene un formato de archivo, también elimina el archivo asociado en el sistema
    de almacenamiento.

    Parámetros:
    - document (RiderDocument): El documento de jinete que se desea eliminar.

    Ejemplo de uso:
    - delete_document(document)
    """

    if document.format == "file":

        client = current_app.storage.client
        bucket_name = "grupo13"
        client.remove_object(bucket_name, document.source)

    db.session.delete(document)
    db.session.commit()


def drop_documents_from_remote(user_id: int) -> None:
    """
    Elimina todos los documentos relacionados con un jinete (usuario) desde el
    almacenamiento remoto.

    Esta función obtiene todos los documentos asociados a un jinete específico y los elimina tanto
    de la base de datos como del almacenamiento remoto.

    Parámetros:
    - user_id (int): El ID del jinete cuyo documentos se eliminarán.

    Ejemplo de uso:
    - drop_documents_from_remote(user_id)
    """

    documents: List[RiderDocument] = RiderDocument.query.filter_by(
        rider_id=user_id, format="file"
    ).all()

    for document in documents:
        delete_document(document)


def add_link(title, link, document_type, rider_id):
    """
    Agrega un enlace a un jinete con el ID especificado.

    Esta función crea un nuevo documento con un enlace (no un archivo) y lo asocia al jinete.

    Parámetros:
    - title (str): El título del enlace.
    - link (str): La URL del enlace.
    - document_type (str): El tipo de documento.
    - rider_id (int): El ID del jinete al que se le asociará el enlace.

    Retorna:
    - RiderDocument: El nuevo documento creado con el enlace.
    """
    new_link = RiderDocument(
        title=title,
        document_type=document_type,
        format="link",
        source=link,
        rider_id=rider_id,
    )
    db.session.add(new_link)
    db.session.commit()

    return new_link


def modify_link(document_id, title, link, document_type):
    """
    Modifica un enlace existente.

    Esta función permite modificar los detalles de un enlace ya existente en la base de datos.

    Parámetros:
    - document_id (int): El ID del documento a modificar.
    - title (str): El nuevo título del enlace.
    - link (str): La nueva URL del enlace.
    - document_type (str): El nuevo tipo de documento.

    Retorna:
    - RiderDocument: El documento modificado.

    Lanza:
    - ValueError: Si no se encuentra el documento con el ID proporcionado.
    """
    enlace: RiderDocument = RiderDocument.query.filter_by(id=document_id).first()

    if not enlace:
        raise ValueError("Documento no encontrado")

    enlace.title = title
    enlace.source = link
    enlace.document_type = document_type

    db.session.commit()

    return enlace


def download_document(document_id):
    """
    Descarga el documento con el ID especificado.

    Esta función recupera el documento de la base de datos y lo descarga desde el
    almacenamiento remoto.

    Parámetros:
    - document_id (int): El ID del documento a descargar.

    Retorna:
    - response: Objeto de respuesta de Flask con el contenido del documento.
    - document: El documento descargado desde la base de datos.

    Lanza:
    - ValueError: Si no se encuentra el documento con el ID proporcionado.
    """
    document = RiderDocument.query.filter_by(id=document_id).first()
    if not document:
        raise ValueError("Documento no encontrado")

    client = current_app.storage.client
    bucket_name = "grupo13"
    response = client.get_object(bucket_name, document.source)

    return response, document


def get_riders():
    """
    Obtiene todos los jinetes ordenados por su ID de forma ascendente.

    Esta función devuelve una consulta (`select`) que obtiene todos los objetos
    `Rider` de la base de datos, ordenados por el campo `id` en orden ascendente.

    Retorna:
    - Consulta de SQLAlchemy: Los jinetes ordenados por su ID de forma ascendente.

    Ejemplo de uso:
    - get_riders()
    """
    return sa.select(Rider).order_by(Rider.id.asc())
