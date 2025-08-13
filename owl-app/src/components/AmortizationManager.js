// src/components/AmortizationManager.js
import { Component, useState, useRef, xml } from "@odoo/owl";
import { AmortizationTable } from "./AmortizationTable.js";
import { AmortizationForm } from "./AmortizationForm.js";
import { AmortizationService } from "../services/AmortizationService.js";

export class AmortizationManager extends Component {
    static template = xml`
        <div class="amortization-manager">
            <div class="manager-header">
                <h2>
                    Gestión de Amortización - 
                    <span t-if="props.type === 'clientes'">Clientes</span>
                    <span t-else="">Proveedores</span>
                </h2>
                
                <div class="header-actions">
                    <button class="btn btn-primary" t-on-click="openCreateForm">
                        Nueva Amortización
                    </button>
                    <button class="btn btn-secondary" t-on-click="syncWithSAP">
                        Sincronizar con SAP
                    </button>
                </div>
            </div>

            <div class="filters-section">
                <div class="filter-group">
                    <label>Estado:</label>
                    <select t-model="state.filters.status" t-on-change="applyFilters">
                        <option value="">Todos</option>
                        <option value="active">Activo</option>
                        <option value="completed">Completado</option>
                        <option value="overdue">Vencido</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Entidad:</label>
                    <input type="text" 
                        t-model="state.filters.entityName" 
                        t-on-input="applyFilters"
                        placeholder="Buscar por nombre..."
                    />
                </div>
                
                <div class="filter-group">
                    <label>Fecha desde:</label>
                    <input type="date" 
                        t-model="state.filters.dateFrom" 
                        t-on-change="applyFilters"
                    />
                </div>
                
                <div class="filter-group">
                    <label>Fecha hasta:</label>
                    <input type="date" 
                        t-model="state.filters.dateTo" 
                        t-on-change="applyFilters"
                    />
                </div>
            </div>

            <div class="amortizations-list">
                <div t-if="state.loading" class="loading">
                    <div class="spinner"></div>
                    <p>Cargando amortizaciones...</p>
                </div>
                
                <div t-elif="state.amortizations.length === 0" class="no-data">
                    <p>No hay amortizaciones para mostrar</p>
                </div>
                
                <div t-else="" class="amortizations-grid">
                    <div t-foreach="state.filteredAmortizations" t-as="amortization" t-key="amortization.id"
                         class="amortization-card" t-att-class="getCardClass(amortization)">
                        
                        <div class="card-header">
                            <h3 t-esc="amortization.entityName"/>
                            <span class="status-badge" t-att-class="'status-' + amortization.status">
                                <t t-esc="getStatusText(amortization.status)"/>
                            </span>
                        </div>
                        
                        <div class="card-content">
                            <div class="info-row">
                                <label>Monto Total:</label>
                                <span class="amount" t-esc="formatCurrency(amortization.totalAmount)"/>
                            </div>
                            
                            <div class="info-row">
                                <label>Monto Pendiente:</label>
                                <span class="amount" t-esc="formatCurrency(amortization.pendingAmount)"/>
                            </div>
                            
                            <div class="info-row">
                                <label>Cuotas:</label>
                                <span t-esc="amortization.paidInstallments + ' / ' + amortization.totalInstallments"/>
                            </div>
                            
                            <div class="info-row">
                                <label>Próximo Vencimiento:</label>
                                <span t-esc="formatDate(amortization.nextDueDate)"/>
                            </div>
                            
                            <div class="progress-bar">
                                <div class="progress-fill" 
                                     t-att-style="'width: ' + getProgressPercentage(amortization) + '%'">
                                </div>
                            </div>
                        </div>
                        
                        <div class="card-actions">
                            <button class="btn btn-sm btn-outline" t-on-click="() => this.viewDetails(amortization)">
                                Ver Detalle
                            </button>
                            <button class="btn btn-sm btn-outline" t-on-click="() => this.editAmortization(amortization)">
                                Editar
                            </button>
                            <button class="btn btn-sm btn-success" t-on-click="() => this.recordPayment(amortization)"
                                    t-if="amortization.status === 'active'">
                                Registrar Pago
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal para formulario de amortización -->
            <div t-if="state.showForm" class="modal-overlay" t-on-click="closeForm">
                <div class="modal-content" t-on-click.stop="">
                    <AmortizationForm 
                        type="props.type"
                        company="props.company"
                        amortization="state.selectedAmortization"
                        onSave="onAmortizationSave"
                        onCancel="closeForm"
                    />
                </div>
            </div>

            <!-- Modal para tabla de amortización -->
            <div t-if="state.showTable" class="modal-overlay" t-on-click="closeTable">
                <div class="modal-content modal-large" t-on-click.stop="">
                    <AmortizationTable 
                        amortization="state.selectedAmortization"
                        onPaymentRecord="onPaymentRecord"
                        onClose="closeTable"
                    />
                </div>
            </div>
        </div>
    `;

    static components = { AmortizationTable, AmortizationForm };

    setup() {
        this.state = useState({
            amortizations: [],
            filteredAmortizations: [],
            loading: false,
            showForm: false,
            showTable: false,
            selectedAmortization: null,
            filters: {
                status: '',
                entityName: '',
                dateFrom: '',
                dateTo: ''
            }
        });

        this.amortizationService = new AmortizationService();
        this.loadAmortizations();
    }

    async loadAmortizations() {
        this.state.loading = true;
        try {
            const amortizations = await this.amortizationService.getAmortizations(
                this.props.company.id, 
                this.props.type
            );
            this.state.amortizations = amortizations;
            this.applyFilters();
        } catch (error) {
            console.error('Error cargando amortizaciones:', error);
        } finally {
            this.state.loading = false;
        }
    }

    applyFilters() {
        let filtered = [...this.state.amortizations];

        // Filtrar por estado
        if (this.state.filters.status) {
            filtered = filtered.filter(a => a.status === this.state.filters.status);
        }

        // Filtrar por nombre de entidad
        if (this.state.filters.entityName) {
            const searchTerm = this.state.filters.entityName.toLowerCase();
            filtered = filtered.filter(a => 
                a.entityName.toLowerCase().includes(searchTerm)
            );
        }

        // Filtrar por fecha desde
        if (this.state.filters.dateFrom) {
            filtered = filtered.filter(a => 
                new Date(a.startDate) >= new Date(this.state.filters.dateFrom)
            );
        }

        // Filtrar por fecha hasta
        if (this.state.filters.dateTo) {
            filtered = filtered.filter(a => 
                new Date(a.startDate) <= new Date(this.state.filters.dateTo)
            );
        }

        this.state.filteredAmortizations = filtered;
    }

    openCreateForm() {
        this.state.selectedAmortization = null;
        this.state.showForm = true;
    }

    editAmortization(amortization) {
        this.state.selectedAmortization = amortization;
        this.state.showForm = true;
    }

    viewDetails(amortization) {
        this.state.selectedAmortization = amortization;
        this.state.showTable = true;
    }

    async recordPayment(amortization) {
        try {
            await this.amortizationService.recordPayment(amortization.id);
            await this.loadAmortizations();
            this.props.onAmortizationChange?.();
        } catch (error) {
            console.error('Error registrando pago:', error);
        }
    }

    async syncWithSAP() {
        this.state.loading = true;
        try {
            await this.amortizationService.syncWithSAP(
                this.props.company.id, 
                this.props.type
            );
            await this.loadAmortizations();
        } catch (error) {
            console.error('Error sincronizando con SAP:', error);
        } finally {
            this.state.loading = false;
        }
    }

    closeForm() {
        this.state.showForm = false;
        this.state.selectedAmortization = null;
    }

    closeTable() {
        this.state.showTable = false;
        this.state.selectedAmortization = null;
    }

    async onAmortizationSave() {
        await this.loadAmortizations();
        this.closeForm();
        this.props.onAmortizationChange?.();
    }

    async onPaymentRecord() {
        await this.loadAmortizations();
        this.props.onAmortizationChange?.();
    }

    // Métodos auxiliares
    getCardClass(amortization) {
        const classes = ['amortization-card'];
        if (amortization.status === 'overdue') {
            classes.push('overdue');
        } else if (amortization.status === 'completed') {
            classes.push('completed');
        }
        return classes.join(' ');
    }

    getStatusText(status) {
        const statusTexts = {
            'active': 'Activo',
            'completed': 'Completado',
            'overdue': 'Vencido',
            'suspended': 'Suspendido'
        };
        return statusTexts[status] || status;
    }

    getProgressPercentage(amortization) {
        if (amortization.totalInstallments === 0) return 0;
        return Math.round((amortization.paidInstallments / amortization.totalInstallments) * 100);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('es-ES');
    }
}