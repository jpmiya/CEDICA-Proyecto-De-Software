from os import environ


class Config(object):
    """Base configuration."""

    SECRET_KEY = "secret"
    TESTING = False
    SESSION_TYPE = "filesystem"

    MAX_NUMBER_ON_DATABASE = 2147483647
    MAX_ELEMENTS_ON_PAGE = 9

    ACCEPTED_EXTENSIONS = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpeg", ".jpg"]
    ARGENTINIAN_PROVINCES = (
        "Buenos Aires",
        "Ciudad Autónoma de Buenos Aires",
        "Catamarca",
        "Chaco",
        "Chubut",
        "Córdoba",
        "Corrientes",
        "Entre Ríos",
        "Formosa",
        "Jujuy",
        "La Pampa",
        "La Rioja",
        "Mendoza",
        "Misiones",
        "Neuquén",
        "Río Negro",
        "Salta",
        "San Juan",
        "San Luis",
        "Santa Cruz",
        "Santa Fe",
        "Santiago del Estero",
        "Tierra del Fuego",
        "Tucumán",
    )
    DISABILITIES_IN_SYSTEM = (
        "ECNE",
        "Lesión post-traumática",
        "Mielomeningocele",
        "Esclerosis Múltiple",
        "Escoliosis Leve",
        "Secuelas de ACV",
        "Discapacidad Intelectual",
        "Trastorno del Espectro Autista",
        "Trastorno del Aprendizaje",
        "TDAH",
        "Trastorno de la Comunicación",
        "Trastorno de Ansiedad",
        "Síndrome de Down",
        "Retraso Madurativo",
        "Psicosis",
        "Trastorno de Conducta",
        "Trastornos del ánimo y afectivos",
        "Trastorno Alimentario",
        "OTRO",
    )


class ProductionConfig(Config):
    """Production configuration."""

    SECRET_KEY = environ.get("BCRYPT_SECRET_KEY")
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }
    GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    GCAPTCHA_SECRET_KEY = environ.get("GCAPTCHA_SECRET_KEY")


class DevelopmentConfig(Config):
    """Development configuration."""

    MINIO_SERVER = "localhost:9000"
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = False
    DB_USER = environ.get("DB_USER")
    DB_PASSWORD = environ.get("DB_PASSWORD")
    DB_HOST = environ.get("DB_HOST")
    DB_NAME = environ.get("DB_NAME")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
    )
    GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    GCAPTCHA_SECRET_KEY = environ.get("GCAPTCHA_SECRET_KEY")


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "test": TestingConfig,
}
