/**
 * Dashboard - Lógica de Interacción
 * Versión simplificada y profesional.
 */

class Dashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initializeCounters();
        this.initializeInteractions();
        this.initializeGreeting();
    }

    // ===== CONTADORES ANIMADOS =====
    initializeCounters() {
        const counterElements = document.querySelectorAll('.metric-value[data-target]');
        counterElements.forEach(element => {
            this.animateCounter(element);
        });
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-target')) || 0;
        const duration = 2000;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                clearInterval(timer);
                element.textContent = this.formatNumber(target);
            } else {
                element.textContent = this.formatNumber(Math.floor(current));
            }
        }, stepTime);
    }

    formatNumber(num) {
        return num.toLocaleString('es-ES');
    }

    // ===== INTERACCIONES =====
    initializeInteractions() {
        const refreshBtn = document.getElementById('refresh-activities');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                // Aquí se podría añadir lógica para recargar las actividades
                console.log('Refrescando actividades...');
                refreshBtn.querySelector('i').style.transform = `rotate(${this.rotation || 0}deg)`;
            });
        }
    }

    // ===== FUNCIONES DE UTILIDAD =====
    initializeGreeting() {
        const greetingElement = document.getElementById('greeting-text');
        if (!greetingElement) return;
        
        const hour = new Date().getHours();
        let greeting = 'Buenos días';
        if (hour >= 12 && hour < 20) {
            greeting = 'Buenas tardes';
        } else if (hour >= 20) {
            greeting = 'Buenas noches';
        }
        greetingElement.textContent = greeting;
    }
}

// Inicialización del dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
}); 