/ src/components/LoginForm.js
import { Component, useState, useRef, xml } from "@odoo/owl";
import { AuthService } from "../services/AuthService.js";

export class LoginForm extends Component {
    static template = xml`
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <div class="login-logo">
                        <i class="icon-briefcase"></i>
                    </div>
                    <h1>Sistema de Amortización</h1>
                    <p>SAP Business One + OWL</p>
                </div>

                <form class="login-form" t-on-submit.prevent="handleLogin">
                    <div class="form-group">
                        <label for="email">Email</label>
                        <div class="input-wrapper">
                            <i class="icon-mail input-icon"></i>
                            <input 
                                type="email" 
                                id="email" 
                                t-model="state.form.email"
                                t-ref="emailInput"
                                class="form-control"
                                placeholder="tu.email@empresa.com"
                                required=""
                                autocomplete="email"
                                t-att-disabled="state.loading"
                            />
                        </div>
                        <span t-if="state.errors.email" class="field-error">
                            <t t-esc="state.errors.email"/>
                        </span>
                    </div>

                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <div class="input-wrapper">
                            <i class="icon-lock input-icon"></i>
                            <input 
                                t-att-type="state.showPassword ? 'text' : 'password'" 
                                id="password" 
                                t-model="state.form.password"
                                class="form-control"
                                placeholder="••••••••"
                                required=""
                                autocomplete="current-password"
                                t-att-disabled="state.loading"
                            />
                            <button 
                                type="button" 
                                class="password-toggle"
                                t-on-click="togglePasswordVisibility"
                                t-att-disabled="state.loading">
                                <i t-att-class="state.showPassword ? 'icon-eye-off' : 'icon-eye'"></i>
                            </button>
                        </div>
                        <span t-if="state.errors.password" class="field-error">
                            <t t-esc="state.errors.password"/>
                        </span>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-wrapper">
                            <input 
                                type="checkbox" 
                                t-model="state.form.remember"
                                t-att-disabled="state.loading"
                            />
                            <span class="checkmark"></span>
                            Recordarme
                        </label>
                        
                        <a href="#" class="forgot-password" t-on-click="showForgotPassword">
                            ¿Olvidaste tu contraseña?
                        </a>
                    </div>

                    <div t-if="state.errorMessage" class="error-message">
                        <i class="icon-alert-circle"></i>
                        <span t-esc="state.errorMessage"/>
                    </div>

                    <button 
                        type="submit" 
                        class="btn btn-primary btn-login"
                        t-att-disabled="state.loading"
                    >
                        <span t-if="state.loading">
                            <i class="icon-loader spinning"></i>
                            Iniciando sesión...
                        </span>
                        <span t-else="">
                            <i class="icon-log-in"></i>
                            Iniciar Sesión
                        </span>
                    </button>
                </form>

                <div class="login-footer">
                    <p>¿No tienes cuenta? <a href="#" t-on-click="showRegister">Regístrate aquí</a></p>
                    <div class="version-info">
                        v1.0.0 - Desarrollo
                    </div>
                </div>
            </div>

            <!-- Formulario de recuperación de contraseña -->
            <div t-if="state.showForgotForm" class="modal-overlay" t-on-click="closeForgotPassword">
                <div class="modal-content" t-on-click.stop="">
                    <ForgotPasswordForm 
                        onCancel="closeForgotPassword"
                        onSuccess="onForgotPasswordSuccess"
                    />
                </div>
            </div>

            <!-- Formulario de registro -->
            <div t-if="state.showRegisterForm" class="modal-overlay" t-on-click="closeRegister">
                <div class="modal-content" t-on-click.stop="">
                    <RegisterForm 
                        onCancel="closeRegister"
                        onSuccess="onRegisterSuccess"
                    />
                </div>
            </div>
        </div>
    `;

    static components = { ForgotPasswordForm, RegisterForm };

    setup() {
        this.state = useState({
            loading: false,
            showPassword: false,
            showForgotForm: false,
            showRegisterForm: false,
            errorMessage: '',
            form: {
                email: '',
                password: '',
                remember: false
            },
            errors: {}
        });

        this.authService = new AuthService();

        // Auto-focus en email al montar
        this.mounted(() => {
            this.emailInputRef?.el?.focus();
        });

        // Cargar credenciales recordadas
        this.loadRememberedCredentials();
    }

    get emailInputRef() {
        return this.refs?.emailInput;
    }

    loadRememberedCredentials() {
        const rememberedEmail = localStorage.getItem('remembered_email');
        if (rememberedEmail) {
            this.state.form.email = rememberedEmail;
            this.state.form.remember = true;
        }
    }

    async handleLogin() {
        if (!this.validateForm()) return;

        this.state.loading = true;
        this.state.errorMessage = '';

        try {
            const response = await this.authService.login({
                email: this.state.form.email,
                password: this.state.form.password
            });

            // Guardar token
            this.authService.setToken(response.access_token);

            // Recordar email si está marcado
            if (this.state.form.remember) {
                localStorage.setItem('remembered_email', this.state.form.email);
            } else {
                localStorage.removeItem('remembered_email');
            }

            // Emitir evento de login exitoso
            this.props.onLoginSuccess?.(response.user);

            // Mostrar mensaje de éxito
            this.showSuccessMessage(`¡Bienvenido, ${response.user.full_name}!`);

        } catch (error) {
            console.error('Error en login:', error);
            
            if (error.message.includes('401')) {
                this.state.errorMessage = 'Email o contraseña incorrectos';
            } else if (error.message.includes('400')) {
                this.state.errorMessage = 'Usuario inactivo';
            } else if (error.message.includes('network')) {
                this.state.errorMessage = 'Error de conexión. Verifique su red.';
            } else {
                this.state.errorMessage = 'Error inesperado. Intente nuevamente.';
            }
        } finally {
            this.state.loading = false;
        }
    }

    validateForm() {
        const errors = {};
        const form = this.state.form;

        // Validar email
        if (!form.email) {
            errors.email = 'El email es requerido';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
            errors.email = 'Formato de email inválido';
        }

        // Validar contraseña
        if (!form.password) {
            errors.password = 'La contraseña es requerida';
        } else if (form.password.length < 6) {
            errors.password = 'La contraseña debe tener al menos 6 caracteres';
        }

        this.state.errors = errors;
        return Object.keys(errors).length === 0;
    }

    togglePasswordVisibility() {
        this.state.showPassword = !this.state.showPassword;
    }

    showForgotPassword(event) {
        event.preventDefault();
        this.state.showForgotForm = true;
    }

    closeForgotPassword() {
        this.state.showForgotForm = false;
    }

    onForgotPasswordSuccess() {
        this.closeForgotPassword();
        this.showSuccessMessage('Se ha enviado un enlace de recuperación a tu email');
    }

    showRegister(event) {
        event.preventDefault();
        this.state.showRegisterForm = true;
    }

    closeRegister() {
        this.state.showRegisterForm = false;
    }

    onRegisterSuccess(user) {
        this.closeRegister();
        this.state.form.email = user.email;
        this.showSuccessMessage('Cuenta creada exitosamente. Puedes iniciar sesión ahora.');
    }

    showSuccessMessage(message) {
        // Implementar sistema de notificaciones
        console.log('Success:', message);
    }
}

// Componente de recuperación de contraseña
class ForgotPasswordForm extends Component {
    static template = xml`
        <div class="forgot-password-form">
            <div class="form-header">
                <h3>Recuperar Contraseña</h3>
                <button class="btn-close" t-on-click="props.onCancel">
                    <i class="icon-x"></i>
                </button>
            </div>

            <form t-on-submit.prevent="handleSubmit">
                <div class="form-content">
                    <p class="form-description">
                        Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña.
                    </p>

                    <div class="form-group">
                        <label for="email">Email</label>
                        <input 
                            type="email" 
                            id="email" 
                            t-model="state.email"
                            class="form-control"
                            placeholder="tu.email@empresa.com"
                            required=""
                            t-att-disabled="state.loading"
                        />
                        <span t-if="state.error" class="field-error">
                            <t t-esc="state.error"/>
                        </span>
                    </div>
                </div>

                <div class="form-footer">
                    <button type="button" class="btn btn-secondary" t-on-click="props.onCancel">
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" t-att-disabled="state.loading">
                        <span t-if="state.loading">
                            <i class="icon-loader spinning"></i>
                            Enviando...
                        </span>
                        <span t-else="">
                            Enviar Enlace
                        </span>
                    </button>
                </div>
            </form>
        </div>
    `;

    setup() {
        this.state = useState({
            email: '',
            loading: false,
            error: ''
        });

        this.authService = new AuthService();
    }

    async handleSubmit() {
        if (!this.state.email) {
            this.state.error = 'El email es requerido';
            return;
        }

        this.state.loading = true;
        this.state.error = '';

        try {
            await this.authService.forgotPassword(this.state.email);
            this.props.onSuccess?.();
        } catch (error) {
            console.error('Error en forgot password:', error);
            this.state.error = 'Error enviando email. Intente nuevamente.';
        } finally {
            this.state.loading = false;
        }
    }
}

// Componente de registro
class RegisterForm extends Component {
    static template = xml`
        <div class="register-form">
            <div class="form-header">
                <h3>Crear Cuenta</h3>
                <button class="btn-close" t-on-click="props.onCancel">
                    <i class="icon-x"></i>
                </button>
            </div>

            <form t-on-submit.prevent="handleSubmit">
                <div class="form-content">
                    <div class="form-group">
                        <label for="fullName">Nombre Completo</label>
                        <input 
                            type="text" 
                            id="fullName" 
                            t-model="state.form.fullName"
                            class="form-control"
                            placeholder="Juan Pérez"
                            required=""
                            t-att-disabled="state.loading"
                        />
                        <span t-if="state.errors.fullName" class="field-error">
                            <t t-esc="state.errors.fullName"/>
                        </span>
                    </div>

                    <div class="form-group">
                        <label for="email">Email</label>
                        <input 
                            type="email" 
                            id="email" 
                            t-model="state.form.email"
                            class="form-control"
                            placeholder="juan@empresa.com"
                            required=""
                            t-att-disabled="state.loading"
                        />
                        <span t-if="state.errors.email" class="field-error">
                            <t t-esc="state.errors.email"/>
                        </span>
                    </div>

                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input 
                            type="password" 
                            id="password" 
                            t-model="state.form.password"
                            class="form-control"
                            placeholder="••••••••"
                            required=""
                            t-att-disabled="state.loading"
                        />
                        <span t-if="state.errors.password" class="field-error">
                            <t t-esc="state.errors.password"/>
                        </span>
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword">Confirmar Contraseña</label>
                        <input 
                            type="password" 
                            id="confirmPassword" 
                            t-model="state.form.confirmPassword"
                            class="form-control"
                            placeholder="••••••••"
                            required=""
                            t-att-disabled="state.loading"
                        />
                        <span t-if="state.errors.confirmPassword" class="field-error">
                            <t t-esc="state.errors.confirmPassword"/>
                        </span>
                    </div>

                    <div class="form-group">
                        <label class="checkbox-wrapper">
                            <input 
                                type="checkbox" 
                                t-model="state.form.acceptTerms"
                                t-att-disabled="state.loading"
                                required=""
                            />
                            <span class="checkmark"></span>
                            Acepto los términos y condiciones
                        </label>
                        <span t-if="state.errors.acceptTerms" class="field-error">
                            <t t-esc="state.errors.acceptTerms"/>
                        </span>
                    </div>

                    <div t-if="state.errorMessage" class="error-message">
                        <i class="icon-alert-circle"></i>
                        <span t-esc="state.errorMessage"/>
                    </div>
                </div>

                <div class="form-footer">
                    <button type="button" class="btn btn-secondary" t-on-click="props.onCancel">
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" t-att-disabled="state.loading">
                        <span t-if="state.loading">
                            <i class="icon-loader spinning"></i>
                            Creando cuenta...
                        </span>
                        <span t-else="">
                            Crear Cuenta
                        </span>
                    </button>
                </div>
            </form>
        </div>
    `;

    setup() {
        this.state = useState({
            loading: false,
            errorMessage: '',
            form: {
                fullName: '',
                email: '',
                password: '',
                confirmPassword: '',
                acceptTerms: false
            },
            errors: {}
        });

        this.authService = new AuthService();
    }

    async handleSubmit() {
        if (!this.validateForm()) return;

        this.state.loading = true;
        this.state.errorMessage = '';

        try {
            const response = await this.authService.register({
                full_name: this.state.form.fullName,
                email: this.state.form.email,
                password: this.state.form.password,
                confirm_password: this.state.form.confirmPassword
            });

            this.props.onSuccess?.(response);

        } catch (error) {
            console.error('Error en registro:', error);
            
            if (error.message.includes('already registered')) {
                this.state.errorMessage = 'Este email ya está registrado';
            } else {
                this.state.errorMessage = 'Error creando cuenta. Intente nuevamente.';
            }
        } finally {
            this.state.loading = false;
        }
    }

    validateForm() {
        const errors = {};
        const form = this.state.form;

        // Validar nombre
        if (!form.fullName.trim()) {
            errors.fullName = 'El nombre es requerido';
        }

        // Validar email
        if (!form.email) {
            errors.email = 'El email es requerido';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
            errors.email = 'Formato de email inválido';
        }

        // Validar contraseña
        if (!form.password) {
            errors.password = 'La contraseña es requerida';
        } else if (form.password.length < 8) {
            errors.password = 'La contraseña debe tener al menos 8 caracteres';
        }

        // Validar confirmación de contraseña
        if (!form.confirmPassword) {
            errors.confirmPassword = 'Debe confirmar la contraseña';
        } else if (form.password !== form.confirmPassword) {
            errors.confirmPassword = 'Las contraseñas no coinciden';
        }

        // Validar términos
        if (!form.acceptTerms) {
            errors.acceptTerms = 'Debe aceptar los términos y condiciones';
        }

        this.state.errors = errors;
        return Object.keys(errors).length === 0;
    }
}