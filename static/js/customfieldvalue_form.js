// static/js/customfieldvalue_form.js
document.addEventListener("DOMContentLoaded", function () {
    // Smooth scroll
    if (window.location.hash) {
        const element = document.getElementById(window.location.hash.substring(1));
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Description toggle logic (via radio button)
    const showDescRadios = document.querySelectorAll('input[name="show_description"]');
    const descContainer = document.getElementById('desc-container');

    function toggleDescription() {
        const selected = document.querySelector('input[name="show_description"]:checked');
        descContainer.style.display = (selected && selected.value === 'yes') ? 'block' : 'none';
    }

    showDescRadios.forEach(radio => radio.addEventListener('change', toggleDescription));
    toggleDescription();

    // Value type toggle logic (via checkboxes)
    const valueTypeCheckboxes = document.querySelectorAll('input[name="value_types"]');
    const intContainer = document.getElementById('int-container');
    const decContainer = document.getElementById('dec-container');
    const charContainer = document.getElementById('char-container');
    const dateContainer = document.getElementById('date-container');

    function toggleValueFields() {
        const selected = Array.from(document.querySelectorAll('input[name="value_types"]:checked'))
            .map(cb => cb.value);

        intContainer.style.display = selected.includes('int_value') ? 'block' : 'none';
        decContainer.style.display = selected.includes('dec_value') ? 'block' : 'none';
        charContainer.style.display = selected.includes('char_value') ? 'block' : 'none';
        dateContainer.style.display = selected.includes('date_value') ? 'block' : 'none';
    }

    valueTypeCheckboxes.forEach(cb => cb.addEventListener('change', toggleValueFields));
    toggleValueFields();
});
