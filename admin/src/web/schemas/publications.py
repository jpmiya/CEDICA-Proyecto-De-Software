from marshmallow import fields, Schema


class PublicationSchema(Schema):
    """
    Esquema de Marshmallow para serializar y deserializar objetos de publicación.

    Attributes:
        id (int): Identificador único de la publicación. Solo para lectura.
        title (str): Título de la publicación. Campo obligatorio.
        author_id (str): Identificador del autor de la publicación. Campo obligatorio.
        author (str): Nombre del autor de la publicación. Campo obligatorio.
        publication_date (datetime.date): Fecha de publicación. Campo opcional.
        creation_date (datetime.datetime): Fecha de creación de la publicación. Solo para lectura.
        updated_date (datetime.datetime): Fecha de última actualización de
        la publicación. Solo para lectura.
        state (str): Estado de la publicación. Campo obligatorio.
        summary (str): Resumen de la publicación. Campo obligatorio.
        content (str): Contenido completo de la publicación. Campo obligatorio.
    """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author_id = fields.Str(required=True)
    author = fields.Str(required=True)
    publication_date = fields.Date(required=False)
    creation_date = fields.DateTime(dump_only=True)
    updated_date = fields.DateTime(dump_only=True)
    state = fields.Str(required=True)
    summary = fields.Str(required=True)
    content = fields.Str(required=True)


publication_schema = PublicationSchema()
publications_schema = PublicationSchema(many=True)
