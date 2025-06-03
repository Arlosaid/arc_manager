// static/js/navbar.js

class NavbarManager {
    constructor() {
        this.navbar = document.getElementById('mainNavbar');
        this.userDropdownToggle = document.getElementById('userDropdownToggle');
        this.userDropdown = null;
        
        this.init();
    }
    
    init() {
        this.initDropdowns();
        this.bindEvents();
        this.handleResize();
        this.initScrollEffects();
        
        console.log('🎨 Navbar Manager inicializado (diseño moderno)');
    }
    
    initDropdowns() {
        console.log('🔍 Inicializando dropdowns...');
        
        // Configurar dropdown del usuario
        this.userDropdownToggle = document.getElementById('userDropdownToggle');
        
        if (this.userDropdownToggle) {
            console.log('✅ Toggle del dropdown encontrado');
            
            // Buscar el dropdown menu
            const dropdownContainer = this.userDropdownToggle.closest('.dropdown');
            if (dropdownContainer) {
                this.userDropdown = dropdownContainer.querySelector('.dropdown-menu');
                console.log('✅ Dropdown menu encontrado:', this.userDropdown);
            }
            
            if (this.userDropdown) {
                // Asegurar que esté oculto inicialmente
                this.userDropdown.style.display = 'none';
                this.userDropdown.classList.remove('show');
                
                // Event listener para el toggle
                this.userDropdownToggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🖱️ Click en dropdown toggle');
                    this.toggleUserDropdown();
                });
                
                // Cerrar dropdown al hacer click fuera
                document.addEventListener('click', (e) => {
                    if (!dropdownContainer.contains(e.target)) {
                        console.log('🖱️ Click fuera del dropdown, cerrando...');
                        this.closeUserDropdown();
                    }
                });
                
                // Cerrar dropdown con Escape
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Escape' && this.userDropdown.classList.contains('show')) {
                        console.log('⌨️ Escape presionado, cerrando dropdown');
                        this.closeUserDropdown();
                    }
                });
                
                console.log('✅ Dropdown configurado correctamente');
            } else {
                console.error('❌ No se encontró el dropdown menu del usuario');
            }
        } else {
            console.error('❌ No se encontró el toggle del dropdown');
        }
    }
    
    bindEvents() {
        // Resize
        window.addEventListener('resize', () => this.handleResize());
    }
    
    initScrollEffects() {
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        const updateNavbar = () => {
            const currentScrollY = window.scrollY;
            
            // Efecto de fondo al hacer scroll
            if (currentScrollY > 50) {
                this.navbar.classList.add('scrolled');
            } else {
                this.navbar.classList.remove('scrolled');
            }
            
            lastScrollY = currentScrollY;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        });
    }
    
    // === Dropdown del usuario ===
    toggleUserDropdown() {
        if (!this.userDropdown) {
            console.warn('⚠️ No se puede toggle el dropdown - no existe');
            return;
        }
        
        const isOpen = this.userDropdown.classList.contains('show');
        console.log('📊 Estado actual del dropdown:', isOpen ? 'abierto' : 'cerrado');
        
        if (isOpen) {
            this.closeUserDropdown();
        } else {
            this.openUserDropdown();
        }
    }
    
    openUserDropdown() {
        if (!this.userDropdown) return;
        
        console.log('📖 Abriendo dropdown del usuario');
        
        // Cerrar otros dropdowns abiertos
        document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
            if (dropdown !== this.userDropdown) {
                dropdown.classList.remove('show');
                dropdown.style.display = 'none';
            }
        });
        
        // Mostrar dropdown
        this.userDropdown.style.display = 'block';
        this.userDropdown.classList.add('show');
        this.userDropdownToggle.setAttribute('aria-expanded', 'true');
        
        // Agregar clase al contenedor padre
        const dropdownContainer = this.userDropdownToggle.closest('.dropdown');
        if (dropdownContainer) {
            dropdownContainer.classList.add('show');
        }
        
        // Posicionamiento
        this.positionDropdown();
        
        console.log('✅ Dropdown abierto exitosamente');
    }
    
    closeUserDropdown() {
        if (!this.userDropdown) return;
        
        console.log('📕 Cerrando dropdown del usuario');
        
        this.userDropdown.classList.remove('show');
        this.userDropdownToggle.setAttribute('aria-expanded', 'false');
        
        // Remover clase del contenedor padre
        const dropdownContainer = this.userDropdownToggle.closest('.dropdown');
        if (dropdownContainer) {
            dropdownContainer.classList.remove('show');
        }
        
        // Esperar la animación antes de ocultar completamente
        setTimeout(() => {
            if (!this.userDropdown.classList.contains('show')) {
                this.userDropdown.style.display = 'none';
            }
        }, 200);
        
        console.log('✅ Dropdown cerrado exitosamente');
    }
    
    positionDropdown() {
        if (!this.userDropdown) return;
        
        const rect = this.userDropdownToggle.getBoundingClientRect();
        const dropdownRect = this.userDropdown.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Resetear estilos de posicionamiento
        this.userDropdown.style.left = '';
        this.userDropdown.style.right = '';
        this.userDropdown.style.top = '';
        this.userDropdown.style.bottom = '';
        
        // Ajustar posición si se sale de la pantalla
        if (rect.right + dropdownRect.width > viewportWidth) {
            this.userDropdown.style.left = 'auto';
            this.userDropdown.style.right = '0';
        }
        
        if (rect.bottom + dropdownRect.height > viewportHeight) {
            this.userDropdown.style.top = 'auto';
            this.userDropdown.style.bottom = '100%';
            this.userDropdown.style.marginTop = '0';
            this.userDropdown.style.marginBottom = '8px';
        }
    }
    
    // === Responsive ===
    handleResize() {
        const isMobile = window.innerWidth <= 768;
        
        // Ajustar navbar para móvil
        if (isMobile) {
            this.navbar.classList.add('mobile');
            this.closeUserDropdown(); // Cerrar dropdown en resize
        } else {
            this.navbar.classList.remove('mobile');
        }
        
        // Reposicionar dropdown si está abierto
        if (this.userDropdown && this.userDropdown.classList.contains('show')) {
            this.positionDropdown();
        }
    }
    
    // === API Pública ===
    updateNotificationCount(count) {
        // Esta función se mantiene por compatibilidad pero no hace nada
        // ya que removimos los iconos de notificación
        console.log(`📢 Notificaciones: ${count} (iconos removidos)`);
    }
    
    showToast(message, type = 'info') {
        // Sistema de notificaciones toast simple
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Estilos inline para el toast
        Object.assign(toast.style, {
            position: 'fixed',
            top: '80px',
            right: '20px',
            background: type === 'error' ? '#ef4444' : '#3b82f6',
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: '9999',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            maxWidth: '300px'
        });
        
        document.body.appendChild(toast);
        
        // Animación de entrada
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
        
        console.log(`📢 Toast (${type}): ${message}`);
    }
    
    // === Métodos de utilidad ===
    setUserInfo(name, email, organization) {
        const userName = this.navbar.querySelector('.user-name');
        const userEmail = this.navbar.querySelector('.user-email');
        const userOrg = this.navbar.querySelector('.user-org');
        
        if (userName) userName.textContent = name;
        if (userEmail) userEmail.textContent = email;
        if (userOrg) userOrg.textContent = organization;
    }
    
    updateBrandLogo(logoUrl, brandName) {
        const brandLogo = this.navbar.querySelector('.brand-logo');
        const brandText = this.navbar.querySelector('.brand-text');
        
        if (brandLogo && logoUrl) {
            brandLogo.innerHTML = `<img src="${logoUrl}" alt="${brandName}">`;
        }
        
        if (brandText) {
            brandText.textContent = brandName;
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Esperar un poco para asegurar que todos los elementos estén cargados
    setTimeout(() => {
        window.navbarManager = new NavbarManager();
    }, 100);
});

// También inicializar si el DOM ya está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            if (!window.navbarManager) {
                window.navbarManager = new NavbarManager();
            }
        }, 100);
    });
} else {
    // DOM ya está listo
    setTimeout(() => {
        if (!window.navbarManager) {
            window.navbarManager = new NavbarManager();
        }
    }, 100);
}

// Exportar para uso global
window.NavbarManager = NavbarManager;