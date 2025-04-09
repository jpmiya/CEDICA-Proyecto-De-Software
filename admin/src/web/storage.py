from minio import Minio


class Storage:
    """Clase para gestionar el almacenamiento en MinIO."""

    def __init__(self, app=None):
        """Inicializa la instancia de Storage.

        Args:
            app: Instancia de la aplicación Flask (opcional).
        """
        self._client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Inicializa el cliente MinIO con la configuración de la aplicación Flask proporcionada.

        Args:
            app: La instancia de la aplicación Flask.

        Returns:
            La instancia de la aplicación Flask.
        """
        minio_server: str = (
            app.config.get("MINIO_SERVER")
            .replace("https://", "")
            .replace("http://", "")
        )
        access_key: str = app.config.get("MINIO_ACCESS_KEY")
        secret_key: str = app.config.get("MINIO_SECRET_KEY")
        secure: bool = app.config.get("MINIO_SECURE", False)

        self._client = Minio(
            minio_server, access_key=access_key, secret_key=secret_key, secure=secure
        )

        app.storage = self
        return app

    @property
    def client(self):
        """Devuelve el cliente MinIO."""
        return self._client

    @client.setter
    def client(self, value):
        """Establece el cliente MinIO.

        Args:
            value: El cliente MinIO que se va a establecer.
        """
        self._client = value


storage = Storage()
