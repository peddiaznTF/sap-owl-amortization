// src/services/SAPService.js
export class SAPService {
    constructor(config = {}) {
        this.baseUrl = config.baseUrl || 'https://localhost:50000/b1s/v1';
        this.username = config.username;
        this.password = config.password;
        this.sessionId = null;
        this.currentCompany = null;
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutos
        this.lastActivity = null;
    }

    // Autenticación con SAP Service Layer
    async login(companyDB, username = this.username, password = this.password) {
        try {
            const response = await fetch(`${this.baseUrl}/Login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    CompanyDB: companyDB,
                    UserName: username,
                    Password: password
                })
            });

            if (!response.ok) {
                throw new Error(`Error de autenticación: ${response.status}`);
            }

            const data = await response.json();
            this.sessionId = data.SessionId;
            this.currentCompany = companyDB;
            this.lastActivity = Date.now();

            console.log(`Sesión iniciada para compañía: ${companyDB}`);
            return data;

        } catch (error) {
            console.error('Error en login SAP:', error);
            throw new Error('No se pudo conectar con SAP Business One');
        }
    }

    // Cerrar sesión
    async logout() {
        if (!this.sessionId) return;

        try {
            await fetch(`${this.baseUrl}/Logout`, {
                method: 'POST',
                headers: this.getHeaders()
            });
        } catch (error) {
            console.error('Error en logout:', error);
        } finally {
            this.sessionId = null;
            this.currentCompany = null;
        }
    }

    // Verificar y renovar sesión si es necesario
    async ensureValidSession() {
        if (!this.sessionId) {
            throw new Error('No hay sesión activa');
        }

        const now = Date.now();
        if (this.lastActivity && (now - this.lastActivity) > this.sessionTimeout) {
            console.log('Sesión expirada, renovando...');
            await this.login(this.currentCompany);
        }

        this.lastActivity = now;
    }

    // Obtener headers para las peticiones
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.sessionId) {
            headers['Cookie'] = `B1SESSION=${this.sessionId}`;
        }

        return headers;
    }

    // Realizar petición GET a SAP
    async get(endpoint, params = {}) {
        await this.ensureValidSession();
        
        const url = new URL(`${this.baseUrl}/${endpoint}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders()
        });

        if (!response.ok) {
            throw new Error(`Error en petición GET: ${response.status}`);
        }

        return await response.json();
    }

    // Realizar petición POST a SAP
    async post(endpoint, data) {
        await this.ensureValidSession();

        const response = await fetch(`${this.baseUrl}/${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Error en petición POST: ${response.status} - ${errorData.error?.message || 'Error desconocido'}`);
        }

        return await response.json();
    }

    // Realizar petición PATCH a SAP
    async patch(endpoint, data) {
        await this.ensureValidSession();

        const response = await fetch(`${this.baseUrl}/${endpoint}`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Error en petición PATCH: ${response.status} - ${errorData.error?.message || 'Error desconocido'}`);
        }

        return response.status === 204 ? {} : await response.json();
    }

    // Métodos específicos para gestión de compañías
    async getCompanies() {
        // Esta información normalmente se obtiene del servidor de aplicaciones
        // o de una configuración externa, ya que Service Layer requiere conexión por compañía
        return [
            { id: 'SBODEMOUS', name: 'Demo Company US', currency: 'USD' },
            { id: 'SBODEMOAR', name: 'Demo Company AR', currency: 'ARS' },
            // Agregar más compañías según configuración
        ];
    }

    async setCompany(companyId) {
        if (this.currentCompany === companyId && this.sessionId) {
            return; // Ya conectado a esta compañía
        }

        // Cerrar sesión actual si existe
        if (this.sessionId) {
            await this.logout();
        }

        // Conectar a la nueva compañía
        await this.login(companyId);
    }

    // Métodos para Business Partners (Clientes/Proveedores)
    async getBusinessPartners(type = 'C') {
        // type: 'C' para clientes, 'S' para proveedores
        const filter = `CardType eq '${type}'`;
        const select = 'CardCode,CardName,CardType,Currency,CreditLine,CurrentAccountBalance';
        
        const response = await this.get('BusinessPartners', {
            $filter: filter,
            $select: select
        });

        return response.value || [];
    }

    async getBusinessPartner(cardCode) {
        const response = await this.get(`BusinessPartners('${cardCode}')`);
        return response;
    }

    // Métodos para Documentos de Marketing (Facturas, etc.)
    async getInvoices(type = 'I') {
        // type: 'I' para facturas de cliente, 'P' para facturas de proveedor
        const endpoint = type === 'I' ? 'Invoices' : 'PurchaseInvoices';
        const response = await this.get(endpoint);
        return response.value || [];
    }

    async createInvoice(invoiceData, type = 'I') {
        const endpoint = type === 'I' ? 'Invoices' : 'PurchaseInvoices';
        return await this.post(endpoint, invoiceData);
    }

    // Métodos para Pagos
    async getIncomingPayments() {
        const response = await this.get('IncomingPayments');
        return response.value || [];
    }

    async createIncomingPayment(paymentData) {
        return await this.post('IncomingPayments', paymentData);
    }

    async getVendorPayments() {
        const response = await this.get('VendorPayments');
        return response.value || [];
    }

    async createVendorPayment(paymentData) {
        return await this.post('VendorPayments', paymentData);
    }

    // Métodos para Journal Entries (Asientos Contables)
    async createJournalEntry(journalData) {
        return await this.post('JournalEntries', journalData);
    }

    // Métodos específicos para amortización
    async getAmortizationDocuments(cardCode, type) {
        const filter = `CardCode eq '${cardCode}' and DocumentStatus eq 'O'`;
        const endpoint = type === 'clientes' ? 'Invoices' : 'PurchaseInvoices';
        
        const response = await this.get(endpoint, {
            $filter: filter,
            $select: 'DocEntry,DocNum,CardCode,CardName,DocDate,DocTotal,PaidToDate'
        });

        return response.value || [];
    }

    // Crear asiento de amortización
    async createAmortizationEntry(amortizationData) {
        const journalEntry = {
            JournalEntries: [{
                ReferenceDate: amortizationData.date,
                Memo: `Amortización ${amortizationData.reference}`,
                JournalEntryLines: amortizationData.lines.map(line => ({
                    AccountCode: line.accountCode,
                    ShortName: line.accountName,
                    Debit: line.debit || 0,
                    Credit: line.credit || 0,
                    LineMemo: line.memo
                }))
            }]
        };

        return await this.createJournalEntry(journalEntry);
    }

    // Método para obtener cuentas contables
    async getChartOfAccounts() {
        const response = await this.get('ChartOfAccounts', {
            $select: 'Code,Name,ActiveAccount'
        });
        return response.value || [];
    }

    // Método para obtener monedas
    async getCurrencies() {
        const response = await this.get('Currencies');
        return response.value || [];
    }

    // Método para obtener series de documentos
    async getDocumentSeries() {
        const response = await this.get('Series');
        return response.value || [];
    }

    // Manejo de errores específicos de SAP
    handleSAPError(error) {
        if (error.message.includes('401')) {
            throw new Error('Credenciales inválidas o sesión expirada');
        } else if (error.message.includes('404')) {
            throw new Error('Recurso no encontrado en SAP');
        } else if (error.message.includes('500')) {
            throw new Error('Error interno del servidor SAP');
        } else {
            throw error;
        }
    }
}

// Clase auxiliar para construcción de filtros OData
export class ODataFilter {
    constructor() {
        this.filters = [];
    }

    eq(field, value) {
        this.filters.push(`${field} eq '${value}'`);
        return this;
    }

    ne(field, value) {
        this.filters.push(`${field} ne '${value}'`);
        return this;
    }

    gt(field, value) {
        this.filters.push(`${field} gt ${value}`);
        return this;
    }

    lt(field, value) {
        this.filters.push(`${field} lt ${value}`);
        return this;
    }

    and() {
        this.filters.push('and');
        return this;
    }

    or() {
        this.filters.push('or');
        return this;
    }

    build() {
        return this.filters.join(' ');
    }
}

// Instancia singleton del servicio SAP
export const sapService = new SAPService();