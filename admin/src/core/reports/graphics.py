from typing import List

from flask import current_app
from sqlalchemy import func

from src.core import riders
from src.core.database import db
from src.core.riders.disability import Disability
from src.core.riders.rider import Rider
from src.core.team.employee import Employee


def calculate_diagnosis_frequencies() -> dict:
    """
    Consulta la base de datos para contar las ocurrencias de cada diagnóstico.
    Retorna un diccionario con los nombres de los diagnósticos como claves y sus
    frecuencias como valores.

    Returns:
        dict: Diccionario con los nombres de los diagnósticos y sus frecuencias.
    """
    results = (
        db.session.query(Disability.diagnosis, func.count(Disability.diagnosis))
        .filter(
            Disability.diagnosis.isnot(None),  # Excluir valores nulos
            Disability.diagnosis != "",  # Excluir cadenas vacías
        )
        .group_by(Disability.diagnosis)
        .all()
    )
    filtered_results = []
    for result in results:
        if result[0] in current_app.config["DISABILITIES_IN_SYSTEM"]:
            filtered_results.append(result)
    frequencies = {diagnosis: count for diagnosis, count in filtered_results}

    return frequencies


def calculate_scholarship_proportion() -> dict:
    """
    Calcula la proporción de riders becados y no becados.
    Retorna un diccionario con las claves "becados" y "no becados" y sus respectivos
    conteos.

    Returns:
        dict: Diccionario con la proporción de riders becados y no becados.
    """
    contador = {"becados": 0, "no becados": 0}
    lista_de_riders: List[Rider] = riders.get_riders_in_list()

    for rider in lista_de_riders:
        if rider.scholarship_holder:
            contador["becados"] += 1
        else:
            contador["no becados"] += 1

    return contador


def calculate_active_job_position_frequencies() -> dict:
    """
    Calcula la frecuencia de las posiciones laborales activas en la base de datos.

    La función consulta la base de datos para obtener el número de empleados activos por cada
    puesto de trabajo específico. Los puestos de trabajo posibles están predefinidos en una lista,
    y la función devuelve un diccionario con el nombre de cada puesto y el número de empleados
    activos asignados a ese puesto. Si un puesto no tiene empleados activos,
    se asigna un valor de 0.

    Returns:
        dict: Un diccionario con los nombres de los puestos de trabajo como claves y el
              número de empleados activos asignados a cada puesto como valores.
    """
    job_positions = [
        "Administrativo/a",
        "Terapeuta",
        "Conductor",
        "Auxiliar de pista",
        "Herrero",
        "Veterinario",
        "Entrenador de Caballos",
        "Domador",
        "Profesor de Equitación",
        "Docente de Capacitación",
        "Auxiliar de mantenimiento",
        "Otro",
    ]
    active_employees = (
        db.session.query(Employee.job_position, db.func.count(Employee.job_position))
        .filter(Employee.active.is_(True))
        .group_by(Employee.job_position)
        .all()
    )
    position_counts = {pos: 0 for pos in job_positions}
    for job_position, count in active_employees:
        position_counts[job_position] = count

    return position_counts
