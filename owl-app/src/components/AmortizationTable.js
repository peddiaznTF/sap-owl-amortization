// src/components/AmortizationTable.js
import { Component, useState, useRef, xml, onMounted } from "@odoo/owl";
import { AmortizationService } from "../services/AmortizationService.js";

export class AmortizationTable extends Component {
    static template = xml`
        <div class="amortization-table">
            <div class="table-header">
                <div class="header-info">
                    <h3>Tabla de Amortización</h3>
                    <div class="amortization-summary">
                        <span class="summary-item">
                            <strong>Referencia:</strong> <t t-esc="props.amortization.reference"/>
                        </span>
                        <span class="summary-item">
                            <strong>Total:</strong> <t t-esc="formatCurrency(props.amortization.total_amount)"/>
                        </span>
                        <span class="summary-item">
                            <strong>Cuotas:</strong> <t t-esc="props.amortization.total_installments"/>
                        </span>
                        <span class="summary-item">
                            <strong>Método:</strong> <t t-esc="getMethodLabel(props.amortization.amortization_method)"/>
                        </span>
                    </div>
                </div>
                <div class="header-actions">
                    <button class="btn btn-sm btn-secondary" t-on-click="exportTable">
                        <i class="icon-download"></i> Exportar
                    </button>
                    <button class="btn btn-sm btn-outline" t-on-click="printTable">
                        <i class="icon-printer"></i> Imprimir
                    </button>
                    <button class="btn btn-sm btn-primary" t-on-click="refreshTable">
                        <i class="icon-refresh"></i> Actualizar
                    </button>
                    <button class="btn-close" t-on-click="props.onClose">
                        <i class="icon-x"></i>
                    </button>
                </div>
            </div>

            <div class="table-filters">
                <div class="filter-group">
                    <label>Estado:</label>
                    <select t-model="state.filters.status" t-on-change="applyFilters">
                        <option value="">Todos</option>
                        <option value="pending">Pendiente</option>
                        <option value="paid">Pagado</option>
                        <option value="overdue">Vencido</option>
                        <option value="partial">Pago Parcial</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Mostrar:</label>
                    <select t-model="state.filters.view" t-on-change="applyFilters">
                        <option value="all">Todas las Cuotas</option>
                        <option value="pending">Solo Pendientes</option>
                        <option value="overdue">Solo Vencidas</option>
                        <option value="upcoming">Próximas 5</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label>Buscar:</label>
                    <input 
                        type="text" 
                        t-model="state.filters.search" 
                        t-on-input="applyFilters"
                        placeholder="Buscar en notas..."
                        class="form-control form-control-sm"
                    />
                </div>
            </div>

            <div class="table-content" t-ref="tableContent">
                <div t-if="state.loading" class="loading">
                    <div class="spinner"></div>
                    <p>Cargando tabla de amortización...</p>
                </div>

                <table t-else="" class="amortization-data-table" id="amortizationTable">
                    <thead>
                        <tr>
                            <th class="col-number">
                                <button class="sort-btn" t-on-click="() => this.sortBy('installment_number')">
                                    #
                                    <i t-att-class="getSortIcon('installment_number')"></i>
                                </button>
                            </th>
                            <th class="col-date">
                                <button class="sort-btn" t-on-click="() => this.sortBy('due_date')">
                                    Fecha Venc.
                                    <i t-att-class="getSortIcon('due_date')"></i>
                                </button>
                            </th>
                            <th class="col-amount">
                                <button class="sort-btn" t-on-click="() => this.sortBy('principal_amount')">
                                    Capital
                                    <i t-att-class="getSortIcon('principal_amount')"></i>
                                </button>
                            </th>
                            <th class="col-amount">
                                <button class="sort-btn" t-on-click="() => this.sortBy('interest_amount')">
                                    Interés
                                    <i t-att-class="getSortIcon('interest_amount')"></i>
                                </button>
                            </th>
                            <th class="col-amount">
                                <button class="sort-btn" t-on-click="() => this.sortBy('total_amount')">
                                    Total Cuota
                                    <i t-att-class="getSortIcon('total_amount')"></i>
                                </button>
                            </th>
                            <th class="col-amount">Pagado</th>
                            <th class="col-amount">Saldo</th>
                            <th class="col-status">Estado</th>
                            <th class="col-date">Fecha Pago</th>
                            <th class="col-actions">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr t-foreach="state.filteredInstallments" t-as="installment" t-key="installment.id"
                            t-att-class="getRowClass(installment)">
                            
                            <td class="col-number">
                                <span class="installment-number" t-esc="installment.installment_number"/>
                            </td>
                            
                            <td class="col-date">
                                <span t-esc="formatDate(installment.due_date)"/>
                                <small t-if="installment.is_overdue" class="overdue-days">
                                    (<t t-esc="installment.days_overdue"/> días)
                                </small>
                            </td>
                            
                            <td class="col-amount">
                                <span t-esc="formatCurrency(installment.principal_amount)"/>
                            </td>
                            
                            <td class="col-amount">
                                <span t-esc="formatCurrency(installment.interest_amount)"/>
                                <span t-if="installment.late_fee > 0" class="late-fee">
                                    + <t t-esc="formatCurrency(installment.late_fee)"/> mora
                                </span>
                            </td>
                            
                            <td class="col-amount total-amount">
                                <span t-esc="formatCurrency(installment.total_amount + installment.late_fee)"/>
                            </td>
                            
                            <td class="col-amount">
                                <span t-esc="formatCurrency(installment.paid_amount)"/>
                                <div t-if="installment.status === 'partial'" class="payment-progress">
                                    <div class="progress-bar">
                                        <div class="progress-fill" 
                                             t-att-style="'width: ' + getPaymentPercentage(installment) + '%'">
                                        </div>
                                    </div>
                                    <span class="progress-text">
                                        <t t-esc="getPaymentPercentage(installment)"/>%
                                    </span>
                                </div>
                            </td>
                            
                            <td class="col-amount">
                                <span t-esc="formatCurrency(installment.remaining_balance)"/>
                            </td>
                            
                            <td class="col-status">
                                <span class="status-badge" t-att-class="'status-' + installment.status">
                                    <t t-esc="getStatusLabel(installment.status)"/>
                                </span>
                            </td>
                            
                            <td class="col-date">
                                <span t-if="installment.payment_date" t-esc="formatDate(installment.payment_date)"/>
                                <span t-else="" class="text-muted">-</span>
                            </td>
                            
                            <td class="col-actions">
                                <div class="action-buttons">
                                    <button t-if="canPay(installment)" 
                                            class="btn btn-xs btn-success" 
                                            t-on-click="() => this.recordPayment(installment)"
                                            title="Registrar Pago">
                                        <i class="icon-dollar-sign"></i>
                                    </button>
                                    
                                    <button t-if="canEdit(installment)" 
                                            class="btn btn-xs btn-outline" 
                                            t-on-click="() => this.editInstallment(installment)"
                                            title="Editar">
                                        <i class="icon-edit"></i>
                                    </button>
                                    
                                    <button class="btn btn-xs btn-outline" 
                                            t-on-click="() => this.viewDetails(installment)"
                                            title="Ver Detalles">
                                        <i class="icon-eye"></i>
                                    </button>
                                    
                                    <button t-if="installment.sap_payment_entry" 
                                            class="btn btn-xs btn-outline" 
                                            t-on-click="() => this.viewSAPDocument(installment)"
                                            title="Ver en SAP">
                                        <i class="icon-external-link"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        
                        <tr t-if="state.filteredInstallments.length === 0">
                            <td colspan="10" class="text-center text-muted no-data">
                                No hay cuotas que mostrar con los filtros aplicados
                            </td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr class="summary-row">
                            <td colspan="2"><strong>Totales:</strong></td>
                            <td class="col-amount"><strong t-esc="formatCurrency(state.totals.principal)"/></td>
                            <td class="col-amount"><strong t-esc="formatCurrency(state.totals.interest)"/></td>
                            <td class="col-amount total-amount"><strong t-esc="formatCurrency(state.totals.total)"/></td>
                            <td class="col-amount"><strong t-esc="formatCurrency(state.totals.paid)"/></td>
                            <td class="col-amount"><strong t-esc="formatCurrency(state.totals.pending)"/></td>
                            <td colspan="3"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <div class="table-footer">
                <div class="table-info">
                    <span>Mostrando <t t-esc="state.filteredInstallments.length"/> de <t t-esc="state.installments.length"/> cuotas</span>
                </div>
                <div class="table-actions">
                    <button class="btn btn-sm btn-outline" t-on-click="selectAllPending">
                        Seleccionar Pendientes
                    </button>
                    <button class="btn btn-sm btn-success" t-on-click="paySelectedInstallments" 
                            t-att-disabled="state.selectedInstallments.length === 0">
                        Pagar Seleccionadas (<t t-esc="state.selectedInstallments.length"/>)
                    </button>
                </div>
            </div>

            <!-- Modal de pago -->
            <div t-if="state.showPaymentModal" class="modal-overlay" t-on-click="closePaymentModal">
                <div class="modal-content" t-on-click.stop="">
                    <PaymentModal 
                        installment="state.selectedInstallment"
                        amortization="props.amortization"
                        onSave="onPaymentSave"
                        onCancel="closePaymentModal"
                    />
                </div>
            </div>

            <!-- Modal de detalles -->
            <div t-if="state.showDetailsModal" class="modal-overlay" t-on-click="closeDetailsModal">
                <div class="modal-content" t-on-click.stop="">
                    <InstallmentDetailsModal 
                        installment="state.selectedInstallment"
                        amortization="props.amortization"
                        onClose="closeDetailsModal"
                    />
                </div>
            </div>
        </div>
    `;

    setup() {
        this.state = useState({
            loading: false,
            installments: [],
            filteredInstallments: [],
            selectedInstallments: [],
            showPaymentModal: false,
            showDetailsModal: false,
            selectedInstallment: null,
            filters: {
                status: '',
                view: 'all',
                search: ''
            },
            sorting: {
                field: 'installment_number',
                direction: 'asc'
            },
            totals: {
                principal: 0,
                interest: 0,
                total: 0,
                paid: 0,
                pending: 0
            }
        });

        this.amortizationService = new AmortizationService();

        onMounted(() => {
            this.loadInstallments();
        });
    }

    async loadInstallments() {
        this.state.loading = true;
        try {
            const installments = await this.amortizationService.getInstallments(
                this.props.amortization.id
            );
            this.state.installments = installments;
            this.applyFilters();
            this.calculateTotals();
        } catch (error) {
            console.error('Error cargando cuotas:', error);
        } finally {
            this.state.loading = false;
        }
    }

    applyFilters() {
        let filtered = [...this.state.installments];

        // Filtrar por estado
        if (this.state.filters.status) {
            filtered = filtered.filter(i => i.status === this.state.filters.status);
        }

        // Filtrar por vista
        switch (this.state.filters.view) {
            case 'pending':
                filtered = filtered.filter(i => i.status === 'pending');
                break;
            case 'overdue':
                filtered = filtered.filter(i => i.is_overdue);
                break;
            case 'upcoming':
                filtered = filtered
                    .filter(i => i.status === 'pending')
                    .slice(0, 5);
                break;
        }

        // Filtrar por búsqueda
        if (this.state.filters.search) {
            const search = this.state.filters.search.toLowerCase();
            filtered = filtered.filter(i => 
                (i.notes && i.notes.toLowerCase().includes(search)) ||
                i.installment_number.toString().includes(search)
            );
        }

        // Aplicar ordenamiento
        filtered.sort((a, b) => {
            const field = this.state.sorting.field;
            const direction = this.state.sorting.direction;
            
            let aVal = a[field];
            let bVal = b[field];
            
            // Convertir fechas
            if (field.includes('date')) {
                aVal = new Date(aVal || 0);
                bVal = new Date(bVal || 0);
            }
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });

        this.state.filteredInstallments = filtered;
    }

    calculateTotals() {
        const totals = this.state.filteredInstallments.reduce((acc, installment) => {
            acc.principal += installment.principal_amount;
            acc.interest += installment.interest_amount;
            acc.total += installment.total_amount;
            acc.paid += installment.paid_amount;
            acc.pending += (installment.total_amount - installment.paid_amount);
            return acc;
        }, {
            principal: 0,
            interest: 0,
            total: 0,
            paid: 0,
            pending: 0
        });

        this.state.totals = totals;
    }

    sortBy(field) {
        if (this.state.sorting.field === field) {
            this.state.sorting.direction = this.state.sorting.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sorting.field = field;
            this.state.sorting.direction = 'asc';
        }
        this.applyFilters();
    }

    async recordPayment(installment) {
        this.state.selectedInstallment = installment;
        this.state.showPaymentModal = true;
    }

    async editInstallment(installment) {
        // Implementar edición de cuota
        console.log('Editar cuota:', installment);
    }

    async viewDetails(installment) {
        this.state.selectedInstallment = installment;
        this.state.showDetailsModal = true;
    }

    async viewSAPDocument(installment) {
        if (installment.sap_payment_entry) {
            // Abrir documento en SAP (si está disponible)
            window.open(`sap://payment/${installment.sap_payment_entry}`, '_blank');
        }
    }

    async onPaymentSave(paymentData) {
        try {
            await this.amortizationService.recordPayment(
                this.state.selectedInstallment.id,
                paymentData
            );
            
            await this.loadInstallments();
            this.closePaymentModal();
            this.props.onPaymentRecord?.();
            
        } catch (error) {
            console.error('Error registrando pago:', error);
        }
    }

    closePaymentModal() {
        this.state.showPaymentModal = false;
        this.state.selectedInstallment = null;
    }

    closeDetailsModal() {
        this.state.showDetailsModal = false;
        this.state.selectedInstallment = null;
    }

    async refreshTable() {
        await this.loadInstallments();
    }

    async exportTable() {
        try {
            const data = await this.amortizationService.exportAmortizationTable(
                this.props.amortization.id,
                'excel'
            );
            
            // Descargar archivo
            const blob = new Blob([data], { 
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tabla-amortizacion-${this.props.amortization.reference}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exportando tabla:', error);
        }
    }

    printTable() {
        const printContent = document.getElementById('amortizationTable').outerHTML;
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Tabla de Amortización - ${this.props.amortization.reference}</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f5f5f5; font-weight: bold; }
                        .status-badge { padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
                        .status-paid { background: #d4edda; color: #155724; }
                        .status-pending { background: #fff3cd; color: #856404; }
                        .status-overdue { background: #f8d7da; color: #721c24; }
                        .no-print { display: none; }
                        h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
                    </style>
                </head>
                <body>
                    <h1>Tabla de Amortización - ${this.props.amortization.reference}</h1>
                    <p><strong>Cliente/Proveedor:</strong> ${this.props.amortization.entity_name}</p>
                    <p><strong>Monto Total:</strong> ${this.formatCurrency(this.props.amortization.total_amount)}</p>
                    <p><strong>Fecha:</strong> ${new Date().toLocaleDateString('es-ES')}</p>
                    ${printContent}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    selectAllPending() {
        const pendingInstallments = this.state.filteredInstallments.filter(
            i => i.status === 'pending'
        );
        this.state.selectedInstallments = pendingInstallments.map(i => i.id);
    }

    async paySelectedInstallments() {
        if (this.state.selectedInstallments.length === 0) return;

        try {
            await this.amortizationService.payMultipleInstallments(
                this.state.selectedInstallments
            );
            
            await this.loadInstallments();
            this.state.selectedInstallments = [];
            this.props.onPaymentRecord?.();
            
        } catch (error) {
            console.error('Error pagando cuotas seleccionadas:', error);
        }
    }

    // Helper methods
    getRowClass(installment) {
        const classes = ['installment-row'];
        
        if (installment.status === 'paid') {
            classes.push('row-paid');
        } else if (installment.is_overdue) {
            classes.push('row-overdue');
        } else if (installment.status === 'partial') {
            classes.push('row-partial');
        }
        
        if (this.state.selectedInstallments.includes(installment.id)) {
            classes.push('row-selected');
        }
        
        return classes.join(' ');
    }

    getSortIcon(field) {
        if (this.state.sorting.field !== field) {
            return 'icon-chevrons-up-down';
        }
        return this.state.sorting.direction === 'asc' ? 'icon-chevron-up' : 'icon-chevron-down';
    }

    getStatusLabel(status) {
        const labels = {
            'pending': 'Pendiente',
            'paid': 'Pagado',
            'overdue': 'Vencido',
            'partial': 'Parcial'
        };
        return labels[status] || status;
    }

    getMethodLabel(method) {
        const labels = {
            'linear': 'Lineal',
            'french': 'Francés',
            'german': 'Alemán',
            'decreasing': 'Decreciente'
        };
        return labels[method] || method;
    }

    getPaymentPercentage(installment) {
        if (installment.total_amount === 0) return 0;
        return Math.round((installment.paid_amount / installment.total_amount) * 100);
    }

    canPay(installment) {
        return installment.status === 'pending' || installment.status === 'partial';
    }

    canEdit(installment) {
        return installment.status === 'pending' && !installment.sap_payment_entry;
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '-';
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