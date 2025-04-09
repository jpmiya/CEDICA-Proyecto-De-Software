document.addEventListener('DOMContentLoaded', () => {
    // Ejecutar updateHorseSelect al cargar la página
    updateHorseSelect();

    // Configurar los listeners de eventos
    document.querySelectorAll('input[name="headquarters"]').forEach((radio) => {
        radio.addEventListener('change', updateHorseSelect);
    });
    document.getElementById('proposal').addEventListener('change', updateHorseSelect);
});

async function updateHorseSelect() {
    
    const headquarters = document.querySelector('input[name="headquarters"]:checked')?.value;
    const proposal = document.getElementById('proposal').value;

    // Crear el FormData y agregar los valores de sede y rider_type
    const formData = new FormData();
    formData.append('headquarters', headquarters);
    formData.append('proposal', proposal);

    // Enviar la solicitud POST al endpoint de Flask
    const response = await fetch('/trabajo_institucional/get_caballos', {
        method: 'POST',
        body: formData
    });
    
    const horses = await response.json();

    // Obtener el valor preseleccionado
    const preselectedHorseId = document.getElementById('horse').dataset.preselectedId;

    // Limpia el select de caballos antes de agregar nuevas opciones
    const horseSelect = document.getElementById('horse');
    horseSelect.innerHTML = '<option value="">Seleccione un Caballo</option>';

    // Si no hay caballos, mostrar mensaje
    if (horses.length === 0) {
        const message = document.createElement('option');
        message.value = "";
        message.textContent = "No hay caballos disponibles con la actividad y sede dados";
        message.disabled = true;
        message.style.backgroundColor = "#f8d7da";
        message.style.color = "#721c24";
        horseSelect.appendChild(message);
    } else {
        horses.forEach(horse => {
            const option = document.createElement('option');
            option.value = horse.id;
            option.textContent = `${horse.name} ► Sede: ${horse.sede}`;
            
            // Si el caballo actual coincide con el preseleccionado, márcalo como seleccionado
            if (horse.id == preselectedHorseId) {
                option.selected = true;
            }

            horseSelect.appendChild(option);
        });
    }
}
