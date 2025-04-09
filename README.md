# Grupo 13

## Miembros
* Damián Bicocchi
* Juan Pablo Miyagusuku
* Miguel Miesionznik
* Valentin Ciamparella

## Descripción de las Librerías Python

A continuación se describe cada una de las dependencias clave utilizadas en el proyecto:

#### Librerías Core

* **`python = "^3.12"`**: Especifica la versión de Python requerida para ejecutar la aplicación.
* **`flask = "^3.0.3"`**: Framework web ligero y flexible para desarrollar aplicaciones web en Python.

#### Librerías para Base de Datos

* **`psycopg2-binary = "^2.9.9"`**: Adaptador de base de datos PostgreSQL para Python, que permite realizar consultas y manejar la base de datos de manera eficiente.
* **`flask-sqlalchemy = "^3.1.1"`**: Extensión de Flask que integra SQLAlchemy, un ORM (Object Relational Mapper) para definir modelos de datos como clases de Python y facilitar operaciones de base de datos.

#### Librerías para Configuración y Seguridad

* **`python-dotenv = "^1.0.1"`**: Permite cargar variables de entorno desde un archivo `.env`, ideal para mantener la configuración sensible fuera del código fuente.
* **`flask-session = "^0.8.0"`**: Extensión para manejar sesiones de usuario en aplicaciones Flask.
* **`flask-bcrypt = "^1.0.1"`**: Extensión que proporciona funciones de hashing de contraseñas seguras usando el algoritmo bcrypt, ideal para el almacenamiento seguro de contraseñas de usuarios.

#### Librerías para Otras Funcionalidades

* **`sqlalchemy = "^2.0.35"`**: ORM de alto nivel para Python que permite realizar operaciones de base de datos de forma eficiente y estructurada.
* **`minio = "^7.2.9"`**: Cliente Python para MinIO, útil para la gestión de almacenamiento en la nube.
* **`ulid = "^1.1"`**: Generador de identificadores únicos (ULIDs) que son útiles para crear identificadores globalmente únicos.
* **`requests = "^2.32.3"`**: Librería para hacer solicitudes HTTP de manera sencilla.
* **`pyopenssl = "^24.2.1"`**: Proporciona soporte para operaciones criptográficas y conexiones seguras en aplicaciones.
* **`oauthlib = "^3.2.2"`**: Librería para implementar OAuth en aplicaciones web.
* **`fpdf2 = "^2.8.1"`**: Librería para la creación de archivos PDF en Python.
* **`matplotlib = "^3.9.2"`**: Librería de visualización de datos en Python para gráficos y diagramas.
* **`marshmallow = "^3.23.1"`**: Librería para la serialización y deserialización de datos, especialmente útil para la validación y transformación de entradas JSON.
* **`flask-cors = "^5.0.0"`**: Extensión de Flask que permite manejar CORS (Cross-Origin Resource Sharing) de manera sencilla.

### Dependencias de Desarrollo

* **`pytest = "^8.3.2"`**: Framework de pruebas para Python, utilizado para realizar pruebas unitarias y de integración en el proyecto.

## Usuarios de prueba y consideraciones

juan@gmail.com
123456
Roles: Administracion y es Sys Admin

user2@gmail.com
123456
Rol: Ecuestre

user3@gmail.com
123456
Rol: Administracion

user4@gmail.com
123456
Rol: Tecnica

uneditor@gmail.com
Prueba123
Rol: Editor


En los casos que hay que crear elementos (caballos, empleados, etc) que incluyan cualquier numero de telefono, hay que poner 10 digitos en total. Ejemplo: 2211234567
El numero de afiliado de la obra social de los empleados debe ingresarse sin la barra.

En los casos donde hay paginacion (listado de empleados, usuarios, etc) la cantidad de elementos mostrados por pagina es 9.


Cuando se crea un empleado, se detecta automaticamente si hay un usuario del sistema con el mismo email. En caso de existir se asocia automaticamente el empleado al usuario, y luego en el listado de empleados y en los detalles del mismo se vera el alias del usuario asociado. Si el usuario esta bloqueado al momento de crear el empleaedo entonces se notifica que se debe desbloquear primero al usuario. 
Si modifico un usuario e ingreso el mail de un empleado existente se vincularan, pero si el empleado esta dado de baja se podra modificar al usuario pero no se vinculara al empleado, si quisiera que se vincule tendria que dar de alta al empleado y luego modificar al usuario con el mismo mail.

## Para probar las API:
1. Ejemplo de GET de publicaciones con filtros opcionales de autor, page, per_page, published_from y published_to
https://admin-grupo13.proyecto2024.unlp.edu.ar/api/publications?author=AliasDelAutor&published_from=2023-10-10&published_to=2023-10-10&page=1&per_page=10

2. Ejemplo de GET de una publicacion en particular (con una publicacion de ID=2)
https://admin-grupo13.proyecto2024.linti.unlp.edu.ar/api/publications/2

3. Para probar la API post, se debe ingresar a la app pública, acceder al formulario de contacto, completar los campos y enviarlo. Luego se puede comprobar en el panel de Contacto en la app privada, accediendo con un usuario system admin o con rol administrador.

Enlace al formulario de la app publica: https://grupo13.proyecto2024.linti.unlp.edu.ar/contacto
Enlace al panel de mensajes de la app privada: 
https://admin-grupo13.proyecto2024.linti.unlp.edu.ar/contacts/
