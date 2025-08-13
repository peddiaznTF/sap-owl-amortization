// src/services/AuthService.js
export class AuthService {
    constructor() {
        this.baseUrl = 'http://localhost:8000/auth';
        this.tokenKey = 'auth_token';
        this.userKey = 'current_user';
    }

    // Obtener token almacenado
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // Guardar token
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    // Eliminar token
    removeToken() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    // Obtener usuario actual
    getCurrentUser() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    // Guardar usuario actual
    setCurrentUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    // Verificar si está autenticado
    isAuthenticated() {
        return !!this.getToken();
    }

    // Headers para peticiones autenticadas
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    }

    // Login
    async login(credentials) {
        const response = await fetch(`${this.baseUrl}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });

        if (!response.ok) {
            throw new Error(`Login failed: ${response.status}`);
        }

        const data = await response.json();
        this.setToken(data.access_token);
        this.setCurrentUser(data.user);
        return data;
    }

    // Registro
    async register(userData) {
        const response = await fetch(`${this.baseUrl}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            throw new Error(`Registration failed: ${response.status}`);
        }

        return await response.json();
    }

    // Cerrar sesión
    async logout() {
        try {
            await fetch(`${this.baseUrl}/logout`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
        } catch (error) {
            console.error('Error during logout:', error);
        } finally {
            this.removeToken();
        }
    }

    // Renovar token
    async refreshToken() {
        const response = await fetch(`${this.baseUrl}/refresh`, {
            method: 'POST',
            headers: this.getAuthHeaders()
        });

        if (!response.ok) {
            this.removeToken();
            throw new Error('Token refresh failed');
        }

        const data = await response.json();
        this.setToken(data.access_token);
        this.setCurrentUser(data.user);
        return data;
    }

    // Obtener información del usuario actual
    async getMe() {
        const response = await fetch(`${this.baseUrl}/me`, {
            headers: this.getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.removeToken();
            }
            throw new Error('Failed to get user info');
        }

        const user = await response.json();
        this.setCurrentUser(user);
        return user;
    }

    // Forgot password
    async forgotPassword(email) {
        const response = await fetch(`${this.baseUrl}/forgot-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            throw new Error('Failed to send reset email');
        }

        return await response.json();
    }

    // Reset password
    async resetPassword(token, newPassword) {
        const response = await fetch(`${this.baseUrl}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: token,
                new_password: newPassword
            })
        });

        if (!response.ok) {
            throw new Error('Failed to reset password');
        }

        return await response.json();
    }

    // Cambiar contraseña
    async changePassword(currentPassword, newPassword) {
        const response = await fetch(`${this.baseUrl}/change-password`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (!response.ok) {
            throw new Error('Failed to change password');
        }

        return await response.json();
    }

    // Verificar token
    async verifyToken() {
        try {
            const response = await fetch(`${this.baseUrl}/verify-token`, {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                this.removeToken();
                return false;
            }

            const data = await response.json();
            return data.valid;
        } catch (error) {
            this.removeToken();
            return false;
        }
    }

    // Configurar interceptor para renovación automática de token
    setupTokenRefresh() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const response = await originalFetch(...args);
            
            if (response.status === 401 && this.isAuthenticated()) {
                try {
                    await this.refreshToken();
                    // Reintentar la petición original con el nuevo token
                    const [url, config] = args;
                    if (config && config.headers) {
                        config.headers['Authorization'] = `Bearer ${this.getToken()}`;
                    }
                    return await originalFetch(...args);
                } catch (error) {
                    this.removeToken();
                    window.location.href = '/login';
                }
            }
            
            return response;
        };
    }
}

// Instancia singleton
export const authService = new AuthService();