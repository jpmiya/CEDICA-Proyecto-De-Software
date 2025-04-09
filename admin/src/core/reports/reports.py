from typing import Dict, List

from sqlalchemy import func

from src.core.database import db
from src.core.riders.institutional_work import InstitutionalWork
from src.core.riders.rider import Rider


def get_ranking_proposals() -> List[Dict[str, int]]:
    """
    Obtiene el ranking de propuestas basándose en la cantidad de veces que
    se ha registrado cada propuesta en el sistema, ordenadas de mayor a menor.

    Returns:
        list: Lista de diccionarios que contienen la propuesta y su respectiva cantidad.
    """
    ranking = (
        db.session.query(
            InstitutionalWork.proposal,
            func.count(InstitutionalWork.proposal).label("count"),
        )
        .group_by(InstitutionalWork.proposal)
        .order_by(func.count(InstitutionalWork.proposal).desc())
        .all()
    )

    return ranking


def get_riders_without_full_information() -> List[Rider]:
    """
    Obtiene la lista de jinetes que no tienen toda la información completa,
    ya sea porque algún campo es nulo o por falta de un tutor principal.

    Returns:
        list: Lista de objetos Rider que tienen información incompleta.
    """
    riders_with_null_fields: List[Rider] = Rider.query.filter(
        db.or_(
            Rider.disability_id.is_(None),
            Rider.benefit_id.is_(None),
            Rider.insurance_id.is_(None),
            Rider.school_id.is_(None),
            Rider.institutional_work_id.is_(None),
        )
    ).all()

    all_riders: List[Rider] = Rider.query.all()
    for rider in all_riders:
        if rider.primary_tutor is None and rider not in riders_with_null_fields:
            riders_with_null_fields.append(rider)

    return riders_with_null_fields


def get_riders_in_debt() -> List[Rider]:
    """
    Obtiene la lista de jinetes que tienen deuda, ordenados alfabéticamente por
    su apellido.

    Returns:
        list: Lista de objetos Rider con deuda.
    """
    riders: List[Rider] = (
        Rider.query.filter_by(has_debt=True).order_by(Rider.last_name.asc()).all()
    )

    return riders
