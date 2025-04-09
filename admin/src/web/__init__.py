import os

from src.core import users
from src.core.functions import get_max_number
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from src.core.bcrypt import bcrypt
from src.web.config import config

from src.core import database
from src.web import routes
from src.web import commands
from src.web.storage import storage


session = Session()


def create_app(env="development", static_folder=None):
    """
    Crea y configura una instancia de la aplicación Flask.

    Esta función es responsable de inicializar y configurar todos los componentes necesarios para
    el funcionamiento de la aplicación. Esto incluye la configuración de la base de datos,
    sesiones, encriptación, almacenamiento de objetos, manejo de errores, registro de rutas,
    CORS, funciones globales para Jinja2 y comandos personalizados.

    Parámetros:
        env (str): El entorno de ejecución de la aplicación. Los valores típicos incluyen
            "development", "testing" y "production". Por defecto, es "development".
        static_folder (str): Ruta opcional a la carpeta estática de la aplicación. Si no se proporciona,
            se establece automáticamente una ruta relativa a la ubicación del archivo.

    Retorna:
        Flask: Una instancia configurada de la aplicación Flask.

    Configuración detallada:
        - Carga la configuración específica del entorno desde el módulo `config`.
        - Inicializa la base de datos usando la función `init_app` de `database`.
        - Configura las sesiones mediante `flask_session.Session`.
        - Inicializa el encriptador mediante la biblioteca `bcrypt`.
        - Registra un servicio de almacenamiento de objetos (object storage) usando `storage`.
        - Configura los manejadores de errores personalizados utilizando `routes.register_error_handlers`.
        - Registra los blueprints para definir las rutas de la aplicación con `routes.register_blueprints`.
        - Activa CORS para permitir solicitudes entre orígenes distintos.
        - Define funciones globales personalizadas para ser utilizadas en las plantillas Jinja2:
            - `is_sys_admin`: Verifica si un usuario tiene permisos de administrador.
            - `check_permission`: Verifica permisos específicos de un usuario.
            - `get_max_number`: Devuelve el valor máximo de un conjunto de datos.
        - Registra comandos personalizados para el CLI de Flask con `commands.register_special_commands`.

    Este diseño asegura que todos los componentes de la aplicación estén listos para su ejecución
    y funcionamiento en el entorno deseado.
    """

    app = Flask(
        __name__,
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../static")
        ),
    )
    # Cargo la configuración
    app.config.from_object(config[env])
    # Inicializo la base de datos
    database.init_app(app)

    # Inicializo la sesión y el encriptador
    session.init_app(app)
    bcrypt.init_app(app)

    # Registro object storage
    storage.init_app(app)

    # Registro de manejadores de errores
    routes.register_error_handlers(app)

    # Registro de blueprints
    routes.register_blueprints(app)

    # Registro de CORS
    CORS(app)

    # registro funciones jinja
    app.jinja_env.globals.update(is_sys_admin=users.is_sys_admin)
    app.jinja_env.globals.update(is_admin=users.is_admin)
    app.jinja_env.globals.update(check_permission=users.check_permission)
    app.jinja_env.globals.update(get_max_number=get_max_number)

    # Registro los comandos personalizados de flask
    commands.register_special_commands(app)

    return app
