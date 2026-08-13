/**
 * AGROCONTROL PRO - Cliente API
 * Gestiona todas las llamadas HTTP a la API backend
 */

class APIClient {
    constructor(baseUrl = 'http://localhost:3000/api') {
        this.baseUrl = baseUrl;
        this.timeout = 10000; // 10 segundos
    }

    /**
     * Realiza una petición GET
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'GET'
        });
    }

    /**
     * Realiza una petición POST
     */
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Realiza una petición PUT
     */
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * Realiza una petición DELETE
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'DELETE'
        });
    }

    /**
     * Realiza una petición genérica
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };

        // Agregar token de autenticación si está disponible
        const token = this.getToken();
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...finalOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            // Manejar respuesta
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    errorData.message || `HTTP ${response.status}`,
                    response.status,
                    errorData
                );
            }

            const data = await response.json();
            return { success: true, data };

        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            if (error.name === 'AbortError') {
                throw new APIError('La petición tardó demasiado tiempo', 0, null);
            }

            throw new APIError(error.message || 'Error desconocido', 0, null);
        }
    }

    /**
     * Obtiene el token de autenticación
     */
    getToken() {
        return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    }

    /**
     * Establece el token de autenticación
     */
    setToken(token) {
        localStorage.setItem('authToken', token);
    }

    /**
     * Limpia el token de autenticación
     */
    clearToken() {
        localStorage.removeItem('authToken');
        sessionStorage.removeItem('authToken');
    }
}

/**
 * Clase personalizada para errores de API
 */
class APIError extends Error {
    constructor(message, status = 0, data = null) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// Crear instancia global del cliente API
const apiClient = new APIClient();

// ========================================
// ENDPOINTS ESPECÍFICOS
// ========================================

/**
 * Autenticación
 */
const AuthAPI = {
    login: (email, password) => apiClient.post('/auth/login', { email, password }),
    logout: () => apiClient.post('/auth/logout', {}),
    refresh: () => apiClient.post('/auth/refresh', {}),
    verifyToken: () => apiClient.get('/auth/verify')
};

/**
 * Insumos
 */
const InsumosAPI = {
    getAll: () => apiClient.get('/insumos'),
    getById: (id) => apiClient.get(`/insumos/${id}`),
    create: (data) => apiClient.post('/insumos', data),
    update: (id, data) => apiClient.put(`/insumos/${id}`, data),
    delete: (id) => apiClient.delete(`/insumos/${id}`),
    getCount: () => apiClient.get('/insumos/count')
};

/**
 * Ganado
 */
const LivestockAPI = {
    getAll: () => apiClient.get('/livestock'),
    getById: (id) => apiClient.get(`/livestock/${id}`),
    create: (data) => apiClient.post('/livestock', data),
    update: (id, data) => apiClient.put(`/livestock/${id}`, data),
    delete: (id) => apiClient.delete(`/livestock/${id}`),
    getCount: () => apiClient.get('/livestock/count')
};

/**
 * Maquinaria
 */
const MachineryAPI = {
    getAll: () => apiClient.get('/machinery'),
    getById: (id) => apiClient.get(`/machinery/${id}`),
    create: (data) => apiClient.post('/machinery', data),
    update: (id, data) => apiClient.put(`/machinery/${id}`, data),
    delete: (id) => apiClient.delete(`/machinery/${id}`),
    getCount: () => apiClient.get('/machinery/count')
};

/**
 * Usuarios
 */
const UsersAPI = {
    getProfile: () => apiClient.get('/users/profile'),
    updateProfile: (data) => apiClient.put('/users/profile', data),
    changePassword: (currentPassword, newPassword) => 
        apiClient.post('/users/change-password', { currentPassword, newPassword })
};

/**
 * Dashboard
 */
const DashboardAPI = {
    getStats: () => apiClient.get('/dashboard/stats'),
    getRecentActivity: () => apiClient.get('/dashboard/activity')
};
