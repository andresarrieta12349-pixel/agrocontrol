/**
 * AGROCONTROL PRO - Gestión de Ganado
 * Maneja CRUD de animales con tabla dinámica
 */

class LivestockManager {
    constructor() {
        this.baseUrl = 'http://localhost:3000/api/livestock';
        this.form = document.getElementById('livestockForm');
        this.tableBody = document.getElementById('livestockTableBody');
        this.searchInput = document.getElementById('searchInput');
        this.recordCountElement = document.getElementById('recordCount');
        this.animals = [];

        this.initializeEventListeners();
        this.loadAnimals();
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
            id_animal: document.getElementById('id_animal').value.trim(),
            nombre_animal: document.getElementById('nombre_animal').value.trim(),
            tipo_animal: document.getElementById('tipo_animal').value,
            raza: document.getElementById('raza').value.trim(),
            sexo: document.getElementById('sexo').value,
            edad: parseInt(document.getElementById('edad').value),
            peso: parseFloat(document.getElementById('peso').value),
            fecha_nacimiento: document.getElementById('fecha_nacimiento').value,
            estado_salud: document.getElementById('estado_salud').value,
            valor_animal: parseFloat(document.getElementById('valor_animal').value)
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

            if (!response.ok) throw new Error('Error al guardar animal');

            const newAnimal = await response.json();
            this.animals.unshift(newAnimal.data || newAnimal);
            this.renderTable();
            this.form.reset();
            this.showSuccessMessage('✅ Animal guardado correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al guardar el animal');
        }
    }

    /**
     * Carga los animales desde la API
     */
    async loadAnimals() {
        try {
            const token = this.getToken();
            const response = await fetch(this.baseUrl, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al cargar animales');

            const data = await response.json();
            this.animals = data.data || data || [];
            this.renderTable();

        } catch (error) {
            console.error('Error al cargar animales:', error);
            // Cargar datos de demostración si hay error
            this.loadDemoData();
        }
    }

    /**
     * Carga datos de demostración
     */
    loadDemoData() {
        this.animals = [
            {
                id: 1,
                id_animal: 'BOV-001',
                nombre_animal: 'Bessie',
                tipo_animal: 'bovino',
                raza: 'Holstein',
                sexo: 'hembra',
                edad: 48,
                peso: 550,
                fecha_nacimiento: '2020-01-15',
                estado_salud: 'excelente',
                valor_animal: 2500
            },
            {
                id: 2,
                id_animal: 'BOV-002',
                nombre_animal: 'Bruno',
                tipo_animal: 'bovino',
                raza: 'Angus',
                sexo: 'macho',
                edad: 36,
                peso: 700,
                fecha_nacimiento: '2021-06-20',
                estado_salud: 'bueno',
                valor_animal: 3000
            }
        ];
        this.renderTable();
    }

    /**
     * Renderiza la tabla de animales
     */
    renderTable() {
        this.tableBody.innerHTML = '';

        if (this.animals.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 20px; color: #999;">No hay animales registrados</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        this.animals.forEach((animal, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${animal.id_animal}</td>
                <td>${this.escapeHtml(animal.nombre_animal)}</td>
                <td><span class="badge badge-${animal.tipo_animal}">${this.getTipoBadge(animal.tipo_animal)}</span></td>
                <td>${this.escapeHtml(animal.raza)}</td>
                <td>${animal.sexo === 'macho' ? '♂️ Macho' : '♀️ Hembra'}</td>
                <td>${animal.edad}</td>
                <td>${animal.peso}</td>
                <td>${animal.fecha_nacimiento}</td>
                <td><span class="badge badge-${this.getSaludClass(animal.estado_salud)}">${this.getSaludBadge(animal.estado_salud)}</span></td>
                <td>$${animal.valor_animal.toFixed(2)}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="livestockManager.editAnimal(${animal.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="livestockManager.deleteAnimal(${animal.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(this.animals.length);
    }

    /**
     * Maneja la búsqueda
     */
    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        const filtrados = this.animals.filter(animal =>
            animal.id_animal.toLowerCase().includes(query) ||
            animal.nombre_animal.toLowerCase().includes(query) ||
            animal.raza.toLowerCase().includes(query) ||
            animal.tipo_animal.toLowerCase().includes(query)
        );

        this.tableBody.innerHTML = '';
        if (filtrados.length === 0) {
            this.tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; padding: 20px; color: #999;">No se encontraron resultados</td></tr>';
            this.updateRecordCount(0);
            return;
        }

        filtrados.forEach((animal, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${animal.id_animal}</td>
                <td>${this.escapeHtml(animal.nombre_animal)}</td>
                <td><span class="badge badge-${animal.tipo_animal}">${this.getTipoBadge(animal.tipo_animal)}</span></td>
                <td>${this.escapeHtml(animal.raza)}</td>
                <td>${animal.sexo === 'macho' ? '♂️ Macho' : '♀️ Hembra'}</td>
                <td>${animal.edad}</td>
                <td>${animal.peso}</td>
                <td>${animal.fecha_nacimiento}</td>
                <td><span class="badge badge-${this.getSaludClass(animal.estado_salud)}">${this.getSaludBadge(animal.estado_salud)}</span></td>
                <td>$${animal.valor_animal.toFixed(2)}</td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-edit btn-small" onclick="livestockManager.editAnimal(${animal.id})">✏️ Editar</button>
                        <button class="btn btn-delete btn-small" onclick="livestockManager.deleteAnimal(${animal.id})">🗑️ Eliminar</button>
                    </div>
                </td>
            `;
            this.tableBody.appendChild(row);
        });

        this.updateRecordCount(filtrados.length);
    }

    /**
     * Edita un animal (placeholder)
     */
    editAnimal(id) {
        alert('Funcionalidad de edición próximamente');
    }

    /**
     * Elimina un animal
     */
    async deleteAnimal(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este animal?')) return;

        try {
            const token = this.getToken();
            const response = await fetch(`${this.baseUrl}/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) throw new Error('Error al eliminar');

            this.animals = this.animals.filter(a => a.id !== id);
            this.renderTable();
            this.showSuccessMessage('✅ Animal eliminado correctamente');

        } catch (error) {
            console.error('Error:', error);
            this.showErrorMessage('Error al eliminar el animal');
        }
    }

    /**
     * Valida los datos del formulario
     */
    validateFormData(data) {
        if (!data.id_animal || !data.tipo_animal || !data.raza || !data.sexo || !data.edad || !data.peso || !data.fecha_nacimiento || !data.estado_salud || !data.valor_animal) {
            this.showErrorMessage('Por favor completa todos los campos obligatorios');
            return false;
        }

        if (data.edad < 0 || data.peso <= 0 || data.valor_animal < 0) {
            this.showErrorMessage('Verifica que los valores numéricos sean válidos');
            return false;
        }

        return true;
    }

    /**
     * Obtiene el badge para el tipo de animal
     */
    getTipoBadge(tipo) {
        const badges = {
            'bovino': '🐄 Bovino',
            'porcino': '🐷 Porcino',
            'ovino': '🐑 Ovino',
            'caprino': '🐐 Caprino',
            'equino': '🐴 Equino',
            'ave': '🐔 Ave'
        };
        return badges[tipo] || tipo;
    }

    /**
     * Obtiene el badge de salud
     */
    getSaludBadge(salud) {
        const badges = {
            'excelente': '✅ Excelente',
            'bueno': '👍 Bueno',
            'regular': '⚠️ Regular',
            'enfermo': '🏥 Enfermo'
        };
        return badges[salud] || salud;
    }

    /**
     * Obtiene la clase CSS de salud
     */
    getSaludClass(salud) {
        const classes = {
            'excelente': 'success',
            'bueno': 'info',
            'regular': 'warning',
            'enfermo': 'danger'
        };
        return classes[salud] || 'info';
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
let livestockManager;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    livestockManager = new LivestockManager();
});
