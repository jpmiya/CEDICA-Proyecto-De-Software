function toggleDisabilityDetails(hasDisability, cleanOther) {
    const disabilityTypeDiv = document.getElementById('disabilityTypeDiv');
    const otherDiagnosisDiv = document.getElementById('otro_diagnosis_div');
    const otherDiagnosisInput = document.getElementById('other_diagnosis_input');
    const detailsDiv = document.getElementById('disability_details');
    const diagnosisSelect = document.getElementById('diagnosis');

    // Función para limpiar los checkboxes del tipo de discapacidad
    function clearDisabilityCheckboxes() {
        const checkboxes = document.querySelectorAll('#disabilityTypeDiv input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    // Si cleanOther está activo, limpia el campo "otro diagnóstico"
    if (cleanOther) {
        otherDiagnosisDiv.style.display = 'none';
        otherDiagnosisInput.value = "";
        otherDiagnosisInput.removeAttribute('required');
    }

    // Manejo según el valor de hasDisability
    if (hasDisability === true) {
        // Si seleccionó "Sí" en certificado
        detailsDiv.style.display = 'block';
        diagnosisSelect.setAttribute('required', 'required');
        disabilityTypeDiv.style.display = 'none';
        clearDisabilityCheckboxes();
    } else if (hasDisability === false) {
        // Si seleccionó "No" en certificado
        detailsDiv.style.display = 'none';
        diagnosisSelect.removeAttribute('required');
        diagnosisSelect.value = '';
        disabilityTypeDiv.style.display = 'block';
    } else {
        // Caso null: Ocultar ambos por defecto
        detailsDiv.style.display = 'none';
        diagnosisSelect.removeAttribute('required');
        diagnosisSelect.value = '';
        disabilityTypeDiv.style.display = 'none';
        clearDisabilityCheckboxes();
    }
}

function toggleOtherDiagnosis(selectedValue) {
    const otherDiagnosisDiv = document.getElementById('otro_diagnosis_div');
    const otherDiagnosisInput = document.getElementById('other_diagnosis_input');

    if (selectedValue === 'OTRO') {
        otherDiagnosisDiv.style.display = 'block';
        otherDiagnosisInput.setAttribute('required', 'required');
    } else {
        otherDiagnosisDiv.style.display = 'none';
        otherDiagnosisInput.removeAttribute('required');
        otherDiagnosisInput.value = "";
    }
}

function togglePensionType(hasPension) {
    const pensionOptions = document.getElementById('pensionOptions');
    const pensionRadios = document.querySelectorAll('input[name="pensionType"]');

    if (hasPension === true) {
        
        pensionOptions.style.display = "block";
        pensionRadios.forEach(radio => {
            radio.required = true;
        });
    } else if (hasPension === false) {
        
        pensionOptions.style.display = "none";
        pensionRadios.forEach(radio => {
            radio.required = false;
            radio.checked = false;
        });
    } else {
        
        pensionOptions.style.display = "none";
        pensionRadios.forEach(radio => {
            radio.required = false;
            radio.checked = false;
        });
    }
}

function toggleFamiliarPension(hasAllowance) {
    const checkboxContainer = document.getElementById('asignacionFamiliarOptions');
    checkboxContainer.style.display = hasAllowance ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    const selectedDisability = document.querySelector('input[name="has_disability"]:checked');
    const hasDisability = selectedDisability ? selectedDisability.value === 'yes' : null;

    const cleanOther = document.getElementById("diagnosis").value === "";
    
    console.log(hasDisability);

    toggleDisabilityDetails(hasDisability, cleanOther);

    const diagnosisSelect = document.getElementById('diagnosis');
    toggleOtherDiagnosis(diagnosisSelect.value);

    const selectedPension = document.querySelector('input[name="has_pension"]:checked');
    const hasPension = selectedPension ? selectedPension.value === 'yes' : null;
    
    togglePensionType(hasPension);

    const hasFamiliarAsignacion = document.querySelector('input[name="asignacion_familiar"]:checked')?.value === 'yes';
    toggleFamiliarPension(hasFamiliarAsignacion);
});
