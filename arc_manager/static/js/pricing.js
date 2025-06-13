// ===== PRICING.JS - INTERACCIONES Y LÓGICA DE LA PÁGINA DE PRECIOS =====

document.addEventListener('DOMContentLoaded', function() {
    initializePricingPage();
});

function initializePricingPage() {
    // Inicializar tooltips de características
    initializeFeatureTooltips();
    
    // Configurar botones CTA
    setupCTAButtons();
    
    // Configurar animaciones de entrada
    setupScrollAnimations();
    
    // Analytics tracking
    setupAnalyticsTracking();
}

// ===== CONFIGURACIÓN DE BOTONES CTA =====
function setupCTAButtons() {
    const ctaButtons = document.querySelectorAll('.cta-button');
    
    ctaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const planType = this.classList.contains('trial-cta') ? 'trial' :
                           this.classList.contains('basic-cta') ? 'basic' : 'premium';
            
            // Agregar estado de carga
            this.classList.add('loading');
            this.disabled = true;
            
            // Track analytics
            trackPlanSelection(planType);
            
            // Si es un enlace externo, permitir navegación normal
            if (this.href && !this.href.includes('#')) {
                return;
            }
            
            // Para enlaces internos o procesamiento AJAX
            e.preventDefault();
            
            // Simular procesamiento (puedes reemplazar con lógica real)
            setTimeout(() => {
                // Remover estado de carga
                this.classList.remove('loading');
                this.disabled = false;
                
                // Mostrar feedback de éxito
                showSuccessFeedback(this, planType);
            }, 2000);
        });
        
        // Efectos de hover mejorados
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.disabled) {
                this.style.transform = '';
            }
        });
    });
}

// ===== FEEDBACK VISUAL =====
function showSuccessFeedback(button, planType) {
    const originalText = button.innerHTML;
    const successMessages = {
        trial: '<i class="fas fa-check"></i> ¡Prueba iniciada!',
        basic: '<i class="fas fa-check"></i> ¡Solicitud enviada!',
        premium: '<i class="fas fa-check"></i> ¡Solicitud enviada!'
    };
    
    button.innerHTML = successMessages[planType];
    button.style.background = 'linear-gradient(135deg, #10b981, #059669)';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '';
    }, 3000);
}

// ===== TOOLTIPS PARA CARACTERÍSTICAS =====
function initializeFeatureTooltips() {
    const featureItems = document.querySelectorAll('.feature-item');
    
    const tooltipTexts = {
        'Hasta 2 usuarios': 'Puedes invitar hasta 2 miembros a tu equipo',
        'Hasta 3 proyectos': 'Gestiona hasta 3 proyectos simultáneamente',
        'Hasta 5 usuarios': 'Puedes invitar hasta 5 miembros a tu equipo',
        'Hasta 10 proyectos': 'Gestiona hasta 10 proyectos simultáneamente', 
        'Hasta 15 usuarios': 'Puedes invitar hasta 15 miembros a tu equipo',
        'Hasta 50 proyectos': 'Gestiona hasta 50 proyectos simultáneamente',
        'Soporte prioritario': 'Respuesta garantizada en menos de 24 horas',
        'Reportes avanzados': 'Dashboards detallados y exportación de datos',
        'Integraciones API': 'Conecta con herramientas externas via API'
    };
    
    featureItems.forEach(item => {
        const text = item.querySelector('span').textContent;
        if (tooltipTexts[text]) {
            item.title = tooltipTexts[text];
            item.style.cursor = 'help';
        }
    });
}

// ===== ANIMACIONES DE SCROLL =====
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observar elementos que necesitan animación
    const elementsToAnimate = document.querySelectorAll('.faq-item, .trust-item');
    elementsToAnimate.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// ===== COMPARACIÓN DE PLANES =====
function togglePlanComparison() {
    const comparisonModal = document.getElementById('comparison-modal');
    if (comparisonModal) {
        comparisonModal.style.display = comparisonModal.style.display === 'none' ? 'block' : 'none';
    }
}

// ===== CALCULADORA DE PRECIOS =====
function calculatePricing(users, projects) {
    const plans = {
        trial: { users: 2, projects: 3, price: 0 },
        basic: { users: 5, projects: 10, price: 299 },
        premium: { users: 15, projects: 50, price: 599 }
    };
    
    let recommendedPlan = 'trial';
    
    if (users > plans.basic.users || projects > plans.basic.projects) {
        recommendedPlan = 'premium';
    } else if (users > plans.trial.users || projects > plans.trial.projects) {
        recommendedPlan = 'basic';
    }
    
    return {
        recommended: recommendedPlan,
        price: plans[recommendedPlan].price,
        savings: calculateAnnualSavings(plans[recommendedPlan].price)
    };
}

function calculateAnnualSavings(monthlyPrice) {
    // Descuento hipotético del 20% por pago anual
    const annualPrice = monthlyPrice * 12 * 0.8;
    const monthlyCost = monthlyPrice * 12;
    return monthlyCost - annualPrice;
}

// ===== ANALYTICS Y TRACKING =====
function trackPlanSelection(planType) {
    // Google Analytics 4
    if (typeof gtag === 'function') {
        gtag('event', 'plan_selected', {
            plan_type: planType,
            page_location: window.location.href
        });
    }
    
    // Facebook Pixel
    if (typeof fbq === 'function') {
        fbq('track', 'InitiateCheckout', {
            content_name: `Plan ${planType}`,
            currency: 'MXN'
        });
    }
    
    // Custom analytics
    console.log('Plan seleccionado:', planType);
}

function trackPageView() {
    if (typeof gtag === 'function') {
        gtag('event', 'page_view', {
            page_title: 'Pricing Page',
            page_location: window.location.href
        });
    }
}

// ===== FAQ INTERACTIVA =====
function initializeFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        
        // Hacer las preguntas clickeables para colapsar/expandir
        question.style.cursor = 'pointer';
        question.addEventListener('click', () => {
            const isExpanded = answer.style.display !== 'none';
            
            // Colapsar todas las respuestas
            faqItems.forEach(otherItem => {
                otherItem.querySelector('.faq-answer').style.display = 'none';
                otherItem.querySelector('.faq-question').style.background = '';
            });
            
            // Expandir la seleccionada si estaba colapsada
            if (isExpanded) {
                answer.style.display = 'none';
            } else {
                answer.style.display = 'block';
                question.style.background = 'var(--arc-bg-secondary)';
            }
        });
    });
}

// ===== VALIDACIÓN DE FORMULARIOS =====
function validateUpgradeForm(formData) {
    const errors = [];
    
    if (!formData.organization) {
        errors.push('Selecciona una organización');
    }
    
    if (!formData.plan) {
        errors.push('Selecciona un plan');
    }
    
    if (!formData.contact_info) {
        errors.push('Proporciona información de contacto');
    }
    
    return errors;
}

// ===== UTILIDADES =====
function formatCurrency(amount, currency = 'MXN') {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0
    }).format(amount);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== CONFIGURACIÓN INICIAL =====
function setupAnalyticsTracking() {
    // Track page view
    trackPageView();
    
    // Track scroll depth
    let maxScroll = 0;
    const trackScrollDepth = debounce(() => {
        const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
        if (scrollPercent > maxScroll) {
            maxScroll = scrollPercent;
            if (scrollPercent >= 25 && scrollPercent < 50) {
                trackScrollMilestone('25%');
            } else if (scrollPercent >= 50 && scrollPercent < 75) {
                trackScrollMilestone('50%');
            } else if (scrollPercent >= 75 && scrollPercent < 100) {
                trackScrollMilestone('75%');
            } else if (scrollPercent >= 100) {
                trackScrollMilestone('100%');
            }
        }
    }, 250);
    
    window.addEventListener('scroll', trackScrollDepth);
}

function trackScrollMilestone(percentage) {
    if (typeof gtag === 'function') {
        gtag('event', 'scroll_depth', {
            custom_parameter: percentage,
            page_location: window.location.href
        });
    }
}

// ===== MANEJO DE ERRORES =====
window.addEventListener('error', function(e) {
    console.error('Error en pricing.js:', e.error);
    
    // Remover estados de carga en caso de error
    const loadingButtons = document.querySelectorAll('.cta-button.loading');
    loadingButtons.forEach(button => {
        button.classList.remove('loading');
        button.disabled = false;
    });
});

// ===== EXPORTAR FUNCIONES PÚBLICAS =====
window.PricingPage = {
    calculatePricing,
    togglePlanComparison,
    formatCurrency,
    trackPlanSelection
}; 