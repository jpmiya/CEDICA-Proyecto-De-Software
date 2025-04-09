const passwordInput = document.getElementById("password");

passwordInput.addEventListener("input", function () {
    // Remueve todos los espacios en blanco del valor del input
    this.value = this.value.replace(/\s/g, "");
});