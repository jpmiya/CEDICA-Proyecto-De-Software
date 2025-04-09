from typing import List

from flask import Blueprint, jsonify, request

from src.core import contacts
from src.web.api import validate_recaptcha


bp = Blueprint("contacts_api", __name__, url_prefix="/api/messages")


@bp.post("/")
def api_save_contact():
    """
    Registra el contacto recibido por post en la base de datos
    """
    try:
        # Obtener los datos del mensaje en formato JSON
        message_data = request.get_json()
        recaptcha_response = message_data.pop("recaptchaToken")
    except Exception as e:
        return str(e), 400

    try:
        # Verificar los parámetros de la consulta
        errors: List[str] = contacts.check_api_get_contacts_params(**message_data)
        if errors:
            return jsonify(errors), 400
    except ValueError as e:
        return jsonify([str(e)]), 400

    # Validar la respuesta de reCaptcha
    if not validate_recaptcha(recaptcha_response):
        return jsonify(["No se pudo validar el reCaptcha"]), 400

    # Crear la consulta de contacto
    contacts.crear_consulta(**message_data)

    return "Mensaje enviado", 201
