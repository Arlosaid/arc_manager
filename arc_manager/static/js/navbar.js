// static/js/navbar.js
document.addEventListener('DOMContentLoaded', function() {
    // Comportamiento específico para el navbar
    console.log('Navbar JS cargado');
    
    // Cerrar automáticamente el menú desplegable en móviles al hacer clic en un elemento
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const menuToggle = document.getElementById('navbarNav');
    const bsCollapse = bootstrap.Collapse.getInstance(menuToggle);
    
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992 && bsCollapse) {
                bsCollapse.hide();
            }
        });
    });
    
    // Cambiar estilo del navbar al hacer scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
});