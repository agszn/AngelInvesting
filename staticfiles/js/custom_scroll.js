window.addEventListener('load', function () {
    if (window.location.hash) {
        const element = document.getElementById(window.location.hash.substring(1));
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }
});
