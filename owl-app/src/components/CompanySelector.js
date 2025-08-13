// src/components/CompanySelector.js
import { Component, useState, xml, onMounted } from "@odoo/owl";

export class CompanySelector extends Component {
    static template = xml`
        <div class="company-selector">
            <label for="company-select">Compañía:</label>
            <select 
                id="company-select" 
                t-model="state.selectedCompanyId"
                t-on-change="onCompanyChange" 
                t-att-disabled="state.loading || props.companies.length === 0"
                class="form-control"
            >
                <option value="">
                    <span t-if="state.loading">Cargando compañías...</span>
                    <span t-elif="props.companies.length === 0">No hay compañías disponibles</span>
                    <span t-else="">Seleccionar compañía...</span>
                </option>
                <option 
                    t-foreach="props.companies" 
                    t-as="company" 
                    t-key="company.id" 
                    t-att-value="company.id"
                    t-att-selected="company.id === props.selectedCompany?.id"
                >
                    <t t-esc="company.name"/> 
                    <span t-if="company.currency" class="currency-info">(<t t-esc="company.currency"/>)</span>
                </option>
            </select>
            
            <div t-if="props.selectedCompany" class="company-info">
                <span class="company-details">
                    <i class="icon-building"></i>
                    <t t-esc="props.selectedCompany.name"/>
                </span>
                <span t-if="props.selectedCompany.sap_database" class="sap-info">
                    SAP: <t t-esc="props.selectedCompany.sap_database"/>
                </span>
            </div>
            
            <div t-if="state.error" class="error-message">
                <i class="icon-alert-circle"></i>
                <span t-esc="state.error"/>
            </div>
        </div>
    `;

    setup() {
        this.state = useState({
            selectedCompanyId: this.props.selectedCompany?.id || '',
            loading: false,
            error: null
        });

        onMounted(() => {
            // Sincronizar estado inicial
            if (this.props.selectedCompany) {
                this.state.selectedCompanyId = this.props.selectedCompany.id;
            }
        });
    }

    async onCompanyChange(event) {
        const companyId = event.target.value;
        
        if (!companyId) {
            this.state.selectedCompanyId = '';
            this.props.onCompanyChange?.(null);
            return;
        }

        this.state.loading = true;
        this.state.error = null;

        try {
            const company = this.props.companies.find(c => c.id === companyId);
            
            if (!company) {
                throw new Error('Compañía no encontrada');
            }

            this.state.selectedCompanyId = companyId;
            
            // Llamar al callback del padre con la compañía seleccionada
            await this.props.onCompanyChange?.(company);

        } catch (error) {
            console.error('Error al cambiar compañía:', error);
            this.state.error = 'Error al conectar con la compañía seleccionada';
            this.state.selectedCompanyId = this.props.selectedCompany?.id || '';
        } finally {
            this.state.loading = false;
        }
    }

    willUpdateProps(nextProps) {
        // Sincronizar cuando cambie la selección desde el padre
        if (nextProps.selectedCompany?.id !== this.state.selectedCompanyId) {
            this.state.selectedCompanyId = nextProps.selectedCompany?.id || '';
        }
    }
}