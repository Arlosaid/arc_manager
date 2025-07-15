/**
 * Dashboard Optimizado - Arc Manager
 * Versión simplificada con funcionalidad esencial
 */

class Dashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupCounters();
        this.setupInteractions();
        this.setupRefreshButtons();
    }

    // Contadores simples sin animaciones
    setupCounters() {
        const counters = document.querySelectorAll('.metric-value[data-target]');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            counter.textContent = target;
        });
    }

    // Interacciones básicas
    setupInteractions() {
        // Card clicks
        document.querySelectorAll('.metric-card').forEach(card => {
            card.addEventListener('click', this.handleCardClick.bind(this));
        });

        // Project cards
        document.querySelectorAll('.project-card-mini').forEach(card => {
            card.addEventListener('click', this.handleProjectClick.bind(this));
        });

        // Summary items
        document.querySelectorAll('.summary-item-mini').forEach(item => {
            item.addEventListener('click', this.handleSummaryClick.bind(this));
        });
    }

    // Botones de refresh
    setupRefreshButtons() {
        document.querySelectorAll('[data-action="refresh"]').forEach(button => {
            button.addEventListener('click', this.handleRefresh.bind(this));
        });
    }

    // Handlers de eventos
    handleCardClick(e) {
        const card = e.currentTarget;
        const label = card.querySelector('.metric-label')?.textContent;
        // Aquí podrías navegar a una página específica
        // window.location.href = `/dashboard/${label.toLowerCase().replace(/\s+/g, '-')}`;
    }

    handleProjectClick(e) {
        const card = e.currentTarget;
        const projectName = card.querySelector('h4')?.textContent;
        // Aquí podrías navegar al proyecto específico
        // window.location.href = `/projects/${projectName.toLowerCase().replace(/\s+/g, '-')}`;
    }

    handleSummaryClick(e) {
        const item = e.currentTarget;
        const title = item.querySelector('h5')?.textContent;
        // Aquí podrías navegar al item específico
        // window.location.href = `/tasks/${title.toLowerCase().replace(/\s+/g, '-')}`;
    }

    handleRefresh(e) {
        e.preventDefault();
        // Aquí podrías recargar datos específicos
        // this.loadDashboardData();
    }

    // Método para actualizar métricas (llamado desde el backend)
    updateMetric(metricId, value) {
        const element = document.querySelector(`[data-metric="${metricId}"]`);
        if (element) {
            element.textContent = value;
        }
    }

    // Método para mostrar notificaciones simples
    showNotification(message, type = 'info') {
        // Implementación básica - podrías usar una librería como toastify
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            background: ${type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Cleanup
    destroy() {
        // Remover event listeners si es necesario
        document.querySelectorAll('.metric-card').forEach(card => {
            card.removeEventListener('click', this.handleCardClick);
        });
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    
    // Exponer para debugging en desarrollo
    if (process.env.NODE_ENV === 'development') {
        window.dashboard = dashboard;
    }
});

// Función auxiliar para formatear números
function formatNumber(number) {
    return number.toLocaleString();
}

// Función auxiliar para formatear fechas
function formatDate(date) {
    return new Date(date).toLocaleDateString();
} 