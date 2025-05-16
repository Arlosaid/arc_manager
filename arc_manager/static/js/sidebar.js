// static/js/sidebar.js
document.addEventListener('DOMContentLoaded', function() {
    // Comportamiento específico para el sidebar
    console.log('Sidebar JS cargado');
    
    // Función para ajustar el sidebar en dispositivos móviles
    function checkWindowSize() {
        const sidebar = document.querySelector('.sidebar');
        if (window.innerWidth < 768) {
            sidebar.classList.add('sidebar-mobile');
        } else {
            sidebar.classList.remove('sidebar-mobile');
        }
    }
    
    // Comprobar al cargar y al cambiar tamaño
    checkWindowSize();
    window.addEventListener('resize', checkWindowSize);
    
    // Toggle para expandir/colapsar secciones del sidebar (si se implementa)
    const sidebarHeadings = document.querySelectorAll('.sidebar-heading');
    sidebarHeadings.forEach(function(heading) {
        heading.addEventListener('click', function() {
            const nextUl = this.nextElementSibling;
            if (nextUl && nextUl.tagName === 'UL') {
                nextUl.classList.toggle('collapsed');
                this.classList.toggle('collapsed');
            }
        });
    });
});