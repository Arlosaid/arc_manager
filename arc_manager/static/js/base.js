// static/js/base.js

class BaseAnimation {
    static init() {
        // Configuración de animaciones base
        // this.setupAnimations(); // DESHABILITADO: animaciones de carga de página
    }

    static setupAnimations() {
        // Configurar animaciones para elementos comunes
        this.animateElements('.page-container, .main-content-grid, .table-container, .info-card-sidebar');
    }

    static animateElements(selector, options = {}) {
        const elements = document.querySelectorAll(selector);
        if (!elements.length) return;

        const defaultOptions = {
            delay: 0,
            stagger: 30,
            distance: 8,
            duration: 0.25,
            easing: 'ease-out'
        };

        const finalOptions = { ...defaultOptions, ...options };

        // Aplicar estilos iniciales de una vez
        elements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = `translateY(${finalOptions.distance}px)`;
            element.style.transition = `opacity ${finalOptions.duration}s ${finalOptions.easing}, transform ${finalOptions.duration}s ${finalOptions.easing}`;
        });

        // Forzar un reflow para asegurar que las transiciones funcionen
        document.body.offsetHeight;

        // Animar elementos con stagger
        elements.forEach((element, index) => {
            setTimeout(() => {
                requestAnimationFrame(() => {
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                });
            }, finalOptions.delay + (index * finalOptions.stagger));
        });
    }

    static animateTableRow(row, options = {}) {
        const defaultOptions = {
            duration: 0.2,
            easing: 'ease-out'
        };

        const finalOptions = { ...defaultOptions, ...options };

        row.style.opacity = '0';
        row.style.transform = 'translateX(-8px)';
        row.style.transition = `opacity ${finalOptions.duration}s ${finalOptions.easing}, transform ${finalOptions.duration}s ${finalOptions.easing}`;

        requestAnimationFrame(() => {
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        });
    }

    static animateButton(button, options = {}) {
        const defaultOptions = {
            duration: 0.15,
            easing: 'ease-out'
        };

        const finalOptions = { ...defaultOptions, ...options };

        button.style.transition = `transform ${finalOptions.duration}s ${finalOptions.easing}`;

        button.addEventListener('click', () => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, finalOptions.duration * 1000);
        });

        // Efecto hover simple
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-1px)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
        });
    }

    static animateCard(card, options = {}) {
        const defaultOptions = {
            duration: 0.2,
            easing: 'ease-out'
        };

        const finalOptions = { ...defaultOptions, ...options };

        card.style.transition = `transform ${finalOptions.duration}s ${finalOptions.easing}`;

        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    }
}

// Inicializar animaciones base cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar animaciones base
    BaseAnimation.init();

    // Activar los tooltips de Bootstrap en toda la aplicación
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Activar los popovers de Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});