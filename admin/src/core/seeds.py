import datetime
import random

from src.core import (
    contacts,
    users,
    team,
    ecuestre,
    payments,
    publications,
    riders,
)


def run():
    """
    Función principal que permite crear:
    * Permisos
    * Roles
    * Usuarios
    * Empleados
    * Pagos
    * Caballos
    * Jinetes
    De manera automática.
    """
    users.create_permissions()
    users.create_roles()
    print("Creando usuarios...")

    users.create_user(
        system_admin=True,
        email="juan@gmail.com",
        password="123456",
        alias="Juan_Perez",
        roles=["Administracion"],
    )
    user2 = users.create_user(
        email="user2@gmail.com",
        password="123456",
        alias="user2",
        roles=["Ecuestre"],
    )
    users.create_user(
        email="user3@gmail.com",
        password="123456",
        alias="user3",
        roles=["Administracion"],
    )
    users.create_user(
        email="user4@gmail.com",
        password="123456",
        alias="user4",
        roles=["Voluntariado", "Editor"],
    )

    print("Creando empleados...")
    job_positions = [
        "Administrativo/a",
        "Terapeuta",
        "Conductor",
        "Auxiliar de pista",
        "Herrero",
        "Veterinario",
        "Entrenador de Caballos",
        "Domador",
        "Profesor de Equitacion",
        "Docente de Capacitación",
        "Auxiliar de mantenimiento",
        "Otro",
    ]
    professions = [
        "Psicologo/a",
        "Psicomotricista",
        "Medico/a",
        "Kinesiologo/a",
        "Terapista Ocupacional",
        "Psicopedagogo/a",
        "Docente",
        "Profesor/a",
        "Fonoaudiologo/a",
        "Veterinario/a",
        "Otra",
    ]

    dni_base = 76543210

    nombres = [
        "Juan",
        "Maria",
        "Carlos",
        "Lucia",
        "Jose",
        "Sofia",
        "Miguel",
        "Ana",
        "Pedro",
        "Laura",
    ]
    apellidos = [
        "Gonzalez",
        "Rodriguez",
        "Perez",
        "Gomez",
        "Martinez",
        "Lopez",
        "Sanchez",
        "Diaz",
        "Fernandez",
        "Romero",
    ]

    for i in range(1, 50):
        name = nombres[random.randint(0, len(nombres) - 1)]
        last_name = apellidos[random.randint(0, len(apellidos) - 1)]
        team.create_employee(
            dni=str(dni_base),
            name=name,
            last_name=last_name,
            address=f"50 y 120 num {i}",
            telephone="2212342249",
            email=f"{name}_{last_name}_{i}@gmail.com",
            profession=professions[random.randint(0, len(professions) - 1)],
            locality="La Plata",
            job_position=job_positions[random.randint(0, len(job_positions) - 1)],
            emergency_contact_name=(
                f"{nombres[random.randint(0, len(nombres) - 1)]} "
                f"{apellidos[random.randint(0, len(apellidos) - 1)]}"
            ),
            emergency_contact_num="2211234567",
            social_insurance="IOMA",
            affiliate_num=f"20123456{i}",
            condition=random.choice(["Voluntario", "Personal Rentado"]),
        )
        dni_base += 1

    team.create_employee(
        dni="12345680",
        name="Jose",
        last_name="Paz",
        address="Calle 1123",
        telephone="221-1332145",
        email="user2@gmail.com",
        profession="Veterinario/a",
        locality="Ensenada",
        job_position="Entrenador de Caballos",
        emergency_contact_name="Miguel",
        emergency_contact_num="221-1234567",
        social_insurance="IOMA",
        affiliate_num="20123456/03",
        condition="Voluntario",
        start_date="2023-01-01",
        user_id=user2.id,
    )

    employee4 = team.create_employee(
        dni="12345681",
        name="Luis",
        last_name="Gomez",
        address="Calle 60 numero 371",
        telephone="221-5467234",
        email="luis.gomez@gmail.com",
        profession="Conductor",
        locality="Berisso",
        job_position="Auxiliar de pista",
        emergency_contact_name="Juan",
        emergency_contact_num="221-3235577",
        social_insurance="OSDE",
        affiliate_num="20123456/01",
        condition="Personal Rentado",
        start_date="2021-01-01",
        end_date="2022-01-01",
    )

    employee5 = team.create_employee(
        dni="12345682",
        name="Juana",
        last_name="Cruz",
        address="Calle 123",
        telephone="221-1234567",
        email="juana.cruz1@gmail.com",
        profession="Domador/a",
        locality="La Plata",
        job_position="Conductor",
        emergency_contact_name="Maria",
        emergency_contact_num="221-1234567",
        social_insurance="IOMA",
        affiliate_num="20123456/02",
        condition="Voluntario",
        start_date="2021-01-01",
    )

    print("Creando caballos...")

    ecuestre.create_horse(
        name="Niamandu",
        birth_date=datetime.date(2020, 5, 17),
        gender="Masculino",
        breed="Andaluz",
        fur="Castaño",
        acquisition_type="Compra",
        entry_date=datetime.date(2021, 3, 1),
        sede="CASJ",
        rider_type="Deporte Ecuestre Adaptado",
        trainer_id=employee4.id,
        conductor_id=employee5.id,
    )

    ecuestre.create_horse(
        name="Tupa",
        birth_date=datetime.date(2018, 7, 23),
        gender="Masculino",
        breed="Árabe",
        fur="Blanco",
        acquisition_type="Donación",
        entry_date=datetime.date(2019, 9, 15),
        sede="HLP",
        rider_type="Hipoterapia",
        trainer_id=employee4.id,
        conductor_id=employee5.id,
    )

    ecuestre.create_horse(
        name="Arasy",
        birth_date=datetime.date(2015, 10, 5),
        gender="Femenino",
        breed="Criollo",
        fur="Negro",
        acquisition_type="Compra",
        entry_date=datetime.date(2016, 12, 20),
        sede="OTRO",
        rider_type="Equitacion",
        trainer_id=employee4.id,
        conductor_id=employee5.id,
    )

    payments.create_payment(
        beneficiary_id=1,
        amount="1000",
        payment_date=datetime.datetime.today(),
        payment_type="Honorarios",
        description="Pago del sueldo",
    )

    print("Creando publicaciones...")

    for i in range(1, 30):
        publications.create_publication(
            title=f"Publicacion {i}",
            summary=f"Este es el resumen de la publicacion numero: {i}",
            content=f"Este es el contenido de la publicacion numero {i} texto texto texto",
            author_id=4,
            state="Publicado",
        )

    print("Creando jinetes")
    dni_base_jinetes = 87654321
    nombres_jinetes = [
        "Andres",
        "Valeria",
        "Felipe",
        "Isabela",
        "Diego",
        "Carolina",
        "Esteban",
        "Camila",
        "Victor",
        "Elena",
    ]

    apellidos_jinetes = [
        "Castro",
        "Vasquez",
        "Morales",
        "Salazar",
        "Hernandez",
        "Mendoza",
        "Paredes",
        "Torres",
        "Cruz",
        "Salas",
    ]

    for i in range(1, 10):
        name = nombres_jinetes[random.randint(0, len(nombres_jinetes) - 1)]
        last_name = apellidos_jinetes[random.randint(0, len(apellidos_jinetes) - 1)]
        jinete_data = {
            "dni": dni_base_jinetes + i,
            "name": name,
            "last_name": last_name,
            "birthday": datetime.datetime.now(),
            "locality": "Berisso",
            "province": "Buenos Aires",
            "locality_address": "Brandsen",
            "province_address": "Buenos Aires",
            "street": "Ferrari",
            "house_num": i,
            "actual_tel": "2223123456",
            "emergency_contact_name": "Pablo",
            "emergency_contact_tel": "2223654321",
            "scholarship_holder": "yes" if bool(random.randint(0, 1)) else "no",
            "rider_observations": "Este jinete fue hecho automáticamente",
            "has_debt": bool(random.randint(0, 1)),
        }

        riders.create_rider(jinete_data)
    print("Creando contactos...")
    for i in range(1, 30):
        contacts.crear_consulta(
            comment=f"prueba {i}",
            creation_date=datetime.datetime.now(),
            title=f"titulo {i}",
            full_name=f"sujeto prueba {i}",
            email=f"prueba{i}@gmail.com",
            message=f"mensaje prueba{i}",
        )

    print("🆗 Done")
