document.addEventListener("DOMContentLoaded", function () {
    const showDescRadios = document.querySelectorAll('input[name="show_description"]');
    const descContainer = document.getElementById('desc-container');

    const valueTypeCheckboxes = document.querySelectorAll('input[name="value_types"]');
    const intContainer = document.getElementById('int-container');
    const decContainer = document.getElementById('dec-container');
    const charContainer = document.getElementById('char-container');
    const dateContainer = document.getElementById('date-container');

    function toggleDescription() {
        const selected = document.querySelector('input[name="show_description"]:checked');
        descContainer.style.display = (selected && selected.value === 'yes') ? '' : 'none';
    }

    function toggleValueFields() {
        const selected = Array.from(document.querySelectorAll('input[name="value_types"]:checked'))
            .map(cb => cb.value);

        intContainer.style.display = selected.includes('int_value') ? '' : 'none';
        decContainer.style.display = selected.includes('dec_value') ? '' : 'none';
        charContainer.style.display = selected.includes('char_value') ? '' : 'none';
        dateContainer.style.display = selected.includes('date_value') ? '' : 'none';
    }

    showDescRadios.forEach(radio => radio.addEventListener('change', toggleDescription));
    valueTypeCheckboxes.forEach(cb => cb.addEventListener('change', toggleValueFields));

    toggleDescription();
    toggleValueFields();
});
