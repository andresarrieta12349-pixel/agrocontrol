/**
 * AGROCONTROL PRO - Gestión de Maquinaria
 * Maneja CRUD de equipos con tabla dinámica
 */

class MachineryManager {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api/machinery';
        this.form = document.getElementById('machineryForm');
        this.tableBody = document.getElementById('machineryTableBody');
        this.searchInput = document.getElementById('searchInput');
        this.recordCountElement = document.getElementById('recordCount');
        this.machinery = [];

        this.initializeEventListeners();
        this.loadMachinery();
    }

    /**
     * Inicializa los event listeners
     */
    initializeEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }

    /**
     * Maneja el envío del formulario
     */
    async handleFormSubmit(e) {
        e.preventDefault();

        // Recopilar datos del formulario
        const formData = {
            codigo_equipo: document.getElementById('codigo_equipo').value.trim(),
            nombre_equipo: document.getElementById('nombre_equipo').value.trim(),
            tipo_equipo: document.getElementById('tipo_equipo').value,
            marca: document.getElementById('marca').value.trim(),
            modelo: document.getElementById('modelo').value.trim(),
            anno_fabricacion: parseInt(document.getElementById('anno_fabricacion').value),
            serie: document.getElementById('serie').value.trim(),
            estado: document.getElementById('estado').value,
            horas_trabajo: parseInt(document.getElementById('horas_trabajo').value),
            valor_adquisicion: parseFloat(document.getElementById('valor_adquisicion').value),
            fecha_adquisicion: document.getElementById('fecha_adquisicion').value,
            proxima_revision: document.getElementById('proxima_revision').value
        };

        // Validar
        if (!this.validateFormData(formData)) {
            return;
        }

        try {
            const token = this.getToken();
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Error al guardar maquinaria');

            const newEquipo = await response.json();
            this.machinery.unshift(newEquipo.data || newEquipo);
            this.renderTable();
            this.form.reset();
            this.showSuccessMessage('✅ Maquinaria guardada correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al guardar la maquinaria');
        }
    }

    /**
     * Carga la maquinaria desde la API
     */
    async loadMachinery() {
        try {
            const token = this.getToken();
            const response = await fetch(this.baseUrl, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al cargar maquinaria');

            const data = await response.json();
            this.machinery = data.data || data || [];
            this.renderTable();

        } catch (error) {
            console.error('Error al cargar maquinaria:', error);
            // Cargar datos de demostración si hay error
            this.loadDemoData();
        }
    }

    /**
     * Carga datos de demostración
     */
    loadDemoData() {
        this.machinery = [
            {
                id: 1,
                codigo_equipo: 'MAQ-001',
                nombre_equipo: 'Tractor John Deere',
                tipo_equipo: 'tractor',
                marca: 'John Deere',
                modelo: '5075E',
                anno_fabricacion: 2022,
                serie: 'JD123456789',
                estado: 'excelente',
                horas_trabajo: 1250,
                valor_adquisicion: 55000,
                fecha_adquisicion: '2022-03-15',
                proxima_revision: '2025-03-15'
            },
            {
                id: 2,
                codigo_equipo: 'MAQ-002',
                nombre_equipo: 'Cosechadora CLAAS',
                tipo_equipo: 'cosechadora',
                marca: 'CLAAS',
                modelo: 'Lexion 580',
                anno_fabricacion: 2021,
                serie: 'CL987654321',
                estado: 'bueno',
                horas_trabajo: 850,
                valor_adquisicion: 85000,
                fecha_adquisicion: '2021-06-20',
                proxima_revision: '2025-06-20'
            }
        ];
        this.renderTable();
    }

    /**
     * Renderiza la tabla de maquinaria
     */
    renderTable() {
        this.tableBody.innerHTML = '';

        if (this.machinery.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 20px; color: #999;">No hay maquinaria registrada</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        this.machinery.forEach((equipo, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.escapeHtml(equipo.codigo_equipo)}</td>
                <td>${this.escapeHtml(equipo.nombre_equipo)}</td>
                <td><span class="badge badge-${equipo.tipo_equipo}">${this.getTipoBadge(equipo.tipo_equipo)}</span></td>
                <td>${this.escapeHtml(equipo.marca)}</td>
                <td>${this.escapeHtml(equipo.modelo)}</td>
                <td>${equipo.anno_fabricacion}</td>
                <td><span class="badge badge-${this.getEstadoClass(equipo.estado)}">${this.getEstadoBadge(equipo.estado)}</span></td>
                <td>${equipo.horas_trabajo}</td>
                <td>$${equipo.valor_adquisicion.toFixed(2)}</td>
                <td>${equipo.proxima_revision}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="machineryManager.editEquipo(${equipo.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="machineryManager.deleteEquipo(${equipo.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(this.machinery.length);
    }

    /**
     * Maneja la búsqueda
     */
    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        const filtrados = this.machinery.filter(equipo =>
            equipo.codigo_equipo.toLowerCase().includes(query) ||
            equipo.nombre_equipo.toLowerCase().includes(query) ||
            equipo.marca.toLowerCase().includes(query) ||
            equipo.modelo.toLowerCase().includes(query) ||
            equipo.tipo_equipo.toLowerCase().includes(query)
        );

        this.tableBody.innerHTML = '';
        if (filtrados.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 20px; color: #999;">No se encontraron resultados</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        filtrados.forEach((equipo, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.escapeHtml(equipo.codigo_equipo)}</td>
                <td>${this.escapeHtml(equipo.nombre_equipo)}</td>
                <td><span class="badge badge-${equipo.tipo_equipo}">${this.getTipoBadge(equipo.tipo_equipo)}</span></td>
                <td>${this.escapeHtml(equipo.marca)}</td>
                <td>${this.escapeHtml(equipo.modelo)}</td>
                <td>${equipo.anno_fabricacion}</td>
                <td><span class="badge badge-${this.getEstadoClass(equipo.estado)}">${this.getEstadoBadge(equipo.estado)}</span></td>
                <td>${equipo.horas_trabajo}</td>
                <td>$${equipo.valor_adquisicion.toFixed(2)}</td>
                <td>${equipo.proxima_revision}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="machineryManager.editEquipo(${equipo.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="machineryManager.deleteEquipo(${equipo.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(filtrados.length);
    }

    /**
     * Edita un equipo (placeholder)
     */
    editEquipo(id) {
        alert('Funcionalidad de edición próximamente');
    }

    /**
     * Elimina un equipo
     */
    async deleteEquipo(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar esta maquinaria?')) return;

        try {
            const token = this.getToken();
            const response = await fetch(`${this.baseUrl}/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al eliminar');

            this.machinery = this.machinery.filter(m => m.id !== id);
            this.renderTable();
            this.showSuccessMessage('✅ Maquinaria eliminada correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al eliminar la maquinaria');
        }
    }

    /**
     * Valida los datos del formulario
     */
    validateFormData(data) {
        if (!data.codigo_equipo || !data.nombre_equipo || !data.tipo_equipo || !data.marca || !data.modelo || !data.anno_fabricacion || !data.serie || !data.estado || !data.fecha_adquisicion || !data.proxima_revision) {
            this.showErrorMessage('Por favor completa todos los campos obligatorios');
            return false;
        }

        if (data.horas_trabajo < 0 || data.valor_adquisicion < 0) {
            this.showErrorMessage('Las horas y valor deben ser números válidos');
            return false;
        }

        if (data.anno_fabricacion < 1900 || data.anno_fabricacion > new Date().getFullYear()) {
            this.showErrorMessage('El año de fabricación no es válido');
            return false;
        }

        return true;
    }

    /**
     * Obtiene el badge para el tipo de equipo
     */
    getTipoBadge(tipo) {
        const badges = {
            'tractor': '🚜 Tractor',
            'cosechadora': '🌾 Cosechadora',
            'arado': '🔧 Arado',
            'sembradora': '🌱 Sembradora',
            'pulverizador': '💨 Pulverizador',
            'rastrillo': '🧹 Rastrillo',
            'otro': '⚙️ Otro'
        };
        return badges[tipo] || tipo;
    }

    /**
     * Obtiene el badge de estado
     */
    getEstadoBadge(estado) {
        const badges = {
            'excelente': '✅ Excelente',
            'bueno': '👍 Bueno',
            'regular': '⚠️ Regular',
            'mantenimiento': '🔧 Mantenimiento',
            'inoperativo': '❌ Inoperativo'
        };
        return badges[estado] || estado;
    }

    /**
     * Obtiene la clase CSS de estado
     */
    getEstadoClass(estado) {
        const classes = {
            'excelente': 'success',
            'bueno': 'info',
            'regular': 'warning',
            'mantenimiento': 'warning',
            'inoperativo': 'danger'
        };
        return classes[estado] || 'info';
    }

    /**
     * Escapa caracteres HTML
     */
    escapeHtml(text) {
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
     * Actualiza el contador de registros
     */
    updateRecordCount(count) {
        if (this.recordCountElement) {
            this.recordCountElement.textContent = `Total de registros: ${count}`;
        }
    }

    /**
     * Obtiene el token
     */
    getToken() {
        return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    }

    /**
     * Muestra mensaje de éxito
     */
    showSuccessMessage(message) {
        console.log(message);
    }

    /**
     * Muestra mensaje de error
     */
    showErrorMessage(message) {
        alert(message);
    }
}

// Variable global para acceso desde HTML
let machineryManager;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    machineryManager = new MachineryManager();
});
