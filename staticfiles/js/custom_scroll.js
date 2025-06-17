window.addEventListener('load', function () {
    if (window.location.hash) {
        const element = document.getElementById(window.location.hash.substring(1));
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    const checkbox = document.getElementById('toggleDescriptionCheckbox');
    const descriptionField = document.querySelector('.description-field');

    if (checkbox && descriptionField) {
        checkbox.addEventListener('change', function () {
            descriptionField.parentElement.style.display = this.checked ? 'block' : 'none';
        });

        descriptionField.parentElement.style.display = 'none';
    }
});
