import datetime
from marshmallow import fields, Schema


class MessageSchema(Schema):
    """
    Esquema de Marshmallow para serializar y deserializar objetos de contacto.

    Atributos:
        id (int): Identificador único del mensaje. Solo para lectura.
        title (str): Título del mensaje.
        state (str): Estado del mensaje.
        message (str): Contenido del mensaje.
        created_at (datetime): Fecha de creación del mensaje. Solo para carga.
        updated_at (datetime): Fecha de última actualización del mensaje.
        full_name (str): Nombre completo del remitente.
        email (str): Correo electrónico del remitente.
        comment (str): Comentario adicional.
    """

    id = fields.Int(dump_only=True)
    title = fields.Str()
    state = fields.Str()
    message = fields.Str()
    created_at = fields.DateTime(load_only=True, onload=datetime.datetime.now())
    updated_at = fields.DateTime()
    full_name = fields.Str()
    email = fields.Email()
    comment = fields.Str()


message_schema = MessageSchema()
