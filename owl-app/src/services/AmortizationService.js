// src/services/AmortizationService.js
export class AmortizationService {
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || 'http://localhost:8000/api';
        this.timeout = config.timeout || 30000;
        this.retryAttempts = config.retryAttempts || 3;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    }

    // Configuración de headers para las peticiones
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };

        // Agregar token de autenticación si existe
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    // Método genérico para hacer peticiones HTTP
    async makeRequest(url, options = {}) {
        const fullUrl = `${this.baseUrl}${url}`;
        const config = {
            headers: this.getHeaders(),
            timeout: this.timeout,
            ...options
        };

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(fullUrl, config);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(
                        errorData.message || 
                        errorData.detail || 
                        `HTTP ${response.status}: ${response.statusText}`
                    );
                }

                return await response.json();
                
            } catch (error) {
                if (attempt === this.retryAttempts) {
                    console.error(`Request failed after ${attempt} attempts:`, error);
                    throw error;
                }
                
                // Esperar antes del siguiente intento
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            }
        }
    }

    // Métodos de caché
    setCacheItem(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    getCacheItem(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() - item.timestamp > this.cacheTimeout) {
            this.cache.delete(key);
            return null;
        }
        
        return item.data;
    }

    clearCache() {
        this.cache.clear();
    }

    // === MÉTODOS PRINCIPALES DE AMORTIZACIÓN ===

    /**
     * Obtener lista de amortizaciones con filtros
     */
    async getAmortizations(companyId, type, filters = {}) {
        const params = new URLSearchParams({
            company_id: companyId,
            entity_type: type,
            ...filters
        });

        const cacheKey = `amortizations_${companyId}_${type}_${params.toString()}`;
        const cached = this.getCacheItem(cacheKey);
        if (cached) return cached;

        const response = await this.makeRequest(`/amortizations?${params}`);
        this.setCacheItem(cacheKey, response);
        return response;
    }

    /**
     * Obtener detalle de una amortización específica
     */
    async getAmortizationDetail(amortizationId, includeInstallments = true) {
        const params = new URLSearchParams({
            include_installments: includeInstallments
        });

        return await this.makeRequest(`/amortizations/${amortizationId}?${params}`);
    }

    /**
     * Crear nueva amortización
     */
    async createAmortization(amortizationData) {
        const response = await this.makeRequest('/amortizations', {
            method: 'POST',
            body: JSON.stringify(amortizationData)
        });

        // Limpiar cache relacionado
        this.clearAmortizationCache(amortizationData.company_id);
        return response;
    }

    /**
     * Actualizar amortización existente
     */
    async updateAmortization(amortizationId, amortizationData) {
        const response = await this.makeRequest(`/amortizations/${amortizationId}`, {
            method: 'PUT',
            body: JSON.stringify(amortizationData)
        });

        // Limpiar cache relacionado
        this.clearAmortizationCache(amortizationData.company_id);
        return response;
    }

    /**
     * Eliminar amortización
     */
    async deleteAmortization(amortizationId, forceDelete = false) {
        const params = new URLSearchParams({
            force_delete: forceDelete
        });

        const response = await this.makeRequest(
            `/amortizations/${amortizationId}?${params}`,
            { method: 'DELETE' }
        );

        // Limpiar cache
        this.clearCache();
        return response;
    }

    // === MÉTODOS DE CUOTAS ===

    /**
     * Obtener cuotas de una amortización
     */
    async getInstallments(amortizationId, filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.makeRequest(`/amortizations/${amortizationId}/installments?${params}`);
    }

    /**
     * Registrar pago de una cuota
     */
    async recordPayment(installmentId, paymentData) {
        const amortizationId = paymentData.amortization_id;
        const params = new URLSearchParams({
            payment_amount: paymentData.amount,
            payment_date: paymentData.date,
            notes: paymentData.notes || '',
            create_sap_entry: paymentData.createSAPEntry !== false
        });

        const response = await this.makeRequest(
            `/amortizations/${amortizationId}/installments/${installmentId}/pay?${params}`,
            { method: 'POST' }
        );

        // Limpiar cache relacionado
        this.clearAmortizationCache();
        return response;
    }

    /**
     * Pagar múltiples cuotas
     */
    async payMultipleInstallments(installmentIds, paymentData = {}) {
        const response = await this.makeRequest('/installments/pay-multiple', {
            method: 'POST',
            body: JSON.stringify({
                installment_ids: installmentIds,
                payment_date: paymentData.date || new Date().toISOString().split('T')[0],
                notes: paymentData.notes || '',
                create_sap_entries: paymentData.createSAPEntries !== false
            })
        });

        this.clearCache();
        return response;
    }

    /**
     * Regenerar tabla de cuotas
     */
    async generateInstallments(amortizationId, overwriteExisting = false) {
        const params = new URLSearchParams({
            overwrite_existing: overwriteExisting
        });

        return await this.makeRequest(
            `/amortizations/${amortizationId}/generate-installments?${params}`,
            { method: 'POST' }
        );
    }

    // === MÉTODOS DE CÁLCULO ===

    /**
     * Calcular cuotas (vista previa)
     */
    async calculateInstallments(calculationData) {
        return await this.makeRequest('/amortizations/calculate', {
            method: 'POST',
            body: JSON.stringify(calculationData)
        });
    }

    /**
     * Calcular amortización lineal
     */
    calculateLinearAmortization(totalAmount, installments, interestRate = 0, startDate) {
        const principalPerInstallment = totalAmount / installments;
        const monthlyInterestRate = (interestRate / 100) / 12;
        const results = [];
        let remainingBalance = totalAmount;

        for (let i = 1; i <= installments; i++) {
            const dueDate = this.calculateDueDate(startDate, i);
            const interestAmount = remainingBalance * monthlyInterestRate;
            const totalInstallmentAmount = principalPerInstallment + interestAmount;

            results.push({
                number: i,
                dueDate: dueDate,
                principal: principalPerInstallment,
                interest: interestAmount,
                total: totalInstallmentAmount,
                balance: remainingBalance - principalPerInstallment
            });

            remainingBalance -= principalPerInstallment;
        }

        return results;
    }

    /**
     * Calcular amortización francesa
     */
    calculateFrenchAmortization(totalAmount, installments, interestRate = 0, startDate) {
        const monthlyInterestRate = (interestRate / 100) / 12;
        let installmentAmount;

        if (monthlyInterestRate === 0) {
            installmentAmount = totalAmount / installments;
        } else {
            installmentAmount = (totalAmount * monthlyInterestRate * 
                Math.pow(1 + monthlyInterestRate, installments)) / 
                (Math.pow(1 + monthlyInterestRate, installments) - 1);
        }

        const results = [];
        let remainingBalance = totalAmount;

        for (let i = 1; i <= installments; i++) {
            const dueDate = this.calculateDueDate(startDate, i);
            const interestAmount = remainingBalance * monthlyInterestRate;
            const principalAmount = installmentAmount - interestAmount;

            results.push({
                number: i,
                dueDate: dueDate,
                principal: principalAmount,
                interest: interestAmount,
                total: installmentAmount,
                balance: remainingBalance - principalAmount
            });

            remainingBalance -= principalAmount;
        }

        return results;
    }

    /**
     * Calcular fecha de vencimiento
     */
    calculateDueDate(startDate, installmentNumber, frequency = 'monthly') {
        const date = new Date(startDate);
        
        switch (frequency) {
            case 'monthly':
                date.setMonth(date.getMonth() + installmentNumber);
                break;
            case 'quarterly':
                date.setMonth(date.getMonth() + (installmentNumber * 3));
                break;
            case 'biannual':
                date.setMonth(date.getMonth() + (installmentNumber * 6));
                break;
            case 'annual':
                date.setFullYear(date.getFullYear() + installmentNumber);
                break;
        }

        return date.toISOString().split('T')[0];
    }

    // === MÉTODOS DE DASHBOARD ===

    /**
     * Obtener métricas del dashboard
     */
    async getDashboardMetrics(companyId) {
        const cacheKey = `dashboard_metrics_${companyId}`;
        const cached = this.getCacheItem(cacheKey);
        if (cached) return cached;

        const response = await this.makeRequest(`/amortizations/reports/summary?company_id=${companyId}`);
        this.setCacheItem(cacheKey, response);
        return response;
    }

    /**
     * Obtener próximos vencimientos
     */
    async getUpcomingDues(companyId, options = {}) {
        const params = new URLSearchParams({
            company_id: companyId,
            limit: options.limit || 10,
            days_ahead: options.daysAhead || 30
        });

        return await this.makeRequest(`/amortizations/upcoming-dues?${params}`);
    }

    /**
     * Obtener amortizaciones recientes
     */
    async getRecentAmortizations(companyId, options = {}) {
        const params = new URLSearchParams({
            company_id: companyId,
            limit: options.limit || 10,
            days_back: options.daysBack || 30
        });

        return await this.makeRequest(`/amortizations/recent?${params}`);
    }

    /**
     * Obtener alertas del sistema
     */
    async getAlerts(companyId) {
        return await this.makeRequest(`/alerts?company_id=${companyId}`);
    }

    /**
     * Obtener distribución por tipo (para gráficos)
     */
    async getTypeDistribution(companyId, period = 'month') {
        const params = new URLSearchParams({
            company_id: companyId,
            period: period
        });

        return await this.makeRequest(`/amortizations/reports/type-distribution?${params}`);
    }

    /**
     * Obtener datos de evolución (para gráficos)
     */
    async getEvolutionData(companyId, period = 'month') {
        const params = new URLSearchParams({
            company_id: companyId,
            period: period
        });

        return await this.makeRequest(`/amortizations/reports/evolution?${params}`);
    }

    // === MÉTODOS DE SINCRONIZACIÓN SAP ===

    /**
     * Sincronizar amortización con SAP
     */
    async syncToSAP(amortizationId, options = {}) {
        const params = new URLSearchParams({
            create_documents: options.createDocuments !== false
        });

        return await this.makeRequest(
            `/amortizations/${amortizationId}/sync-to-sap?${params}`,
            { method: 'POST' }
        );
    }

    /**
     * Importar documentos desde SAP
     */
    async importFromSAP(companyId, entityType, options = {}) {
        const body = {
            company_id: companyId,
            entity_type: entityType,
            document_types: options.documentTypes || ['Invoices'],
            date_from: options.dateFrom,
            date_to: options.dateTo,
            auto_create_amortizations: options.autoCreate || false
        };

        return await this.makeRequest('/amortizations/import-from-sap', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    /**
     * Sincronizar todas las amortizaciones de una compañía
     */
    async syncWithSAP(companyId, entityType) {
        return await this.makeRequest('/amortizations/sync-all', {
            method: 'POST',
            body: JSON.stringify({
                company_id: companyId,
                entity_type: entityType
            })
        });
    }

    // === MÉTODOS DE REPORTES ===

    /**
     * Obtener reporte de aging
     */
    async getAgingReport(companyId, options = {}) {
        const params = new URLSearchParams({
            company_id: companyId,
            entity_type: options.entityType || '',
            aging_periods: (options.agingPeriods || [30, 60, 90, 120]).join(',')
        });

        return await this.makeRequest(`/amortizations/reports/aging?${params}`);
    }

    /**
     * Generar reporte de dashboard en PDF
     */
    async generateDashboardReport(companyId) {
        const response = await fetch(`${this.baseUrl}/reports/dashboard-pdf?company_id=${companyId}`, {
            headers: this.getHeaders()
        });

        if (!response.ok) {
            throw new Error('Error generando reporte');
        }

        return await response.blob();
    }

    /**
     * Exportar tabla de amortización
     */
    async exportAmortizationTable(amortizationId, format = 'excel') {
        const response = await fetch(
            `${this.baseUrl}/amortizations/${amortizationId}/export?format=${format}`,
            { headers: this.getHeaders() }
        );

        if (!response.ok) {
            throw new Error('Error exportando tabla');
        }

        return await response.blob();
    }

    // === MÉTODOS DE NOTIFICACIONES ===

    /**
     * Configurar notificaciones
     */
    async setupNotifications(companyId, settings) {
        return await this.makeRequest('/notifications/setup', {
            method: 'POST',
            body: JSON.stringify({
                company_id: companyId,
                settings: settings
            })
        });
    }

    /**
     * Enviar notificaciones de vencimiento
     */
    async sendDueNotifications(companyId) {
        return await this.makeRequest('/notifications/send-due', {
            method: 'POST',
            body: JSON.stringify({
                company_id: companyId
            })
        });
    }

    // === MÉTODOS AUXILIARES ===

    /**
     * Limpiar cache de amortizaciones por compañía
     */
    clearAmortizationCache(companyId = null) {
        if (companyId) {
            // Limpiar cache específico de la compañía
            for (const key of this.cache.keys()) {
                if (key.includes(`_${companyId}_`)) {
                    this.cache.delete(key);
                }
            }
        } else {
            // Limpiar todo el cache de amortizaciones
            for (const key of this.cache.keys()) {
                if (key.includes('amortizations') || key.includes('dashboard')) {
                    this.cache.delete(key);
                }
            }
        }
    }

    /**
     * Validar datos de amortización
     */
    validateAmortizationData(data) {
        const errors = {};

        if (!data.reference || data.reference.trim() === '') {
            errors.reference = 'La referencia es requerida';
        }

        if (!data.entity_id) {
            errors.entity_id = 'Debe seleccionar una entidad';
        }

        if (!data.total_amount || data.total_amount <= 0) {
            errors.total_amount = 'El monto debe ser mayor a cero';
        }

        if (!data.total_installments || data.total_installments < 1) {
            errors.total_installments = 'Debe tener al menos una cuota';
        }

        if (!data.start_date) {
            errors.start_date = 'La fecha de inicio es requerida';
        }

        if (data.interest_rate < 0 || data.interest_rate > 100) {
            errors.interest_rate = 'La tasa debe estar entre 0 y 100%';
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }

    /**
     * Formatear moneda
     */
    formatCurrency(amount, currency = 'EUR') {
        if (!amount && amount !== 0) return '-';
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    /**
     * Formatear fecha
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('es-ES');
    }

    /**
     * Calcular días entre fechas
     */
    daysBetween(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000;
        const firstDate = new Date(date1);
        const secondDate = new Date(date2);
        return Math.round(Math.abs((firstDate - secondDate) / oneDay));
    }

    /**
     * Verificar si una fecha está vencida
     */
    isOverdue(dueDate) {
        const today = new Date();
        const due = new Date(dueDate);
        today.setHours(0, 0, 0, 0);
        due.setHours(0, 0, 0, 0);
        return due < today;
    }

    /**
     * Obtener estado de salud del servicio
     */
    async getServiceHealth() {
        try {
            return await this.makeRequest('/health');
        } catch (error) {
            return { status: 'unhealthy', error: error.message };
        }
    }
}

// Instancia singleton del servicio
export const amortizationService = new AmortizationService();