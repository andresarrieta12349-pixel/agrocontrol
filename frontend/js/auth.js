/**
 * AGROCONTROL PRO - Autenticación y Login
 * Maneja la validación y autenticación de usuarios
 */

class AuthManager {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api';
        this.form = document.getElementById('loginForm');
        this.loginButton = document.getElementById('loginButton');
        this.togglePasswordButton = document.getElementById('togglePassword');
        this.passwordInput = document.getElementById('password');
        this.emailInput = document.getElementById('email');
        
        this.initializeEventListeners();
        this.checkIfAlreadyLoggedIn();
    }

    /**
     * Inicializa los event listeners
     */
    initializeEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        if (this.togglePasswordButton) {
            this.togglePasswordButton.addEventListener('click', (e) => this.togglePasswordVisibility(e));
        }
    }

    /**
     * Verifica si el usuario ya está autenticado
     */
    checkIfAlreadyLoggedIn() {
        const token = this.getToken();
        if (token && this.isTokenValid(token)) {
            window.location.href = './frontend/pages/dashboard.html';
        }
    }

    /**
     * Maneja el envío del formulario de login
     */
    async handleLogin(e) {
        e.preventDefault();

        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const remember = document.getElementById('remember').checked;

        // Limpiar mensajes previos
        this.clearMessages();

        // Validar campos
        if (!this.validateForm(email, password)) {
            return;
        }

        // Desabilitar botón y mostrar loader
        this.setLoginButtonLoading(true);

        try {
            const response = await fetch(`${this.baseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Error al iniciar sesión');
            }

            // Guardar token
            if (remember) {
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('userEmail', email);
            } else {
                sessionStorage.setItem('authToken', data.token);
            }

            // Guardar información del usuario
            localStorage.setItem('userData', JSON.stringify(data.user));

            // Mostrar mensaje de éxito
            this.showSuccessMessage('¡Bienvenido! Redirigiendo al dashboard...');

            // Redirigir después de 2 segundos
            setTimeout(() => {
                window.location.href = './frontend/pages/dashboard.html';
            }, 2000);

        } catch (error) {
            console.error('Error de login:', error);
            this.showErrorMessage(error.message || 'Error al conectar con el servidor');
        } finally {
            this.setLoginButtonLoading(false);
        }
    }

    /**
     * Valida los campos del formulario
     */
    validateForm(email, password) {
        let isValid = true;
        const emailError = document.getElementById('emailError');
        const passwordError = document.getElementById('passwordError');

        // Validar email
        if (!email) {
            emailError.textContent = 'El correo es requerido';
            isValid = false;
        } else if (!this.isValidEmail(email)) {
            emailError.textContent = 'Formato de correo inválido';
            isValid = false;
        } else {
            emailError.textContent = '';
        }

        // Validar contraseña
        if (!password) {
            passwordError.textContent = 'La contraseña es requerida';
            isValid = false;
        } else if (password.length < 6) {
            passwordError.textContent = 'La contraseña debe tener mínimo 6 caracteres';
            isValid = false;
        } else {
            passwordError.textContent = '';
        }

        return isValid;
    }

    /**
     * Valida el formato del email
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Alterna la visibilidad de la contraseña
     */
    togglePasswordVisibility(e) {
        e.preventDefault();
        const isPassword = this.passwordInput.type === 'password';
        this.passwordInput.type = isPassword ? 'text' : 'password';
        this.togglePasswordButton.textContent = isPassword ? '🙈' : '👁️';
    }

    /**
     * Cambia el estado del botón de login
     */
    setLoginButtonLoading(isLoading) {
        this.loginButton.disabled = isLoading;
        const buttonText = document.querySelector('.btn-text');
        const buttonLoader = document.querySelector('.btn-loader');
        
        if (isLoading) {
            buttonText.style.display = 'none';
            buttonLoader.style.display = 'inline-block';
        } else {
            buttonText.style.display = 'inline-block';
            buttonLoader.style.display = 'none';
        }
    }

    /**
     * Muestra mensaje de error
     */
    showErrorMessage(message) {
        const errorDiv = document.getElementById('generalError');
        errorDiv.textContent = '❌ ' + message;
        errorDiv.style.display = 'block';
    }

    /**
     * Muestra mensaje de éxito
     */
    showSuccessMessage(message) {
        const successDiv = document.getElementById('successMessage');
        successDiv.textContent = '✅ ' + message;
        successDiv.style.display = 'block';
    }

    /**
     * Limpia todos los mensajes
     */
    clearMessages() {
        document.getElementById('generalError').style.display = 'none';
        document.getElementById('successMessage').style.display = 'none';
    }

    /**
     * Obtiene el token del almacenamiento
     */
    getToken() {
        return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    }

    /**
     * Verifica si el token es válido
     */
    isTokenValid(token) {
        try {
            // Aquí puedes decodificar y verificar el JWT si es necesario
            return !!token && token.length > 0;
        } catch (e) {
            return false;
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});
