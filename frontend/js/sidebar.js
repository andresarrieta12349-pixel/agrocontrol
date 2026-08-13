/**
 * AGROCONTROL PRO - Gestión del Sidebar
 * Maneja la interactividad y estado del sidebar
 */

class SidebarManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.userName = document.getElementById('userName');

        this.initializeEventListeners();
        this.loadUserData();
        this.checkAuthentication();
    }

    /**
     * Inicializa los event listeners
     */
    initializeEventListeners() {
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.logoutBtn) {
            this.logoutBtn.addEventListener('click', () => this.logout());
        }

        // Cerrar sidebar al hacer clic en un enlace (en dispositivos móviles)
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 768) {
                    this.closeSidebar();
                }
            });
        });
    }

    /**
     * Alterna el sidebar entre abierto y cerrado
     */
    toggleSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('collapsed');
            const isCollapsed = this.sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        }
    }

    /**
     * Cierra el sidebar
     */
    closeSidebar() {
        if (this.sidebar && !this.sidebar.classList.contains('collapsed')) {
            this.sidebar.classList.add('collapsed');
            localStorage.setItem('sidebarCollapsed', true);
        }
    }

    /**
     * Abre el sidebar
     */
    openSidebar() {
        if (this.sidebar && this.sidebar.classList.contains('collapsed')) {
            this.sidebar.classList.remove('collapsed');
            localStorage.setItem('sidebarCollapsed', false);
        }
    }

    /**
     * Carga el estado del sidebar desde localStorage
     */
    loadSidebarState() {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed && this.sidebar) {
            this.sidebar.classList.add('collapsed');
        }
    }

    /**
     * Carga los datos del usuario
     */
    loadUserData() {
        try {
            const userData = localStorage.getItem('userData');
            if (userData) {
                const user = JSON.parse(userData);
                if (this.userName && user.name) {
                    this.userName.textContent = user.name.split(' ')[0]; // Mostrar solo el primer nombre
                }
            }
        } catch (error) {
            console.error('Error al cargar datos del usuario:', error);
        }
    }

    /**
     * Verifica si el usuario está autenticado
     */
    checkAuthentication() {
        const token = this.getToken();
        if (!token || !this.isTokenValid(token)) {
            this.redirectToLogin();
        }
    }

    /**
     * Cierra sesión del usuario
     */
    logout() {
        // Confirmar antes de cerrar sesión
        if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
            // Limpiar almacenamiento
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
            sessionStorage.removeItem('authToken');

            // Mostrar mensaje y redirigir
            this.showNotification('Sesión cerrada correctamente', 'success');
            
            setTimeout(() => {
                window.location.href = '../../index.html';
            }, 1500);
        }
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
            return !!token && token.length > 0;
        } catch (e) {
            return false;
        }
    }

    /**
     * Redirige al login si no está autenticado
     */
    redirectToLogin() {
        window.location.href = '../../index.html';
    }

    /**
     * Muestra una notificación al usuario
     */
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background-color: ${type === 'success' ? '#2e7d32' : '#0288d1'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            font-weight: 500;
            animation: slideIn 300ms ease-out;
        `;

        document.body.appendChild(notification);

        // Eliminar después de 3 segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * Marca el elemento de navegación activo
     */
    setActiveNavItem() {
        const currentUrl = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link && link.href.includes(currentUrl.split('/').pop())) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
}

// Agregar estilos de animación al documento
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const sidebarManager = new SidebarManager();
    sidebarManager.loadSidebarState();
    sidebarManager.setActiveNavItem();

    // Manejar cambios de tamaño de ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebarManager.sidebar) {
            sidebarManager.openSidebar();
        }
    });
});
