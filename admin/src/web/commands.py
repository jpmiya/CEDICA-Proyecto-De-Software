from src.core import database
from src.core import seeds
from src.core import users


def register_special_commands(app):
    """
    Método que registra comandos personalizados
    """

    @app.cli.command(name="reset-db")
    def reset_db():
        database.reset()

    @app.cli.command(name="seeds-db")
    def seeds_db():
        seeds.run()

    @app.cli.command(name="create-roles")
    def create_roles():
        users.create_roles()
