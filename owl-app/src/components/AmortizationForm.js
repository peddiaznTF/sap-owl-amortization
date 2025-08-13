// src/components/AmortizationForm.js
import { Component, useState, useRef, xml, onMounted } from "@odoo/owl";
import { AmortizationService } from "../services/AmortizationService.js";
import { SAPService } from "../services/SAPService.js";

export class AmortizationForm extends Component {
    static template = xml`
        <div class="amortization-form">
            <div class="form-header">
                <h3>
                    <span t-if="!props.amortization">Nueva Amortización</span>
                    <span t-else="">Editar Amortización</span>
                    - <t t-esc="getTypeLabel()"/>
                </h3>
                <button class="btn-close" t-on-click="props.onCancel">
                    <i class="icon-x"></i>
                </button>
            </div>

            <form class="form-content" t-on-submit.prevent="handleSubmit">
                <div class="form-sections">
                    <!-- Sección: Información Básica -->
                    <div class="form-section">
                        <h4>Información Básica</h4>
                        <div class="form-grid">
                            <div class="form-group">
                                <label for="reference" class="required">Referencia</label>
                                <input 
                                    type="text" 
                                    id="reference" 
                                    t-model="state.form.reference"
                                    class="form-control"
                                    placeholder="Ej: AMORT-2024-001"
                                    required=""
                                    t-att-readonly="props.amortization"
                                />
                                <span t-if="state.errors.reference" class="field-error">
                                    <t t-esc="state.errors.reference"/>
                                </span>
                            </div>

                            <div class="form-group">
                                <label for="entity" class="required">
                                    <span t-if="props.type === 'clientes'">Cliente</span>
                                    <span t-else="">Proveedor</span>
                                </label>
                                <select 
                                    id="entity" 
                                    t-model="state.form.entity_id"
                                    class="form-control"
                                    required=""
                                    t-on-change="onEntityChange"
                                >
                                    <option value="">Seleccionar...</option>
                                    <option t-foreach="state.entities" t-as="entity" 
                                            t-key="entity.id" t-att-value="entity.id">
                                        <t t-esc="entity.sap_card_code"/> - <t t-esc="entity.name"/>
                                    </option>
                                </select>
                                <span t-if="state.errors.entity_id" class="field-error">
                                    <t t-esc="state.errors.entity_id"/>
                                </span>
                            </div>

                            <div class="form-group full-width">
                                <label for="description">Descripción</label>
                                <textarea 
                                    id="description" 
                                    t-model="state.form.description"
                                    class="form-control"
                                    rows="3"
                                    placeholder="Descripción de la amortización..."
                                ></textarea>
                            </div>
                        </div>
                    </div>

                    <!-- Sección: Montos y Configuración -->
                    <div class="form-section">
                        <h4>Configuración Financiera</h4>
                        <div class="form-grid">
                            <div class="form-group">
                                <label for="total_amount" class="required">Monto Total</label>
                                <div class="input-group">
                                    <span class="input-group-text">
                                        <t t-esc="props.company.currency"/>
                                    </span>
                                    <input 
                                        type="number" 
                                        id="total_amount" 
                                        t-model="state.form.total_amount"
                                        class="form-control"
                                        step="0.01"
                                        min="0"
                                        required=""
                                        t-on-input="onAmountChange"
                                    />
                                </div>
                                <span t-if="state.errors.total_amount" class="field-error">
                                    <t t-esc="state.errors.total_amount"/>
                                </span>
                            </div>

                            <div class="form-group">
                                <label for="total_installments" class="required">Número de Cuotas</label>
                                <input 
                                    type="number" 
                                    id="total_installments" 
                                    t-model="state.form.total_installments"
                                    class="form-control"
                                    min="1"
                                    max="999"
                                    required=""
                                    t-on-input="onInstallmentsChange"
                                />
                                <span t-if="state.errors.total_installments" class="field-error">
                                    <t t-esc="state.errors.total_installments"/>
                                </span>
                            </div>

                            <div class="form-group">
                                <label for="interest_rate">Tasa de Interés (%)</label>
                                <input 
                                    type="number" 
                                    id="interest_rate" 
                                    t-model="state.form.interest_rate"
                                    class="form-control"
                                    step="0.01"
                                    min="0"
                                    max="100"
                                    t-on-input="onInterestChange"
                                />
                                <span t-if="state.errors.interest_rate" class="field-error">
                                    <t t-esc="state.errors.interest_rate"/>
                                </span>
                            </div>

                            <div class="form-group">
                                <label for="amortization_method">Método de Amortización</label>
                                <select 
                                    id="amortization_method" 
                                    t-model="state.form.amortization_method"
                                    class="form-control"
                                    t-on-change="onMethodChange"
                                >
                                    <option value="linear">Lineal (Cuotas de capital iguales)</option>
                                    <option value="french">Francés (Cuotas totales iguales)</option>
                                    <option value="german">Alemán (Cuotas decrecientes)</option>
                                    <option value="decreasing">Decreciente</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="frequency">Frecuencia de Pago</label>
                                <select 
                                    id="frequency" 
                                    t-model="state.form.frequency"
                                    class="form-control"
                                    t-on-change="onFrequencyChange"
                                >
                                    <option value="monthly">Mensual</option>
                                    <option value="quarterly">Trimestral</option>
                                    <option value="biannual">Semestral</option>
                                    <option value="annual">Anual</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="start_date" class="required">Fecha de Inicio</label>
                                <input 
                                    type="date" 
                                    id="start_date" 
                                    t-model="state.form.start_date"
                                    class="form-control"
                                    required=""
                                    t-on-change="onStartDateChange"
                                />
                                <span t-if="state.errors.start_date" class="field-error">
                                    <t t-esc="state.errors.start_date"/>
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- Sección: Integración SAP -->
                    <div class="form-section" t-if="!props.amortization">
                        <h4>Integración SAP Business One</h4>
                        <div class="form-grid">
                            <div class="form-group">
                                <label for="sap_document">Documento Base SAP</label>
                                <select 
                                    id="sap_document" 
                                    t-model="state.form.sap_doc_entry"
                                    class="form-control"
                                    t-on-change="onSAPDocumentChange"
                                >
                                    <option value="">Sin documento base</option>
                                    <option t-foreach="state.sapDocuments" t-as="doc" 
                                            t-key="doc.DocEntry" t-att-value="doc.DocEntry">
                                        <t t-esc="doc.DocNum"/> - <t t-esc="doc.CardName"/> - 
                                        <t t-esc="formatCurrency(doc.DocTotal)"/>
                                    </option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>
                                    <input 
                                        type="checkbox" 
                                        t-model="state.form.auto_payment"
                                        class="form-check"
                                    />
                                    Crear pagos automáticamente en SAP
                                </label>
                            </div>

                            <div class="form-group">
                                <label>
                                    <input 
                                        type="checkbox" 
                                        t-model="state.form.send_notifications"
                                        class="form-check"
                                    />
                                    Enviar notificaciones de vencimiento
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- Sección: Preview de Cuotas -->
                    <div class="form-section" t-if="state.preview.length > 0">
                        <h4>
                            Vista Previa de Cuotas
                            <button type="button" class="btn btn-sm btn-secondary" t-on-click="calculatePreview">
                                Recalcular
                            </button>
                        </h4>
                        <div class="preview-table">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Cuota</th>
                                        <th>Fecha Venc.</th>
                                        <th>Capital</th>
                                        <th>Interés</th>
                                        <th>Total Cuota</th>
                                        <th>Saldo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr t-foreach="state.preview.slice(0, 5)" t-as="installment" t-key="installment.number">
                                        <td t-esc="installment.number"/>
                                        <td t-esc="formatDate(installment.dueDate)"/>
                                        <td t-esc="formatCurrency(installment.principal)"/>
                                        <td t-esc="formatCurrency(installment.interest)"/>
                                        <td t-esc="formatCurrency(installment.total)"/>
                                        <td t-esc="formatCurrency(installment.balance)"/>
                                    </tr>
                                    <tr t-if="state.preview.length > 5">
                                        <td colspan="6" class="text-center text-muted">
                                            ... y <t t-esc="state.preview.length - 5"/> cuotas más
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="form-footer">
                    <button type="button" class="btn btn-secondary" t-on-click="props.onCancel">
                        Cancelar
                    </button>
                    <button type="button" class="btn btn-outline" t-on-click="calculatePreview">
                        Vista Previa
                    </button>
                    <button type="submit" class="btn btn-primary" t-att-disabled="state.loading">
                        <span t-if="state.loading">
                            <i class="icon-loader spinning"></i> Guardando...
                        </span>
                        <span t-else="">
                            <span t-if="!props.amortization">Crear Amortización</span>
                            <span t-else="">Actualizar Amortización</span>
                        </span>
                    </button>
                </div>
            </form>
        </div>
    `;

    setup() {
        this.state = useState({
            loading: false,
            entities: [],
            sapDocuments: [],
            preview: [],
            form: {
                reference: '',
                entity_id: '',
                description: '',
                total_amount: 0,
                total_installments: 12,
                interest_rate: 0,
                amortization_method: 'french',
                frequency: 'monthly',
                start_date: new Date().toISOString().split('T')[0],
                sap_doc_entry: '',
                auto_payment: false,
                send_notifications: true
            },
            errors: {}
        });

        this.amortizationService = new AmortizationService();
        this.sapService = new SAPService();

        onMounted(() => {
            this.loadFormData();
            if (this.props.amortization) {
                this.populateForm();
            }
        });
    }

    async loadFormData() {
        try {
            // Cargar entidades (clientes o proveedores)
            const entities = await this.sapService.getBusinessPartners(
                this.props.type === 'clientes' ? 'C' : 'S'
            );
            this.state.entities = entities;

            // Cargar documentos SAP pendientes
            if (!this.props.amortization) {
                const documents = await this.sapService.getPendingDocuments(
                    this.props.type,
                    this.props.company.id
                );
                this.state.sapDocuments = documents;
            }

        } catch (error) {
            console.error('Error cargando datos del formulario:', error);
        }
    }

    populateForm() {
        if (!this.props.amortization) return;

        const amort = this.props.amortization;
        this.state.form = {
            reference: amort.reference || '',
            entity_id: amort.entity_id || '',
            description: amort.description || '',
            total_amount: amort.total_amount || 0,
            total_installments: amort.total_installments || 12,
            interest_rate: amort.interest_rate || 0,
            amortization_method: amort.amortization_method || 'french',
            frequency: amort.frequency || 'monthly',
            start_date: amort.start_date || new Date().toISOString().split('T')[0],
            sap_doc_entry: amort.sap_doc_entry || '',
            auto_payment: amort.auto_payment || false,
            send_notifications: amort.send_notifications !== false
        };
    }

    async handleSubmit() {
        if (!this.validateForm()) return;

        this.state.loading = true;
        try {
            const formData = {
                ...this.state.form,
                company_id: this.props.company.id,
                type: this.props.type
            };

            let result;
            if (this.props.amortization) {
                result = await this.amortizationService.updateAmortization(
                    this.props.amortization.id,
                    formData
                );
            } else {
                result = await this.amortizationService.createAmortization(formData);
            }

            this.props.onSave(result);

        } catch (error) {
            console.error('Error guardando amortización:', error);
            this.showError('Error al guardar la amortización');
        } finally {
            this.state.loading = false;
        }
    }

    validateForm() {
        const errors = {};
        const form = this.state.form;

        if (!form.reference?.trim()) {
            errors.reference = 'La referencia es requerida';
        }

        if (!form.entity_id) {
            errors.entity_id = 'Debe seleccionar una entidad';
        }

        if (!form.total_amount || form.total_amount <= 0) {
            errors.total_amount = 'El monto debe ser mayor a cero';
        }

        if (!form.total_installments || form.total_installments < 1) {
            errors.total_installments = 'Debe tener al menos una cuota';
        }

        if (!form.start_date) {
            errors.start_date = 'La fecha de inicio es requerida';
        }

        if (form.interest_rate < 0 || form.interest_rate > 100) {
            errors.interest_rate = 'La tasa debe estar entre 0 y 100%';
        }

        this.state.errors = errors;
        return Object.keys(errors).length === 0;
    }

    async calculatePreview() {
        if (!this.state.form.total_amount || !this.state.form.total_installments) {
            return;
        }

        try {
            const preview = await this.amortizationService.calculateInstallments({
                total_amount: this.state.form.total_amount,
                total_installments: this.state.form.total_installments,
                interest_rate: this.state.form.interest_rate,
                amortization_method: this.state.form.amortization_method,
                frequency: this.state.form.frequency,
                start_date: this.state.form.start_date
            });

            this.state.preview = preview;

        } catch (error) {
            console.error('Error calculando vista previa:', error);
        }
    }

    // Event Handlers
    onEntityChange() {
        // Limpiar documento SAP al cambiar entidad
        this.state.form.sap_doc_entry = '';
        this.loadSAPDocuments();
    }

    onAmountChange() {
        this.calculatePreview();
    }

    onInstallmentsChange() {
        this.calculatePreview();
    }

    onInterestChange() {
        this.calculatePreview();
    }

    onMethodChange() {
        this.calculatePreview();
    }

    onFrequencyChange() {
        this.calculatePreview();
    }

    onStartDateChange() {
        this.calculatePreview();
    }

    async onSAPDocumentChange() {
        if (!this.state.form.sap_doc_entry) return;

        try {
            const document = this.state.sapDocuments.find(
                doc => doc.DocEntry == this.state.form.sap_doc_entry
            );

            if (document) {
                // Auto-rellenar campos desde el documento SAP
                this.state.form.total_amount = document.DocTotal - document.PaidToDate;
                this.state.form.entity_id = this.findEntityByCardCode(document.CardCode)?.id || '';
                
                if (!this.state.form.reference) {
                    this.state.form.reference = `AMORT-${document.DocNum}`;
                }

                this.calculatePreview();
            }

        } catch (error) {
            console.error('Error procesando documento SAP:', error);
        }
    }

    async loadSAPDocuments() {
        if (!this.state.form.entity_id) return;

        try {
            const entity = this.state.entities.find(e => e.id === this.state.form.entity_id);
            if (entity) {
                const documents = await this.sapService.getEntityDocuments(
                    entity.sap_card_code,
                    this.props.type
                );
                this.state.sapDocuments = documents;
            }
        } catch (error) {
            console.error('Error cargando documentos SAP:', error);
        }
    }

    // Helper methods
    getTypeLabel() {
        return this.props.type === 'clientes' ? 'Clientes' : 'Proveedores';
    }

    findEntityByCardCode(cardCode) {
        return this.state.entities.find(entity => entity.sap_card_code === cardCode);
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '-';
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: this.props.company?.currency || 'EUR'
        }).format(amount);
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('es-ES');
    }

    showError(message) {
        alert(message); // Temporal - implementar sistema de notificaciones
    }
}