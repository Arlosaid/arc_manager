document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded');
    
    // Verificar si el botón existe
    const btn = document.querySelector('.sign-in-btn');
    if (btn) {
        console.log('Botón encontrado:', btn);
        console.log('Texto inicial del botón:', btn.textContent);
        
        // Verificar clases
        console.log('Clases del botón:', btn.className);
        
        // Verificar estilos computados
        const styles = window.getComputedStyle(btn);
        console.log('Color de fondo:', styles.backgroundColor);
    } else {
        console.log('No se encontró el botón');
    }
    
    // El resto de tu código...
    animateLoginForm();
    // ...
});
document.addEventListener('DOMContentLoaded', function() {
    // Animación de entrada
    animateLoginForm();
    
    // Selecciona elementos del formulario
    const inputs = document.querySelectorAll('.login-form input');
    const passwordInput = document.getElementById('id_password');
    const passwordToggle = document.querySelector('.password-toggle');
    const signInBtn = document.querySelector('.sign-in-btn');
    const loginForm = document.querySelector('.login-form');
    
    // Aplicar efectos en los inputs
    setupInputEffects(inputs);
    
    // Configurar toggle de contraseña
    setupPasswordToggle(passwordInput, passwordToggle);
    
    // Configurar efecto de botón
    setupButtonEffect(signInBtn);
    
    // Configurar validación de formulario
    setupFormValidation(loginForm);
});

// Función para animar la entrada del formulario
function animateLoginForm() {
    const formElements = document.querySelectorAll('.login-title, .form-group, .login-options, .signup-section, .notification-box');
    
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
}

// Configurar efectos en los inputs
function setupInputEffects(inputs) {
    if (inputs.length > 0) {
        inputs.forEach(input => {
            const inputWrapper = input.parentElement;
            const inputIcon = inputWrapper.querySelector('.input-icon');
            
            // Verificar si tiene contenido al cargar
            if (input.value !== '') {
                inputWrapper.classList.add('has-value');
            }
            
            // Efectos al enfocar
            input.addEventListener('focus', function() {
                inputWrapper.classList.add('focused');
                if (inputIcon) {
                    inputIcon.style.color = 'var(--primary-color)';
                }
            });
            
            // Efectos al quitar foco
            input.addEventListener('blur', function() {
                inputWrapper.classList.remove('focused');
                if (inputIcon) {
                    inputIcon.style.color = '';
                }
                
                if (this.value.length > 0) {
                    inputWrapper.classList.add('has-value');
                } else {
                    inputWrapper.classList.remove('has-value');
                }
            });
        });
    }
}

// Configurar toggle de contraseña
function setupPasswordToggle(passwordInput, passwordToggle) {
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Cambiar icono
            const icon = this.querySelector('span');
            if (type === 'password') {
                icon.className = 'mdi mdi-eye-outline';
            } else {
                icon.className = 'mdi mdi-eye-off-outline';
            }
        });
    }
}

// Configurar efecto de botón
function setupButtonEffect(signInBtn) {
    if (signInBtn) {
        signInBtn.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        signInBtn.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        signInBtn.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }
}

// Configurar validación de formulario
function setupFormValidation(loginForm) {
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            let isValid = true;
            const username = document.getElementById('id_username');
            const password = document.getElementById('id_password');
            
            // Validación de email
            if (username && !validateEmail(username.value)) {
                showError(username, 'Por favor, introduce un email válido');
                isValid = false;
            } else if (username) {
                removeError(username);
            }
            
            // Validación de contraseña
            if (password && password.value.length < 1) {
                showError(password, 'La contraseña es obligatoria');
                isValid = false;
            } else if (password) {
                removeError(password);
            }
            
            if (!isValid) {
                event.preventDefault();
                shakeElement(loginForm.querySelector('.sign-in-btn'));
            } else {
                // Animación de carga
                const btn = this.querySelector('.sign-in-btn'); // Usar 'this' en lugar de loginForm
                if (btn) {
                    btn.innerHTML = 'Iniciando sesión...'; // Sin el spinner por ahora
                    btn.disabled = true;
                }
            }
        });
    }
}

// Función para validar email
function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// Función para mostrar errores
function showError(element, message) {
    // Quitar error previo si existe
    removeError(element);
    
    // Obtener el wrapper
    const wrapper = element.closest('.input-wrapper');
    
    // Crear y mostrar nuevo error
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Aplicar clases de error
    element.classList.add('error');
    if (wrapper) wrapper.classList.add('has-error');
    
    // Insertar después del wrapper
    wrapper.parentNode.insertBefore(errorDiv, wrapper.nextSibling);
    
    // Animar el campo con error
    shakeElement(wrapper);
}

// Función para quitar errores
function removeError(element) {
    // Obtener el wrapper
    const wrapper = element.closest('.input-wrapper');
    
    // Quitar mensaje de error
    if (wrapper) {
        const parent = wrapper.parentNode;
        const errorDiv = parent.querySelector('.error-message');
        
        if (errorDiv) {
            parent.removeChild(errorDiv);
        }
        
        // Quitar clases de error
        element.classList.remove('error');
        wrapper.classList.remove('has-error');
    }
}

// Función para hacer vibrar un elemento
function shakeElement(element) {
    element.classList.add('shake');
    setTimeout(() => {
        element.classList.remove('shake');
    }, 500);
}

// Añadir estilos dinámicos para animaciones adicionales
(function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .shake {
            animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
        }
        
        @keyframes shake {
            10%, 90% { transform: translate3d(-1px, 0, 0); }
            20%, 80% { transform: translate3d(2px, 0, 0); }
            30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
            40%, 60% { transform: translate3d(4px, 0, 0); }
        }
        
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .input-wrapper.has-error {
            position: relative;
        }
        
        .input-wrapper.has-error::after {
            content: '!';
            position: absolute;
            right: -20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--danger);
            font-weight: bold;
            font-size: 14px;
            width: 16px;
            height: 16px;
            text-align: center;
            line-height: 16px;
            border-radius: 50%;
            border: 1px solid var(--danger);
        }
        
        .has-value .input-icon {
            color: var(--gray-dark);
        }
        
        .focused .input-icon {
            color: var(--primary-color) !important;
        }
    `;
    document.head.appendChild(style);
})();

// Añade esta función al final del archivo auth.js
function setupButtonEffects() {
    const buttons = document.querySelectorAll('.sign-in-btn');
    
    buttons.forEach(button => {
        button.addEventListener('mousedown', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Asegúrate de llamar a esta función al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Resto de tu código existente...
    
    // Añadir efectos adicionales a los botones
    setupButtonEffects();
});