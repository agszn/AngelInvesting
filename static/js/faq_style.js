// faq_style.js
document.addEventListener("DOMContentLoaded", function () {
    const styleDropdown = document.getElementById("id_style");
    const descTextarea = document.getElementById("id_description");

    if (!styleDropdown || !descTextarea) return;

    styleDropdown.addEventListener("change", function () {
        let rawText = descTextarea.value.trim();
        if (!rawText) return;

        let lines = rawText.split('\n').filter(line => line.trim().startsWith('--'));
        let points = lines.map(line => line.replace(/^--/, '').trim());
        let formatted = "";

        switch (this.value) {
            case 'ul':
                formatted = "<ul>" + points.map(p => `<li>${p}</li>`).join('') + "</ul>";
                break;
            case 'ol_number':
                formatted = "<ol type='1'>" + points.map(p => `<li>${p}</li>`).join('') + "</ol>";
                break;
            case 'ol_alpha':
                formatted = "<ol type='A'>" + points.map(p => `<li>${p}</li>`).join('') + "</ol>";
                break;
            default:
                formatted = "<p>" + rawText + "</p>";
        }

        descTextarea.value = formatted;
    });
});
