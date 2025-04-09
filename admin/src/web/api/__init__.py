import requests

from flask import current_app


def validate_recaptcha(recaptcha_response):
    """
    Validar la respuesta de Google reCaptcha v2.

    Parámetros:
        recaptcha_response (str): La respuesta del cliente al desafío de reCaptcha.

    Retorna:
        bool: `True` si la validación es exitosa, `False` en caso contrario.

    Nota:
        La función utiliza la clave secreta almacenada en la configuración de la aplicación Flask
        bajo el nombre "GCAPTCHA_SECRET_KEY".
    """
    secret = current_app.config.get("GCAPTCHA_SECRET_KEY")
    verify_response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": secret, "response": recaptcha_response},
        timeout=600,
    )
    result = verify_response.json()
    return result.get("success", False)
