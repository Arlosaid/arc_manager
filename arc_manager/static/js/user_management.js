// Gestión de Usuarios - JavaScript Moderno con Tooltips Mejorados
class UserManagement {
    constructor() {
        this.searchInput = document.querySelector('.table-search-input');
        this.checkboxes = document.querySelectorAll('.checkbox');
        this.actionButtons = document.querySelectorAll('.action-btn');
        this.paginationButtons = document.querySelectorAll('.pagination-btn, .pagination-number');
        this.tooltipContainer = document.getElementById('tooltip-container');
        this.currentTooltip = null;
        this.tooltipTimeout = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSearch();
        this.setupCheckboxes();
        this.setupTooltips();
        this.animateOnLoad();
        this.createTooltipContainer();
    }

    createTooltipContainer() {
        if (!this.tooltipContainer) {
            this.tooltipContainer = document.createElement('div');
            this.tooltipContainer.id = 'tooltip-container';
            document.body.appendChild(this.tooltipContainer);
        }
    }

    setupEventListeners() {
        // Búsqueda en tiempo real
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        }

        // Botones de acción
        this.actionButtons.forEach(button => {
            button.addEventListener('click', this.handleActionClick.bind(this));
        });

        // Paginación
        this.paginationButtons.forEach(button => {
            button.addEventListener('click', this.handlePaginationClick.bind(this));
        });

        // Checkbox principal
        const mainCheckbox = document.querySelector('thead .checkbox');
        if (mainCheckbox) {
            mainCheckbox.addEventListener('change', this.handleSelectAll.bind(this));
        }

        // Event listeners globales para tooltips
        document.addEventListener('scroll', () => {
            this.hideTooltip();
        });

        window.addEventListener('resize', () => {
            this.hideTooltip();
        });
    }

    setupSearch() {
        // Animación del icono de búsqueda
        if (this.searchInput) {
            this.searchInput.addEventListener('focus', () => {
                const searchIcon = document.querySelector('.table-search-icon');
                if (searchIcon) {
                    searchIcon.style.color = 'var(--primary-color)';
                    searchIcon.style.transform = 'translateY(-50%) scale(1.1)';
                }
            });

            this.searchInput.addEventListener('blur', () => {
                const searchIcon = document.querySelector('.table-search-icon');
                if (searchIcon) {
                    searchIcon.style.color = 'var(--text-muted)';
                    searchIcon.style.transform = 'translateY(-50%) scale(1)';
                }
            });
        }
    }

    setupCheckboxes() {
        // Gestión de checkboxes individuales
        const bodyCheckboxes = document.querySelectorAll('tbody .checkbox');
        bodyCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', this.updateMainCheckbox.bind(this));
        });
    }

    setupTooltips() {
        // Tooltips mejorados para botones de acción
        this.actionButtons.forEach(button => {
            const tooltipText = button.getAttribute('data-tooltip');
            if (tooltipText) {
                button.addEventListener('mouseenter', (e) => {
                    this.showTooltip(e.target, tooltipText);
                });
                
                button.addEventListener('mouseleave', () => {
                    this.hideTooltip();
                });

                // Ocultar tooltip al hacer click
                button.addEventListener('click', () => {
                    this.hideTooltip();
                });

                // Ocultar tooltip si el elemento pierde el focus
                button.addEventListener('blur', () => {
                    this.hideTooltip();
                });
            }
        });
    }

    animateOnLoad() {
        // DESHABILITADO: animaciones de carga
        /*
        // Usar la clase base para animaciones
        BaseAnimation.animateElements('.stat-card-mini, .table-container, .info-card-sidebar', {
            stagger: 30,
            distance: 8
        });

        // Animar filas de la tabla
        const tableRows = document.querySelectorAll('.modern-table tbody tr');
        tableRows.forEach(row => {
            BaseAnimation.animateTableRow(row);
        });

        // Animar botones de acción
        const actionButtons = document.querySelectorAll('.action-btn');
        actionButtons.forEach(button => {
            BaseAnimation.animateButton(button);
        });
        */
    }

    handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        const rows = document.querySelectorAll('tbody tr');
        let visibleCount = 0;

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(searchTerm);
            
            row.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
            
            // DESHABILITADO: Animación suave
            /*
            if (isVisible) {
                row.style.opacity = '0';
                setTimeout(() => {
                    row.style.transition = 'opacity 0.3s ease';
                    row.style.opacity = '1';
                }, 50);
            }
            */
        });

        this.updateResultCount(visibleCount, searchTerm);
    }

    handleActionClick(event) {
        const button = event.currentTarget;
        const action = button.classList.contains('view') ? 'view' : 
                      button.classList.contains('edit') ? 'edit' : 'delete';
        
        // Ocultar tooltip inmediatamente
        this.hideTooltip();

        // Agregar efecto visual
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);

        // No manejar aquí los botones con onclick específico
        if (button.hasAttribute('onclick')) {
            return; // Dejar que el onclick maneje la acción
        }

        const row = button.closest('tr');
        const userName = row ? row.querySelector('.user-name').textContent : '';

        switch (action) {
            case 'view':
                this.showUserDetails(userName);
                break;
            case 'edit':
                this.editUser(userName);
                break;
            case 'delete':
                // Esta ruta ya no se usa porque los botones tienen onclick
                this.confirmDeleteUser(userName);
                break;
        }
    }

    handlePaginationClick(event) {
        event.preventDefault();
        const button = event.currentTarget;
        
        if (button.classList.contains('disabled')) return;

        // Remover clase active de todos los números
        document.querySelectorAll('.pagination-number').forEach(btn => {
            btn.classList.remove('active');
        });

        // Agregar clase active al botón clickeado si es un número
        if (button.classList.contains('pagination-number')) {
            button.classList.add('active');
        }

        // Simular carga
        this.showLoading();
        setTimeout(() => {
            this.hideLoading();
        }, 500);
    }

    handleSelectAll(event) {
        const isChecked = event.target.checked;
        const bodyCheckboxes = document.querySelectorAll('tbody .checkbox');
        
        bodyCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            this.animateCheckbox(checkbox);
        });

        this.updateSelectedCount();
    }

    updateMainCheckbox() {
        const bodyCheckboxes = document.querySelectorAll('tbody .checkbox');
        const checkedBoxes = document.querySelectorAll('tbody .checkbox:checked');
        const mainCheckbox = document.querySelector('thead .checkbox');
        
        if (mainCheckbox) {
            mainCheckbox.checked = bodyCheckboxes.length === checkedBoxes.length;
            mainCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < bodyCheckboxes.length;
        }

        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('tbody .checkbox:checked');
        // Aquí podrías mostrar un contador de elementos seleccionados
        console.log(`${checkedBoxes.length} usuarios seleccionados`);
    }

    updateResultCount(count, searchTerm) {
        const resultCountElement = document.querySelector('.result-count');
        if (resultCountElement) {
            if (searchTerm) {
                resultCountElement.textContent = `${count} resultado${count !== 1 ? 's' : ''} para "${searchTerm}"`;
            } else {
                resultCountElement.textContent = `Mostrando 1-${count} de ${count} resultados`;
            }
        }
    }

    showUserDetails(userName) {
        this.showNotification(`Mostrando detalles de ${userName}`, 'info');
    }

    editUser(userName) {
        this.showNotification(`Editando usuario ${userName}`, 'warning');
    }

    confirmDeleteUser(userName) {
        const confirmed = confirm(`¿Estás seguro de que deseas eliminar al usuario ${userName}?\n\nEsta acción no se puede deshacer.`);
        if (confirmed) {
            this.deleteUser(userName);
        }
    }

    deleteUser(userName) {
        // Simular eliminación
        this.showNotification(`Usuario ${userName} eliminado correctamente`, 'success');
        
        // Aquí harías la petición real al servidor
        // fetch('/api/users/delete', { method: 'DELETE', ... })
    }

    showNotification(message, type = 'info') {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Estilos inline para la notificación
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            backgroundColor: type === 'success' ? '#10b981' : 
                           type === 'warning' ? '#f59e0b' : 
                           type === 'error' ? '#ef4444' : '#06b6d4'
        });

        document.body.appendChild(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showTooltip(element, text) {
        // Limpiar tooltip anterior y timeout
        this.hideTooltip();
        
        // Crear nuevo tooltip
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = text;
        
        // Agregar al container
        this.tooltipContainer.appendChild(tooltip);
        
        // Posicionar el tooltip
        this.positionTooltip(element, tooltip);
        
        // Guardar referencia
        this.currentTooltip = tooltip;
        
        // Mostrar con delay
        this.tooltipTimeout = setTimeout(() => {
            if (this.currentTooltip) {
                this.currentTooltip.classList.add('show');
            }
        }, 200);
    }

    positionTooltip(element, tooltip) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        // Calcular posición inicial (arriba del elemento)
        let top = rect.top + scrollTop - tooltipRect.height - 10;
        let left = rect.left + scrollLeft + (rect.width / 2) - (tooltipRect.width / 2);
        
        // Ajustar si se sale de la pantalla por arriba
        if (top < scrollTop + 10) {
            top = rect.bottom + scrollTop + 10;
            // Cambiar la flecha hacia arriba
            tooltip.style.setProperty('--arrow-direction', 'up');
        }
        
        // Ajustar si se sale de la pantalla por los lados
        const viewportWidth = window.innerWidth;
        if (left < 10) {
            left = 10;
        } else if (left + tooltipRect.width > viewportWidth - 10) {
            left = viewportWidth - tooltipRect.width - 10;
        }
        
        // Aplicar posición
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    hideTooltip() {
        // Limpiar timeout
        if (this.tooltipTimeout) {
            clearTimeout(this.tooltipTimeout);
            this.tooltipTimeout = null;
        }
        
        // Ocultar tooltip actual
        if (this.currentTooltip) {
            this.currentTooltip.classList.remove('show');
            
            // Remover después de la animación
            setTimeout(() => {
                if (this.currentTooltip && this.currentTooltip.parentNode) {
                    this.tooltipContainer.removeChild(this.currentTooltip);
                }
                this.currentTooltip = null;
            }, 200);
        }
    }

    animateCheckbox(checkbox) {
        checkbox.style.transform = 'scale(1.2)';
        setTimeout(() => {
            checkbox.style.transform = 'scale(1)';
        }, 150);
    }

    showLoading() {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.classList.add('loading');
        }
    }

    hideLoading() {
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.classList.remove('loading');
        }
    }

    // Utility function para debounce
    debounce(func, wait) {
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

    // Método para limpiar tooltips al destruir la instancia
    destroy() {
        this.hideTooltip();
        if (this.tooltipContainer && this.tooltipContainer.parentNode) {
            document.body.removeChild(this.tooltipContainer);
        }
    }
}

// Funciones utilitarias adicionales
const Utils = {
    // Formatear fechas
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    },

    // Generar avatar con iniciales
    generateAvatar(firstName, lastName) {
        const initials = (firstName?.charAt(0) || '') + (lastName?.charAt(0) || '');
        return initials.toUpperCase();
    },

    // Validar email
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Escapar HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Detectar si el dispositivo es móvil
    isMobile() {
        return window.innerWidth <= 768;
    },

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
};

// Variable global para la instancia
let userManagementInstance = null;

// Función global para notificaciones (fallback)
function showGlobalNotification(message, type = 'info') {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos inline para la notificación
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        backgroundColor: type === 'success' ? '#10b981' : 
                       type === 'warning' ? '#f59e0b' : 
                       type === 'error' ? '#ef4444' : '#06b6d4'
    });

    document.body.appendChild(notification);

    // Animación de entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    userManagementInstance = new UserManagement();
    
    // Agregar algunos event listeners globales
    document.addEventListener('keydown', (e) => {
        // Esc para cerrar modales o limpiar búsqueda
        if (e.key === 'Escape') {
            // Ocultar tooltips
            if (userManagementInstance) {
                userManagementInstance.hideTooltip();
            }
            
            // Limpiar búsqueda
            const searchInput = document.querySelector('.table-search-input');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
        
        // Ctrl+F para enfocar búsqueda
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('.table-search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
});

// Limpiar al cerrar la página
window.addEventListener('beforeunload', () => {
    if (userManagementInstance) {
        userManagementInstance.destroy();
    }
});

// ===== JAVASCRIPT EXTRAÍDO DE TEMPLATES =====

// Funciones para modal de eliminación
function openDeleteModal(userId) {
    // Buscar información del usuario en la tabla
    let userRow = null;
    const deleteButtons = document.querySelectorAll('button[onclick*="openDeleteModal"]');
    
    for (let btn of deleteButtons) {
        if (btn.onclick.toString().includes(userId)) {
            userRow = btn.closest('tr');
            if (!userRow) {
                userRow = btn.closest('.mobile-user-card');
            }
            break;
        }
    }
    
    if (!userRow) {
        console.error('No se encontró información del usuario');
        return;
    }
    
    // Poblar modal
    if (userRow.tagName === 'TR') {
        populateDeleteModalFromTable(userId, userRow);
    } else {
        populateDeleteModalFromMobile(userId, userRow);
    }
    
    // Mostrar modal manualmente
    const modalElement = document.getElementById('deleteUserModal');
    modalElement.style.display = 'block';
    modalElement.classList.add('show');
    document.body.classList.add('modal-open');
}

// Función para cerrar el modal
function closeDeleteModal() {
    const modalElement = document.getElementById('deleteUserModal');
    modalElement.style.display = 'none';
    modalElement.classList.remove('show');
    document.body.classList.remove('modal-open');
}

function populateDeleteModalFromTable(userId, row) {
    const userInfo = extractUserInfoFromTableRow(row);
    populateDeleteModal(userId, userInfo);
}

function populateDeleteModalFromMobile(userId, card) {
    const userInfo = extractUserInfoFromMobileCard(card);
    populateDeleteModal(userId, userInfo);
}

function extractUserInfoFromTableRow(row) {
    const userNameEl = row.querySelector('.user-name');
    const emailEl = row.querySelector('.email-link');
    const roleEl = row.querySelector('.role-badge');
    const statusEl = row.querySelector('.status-badge');
    
    return {
        fullName: userNameEl ? userNameEl.textContent.trim() : 'N/A',
        email: emailEl ? emailEl.textContent.trim() : 'N/A',
        role: roleEl ? roleEl.textContent.trim() : 'N/A',
        status: statusEl ? statusEl.textContent.trim() : 'N/A',
        initials: userNameEl ? getInitials(userNameEl.textContent) : 'NA'
    };
}

function extractUserInfoFromMobileCard(card) {
    const userNameEl = card.querySelector('.user-name');
    const emailEl = card.querySelector('.user-username');
    const roleEl = card.querySelector('.role-badge');
    const statusEl = card.querySelector('.status-badge');
    
    return {
        fullName: userNameEl ? userNameEl.textContent.trim() : 'N/A',
        email: emailEl ? emailEl.textContent.trim() : 'N/A',
        role: roleEl ? roleEl.textContent.trim() : 'N/A',
        status: statusEl ? statusEl.textContent.trim() : 'N/A',
        initials: userNameEl ? getInitials(userNameEl.textContent) : 'NA'
    };
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

function populateDeleteModal(userId, userInfo) {
    document.getElementById('userInitials').textContent = userInfo.initials;
    document.getElementById('userFullName').textContent = userInfo.fullName;
    document.getElementById('userEmail').textContent = userInfo.email;
    // Note: userOrganization será interpolado en el template
    document.getElementById('userStatus').innerHTML = `<span class="badge ${userInfo.status.toLowerCase() === 'activo' ? 'bg-success' : 'bg-secondary'}">${userInfo.status}</span>`;
    
    // Configurar el botón de confirmación
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    confirmBtn.setAttribute('data-user-id', userId);
    
    // Resetear checkbox y botón
    const checkbox = document.getElementById('confirmUnderstand');
    checkbox.checked = false;
    confirmBtn.disabled = true;
    
    // Resetear spinner
    const spinner = confirmBtn.querySelector('.spinner-border');
    if (spinner) spinner.classList.add('d-none');
}

function deleteUser(userId) {
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const spinner = confirmBtn.querySelector('.spinner-border');
    
    // Mostrar loading
    confirmBtn.disabled = true;
    if (spinner) spinner.classList.remove('d-none');
    
    // Realizar petición de eliminación con la URL correcta
    const formData = new FormData();
    formData.append('confirm_delete', 'yes');
    
    fetch(`/users/${userId}/delete-ajax/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal
            closeDeleteModal();
            
            // Obtener nombre del usuario para la notificación
            const userNameEl = document.getElementById('userFullName');
            const userName = userNameEl ? userNameEl.textContent : 'Usuario';
            
            // Mostrar notificación de éxito
            if (userManagementInstance) {
                userManagementInstance.showNotification(
                    `${userName} eliminado correctamente`, 
                    'success'
                );
            } else {
                // Fallback si no hay instancia
                showGlobalNotification(`${userName} eliminado correctamente`, 'success');
            }
            
            // Recargar después de mostrar la notificación
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.error || 'Error al eliminar usuario');
        }
    })
    .catch(error => {
        // Restaurar botón
        confirmBtn.disabled = false;
        if (spinner) spinner.classList.add('d-none');
        
        // Mostrar notificación de error
        if (userManagementInstance) {
            userManagementInstance.showNotification(
                `Error al eliminar usuario: ${error.message}`, 
                'error'
            );
        } else {
            // Fallback si no hay instancia
            showGlobalNotification(`Error al eliminar usuario: ${error.message}`, 'error');
        }
        
        // Log en consola para debug
        console.error('Error al eliminar usuario:', error);
        
        // Cerrar modal 
        closeDeleteModal();
    });
}



// Funciones de validación para formularios
const FormValidation = {
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    validateRequired(value) {
        return value && value.trim().length > 0;
    },
    
    validateName(name) {
        return name && name.trim().length >= 2;
    },
    
    showFieldError(field, message) {
        // Remover errores anteriores
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Agregar nuevo error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        field.parentNode.appendChild(errorDiv);
        
        // Estilo del campo con error
        field.classList.add('is-invalid');
    },
    
    clearFieldError(field) {
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        field.classList.remove('is-invalid');
    }
};

// Inicialización específica para modal de eliminación
document.addEventListener('DOMContentLoaded', function() {
    // Configurar modal de eliminación
    const confirmCheckbox = document.getElementById('confirmUnderstand');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    if (confirmCheckbox && confirmBtn) {
        confirmCheckbox.addEventListener('change', function() {
            confirmBtn.disabled = !this.checked;
        });
        
        // Manejar click del botón de eliminar
        confirmBtn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            if (userId && confirmCheckbox.checked) {
                deleteUser(userId);
            }
        });
    }
    

    
    // Configurar validación en tiempo real para formularios
    const formInputs = document.querySelectorAll('.modern-input, .modern-select');
    formInputs.forEach(input => {
        input.addEventListener('blur', function() {
            FormValidation.clearFieldError(this);
            
            // Validaciones específicas según el tipo de campo
            if (this.type === 'email' && this.value) {
                if (!FormValidation.validateEmail(this.value)) {
                    FormValidation.showFieldError(this, 'Por favor, ingresa un email válido');
                }
            }
            
            if (this.required && !FormValidation.validateRequired(this.value)) {
                FormValidation.showFieldError(this, 'Este campo es obligatorio');
            }
        });
        
        // Limpiar errores al escribir
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                FormValidation.clearFieldError(this);
            }
        });
    });
});

// ===== JavaScript BÁSICO PARA USUARIOS =====

// ===== FIN DEL ARCHIVO =====