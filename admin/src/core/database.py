from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


db = SQLAlchemy()


def init_app(app):
    """
    Inicializa la base de datos con la aplicación de Flask.

    Args:
        app (_type_): _description_
    """
    db.init_app(app)
    config(app)

    return app


def config(app):
    """
    Configuración de hooks para la base de datos.

    Args:
        app (_type_): _description_

    Returns:
        _type_: _description_
    """

    @app.teardown_appcontext
    def close_session(exception=None):
        db.session.close()

    return app


def reset():
    """
    Resetea la base de datos
    """
    app = current_app

    with app.app_context():

        print("Eliminando base de datos...")
        with db.engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS rider_tutor"))
            connection.execute(text("DROP TABLE IF EXISTS rider_disability"))
            connection.execute(text("DROP TABLE IF EXISTS charges"))
            connection.execute(text("DROP TABLE IF EXISTS rider_documents"))
            connection.execute(text("DROP TABLE IF EXISTS riders"))
            connection.execute(text("DROP TABLE IF EXISTS employee_documents"))
            connection.execute(text("DROP TABLE IF EXISTS publications"))

        db.drop_all()

        print("Creando base nuevamente...")
        try:
            db.create_all()
        except Exception as e:
            print(f"Error al crear tablas: {e}")
    print("🆗 Done!")
