class DniExistsException(Exception):
    """Excepción lanzada cuando el DNI ya existe."""

    def __init__(self, message="El DNI ingresado ya está en uso."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class RiderNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra un jinete."""

    def __init__(
        self,
        message="""No se encontró al jinete.
                 Reintente o comuníquese con el administrador""",
    ):
        self.message = message
        super().__init__(self.message)


class DniNotNumberException(Exception):
    """Excepción lanzada cuando el DNI no es un número."""

    def __init__(self, message="El DNI debe ser un número."):
        self.message = message
        super().__init__(self.message)


class DniLengthException(Exception):
    """Excepción lanzada cuando la longitud del DNI es inválida."""

    def __init__(self, message="El DNI debe tener 8 caracteres."):
        self.message = message
        super().__init__(self.message)


class EmailNotValidException(Exception):
    """Excepción lanzada cuando el correo electrónico no es válido."""

    def __init__(self, message="El email no es válido."):
        self.message = message
        super().__init__(self.message)


class EmailExistsException(Exception):
    """Excepción lanzada cuando el correo electrónico ya está registrado."""

    def __init__(self, message="El email ingresado ya está registrado."):
        self.message = message
        super().__init__(self.message)


class StartDateNullException(Exception):
    """Excepción lanzada cuando la fecha de inicio es nula."""

    def __init__(self, message="La fecha de inicio no puede ser nula."):
        self.message = message
        super().__init__(self.message)


class NameNotValidException(Exception):
    """Excepción lanzada cuando el nombre no es válido."""

    def __init__(self, message="El nombre no es válido."):
        self.message = message
        super().__init__(self.message)


class AliasNotValidException(Exception):
    """Excepción lanzada cuando el alias no es válido."""

    def __init__(
        self, message="El alias no es válido. Solo letras, números y guiones bajos."
    ):
        self.message = message
        super().__init__(self.message)


class AliasExistsException(Exception):
    """Excepción lanzada cuando el alias ya está registrado."""

    def __init__(self, message="El alias ingresado ya está registrado."):
        self.message = message
        super().__init__(self.message)


class DocumentNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra el documento."""

    def __init__(
        self,
        message="""No se encontró el documento.
                 Reintente o comuníquese con el administrador""",
    ):
        self.message = message
        super().__init__(self.message)


class AliasExistsLengthException(Exception):
    """Excepción lanzada cuando la longitud del alias es inválida."""

    def __init__(self, message="El alias debe tener entre 4 y 20 caracteres."):
        self.message = message
        super().__init__(self.message)


class SameTutorException(Exception):
    """Excepción lanzada cuando se intenta asignar dos veces el mismo tutor
    a un jinete o amazona."""

    def __init__(
        self,
        message="No puede asignar dos veces el mismo tutor al mismo jinete/amazona",
    ):
        self.message = message
        super().__init__(self.message)


class NotSufficientDataException(Exception):
    """Excepción lanzada cuando no se proporcionan todos los campos necesarios."""

    def __init__(self, message="Todos los campos son requeridos"):
        self.message = message
        super().__init__(self.message)


class PhoneLengthException(Exception):
    """Excepción lanzada cuando la longitud del número de teléfono es inválida."""

    def __init__(
        self, message="El número de teléfono debe tener entre 8 y 15 caracteres."
    ):
        self.message = message
        super().__init__(self.message)


class PhoneNotNumberException(Exception):
    """Excepción lanzada cuando el número de teléfono no es un número."""

    def __init__(self, message="El número de teléfono debe ser un número."):
        self.message = message
        super().__init__(self.message)


class InvalidDateException(Exception):
    """Excepción lanzada cuando la fecha es inválida."""

    def __init__(self, message="La fecha ingresada no es válida."):
        self.message = message
        super().__init__(self.message)


class BirthdayNotValidException(Exception):
    """Excepción lanzada cuando la fecha de nacimiento es inválida."""

    def __init__(self, message="La fecha de nacimiento ingresada no es válida."):
        self.message = message
        super().__init__(self.message)


class OptionNotInPermittedValuesException(Exception):
    """Excepción lanzada cuando la opción ingresada no forma parte de las opciones habilitadas."""

    def __init__(
        self, message="La opción ingresada no forma parte de las opciones habilitadas"
    ):
        self.message = message
        super().__init__(self.message)


class NotANumberException(Exception):
    """Excepción lanzada cuando el valor ingresado no es un número."""

    def __init__(self, message="Lo ingresado no corresponde a un número"):
        self.message = message
        super().__init__(self.message)


class InvalidLengthException(Exception):
    """Excepción lanzada cuando el valor ingresado supera el máximo permitido."""

    def __init__(self, message="Lo ingresado supera el máximo permitido"):
        self.message = message
        super().__init__(self.message)


class PaymentNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra el pago."""

    def __init__(self, message="El pago no existe."):
        self.message = message
        super().__init__(self.message)


class ChargeNotFoundException(Exception):
    """Excepción lanzada cuando no se encuentra el cobro."""

    def __init__(self, message="El cobro no existe"):
        self.message = message
        super().__init__(self.message)


class AmountNotNumberException(Exception):
    """Excepción lanzada cuando el monto no es un número."""

    def __init__(self, message="El monto no es un número."):
        self.message = message
        super().__init__(self.message)


class RolesNotValidException(Exception):
    """Excepción lanzada cuando los roles no son válidos."""

    def __init__(self, message="Los roles no son válidos."):
        self.message = message
        super().__init__(self.message)


class StringNotValidException(Exception):
    """Excepción lanzada cuando el valor ingresado no es una cadena."""

    def __init__(self, message="Debe ingresar una cadena de texto."):
        self.message = message
        super().__init__(self.message)
