// static/js/sidebar.js

class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.sectionHeaders = document.querySelectorAll('.section-header');
        this.mainContent = document.querySelector('.main-content');
        this.body = document.body;
        this.isOpen = false;
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.handleResize();
        this.setActiveLink();
        this.updateLayout();
    }
    
    bindEvents() {
        // Toggle sidebar en móvil
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleSidebar();
            });
        }
        
        // Cerrar sidebar al hacer click en overlay
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => this.closeSidebar());
        }
        
        // Cerrar sidebar con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen && this.isMobile) {
                this.closeSidebar();
            }
        });
        
        // Manejo responsive
        window.addEventListener('resize', () => this.handleResize());
        
        // Efectos de hover para los enlaces
        this.navLinks.forEach(link => {
            link.addEventListener('mouseenter', (e) => this.handleLinkHover(e));
            link.addEventListener('mouseleave', (e) => this.handleLinkLeave(e));
            link.addEventListener('click', (e) => this.handleLinkClick(e));
        });
        
        // Efectos para headers de sección
        this.sectionHeaders.forEach(header => {
            header.addEventListener('click', (e) => this.handleSectionClick(e));
        });
        
        // Prevenir scroll cuando sidebar está abierto en móvil
        document.addEventListener('touchmove', (e) => {
            if (this.isOpen && this.isMobile && !this.sidebar.contains(e.target)) {
                e.preventDefault();
            }
        }, { passive: false });
    }
    
    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        if (!this.isMobile) return;
        
        this.sidebar.classList.add('sidebar-open');
        this.sidebarOverlay.classList.add('show');
        this.body.classList.add('sidebar-open');
        this.isOpen = true;
        
        // Disparar evento personalizado
        this.dispatchEvent('sidebar:opened');
    }
    
    closeSidebar() {
        if (!this.isMobile) return;
        
        this.sidebar.classList.remove('sidebar-open');
        this.sidebarOverlay.classList.remove('show');
        this.body.classList.remove('sidebar-open');
        this.isOpen = false;
        
        // Disparar evento personalizado
        this.dispatchEvent('sidebar:closed');
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        // Si cambió de móvil a desktop
        if (wasMobile && !this.isMobile) {
            this.closeSidebar();
            this.sidebar.classList.remove('sidebar-open');
            this.sidebarOverlay.classList.remove('show');
            this.body.classList.remove('sidebar-open');
        }
        
        // Actualizar layout
        this.updateLayout();
    }
    
    updateLayout() {
        if (!this.isMobile && this.mainContent) {
            // En desktop, asegurar margen correcto
            this.mainContent.style.marginLeft = 'var(--side-layout-width)';
        } else if (this.mainContent) {
            this.mainContent.style.marginLeft = '0';
        }
    }
    
    handleLinkHover(e) {
        const link = e.currentTarget;
        const icon = link.querySelector('.nav-icon i');
        
        // Efecto de rotación sutil en el icono
        if (icon) {
            icon.style.transform = 'rotate(5deg) scale(1.1)';
            icon.style.transition = 'transform 0.3s ease';
        }
    }
    
    handleLinkLeave(e) {
        const link = e.currentTarget;
        const icon = link.querySelector('.nav-icon i');
        
        if (icon) {
            icon.style.transform = '';
        }
    }
    
    handleLinkClick(e) {
        const link = e.currentTarget;
        
        // Agregar efecto de click
        this.addClickEffect(link);
        
        // En móvil, cerrar sidebar después del click
        if (this.isMobile && this.isOpen) {
            setTimeout(() => this.closeSidebar(), 250);
        }
        
        // Actualizar estado activo
        this.setActiveLink(link);
    }
    
    handleSectionClick(e) {
        const header = e.currentTarget;
        const section = header.closest('.nav-section');
        const navList = section.querySelector('.nav-list');
        
        if (navList) {
            // Toggle collapse de la sección
            section.classList.toggle('collapsed');
            
            // Animar colapso
            if (section.classList.contains('collapsed')) {
                navList.style.maxHeight = '0';
                navList.style.opacity = '0';
            } else {
                navList.style.maxHeight = navList.scrollHeight + 'px';
                navList.style.opacity = '1';
            }
        }
    }
    
    setActiveLink(activeLink = null) {
        // Remover clase activa de todos los enlaces
        this.navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        if (activeLink) {
            activeLink.classList.add('active');
        } else {
            // Buscar enlace activo basado en la URL actual
            const currentPath = window.location.pathname;
            this.navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href !== '#' && currentPath.includes(href)) {
                    link.classList.add('active');
                }
            });
        }
    }
    
    addClickEffect(element) {
        element.style.transform = 'scale(0.95)';
        element.style.transition = 'transform 0.15s ease';
        
        setTimeout(() => {
            element.style.transform = '';
        }, 150);
    }

    dispatchEvent(eventName) {
        const event = new CustomEvent(eventName, {
            detail: {
                isOpen: this.isOpen,
                isMobile: this.isMobile
            }
        });
        document.dispatchEvent(event);
    }
    
    // Métodos públicos para control externo
    collapse() {
        this.sidebar.classList.add('sidebar-collapsed');
    }
    
    expand() {
        this.sidebar.classList.remove('sidebar-collapsed');
    }
    
    isCollapsed() {
        return this.sidebar.classList.contains('sidebar-collapsed');
    }
    
    // Método para forzar actualización
    refresh() {
        this.handleResize();
        this.setActiveLink();
        this.updateLayout();
    }
}

// Agregar estilos CSS para funcionalidades necesarias
const additionalStyles = `
    .nav-list {
        transition: max-height 0.3s ease, opacity 0.3s ease;
        overflow: hidden;
    }
    
    .nav-section.collapsed .nav-list {
        max-height: 0 !important;
        opacity: 0 !important;
    }
    
    .sidebar-collapsed {
        width: var(--sidebar-collapsed-width) !important;
    }
    
    .sidebar-collapsed .nav-text,
    .sidebar-collapsed .brand-text,
    .sidebar-collapsed .section-title,
    .sidebar-collapsed .user-info {
        opacity: 0;
        visibility: hidden;
    }
    
    .sidebar-collapsed .nav-icon {
        margin-right: 0;
        justify-content: center;
    }
    
    /* Mejoras de performance */
    .sidebar {
        will-change: transform;
    }
    
    .nav-link {
        will-change: transform, background-color;
    }
`;

// Agregar estilos al head
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.sidebarManager = new SidebarManager();
        
        // Eventos globales para debugging
        document.addEventListener('sidebar:opened', () => {
            console.log('🎨 Sidebar abierto');
        });
        
        document.addEventListener('sidebar:closed', () => {
            console.log('🎨 Sidebar cerrado');
        });
        
    } catch (error) {
        console.error('❌ Error inicializando Sidebar Manager:', error);
    }
});

// Exportar para uso global
window.SidebarManager = SidebarManager;