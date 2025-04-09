"""
Este módulo gestiona la autenticación y el registro de usuarios en la aplicación a través de métodos 
de inicio de sesión tradicionales y autenticación con Google.

Este módulo define un blueprint `auth` que maneja las rutas y vistas relacionadas con:
- Login y logout del sistema.
- Autenticación de usuarios a través de credenciales locales.
- Autenticación y registro mediante el proveedor de identidad de Google.
"""

import json
from typing import Dict, Tuple
import requests
from flask import (
    Blueprint,
    Request,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from src.core import users
from src.core import pending_users
from src.core.pending_users.pending_user import PendingUser
from src.core.users.user import User
from src.web.google_client import client


bp = Blueprint("auth", __name__, url_prefix="/")


@bp.get("/")
def login():
    """
    Renderiza la página de inicio de sesión si no hay un usuario en la sesión,
    de lo contrario, redirige a la página de inicio.

    Returns:
        Response: Renderiza la plantilla de inicio de sesión o redirige a la página de inicio.
    """
    if "user" in session:
        return redirect(url_for("auth.home"))

    return render_template("auth/inicio.html")


@bp.get("/home")
def home():
    """
    Renderiza la página de inicio ('home.html') si el usuario ha iniciado sesión.

    Si la clave "user" está presente en la sesión, significa que el usuario ha iniciado sesión
    correctamente y se le muestra la página de inicio. Si no está presente, redirige al usuario
    a la página de inicio de sesión.

    Returns:
        - `render_template('home.html')`: Renderiza la página de inicio si el
        usuario está autenticado.
        - `redirect(url_for('auth.login'))`: Redirige al usuario a la página de
        inicio de sesión si
        no ha iniciado sesión.
    """
    if "user" in session:
        return render_template("home.html")

    return redirect(url_for("auth.login"))


@bp.post("/authenticate")
def authenticate():
    """
    Autenticar al usuario según el correo electrónico y la contraseña proporcionados.
    Si la autenticación falla, muestra un mensaje de error y
    redirige a la página de inicio de sesión.
    En caso de éxito, establece las variables de sesión del usuario y
    redirige a la página de inicio.

    Returns:
        Response: Redirige a la página de inicio o muestra un mensaje de error.
    """
    params = request.form
    user = users.check_user(params["email"], params["password"])

    if not user or user.google_logged:
        flash("Email y/o contraseña incorrectas", "error")
        return redirect(url_for("auth.login"))
    if not user.active:
        flash("El usuario esta bloqueado", "error")
        return redirect(url_for("auth.login"))
    session["user"] = user.email
    session["sysAdm"] = user.system_admin
    session["roles"] = users.get_roles(user)
    session["permissions"] = users.get_permissions(user)
    session["id"] = user.id
    session["alias"] = user.alias
    flash(f"Bienvenido a Cedica {user.alias}", "success")

    return redirect(url_for("auth.home"))


@bp.get("/logout")
def logout():
    """
    Cierra la sesión del usuario eliminando los datos de la sesión.
    Redirige a la página de inicio de sesión.

    Returns:
        Response: Redirige a la página de inicio de sesión.
    """
    if session.get("user"):  # type: ignore
        del session["user"]
        session.clear()
        flash("Has cerrado sesión correctamente", "error")
    else:
        flash("No hay sesión activa", "error")

    return redirect(url_for("auth.login"))


def get_google_provider_cfg() -> Dict[str, str]:
    """
    Obtiene y devuelve la configuración del proveedor de Google para la autenticación.

    La función realiza una solicitud GET a la URL de descubrimiento de Google especificada en
    la configuración de la aplicación (`GOOGLE_DISCOVERY_URL`). Esta URL proporciona los
    endpoints necesarios para los flujos de autenticación de OAuth2 y OpenID Connect,
    devolviéndolos en un formato JSON que se interpreta como un diccionario en Python.

    Returns:
        dict: Diccionario que contiene la configuración del proveedor de Google, incluyendo
              endpoints para la autorización, tokens, y el perfil del usuario.
    """
    return requests.get(current_app.config["GOOGLE_DISCOVERY_URL"], timeout=600).json()


def get_email_from_google(request_auth: Request) -> Tuple[str, int]:
    """
    Obtiene el correo electrónico verificado del usuario autenticado en Google.

    Esta función utiliza el protocolo OpenID Connect (OIDC) para obtener la
    dirección de correo electrónico del usuario autenticado mediante Google.
    Primero, intercambia el código de autorización por un token de acceso,
    y luego utiliza el token para solicitar la información del usuario desde
    el endpoint de Google.

    Args:
        request_auth (Request): El objeto de solicitud Flask que contiene el código de
                 autorización en la URL de retorno de llamada.

    Returns:
        str: El correo electrónico verificado del usuario.
    """
    # Usamos OIDC como protocolo de autenticación
    # https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc
    # Empezamos aquí desde el paso 5 en esta función

    # Google me manda un código de autorización de que el usuario me deja
    # preguntar sus datos
    code: str = request_auth.args.get("code")
    # Le pedimos a google los lugares de la api a llamar para obtener los
    # tokens
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Dado la url de la api de arriba, y la autorización que me dio el
    # usuario, creo la url del token, los headers correspondientes
    # y el cuerpo del requerimiento
    token_url, headers, body = client.prepare_token_request(
        token_url=token_endpoint,
        authorization_response=request_auth.url,
        redirect_url=request_auth.base_url,
        code=code,
    )
    # Obtengo las credenciales del proyecto de google para este proyecto
    google_client_id: str = current_app.config["GOOGLE_CLIENT_ID"]
    google_client_secret: str = current_app.config["GOOGLE_CLIENT_SECRET"]
    # Mando un post a la api de google y guardo lo que me mando
    token_response = requests.post(
        url=token_url,
        headers=headers,
        data=body,
        auth=(google_client_id, google_client_secret),
        timeout=600,
    )
    # Parseo los tokens
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Los tokens son los necesarios para acceder a los datos del usuario
    # Ya no hablo con la autorización de Google, hablo con los servers de google
    # Para obtener los datos del usuario
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body, timeout=600)
    # Del JWT (un json con los datos del cliente) obtengo los datos necesarios
    if not userinfo_response.json().get("email_verified"):
        return (
            "El correo del usuario no esta disponible o no fue verificado por Google",
            400,
        )

    return userinfo_response.json()["email"]


@bp.post("/login_with_google")
def login_with_google():
    """
    Inicia el proceso de autenticación con Google.

    Esta función obtiene la URL de autorización de Google y redirige al usuario
    para iniciar sesión con Google, solicitando permisos para acceder a su
    perfil y correo electrónico. Se configura el alcance (scope) para obtener
    la información básica del usuario, que incluye el email verificado.

    Returns:
        Response: Redirección a la URL de autorización de Google donde el
                  usuario puede autenticarse.
    """
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri: str = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )

    return redirect(request_uri)


@bp.route("/login_with_google/callback")
def login_callback():
    """
    Maneja la respuesta de autenticación de Google y gestiona la sesión
    del usuario en el sistema.

    Después de que el usuario ha iniciado sesión en Google, esta función:
    1. Obtiene el correo electrónico del usuario autenticado en Google.
    2. Verifica si el correo electrónico pertenece a un usuario registrado
    o pendiente en el sistema.
    3. Muestra mensajes de estado al usuario según su situación en el sistema y
    redirige a la página de inicio.

    Returns:
        Response: Redirige a la página de inicio o muestra un mensaje de error.
    """
    users_email = get_email_from_google(request_auth=request)
    user: User = users.find_user_by_email(users_email)
    pending_user: PendingUser = pending_users.find_pending_user_by_email(users_email)
    if pending_user:
        flash(
            """Su solicitud de registro ya fue enviada, pero aún no ha
              sido aceptado como usuario.
              Contactese con un administrador""",
            "warning",
        )
        return redirect(url_for("auth.home", _external=True))
    if not user or not user.google_logged:
        flash("Usted no realizó el registro para usuario de CEDICA.", "error")
        return redirect(url_for("auth.home", _external=True))
    if not user.active:
        flash("El usuario esta bloqueado", "error")
        return redirect(url_for("auth.home", _external=True))
    session["user"] = user.email
    session["sysAdm"] = user.system_admin
    session["roles"] = users.get_roles(user)
    session["permissions"] = users.get_permissions(user)
    session["id"] = user.id
    session["alias"] = user.alias
    flash(f"Bienvenido a Cedica {user.alias}", "success")

    return redirect(url_for("auth.home"))


@bp.post("/register_with_google")
def register_with_google():
    """
    Inicia el proceso de registro del usuario utilizando Google como
    proveedor de autenticación.

    Esta función realiza los siguientes pasos:
    1. Obtiene la configuración del proveedor de Google para obtener la URL
    del endpoint de autorización.
    2. Construye una solicitud de autorización a Google, especificando
    el alcance de la información que se requiere,
       como el perfil y el correo electrónico del usuario.
    3. Redirige al usuario a la página de inicio de sesión de Google,
    donde puede autorizar el acceso.

    Returns:
        Response: Redirección a la URL de autenticación de Google, donde
        el usuario puede iniciar sesión y autorizar el
        acceso a sus datos de perfil y correo electrónico.
    """
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri: str = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )

    return redirect(request_uri)


@bp.get("/register_with_google/callback")
def register_callback():
    """
    Callback de registro que maneja la respuesta de Google después de que el usuario
    autoriza el acceso.
    Esta función realiza los siguientes pasos:
    1. Obtiene el correo electrónico del usuario autenticado desde Google.
    2. Verifica si el usuario ya existe en el sistema o si tiene una solicitud pendiente
     de registro.
       - Si el usuario tiene una solicitud pendiente, muestra un mensaje informativo y no
        crea otra solicitud.
       - Si el correo electrónico ya pertenece a un usuario registrado, muestra un mensaje
       de error.
    3. Si el usuario no está registrado ni tiene una solicitud pendiente, crea un nuevo
        registro en estado pendiente.
    4. Informa al usuario que su solicitud de registro fue enviada y que debe esperar la
        aprobación de un administrador.

    Returns:
        Response: Un "template" de la página de inicio (`auth/inicio.html`) con un mensaje
        adecuado al estado del registro.
    """
    users_email = get_email_from_google(request_auth=request)
    user: User = users.find_user_by_email(users_email)
    pending_user: PendingUser = pending_users.find_pending_user_by_email(users_email)
    if pending_user:
        flash(
            """Su solicitud de registro ya fue enviada, pero aún no ha sido
              aceptado como usuario.
              Contactese con un administrador""",
            "warning",
        )
        return redirect(url_for("auth.home", _external=True))
    if user:
        flash(f"El correo {users_email} ya pertenece a un usuario", "error")
        return redirect(url_for("auth.home", _external=True))

    pending_users.create_pending_user(email=users_email)
    flash(
        "Su solicitud se ha enviado. Espere a que un administrador lo acepte en el sistema",
        "info",
    )

    return redirect(url_for("auth.home", _external=True))
