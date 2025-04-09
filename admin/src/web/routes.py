from src.web.controllers.auth import bp as auth_bp
from src.web.controllers.riders import bp as riders_bp
from src.web.controllers.team import bp as team_bp
from src.web.controllers.team_dashboard import bp as team_dashboard_bp
from src.web.controllers.user import bp as user_bp
from src.web.controllers.user_dashboard import bp as user_dashboard_bp
from src.web.controllers.charges import bp as charges_bp
from src.web.controllers.equestrian import bp as equestrian_bp
from src.web.controllers.equestrian_dashboard import bp as equestrian_dashboard_bp
from src.web.controllers.equestrian_details import bp as equestrian_details_bp
from src.web.controllers.team_details import bp as team_details_bp
from src.web.controllers.payments import bp as payments_bp
from src.web.controllers.tutors import bp as tutors_bp
from src.web.controllers.disabilities import bp as disabilities_bp
from src.web.controllers.insurance_and_schools import bp as insurance_and_schools_bp
from src.web.controllers.institutional_works import bp as institutional_works_bp
from src.web.controllers.pending_users import bp as pending_users_bp
from src.web.controllers.reports import bp as reports_bp
from src.web.controllers.graphics import bp as graphics_bp
from src.web.controllers.publication import bp as publication_bp
from src.web.controllers.publication_dashboard import bp as publication_dashboard_bp
from src.web.api.publications import bp as api_publications_bp
from src.web.controllers.publication_details import bp as publication_details_bp
from src.web.controllers.contacts import bp as contacts_bp
from src.web.api.messages import bp as messages_bp

from src.web.handlers import error
from src.web.handlers.exceptions import RiderNotFoundException


def register_error_handlers(app):
    """
    Método donde se registran los manejadores de errores
    """
    app.register_error_handler(404, error.not_found_error)

    app.register_error_handler(403, error.forbidden_error)

    app.register_error_handler(500, error.internal_server_error)

    app.register_error_handler(RiderNotFoundException, error.rider_not_found)


def register_blueprints(app):
    """
    Método que toma a la aplicación como parametro y registra los blueprints
    definidos
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(team_dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(user_dashboard_bp)
    app.register_blueprint(tutors_bp)
    app.register_blueprint(charges_bp)
    app.register_blueprint(equestrian_bp)
    app.register_blueprint(equestrian_dashboard_bp)
    app.register_blueprint(equestrian_details_bp)
    app.register_blueprint(team_details_bp)
    app.register_blueprint(riders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(disabilities_bp)
    app.register_blueprint(insurance_and_schools_bp)
    app.register_blueprint(institutional_works_bp)
    app.register_blueprint(pending_users_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(graphics_bp)
    app.register_blueprint(publication_bp)
    app.register_blueprint(publication_dashboard_bp)
    app.register_blueprint(api_publications_bp)
    app.register_blueprint(publication_details_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(messages_bp)
