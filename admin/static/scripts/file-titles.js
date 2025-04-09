let filesData = [];

document.getElementById('file_source').addEventListener('change', function (event) {
    const files = event.target.files;
    const fileTitles = document.getElementById('file_titles');
    // Iterar sobre los archivos seleccionados
    Array.from(files).forEach(file => {
        const validExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpeg', '.jpg'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!validExtensions.includes(`.${fileExtension}`)) {
            alert('El archivo seleccionado no tiene una extensión válida.');
            return;
        }
        const title = prompt(`Por favor, ingresa el título para el archivo: ${file.name}`);
        if (title) {
            // Agregar el archivo y su título al array
            filesData.push({ file: file, title: title });
            // Crear un elemento de lista para mostrar el archivo y su título
            const li = document.createElement('li');
            li.textContent = `${file.name} - Título: ${title}`;
        }
    });
    // Guardar los títulos como un JSON para enviarlo al servidor
    fileTitles.value = JSON.stringify(filesData.map(f => ({ title: f.title, name: f.file.name })));
    // Aquí se puede manejar cómo pasar los archivos a un formData al hacer submit o puedes manejarlos en el servidor.
});
// Evitar que el input reemplace archivos anteriores al seleccionar nuevos
document.getElementById('file_source').addEventListener('click', function (event) {
    event.target.value = null;
});

function addLink() {
    // Contenedor donde se agregarán los inputs
    const container = document.getElementById('inputContainer');

    // Crear un div que envuelve los dos inputs y el botón de eliminación
    const inputGroup = document.createElement('div');
    inputGroup.classList.add('input-group');

    // Crear input para el enlace (link)
    const linkInput = document.createElement('input');
    linkInput.type = 'url';
    linkInput.name = 'links[]';
    linkInput.placeholder = 'Ingrese el enlace';
    linkInput.required = true;

    // Crear input para el título del enlace
    const titleInput = document.createElement('input');
    titleInput.type = 'text';
    titleInput.name = 'link_titles[]';
    titleInput.placeholder = 'Ingrese el título del enlace';
    titleInput.required = true;

    // Crear botón de eliminación (una cruz ❌)
    const removeButton = document.createElement('button');
    removeButton.type = 'button'; // Evita que se envíe el formulario al hacer clic
    removeButton.innerHTML = '❌';
    removeButton.classList.add('remove-btn');

    // Evento para eliminar el grupo de inputs
    removeButton.addEventListener('click', function () {
        container.removeChild(inputGroup);
    });

    // Agregar los inputs y el botón al grupo de inputs
    inputGroup.appendChild(linkInput);
    inputGroup.appendChild(titleInput);
    inputGroup.appendChild(removeButton);

    // Agregar el grupo de inputs al contenedor dentro del formulario existente
    container.appendChild(inputGroup);
}