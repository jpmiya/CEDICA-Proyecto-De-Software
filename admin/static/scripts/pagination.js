const toggleButton = document.getElementById('toggleOrder');
const orderInput = document.getElementById('orderInput');


toggleButton.addEventListener('click', function () {
    if (toggleButton.value === 'asc') {
        toggleButton.textContent = 'Desc';
        toggleButton.value = 'desc';
        orderInput.value = 'desc';
    } else {
        toggleButton.textContent = 'Asc';
        toggleButton.value = 'asc';
        orderInput.value = 'asc';
    }
});

function goToPage(pageNumber) {
    const pageInput = document.getElementById('page');
    
    pageInput.value = pageNumber;
    document.forms[0].submit();
}