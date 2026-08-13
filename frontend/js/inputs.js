/**
 * AGROCONTROL PRO - Gestión de Insumos
 * Maneja CRUD de insumos con tabla dinámica
 */

class InsumosManager {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api/insumos';
        this.form = document.getElementById('insumosForm');
        this.tableBody = document.getElementById('insumosTableBody');
        this.searchInput = document.getElementById('searchInput');
        this.recordCountElement = document.getElementById('recordCount');
        this.insumos = [];

        this.initializeEventListeners();
        this.loadInsumos();
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
            nombre: document.getElementById('nombre').value.trim(),
            tipo: document.getElementById('tipo').value,
            cantidad: parseFloat(document.getElementById('cantidad').value),
            unidad: document.getElementById('unidad').value,
            precio: parseFloat(document.getElementById('precio').value),
            fecha: document.getElementById('fecha').value,
            proveedor: document.getElementById('proveedor').value.trim(),
            lote: document.getElementById('lote').value.trim()
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

            if (!response.ok) throw new Error('Error al guardar insumo');

            const newInsumo = await response.json();
            this.insumos.unshift(newInsumo.data || newInsumo);
            this.renderTable();
            this.form.reset();
            this.showSuccessMessage('✅ Insumo guardado correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al guardar el insumo');
        }
    }

    /**
     * Carga los insumos desde la API
     */
    async loadInsumos() {
        try {
            const token = this.getToken();
            const response = await fetch(this.baseUrl, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al cargar insumos');

            const data = await response.json();
            this.insumos = data.data || data || [];
            this.renderTable();

        } catch (error) {
            console.error('Error al cargar insumos:', error);
            // Cargar datos de demostración si hay error
            this.loadDemoData();
        }
    }

    /**
     * Carga datos de demostración
     */
    loadDemoData() {
        this.insumos = [
            {
                id: 1,
                nombre: 'Fertilizante NPK 15-15-15',
                tipo: 'fertilizante',
                cantidad: 500,
                unidad: 'kg',
                precio: 45.50,
                fecha: new Date().toISOString().split('T')[0],
                proveedor: 'Agrícola Express',
                lote: 'LOTE-2024-001'
            },
            {
                id: 2,
                nombre: 'Pesticida Orgánico',
                tipo: 'pesticida',
                cantidad: 100,
                unidad: 'lt',
                precio: 120.00,
                fecha: new Date().toISOString().split('T')[0],
                proveedor: 'BioControl S.A.',
                lote: 'LOTE-2024-002'
            }
        ];
        this.renderTable();
    }

    /**
     * Renderiza la tabla de insumos
     */
    renderTable() {
        this.tableBody.innerHTML = '';

        if (this.insumos.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px; color: #999;">No hay insumos registrados</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        this.insumos.forEach((insumo, index) => {
            const total = (insumo.cantidad * insumo.precio).toFixed(2);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${insumo.id || index + 1}</td>
                <td>${this.escapeHtml(insumo.nombre)}</td>
                <td><span class="badge badge-${insumo.tipo}">${this.getTipoBadge(insumo.tipo)}</span></td>
                <td>${insumo.cantidad}</td>
                <td>${insumo.unidad}</td>
                <td>$${insumo.precio.toFixed(2)}</td>
                <td>$${total}</td>
                <td>${this.escapeHtml(insumo.proveedor)}</td>
                <td>${insumo.fecha}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="insumosManager.editInsumo(${insumo.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="insumosManager.deleteInsumo(${insumo.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(this.insumos.length);
    }

    /**
     * Maneja la búsqueda
     */
    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        const filtrados = this.insumos.filter(insumo =>
            insumo.nombre.toLowerCase().includes(query) ||
            insumo.proveedor.toLowerCase().includes(query) ||
            insumo.tipo.toLowerCase().includes(query)
        );

        this.tableBody.innerHTML = '';
        if (filtrados.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px; color: #999;">No se encontraron resultados</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        filtrados.forEach((insumo, index) => {
            const total = (insumo.cantidad * insumo.precio).toFixed(2);
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${insumo.id || index + 1}</td>
                <td>${this.escapeHtml(insumo.nombre)}</td>
                <td><span class="badge badge-${insumo.tipo}">${this.getTipoBadge(insumo.tipo)}</span></td>
                <td>${insumo.cantidad}</td>
                <td>${insumo.unidad}</td>
                <td>$${insumo.precio.toFixed(2)}</td>
                <td>$${total}</td>
                <td>${this.escapeHtml(insumo.proveedor)}</td>
                <td>${insumo.fecha}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="insumosManager.editInsumo(${insumo.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="insumosManager.deleteInsumo(${insumo.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(filtrados.length);
    }

    /**
     * Edita un insumo (placeholder)
     */
    editInsumo(id) {
        alert('Funcionalidad de edición próximamente');
    }

    /**
     * Elimina un insumo
     */
    async deleteInsumo(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este insumo?')) return;

        try {
            const token = this.getToken();
            const response = await fetch(`${this.baseUrl}/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al eliminar');

            this.insumos = this.insumos.filter(i => i.id !== id);
            this.renderTable();
            this.showSuccessMessage('✅ Insumo eliminado correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al eliminar el insumo');
        }
    }

    /**
     * Valida los datos del formulario
     */
    validateFormData(data) {
        if (!data.nombre || !data.tipo || !data.cantidad || !data.unidad || !data.precio || !data.fecha || !data.proveedor) {
            this.showErrorMessage('Por favor completa todos los campos obligatorios');
            return false;
        }

        if (data.cantidad <= 0 || data.precio <= 0) {
            this.showErrorMessage('La cantidad y precio deben ser mayores a 0');
            return false;
        }

        return true;
    }

    /**
     * Obtiene el badge para el tipo de insumo
     */
    getTipoBadge(tipo) {
        const badges = {
            'fertilizante': '🌱 Fertilizante',
            'pesticida': '🐛 Pesticida',
            'fungicida': '🍄 Fungicida',
            'herbicida': '🌿 Herbicida',
            'semilla': '🌾 Semilla',
            'otro': '📦 Otro'
        };
        return badges[tipo] || tipo;
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
        // Implementar notificación visual si lo deseas
    }

    /**
     * Muestra mensaje de error
     */
    showErrorMessage(message) {
        alert(message);
    }
}

// Variable global para acceso desde HTML
let insumosManager;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    insumosManager = new InsumosManager();
});
