/**
 * AGROCONTROL PRO - Dashboard
 * Maneja la lógica y visualización del dashboard
 */

class DashboardManager {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api';
        this.initializeEventListeners();
        this.loadDashboardData();
    }

    /**
     * Inicializa los event listeners
     */
    initializeEventListeners() {
        // Agregar listeners para botones específicos del dashboard si es necesario
    }

    /**
     * Carga los datos del dashboard desde la API
     */
    async loadDashboardData() {
        try {
            const token = this.getToken();
            
            // Cargar conteos
            await this.loadInsumosCount(token);
            await this.loadGanadeCount(token);
            await this.loadMaquinariaCount(token);
        } catch (error) {
            console.error('Error al cargar datos del dashboard:', error);
            this.showErrorMessage('Error al cargar los datos del dashboard');
        }
    }

    /**
     * Carga el conteo de insumos
     */
    async loadInsumosCount(token) {
        try {
            const response = await fetch(`${this.baseUrl}/insumos/count`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al obtener conteo de insumos');
            
            const data = await response.json();
            const insumosCountElement = document.getElementById('insumosCount');
            if (insumosCountElement) {
                insumosCountElement.textContent = data.count || 0;
            }
        } catch (error) {
            console.error('Error:', error);
            // Mostrar 0 si hay error
            const insumosCountElement = document.getElementById('insumosCount');
            if (insumosCountElement) {
                insumosCountElement.textContent = '0';
            }
        }
    }

    /**
     * Carga el conteo de ganado
     */
    async loadGanadeCount(token) {
        try {
            const response = await fetch(`${this.baseUrl}/livestock/count`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al obtener conteo de ganado');
            
            const data = await response.json();
            const ganadeCountElement = document.getElementById('ganadeCount');
            if (ganadeCountElement) {
                ganadeCountElement.textContent = data.count || 0;
            }
        } catch (error) {
            console.error('Error:', error);
            const ganadeCountElement = document.getElementById('ganadeCount');
            if (ganadeCountElement) {
                ganadeCountElement.textContent = '0';
            }
        }
    }

    /**
     * Carga el conteo de maquinaria
     */
    async loadMaquinariaCount(token) {
        try {
            const response = await fetch(`${this.baseUrl}/machinery/count`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al obtener conteo de maquinaria');
            
            const data = await response.json();
            const maquinariaCountElement = document.getElementById('maquinariaCount');
            if (maquinariaCountElement) {
                maquinariaCountElement.textContent = data.count || 0;
            }
        } catch (error) {
            console.error('Error:', error);
            const maquinariaCountElement = document.getElementById('maquinariaCount');
            if (maquinariaCountElement) {
                maquinariaCountElement.textContent = '0';
            }
        }
    }

    /**
     * Obtiene el token del almacenamiento
     */
    getToken() {
        return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    }

    /**
     * Muestra mensaje de error
     */
    showErrorMessage(message) {
        console.error(message);
        // Aquí puedes implementar una notificación visual si lo deseas
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});
