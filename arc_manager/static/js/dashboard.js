// Dashboard JavaScript - Extiende BaseAnimation
class DashboardManager extends BaseAnimation {
    constructor() {
        super();
        this.initializeDashboard();
    }

    initializeDashboard() {
        // Inicializar animaciones específicas del dashboard
        this.initializeDashboardAnimations();
        this.initializeProgressBars();
        this.initializeTooltips();
    }

    initializeDashboardAnimations() {
        // Animar las tarjetas del dashboard
        this.animateElements('.dashboard-card', {
            delay: 0,
            stagger: 100,
            distance: 20,
            duration: 0.3
        });

        // Animar elementos de actividad
        this.animateElements('.dashboard-activity-item', {
            delay: 300,
            stagger: 50,
            distance: 20,
            duration: 0.3
        });
    }

    initializeProgressBars() {
        const progressBars = document.querySelectorAll('.dashboard-progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('data-progress') + '%';
            bar.style.width = '0';
            
            setTimeout(() => {
                bar.style.width = targetWidth;
            }, 300);
        });
    }

    initializeTooltips() {
        // Inicializar tooltips de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover'
            });
        });
    }

    updateCardValue(cardId, newValue, animate = true) {
        const card = document.querySelector(`#${cardId} .dashboard-card-value`);
        if (!card) return;

        if (animate) {
            const oldValue = parseInt(card.textContent);
            const diff = newValue - oldValue;
            const duration = 1000;
            const steps = 20;
            const stepValue = diff / steps;
            let currentStep = 0;

            const interval = setInterval(() => {
                currentStep++;
                const currentValue = Math.round(oldValue + (stepValue * currentStep));
                card.textContent = currentValue;

                if (currentStep >= steps) {
                    clearInterval(interval);
                    card.textContent = newValue;
                }
            }, duration / steps);
        } else {
            card.textContent = newValue;
        }
    }

    updateProgressBar(barId, newProgress) {
        const bar = document.querySelector(`#${barId} .dashboard-progress-bar`);
        if (!bar) return;

        bar.style.width = `${newProgress}%`;
        bar.setAttribute('data-progress', newProgress);
    }

    animateStatsCards() {
        // Animar aparición de tarjetas estadísticas
        const cards = document.querySelectorAll('.dashboard-stat-card');
        cards.forEach((card, idx) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(.4,2,.3,1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 + idx * 120);
        });
    }

    animateProgressBars() {
        // Animar barras de progreso
        const bars = document.querySelectorAll('.dashboard-progress-bar .progress-bar');
        bars.forEach(bar => {
            const target = parseInt(bar.getAttribute('aria-valuenow')) || 0;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1s cubic-bezier(.4,2,.3,1)';
                bar.style.width = target + '%';
            }, 400);
        });
    }
}

// Inicializar el dashboard cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardManager = new DashboardManager();
}); 