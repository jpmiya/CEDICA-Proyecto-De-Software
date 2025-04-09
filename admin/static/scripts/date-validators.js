document.addEventListener('DOMContentLoaded', function() {
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');

    function validateDates() {
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);
        const maxDate = new Date('2100-12-31');

        // Verificar si la fecha de finalización es mayor a la de inicio
        if (end < start) {
            alert('La fecha de finalización no puede ser anterior a la fecha de inicio.');
            endDate.value = ""; // Limpiar el campo si es inválido
            return false;
        }

        // Verificar si la fecha de finalización no es mayor a 2100
        if (end > maxDate) {
            alert('El año no puede ser mayor a 2100.');
            endDate.value = ""; // Limpiar el campo si es inválido
            return false;
        }

        return true;
    }

    // Validar cada vez que el usuario cambie la fecha de finalización
    endDate.addEventListener('change', validateDates);
});