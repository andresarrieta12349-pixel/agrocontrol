/**
 * AGROCONTROL PRO - Funciones de Utilidad
 * Funciones reutilizables para el frontend
 */

/**
 * Formatea un número como moneda
 */
function formatCurrency(value, currency = 'USD', locale = 'es-CO') {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Formatea una fecha
 */
function formatDate(dateString, locale = 'es-CO') {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

/**
 * Formatea una fecha y hora
 */
function formatDateTime(dateString, locale = 'es-CO') {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Escapa caracteres HTML para prevenir XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Valida un email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Valida una URL
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Valida que un campo no esté vacío
 */
function isNotEmpty(value) {
    return value && value.trim().length > 0;
}

/**
 * Valida que un número sea positivo
 */
function isPositiveNumber(value) {
    return !isNaN(value) && value > 0;
}

/**
 * Obtiene un parámetro de la URL
 */
function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

/**
 * Copia un texto al portapapeles
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('Error al copiar:', error);
        return false;
    }
}

/**
 * Descarga un archivo
 */
function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

/**
 * Exporta datos a CSV
 */
function exportToCSV(data, filename = 'datos.csv') {
    if (!data || data.length === 0) {
        alert('No hay datos para exportar');
        return;
    }

    // Obtener headers
    const headers = Object.keys(data[0]);
    
    // Crear contenido CSV
    let csv = headers.join(',') + '\n';
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // Escapar comillas y envolver en comillas si contiene coma
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csv += values.join(',') + '\n';
    });

    downloadFile(csv, filename, 'text/csv');
}

/**
 * Exporta datos a JSON
 */
function exportToJSON(data, filename = 'datos.json') {
    const json = JSON.stringify(data, null, 2);
    downloadFile(json, filename, 'application/json');
}

/**
 * Calcula el tiempo transcurrido desde una fecha
 */
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Hace unos segundos';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)} minutos`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)} horas`;
    if (seconds < 2592000) return `Hace ${Math.floor(seconds / 86400)} días`;
    if (seconds < 31536000) return `Hace ${Math.floor(seconds / 2592000)} meses`;
    return `Hace ${Math.floor(seconds / 31536000)} años`;
}

/**
 * Calcula el porcentaje
 */
function calculatePercentage(part, total) {
    if (total === 0) return 0;
    return Math.round((part / total) * 100);
}

/**
 * Genera un UUID v4
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0,
            v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Debounce - Ejecuta una función después de que ha dejado de ser llamada
 */
function debounce(func, wait = 300) {
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

/**
 * Throttle - Ejecuta una función como máximo una vez cada X milisegundos
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Muestra una notificación toast
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 16px 24px;
        background-color: ${getToastColor(type)};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        font-weight: 500;
        animation: slideInUp 300ms ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutDown 300ms ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Obtiene el color del toast según el tipo
 */
function getToastColor(type) {
    const colors = {
        success: '#2e7d32',
        error: '#c62828',
        warning: '#f57c00',
        info: '#0288d1'
    };
    return colors[type] || colors.info;
}

/**
 * Validación de formulario simple
 */
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input, textarea, select');
    let isValid = true;
    const errors = {};

    inputs.forEach(input => {
        if (!input.value.trim()) {
            errors[input.name] = 'Este campo es requerido';
            isValid = false;
        }

        // Validación de email
        if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
            errors[input.name] = 'Email inválido';
            isValid = false;
        }

        // Validación de número
        if (input.type === 'number' && input.value && isNaN(input.value)) {
            errors[input.name] = 'Debe ser un número';
            isValid = false;
        }
    });

    return { isValid, errors };
}

/**
 * Agrupa un array por una propiedad
 */
function groupBy(array, property) {
    return array.reduce((groups, item) => {
        const key = item[property];
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(item);
        return groups;
    }, {});
}

/**
 * Ordena un array de objetos
 */
function sortBy(array, property, ascending = true) {
    return [...array].sort((a, b) => {
        if (a[property] < b[property]) return ascending ? -1 : 1;
        if (a[property] > b[property]) return ascending ? 1 : -1;
        return 0;
    });
}

/**
 * Filtra un array de objetos por múltiples criterios
 */
function filterBy(array, criteria) {
    return array.filter(item => {
        return Object.entries(criteria).every(([key, value]) => {
            if (Array.isArray(value)) {
                return value.includes(item[key]);
            }
            return item[key] === value;
        });
    });
}

// Agregar estilos de animación
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            transform: translateY(100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes slideOutDown {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(100%);
            opacity: 0;
        }
    }
`;
if (document.head) {
    document.head.appendChild(style);
}
