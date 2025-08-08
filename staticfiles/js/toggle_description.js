window.addEventListener('load', function () {
    const checkbox = document.getElementById("toggleDescriptionCheckbox");
    const descFields = document.querySelectorAll(".description-field");

    if (checkbox) {
        checkbox.addEventListener('change', function () {
            descFields.forEach(field => {
                field.style.display = checkbox.checked ? 'block' : 'none';
            });
        });
    }
});
