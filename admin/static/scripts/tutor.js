const secondTutorFields = document.querySelectorAll('#second_tutor_fields input, #second_tutor_fields select');
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('input[name="second_tutor_enabled"]').forEach(radio => {
        radio.addEventListener('change', () => {
            
            if (document.getElementById('second_tutor_no').checked) {
                // Limpiar y deshabilitar todos los campos del segundo tutor
                secondTutorFields.forEach(field => {
                    field.removeAttribute('required')
                    field.value = ''; // Limpiar el campo
                    field.disabled = true; // Deshabilitar el campo
                });
            } else {
                // Habilitar los campos del segundo tutor
                secondTutorFields.forEach(field => {
                    if (field.id != "piso_secundario" && field.id != "departamento_secundario"){
                        field.setAttribute('required', 'required');
                    }
                    
                    field.disabled = false;
                });
            }
        });
    });


    // Deshabilitar campos al cargar si el radio "no" está seleccionado
    if (document.getElementById('second_tutor_no').checked) {
        secondTutorFields.forEach(field => {
            field.disabled = true;
        });
    }
});

const radioYes = document.getElementById('second_tutor_yes');
const radioNo = document.getElementById('second_tutor_no');
const secondTutorSection = document.getElementById('second_tutor_fields');
let i = 0;
// Función para limpiar los campos del segundo tutor
function clearSecondTutorFields(deshabilitar) {
    const inputs = secondTutorSection.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        
        if (deshabilitar){
            input.value = '';
            input.setAttribute('disabled', 'disabled') ; 
            input.removeAttribute('required');
            input.classList.add('disabled-input');
        } else {
            if(! ((input.id === "piso_secundario") || (input.id === "departamento_secundario"))){
                input.setAttribute('required', 'required');
            }                
            input.removeAttribute('disabled');
            input.classList.remove('disabled-input');
        }
    });
}

// Detectar el cambio en los inputs radio
radioNo.addEventListener('change', function() {
    if (this.checked) {
        clearSecondTutorFields(true);  // Limpiar los campos si se selecciona "NO"
    }
    else{
        clearSecondTutorFields(false);
    }
});

// Opcional: Mostrar los campos si se selecciona "SI"
radioYes.addEventListener('change', function() {
    if (this.checked) {
        clearSecondTutorFields(false);
    }
    else{
        clearSecondTutorFields(true);
    }
});



window.addEventListener('DOMContentLoaded', function() {
if (radioYes.checked) {
    clearSecondTutorFields(false); // Si "SI" está seleccionado, mostrar los campos
} else if (radioNo.checked) {
    clearSecondTutorFields(true); // Si "NO" está seleccionado, limpiar los campos
} else {
    clearSecondTutorFields(false); // Si no hay selección, mostrar los campos
}
});