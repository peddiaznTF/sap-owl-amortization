// src/main.js - Aplicación Principal OWL
import { Component, mount, useState, useRef, xml } from "@odoo/owl";
import { CompanySelector } from "./components/CompanySelector.js";
import { AmortizationManager } from "./components/AmortizationManager.js";
import { Dashboard } from "./components/Dashboard.js";
import { SAPService } from "./services/SAPService.js";
import { AmortizationService } from "./services/AmortizationService.js";

// Componente Principal de la Aplicación
class AmortizationApp extends Component {
    static template = xml`
        <div class="amortization-app">
            <header class="app-header">
                <div class="header-content">
                    <h1>Sistema de Gestión de Amortización Financiera</h1>
                    <CompanySelector 
                        companies="state.companies"
                        selectedCompany="state.selectedCompany"
                        onCompanyChange="onCompanyChange"
                    />
                </div>
            </header>
            
            <nav class="app-navigation">
                <ul class="nav-menu">
                    <li class="nav-item" t-att-class="{ active: state.activeView === 'dashboard' }">
                        <button t-on-click="() => this.setActiveView('dashboard')">
                            Dashboard
                        </button>
                    </li>
                    <li class="nav-item" t-att-class="{ active: state.activeView === 'clientes' }">
                        <button t-on-click="() => this.setActiveView('clientes')">
                            Amortización Clientes
                        </button>
                    </li>
                    <li class="nav-item" t-att-class="{ active: state.activeView === 'proveedores' }">
                        <button t-on-click="() => this.setActiveView('proveedores')">
                            Amortización Proveedores
                        </button>
                    </li>
                    <li class="nav-item" t-att-class="{ active: state.activeView === 'reportes' }">
                        <button t-on-click="() => this.setActiveView('reportes')">
                            Reportes
                        </button>
                    </li>
                </ul>
            </nav>

            <main class="app-content">
                <div t-if="!state.selectedCompany" class="no-company-selected">
                    <h2>Seleccione una compañía para continuar</h2>
                </div>
                
                <div t-elif="state.loading" class="loading-container">
                    <div class="loading-spinner"></div>
                    <p>Cargando datos...</p>
                </div>
                
                <div t-else="" class="view-container">
                    <Dashboard t-if="state.activeView === 'dashboard'" 
                        company="state.selectedCompany"
                        data="state.dashboardData"
                    />
                    
                    <AmortizationManager t-if="state.activeView === 'clientes'" 
                        type="'clientes'"
                        company="state.selectedCompany"
                        onAmortizationChange="onAmortizationChange"
                    />
                    
                    <AmortizationManager t-if="state.activeView === 'proveedores'" 
                        type="'proveedores'"
                        company="state.selectedCompany"
                        onAmortizationChange="onAmortizationChange"
                    />
                    
                    <ReportsView t-if="state.activeView === 'reportes'" 
                        company="state.selectedCompany"
                        data="state.reportsData"
                    />
                </div>
            </main>
        </div>
    `;

    static components = { CompanySelector, AmortizationManager, Dashboard };

    setup() {
        this.state = useState({
            companies: [],
            selectedCompany: null,
            activeView: 'dashboard',
            loading: false,
            dashboardData: {},
            reportsData: {}
        });

        this.sapService = new SAPService();
        this.amortizationService = new AmortizationService();

        this.loadCompanies();
    }

    async loadCompanies() {
        try {
            this.state.loading = true;
            const companies = await this.sapService.getCompanies();
            this.state.companies = companies;
        } catch (error) {
            console.error('Error cargando compañías:', error);
            this.showError('Error al cargar las compañías');
        } finally {
            this.state.loading = false;
        }
    }

    async onCompanyChange(company) {
        this.state.selectedCompany = company;
        this.state.loading = true;
        
        try {
            // Configurar conexión SAP para la compañía seleccionada
            await this.sapService.setCompany(company.id);
            
            // Cargar datos del dashboard
            await this.loadDashboardData();
            
        } catch (error) {
            console.error('Error al cambiar compañía:', error);
            this.showError('Error al conectar con la compañía seleccionada');
        } finally {
            this.state.loading = false;
        }
    }

    async loadDashboardData() {
        try {
            const dashboardData = await this.amortizationService.getDashboardData(
                this.state.selectedCompany.id
            );
            this.state.dashboardData = dashboardData;
        } catch (error) {
            console.error('Error cargando datos del dashboard:', error);
        }
    }

    setActiveView(view) {
        this.state.activeView = view;
    }

    async onAmortizationChange() {
        // Recargar datos cuando hay cambios en amortizaciones
        await this.loadDashboardData();
    }

    showError(message) {
        // Implementar sistema de notificaciones
        alert(message); // Temporal
    }
}

// Componente Selector de Compañía
class CompanySelectorComponent extends Component {
    static template = xml`
        <div class="company-selector">
            <label for="company-select">Compañía:</label>
            <select id="company-select" t-on-change="onCompanyChange" t-att-value="props.selectedCompany?.id || ''">
                <option value="">Seleccionar compañía...</option>
                <option t-foreach="props.companies" t-as="company" t-key="company.id" t-att-value="company.id">
                    <t t-esc="company.name"/>
                </option>
            </select>
        </div>
    `;

    onCompanyChange(event) {
        const companyId = event.target.value;
        if (companyId) {
            const company = this.props.companies.find(c => c.id === companyId);
            this.props.onCompanyChange(company);
        }
    }
}

// Configuración de la aplicación
const appConfig = {
    dev: true,
    test: false,
    sapService: {
        baseUrl: process.env.SAP_SERVICE_LAYER_URL || 'https://localhost:50000/b1s/v1',
        username: process.env.SAP_USERNAME,
        password: process.env.SAP_PASSWORD
    },
    apiGateway: {
        baseUrl: process.env.API_GATEWAY_URL || 'http://localhost:8000/api'
    }
};

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', () => {
    mount(AmortizationApp, document.getElementById('app'), {
        dev: appConfig.dev,
        test: appConfig.test
    });
});

export { AmortizationApp, appConfig };