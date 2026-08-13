/**
 * AGROCONTROL PRO - Validaciones Personalizadas
 * Validaciones específicas del dominio agrícola
 */

/**
 * Validador de Insumos
 */
class InsumosValidator {
    static validate(data) {
        const errors = {};

        // Validar nombre
        if (!data.nombre || data.nombre.trim().length < 3) {
            errors.nombre = 'El nombre debe tener al menos 3 caracteres';
        }

        // Validar tipo
        const tiposValidos = ['fertilizante', 'pesticida', 'fungicida', 'herbicida', 'semilla', 'otro'];
        if (!data.tipo || !tiposValidos.includes(data.tipo)) {
            errors.tipo = 'Tipo de insumo inválido';
        }

        // Validar cantidad
        if (!data.cantidad || data.cantidad <= 0) {
            errors.cantidad = 'La cantidad debe ser mayor a 0';
        }

        // Validar unidad
        const unidadesValidas = ['kg', 'lt', 'u', 'bolsa', 'caneca'];
        if (!data.unidad || !unidadesValidas.includes(data.unidad)) {
            errors.unidad = 'Unidad de medida inválida';
        }

        // Validar precio
        if (!data.precio || data.precio <= 0) {
            errors.precio = 'El precio debe ser mayor a 0';
        }

        // Validar fecha
        if (!data.fecha || !this.isValidDate(data.fecha)) {
            errors.fecha = 'Fecha inválida';
        }

        // Validar proveedor
        if (!data.proveedor || data.proveedor.trim().length < 3) {
            errors.proveedor = 'El proveedor debe tener al menos 3 caracteres';
        }

        return Object.keys(errors).length === 0 ? { valid: true } : { valid: false, errors };
    }

    static isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }
}

/**
 * Validador de Ganado
 */
class LivestockValidator {
    static validate(data) {
        const errors = {};

        // Validar ID del animal
        if (!data.id_animal || data.id_animal.trim().length < 2) {
            errors.id_animal = 'El ID del animal es requerido';
        }

        // Validar tipo de animal
        const tiposValidos = ['bovino', 'porcino', 'ovino', 'caprino', 'equino', 'ave'];
        if (!data.tipo_animal || !tiposValidos.includes(data.tipo_animal)) {
            errors.tipo_animal = 'Tipo de animal inválido';
        }

        // Validar raza
        if (!data.raza || data.raza.trim().length < 2) {
            errors.raza = 'La raza es requerida';
        }

        // Validar sexo
        if (!data.sexo || !['macho', 'hembra'].includes(data.sexo)) {
            errors.sexo = 'Sexo inválido';
        }

        // Validar edad
        if (data.edad === null || data.edad === undefined || data.edad < 0) {
            errors.edad = 'La edad debe ser un número válido';
        }

        // Validar peso
        if (!data.peso || data.peso <= 0) {
            errors.peso = 'El peso debe ser mayor a 0';
        }

        // Validar fecha de nacimiento
        if (!data.fecha_nacimiento || !this.isValidDate(data.fecha_nacimiento)) {
            errors.fecha_nacimiento = 'Fecha de nacimiento inválida';
        } else if (new Date(data.fecha_nacimiento) > new Date()) {
            errors.fecha_nacimiento = 'La fecha de nacimiento no puede ser en el futuro';
        }

        // Validar estado de salud
        const estadosValidos = ['excelente', 'bueno', 'regular', 'enfermo'];
        if (!data.estado_salud || !estadosValidos.includes(data.estado_salud)) {
            errors.estado_salud = 'Estado de salud inválido';
        }

        // Validar valor
        if (!data.valor_animal || data.valor_animal < 0) {
            errors.valor_animal = 'El valor del animal debe ser válido';
        }

        return Object.keys(errors).length === 0 ? { valid: true } : { valid: false, errors };
    }

    static isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    /**
     * Valida la consistencia de edad y fecha de nacimiento
     */
    static validateAgeConsistency(edad, fechaNacimiento) {
        const birthDate = new Date(fechaNacimiento);
        const today = new Date();
        const calculatedAge = Math.floor((today - birthDate) / (365.25 * 24 * 60 * 60 * 1000));
        
        // Permitir una diferencia de hasta 1 mes
        return Math.abs(calculatedAge - edad) <= 1;
    }
}

/**
 * Validador de Maquinaria
 */
class MachineryValidator {
    static validate(data) {
        const errors = {};

        // Validar código
        if (!data.codigo_equipo || data.codigo_equipo.trim().length < 2) {
            errors.codigo_equipo = 'El código del equipo es requerido';
        }

        // Validar nombre
        if (!data.nombre_equipo || data.nombre_equipo.trim().length < 3) {
            errors.nombre_equipo = 'El nombre debe tener al menos 3 caracteres';
        }

        // Validar tipo
        const tiposValidos = ['tractor', 'cosechadora', 'arado', 'sembradora', 'pulverizador', 'rastrillo', 'otro'];
        if (!data.tipo_equipo || !tiposValidos.includes(data.tipo_equipo)) {
            errors.tipo_equipo = 'Tipo de equipo inválido';
        }

        // Validar marca
        if (!data.marca || data.marca.trim().length < 2) {
            errors.marca = 'La marca es requerida';
        }

        // Validar modelo
        if (!data.modelo || data.modelo.trim().length < 2) {
            errors.modelo = 'El modelo es requerido';
        }

        // Validar año de fabricación
        const currentYear = new Date().getFullYear();
        if (!data.anno_fabricacion || data.anno_fabricacion < 1900 || data.anno_fabricacion > currentYear) {
            errors.anno_fabricacion = `Año debe estar entre 1900 y ${currentYear}`;
        }

        // Validar serie
        if (!data.serie || data.serie.trim().length < 3) {
            errors.serie = 'El número de serie es requerido';
        }

        // Validar estado
        const estadosValidos = ['excelente', 'bueno', 'regular', 'mantenimiento', 'inoperativo'];
        if (!data.estado || !estadosValidos.includes(data.estado)) {
            errors.estado = 'Estado del equipo inválido';
        }

        // Validar horas de trabajo
        if (data.horas_trabajo === null || data.horas_trabajo === undefined || data.horas_trabajo < 0) {
            errors.horas_trabajo = 'Las horas de trabajo deben ser válidas';
        }

        // Validar valor de adquisición
        if (!data.valor_adquisicion || data.valor_adquisicion < 0) {
            errors.valor_adquisicion = 'El valor de adquisición debe ser válido';
        }

        // Validar fecha de adquisición
        if (!data.fecha_adquisicion || !this.isValidDate(data.fecha_adquisicion)) {
            errors.fecha_adquisicion = 'Fecha de adquisición inválida';
        }

        // Validar próxima revisión
        if (!data.proxima_revision || !this.isValidDate(data.proxima_revision)) {
            errors.proxima_revision = 'Fecha de próxima revisión inválida';
        }

        return Object.keys(errors).length === 0 ? { valid: true } : { valid: false, errors };
    }

    static isValidDate(dateString) {
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date);
    }

    /**
     * Verifica si la máquina está cerca de la revisión
     */
    static isReviewDue(proximaRevision, daysThreshold = 30) {
        const revisionDate = new Date(proximaRevision);
        const today = new Date();
        const daysUntilReview = Math.ceil((revisionDate - today) / (1000 * 60 * 60 * 24));
        
        return daysUntilReview <= daysThreshold;
    }

    /**
     * Calcula la depreciación del equipo
     */
    static calculateDepreciation(valorAdquisicion, annoFabricacion, metodo = 'lineal') {
        const currentYear = new Date().getFullYear();
        const yearsInUse = currentYear - annoFabricacion;

        if (metodo === 'lineal') {
            // Depreciación lineal: 10% anual
            const depreciation = valorAdquisicion * 0.10 * yearsInUse;
            return Math.max(valorAdquisicion - depreciation, 0);
        } else if (metodo === 'exponencial') {
            // Depreciación exponencial: 15% anual
            return valorAdquisicion * Math.pow(0.85, yearsInUse);
        }

        return valorAdquisicion;
    }
}

/**
 * Utilidades de Validación General
 */
class ValidationUtils {
    /**
     * Valida un rango de números
     */
    static isInRange(value, min, max) {
        return value >= min && value <= max;
    }

    /**
     * Valida que dos valores sean iguales
     */
    static areEqual(value1, value2) {
        return value1 === value2;
    }

    /**
     * Valida que un valor esté en una lista
     */
    static isInList(value, list) {
        return list.includes(value);
    }

    /**
     * Valida que un string cumpla con un patrón regex
     */
    static matchesPattern(value, pattern) {
        const regex = new RegExp(pattern);
        return regex.test(value);
    }

    /**
     * Obtiene un mensaje de error amigable
     */
    static getFriendlyErrorMessage(error) {
        const messages = {
            'required': 'Este campo es requerido',
            'email': 'Email inválido',
            'min': 'El valor es menor al mínimo permitido',
            'max': 'El valor es mayor al máximo permitido',
            'pattern': 'El formato es inválido',
            'unique': 'Este valor ya existe'
        };

        return messages[error] || error;
    }
}

// Exportar validadores
window.Validators = {
    InsumosValidator,
    LivestockValidator,
    MachineryValidator,
    ValidationUtils
};
