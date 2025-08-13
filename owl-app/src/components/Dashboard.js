// src/components/Dashboard.js
import { Component, useState, useRef, xml, onMounted, onWillUnmount } from "@odoo/owl";
import { Chart, registerables } from "chart.js";
import { AmortizationService } from "../services/AmortizationService.js";

// Registrar componentes de Chart.js
Chart.register(...registerables);

export class Dashboard extends Component {
    static template = xml`
        <div class="dashboard">
            <div class="dashboard-header">
                <h2>Dashboard - <t t-esc="props.company.name"/></h2>
                <div class="dashboard-actions">
                    <button class="btn btn-secondary" t-on-click="refreshData">
                        <i class="icon-refresh"></i> Actualizar
                    </button>
                    <button class="btn btn-primary" t-on-click="exportReport">
                        <i class="icon-download"></i> Exportar
                    </button>
                </div>
            </div>

            <div class="dashboard-metrics">
                <div class="metric-card">
                    <div class="metric-icon bg-blue">
                        <i class="icon-calculator"></i>
                    </div>
                    <div class="metric-content">
                        <h3 t-esc="formatCurrency(state.metrics.totalAmortizations)"/>
                        <p>Total Amortizaciones</p>
                        <span class="metric-trend" t-att-class="getTrendClass(state.metrics.amortizationsTrend)">
                            <t t-esc="state.metrics.amortizationsTrend"/>%
                        </span>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon bg-green">
                        <i class="icon-check-circle"></i>
                    </div>
                    <div class="metric-content">
                        <h3 t-esc="formatCurrency(state.metrics.paidAmount)"/>
                        <p>Monto Pagado</p>
                        <span class="metric-trend positive">
                            +<t t-esc="state.metrics.paidTrend"/>%
                        </span>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon bg-orange">
                        <i class="icon-clock"></i>
                    </div>
                    <div class="metric-content">
                        <h3 t-esc="formatCurrency(state.metrics.pendingAmount)"/>
                        <p>Monto Pendiente</p>
                        <span class="metric-trend" t-att-class="getTrendClass(-state.metrics.pendingTrend)">
                            <t t-esc="state.metrics.pendingTrend"/>%
                        </span>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-icon bg-red">
                        <i class="icon-alert-triangle"></i>
                    </div>
                    <div class="metric-content">
                        <h3 t-esc="state.metrics.overdueCount"/>
                        <p>Cuotas Vencidas</p>
                        <span class="metric-detail">
                            <t t-esc="formatCurrency(state.metrics.overdueAmount)"/>
                        </span>
                    </div>
                </div>
            </div>

            <div class="dashboard-charts">
                <div class="chart-container">
                    <div class="chart-header">
                        <h3>Distribución por Tipo</h3>
                        <select t-model="state.chartFilters.period" t-on-change="updateCharts">
                            <option value="month">Este Mes</option>
                            <option value="quarter">Este Trimestre</option>
                            <option value="year">Este Año</option>
                        </select>
                    </div>
                    <div class="chart-content">
                        <canvas t-ref="typeChart" width="400" height="200"></canvas>
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-header">
                        <h3>Evolución Mensual</h3>
                        <div class="chart-legend">
                            <span class="legend-item">
                                <span class="legend-color bg-blue"></span>
                                Nuevas Amortizaciones
                            </span>
                            <span class="legend-item">
                                <span class="legend-color bg-green"></span>
                                Pagos Recibidos
                            </span>
                        </div>
                    </div>
                    <div class="chart-content">
                        <canvas t-ref="evolutionChart" width="800" height="300"></canvas>
                    </div>
                </div>
            </div>

            <div class="dashboard-tables">
                <div class="table-container">
                    <div class="table-header">
                        <h3>Próximos Vencimientos</h3>
                        <a href="#" t-on-click="() => this.viewAll('upcoming')">Ver todos</a>
                    </div>
                    <div class="table-content">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Cliente/Proveedor</th>
                                    <th>Referencia</th>
                                    <th>Fecha Vencimiento</th>
                                    <th>Monto</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="state.upcomingDues" t-as="due" t-key="due.id">
                                    <td t-esc="due.entityName"/>
                                    <td t-esc="due.reference"/>
                                    <td t-esc="formatDate(due.dueDate)"/>
                                    <td t-esc="formatCurrency(due.amount)"/>
                                    <td>
                                        <span class="status-badge" t-att-class="'status-' + due.status">
                                            <t t-esc="due.statusText"/>
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-outline" t-on-click="() => this.viewDetails(due)">
                                            Ver
                                        </button>
                                    </td>
                                </tr>
                                <tr t-if="state.upcomingDues.length === 0">
                                    <td colspan="6" class="text-center text-muted">
                                        No hay vencimientos próximos
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="table-container">
                    <div class="table-header">
                        <h3>Amortizaciones Recientes</h3>
                        <a href="#" t-on-click="() => this.viewAll('recent')">Ver todas</a>
                    </div>
                    <div class="table-content">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Cliente/Proveedor</th>
                                    <th>Referencia</th>
                                    <th>Monto Total</th>
                                    <th>Estado</th>
                                    <th>Progreso</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="state.recentAmortizations" t-as="amort" t-key="amort.id">
                                    <td t-esc="formatDate(amort.startDate)"/>
                                    <td t-esc="amort.entityName"/>
                                    <td t-esc="amort.reference"/>
                                    <td t-esc="formatCurrency(amort.totalAmount)"/>
                                    <td>
                                        <span class="status-badge" t-att-class="'status-' + amort.status">
                                            <t t-esc="amort.statusText"/>
                                        </span>
                                    </td>
                                    <td>
                                        <div class="progress-container">
                                            <div class="progress-bar">
                                                <div class="progress-fill" 
                                                     t-att-style="'width: ' + getProgressPercentage(amort) + '%'">
                                                </div>
                                            </div>
                                            <span class="progress-text">
                                                <t t-esc="amort.paidInstallments"/>/<t t-esc="amort.totalInstallments"/>
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                                <tr t-if="state.recentAmortizations.length === 0">
                                    <td colspan="6" class="text-center text-muted">
                                        No hay amortizaciones recientes
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="dashboard-alerts" t-if="state.alerts.length > 0">
                <div class="alerts-header">
                    <h3>Alertas y Notificaciones</h3>
                </div>
                <div class="alerts-content">
                    <div t-foreach="state.alerts" t-as="alert" t-key="alert.id"
                         class="alert" t-att-class="'alert-' + alert.type">
                        <div class="alert-icon">
                            <i t-att-class="getAlertIcon(alert.type)"></i>
                        </div>
                        <div class="alert-content">
                            <h4 t-esc="alert.title"/>
                            <p t-esc="alert.message"/>
                            <span class="alert-time" t-esc="formatDateTime(alert.timestamp)"/>
                        </div>
                        <button class="alert-close" t-on-click="() => this.dismissAlert(alert.id)">
                            <i class="icon-x"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    setup() {
        this.state = useState({
            loading: false,
            metrics: {
                totalAmortizations: 0,
                amortizationsTrend: 0,
                paidAmount: 0,
                paidTrend: 0,
                pendingAmount: 0,
                pendingTrend: 0,
                overdueCount: 0,
                overdueAmount: 0
            },
            chartFilters: {
                period: 'month'
            },
            upcomingDues: [],
            recentAmortizations: [],
            alerts: []
        });

        this.amortizationService = new AmortizationService();
        this.charts = {};
        
        onMounted(() => {
            this.loadDashboardData();
            this.setupCharts();
        });

        onWillUnmount(() => {
            this.destroyCharts();
        });
    }

    async loadDashboardData() {
        if (!this.props.company) return;

        this.state.loading = true;
        try {
            // Cargar métricas
            const metrics = await this.amortizationService.getDashboardMetrics(
                this.props.company.id
            );
            this.state.metrics = metrics;

            // Cargar próximos vencimientos
            const upcomingDues = await this.amortizationService.getUpcomingDues(
                this.props.company.id,
                { limit: 5 }
            );
            this.state.upcomingDues = upcomingDues;

            // Cargar amortizaciones recientes
            const recentAmortizations = await this.amortizationService.getRecentAmortizations(
                this.props.company.id,
                { limit: 5 }
            );
            this.state.recentAmortizations = recentAmortizations;

            // Cargar alertas
            const alerts = await this.amortizationService.getAlerts(
                this.props.company.id
            );
            this.state.alerts = alerts;

            // Actualizar gráficos
            this.updateCharts();

        } catch (error) {
            console.error('Error cargando datos del dashboard:', error);
            this.showError('Error al cargar datos del dashboard');
        } finally {
            this.state.loading = false;
        }
    }

    setupCharts() {
        this.setupTypeChart();
        this.setupEvolutionChart();
    }

    setupTypeChart() {
        const ctx = this.typeChartRef.el;
        if (!ctx) return;

        this.charts.type = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Clientes', 'Proveedores'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: [
                        '#3B82F6',
                        '#10B981'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    setupEvolutionChart() {
        const ctx = this.evolutionChartRef.el;
        if (!ctx) return;

        this.charts.evolution = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Nuevas Amortizaciones',
                        data: [],
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Pagos Recibidos',
                        data: [],
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this.formatCurrency(value)
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${this.formatCurrency(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    async updateCharts() {
        if (!this.props.company) return;

        try {
            // Obtener datos de distribución por tipo
            const typeData = await this.amortizationService.getTypeDistribution(
                this.props.company.id,
                this.state.chartFilters.period
            );

            if (this.charts.type) {
                this.charts.type.data.datasets[0].data = [
                    typeData.clientes || 0,
                    typeData.proveedores || 0
                ];
                this.charts.type.update();
            }

            // Obtener datos de evolución mensual
            const evolutionData = await this.amortizationService.getEvolutionData(
                this.props.company.id,
                this.state.chartFilters.period
            );

            if (this.charts.evolution) {
                this.charts.evolution.data.labels = evolutionData.labels || [];
                this.charts.evolution.data.datasets[0].data = evolutionData.newAmortizations || [];
                this.charts.evolution.data.datasets[1].data = evolutionData.payments || [];
                this.charts.evolution.update();
            }

        } catch (error) {
            console.error('Error actualizando gráficos:', error);
        }
    }

    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = {};
    }

    async refreshData() {
        await this.loadDashboardData();
    }

    async exportReport() {
        try {
            const reportData = await this.amortizationService.generateDashboardReport(
                this.props.company.id
            );
            
            // Crear y descargar archivo
            const blob = new Blob([reportData], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard-report-${this.props.company.id}-${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error exportando reporte:', error);
            this.showError('Error al exportar reporte');
        }
    }

    viewDetails(item) {
        // Emitir evento para mostrar detalles
        this.props.onViewDetails?.(item);
    }

    viewAll(type) {
        // Emitir evento para mostrar vista completa
        this.props.onViewAll?.(type);
    }

    dismissAlert(alertId) {
        this.state.alerts = this.state.alerts.filter(alert => alert.id !== alertId);
    }

    // Métodos auxiliares
    get typeChartRef() {
        return this.refs ? this.refs.typeChart : null;
    }

    get evolutionChartRef() {
        return this.refs ? this.refs.evolutionChart : null;
    }

    getTrendClass(trend) {
        if (trend > 0) return 'positive';
        if (trend < 0) return 'negative';
        return 'neutral';
    }

    getProgressPercentage(amortization) {
        if (amortization.totalInstallments === 0) return 0;
        return Math.round((amortization.paidInstallments / amortization.totalInstallments) * 100);
    }

    getAlertIcon(type) {
        const icons = {
            'warning': 'icon-alert-triangle',
            'error': 'icon-alert-circle',
            'info': 'icon-info',
            'success': 'icon-check-circle'
        };
        return icons[type] || 'icon-info';
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '-';
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: this.props.company?.currency || 'EUR',
            minimumFractionDigits: 2
        }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('es-ES');
    }

    formatDateTime(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString('es-ES');
    }

    showError(message) {
        // Implementar sistema de notificaciones
        alert(message); // Temporal
    }
}