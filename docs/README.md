# Proyecto Híbrido SAP Business One + OWL
## Arquitectura del Sistema de Gestión de Amortización Financiera

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA HÍBRIDA                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌──────────────────┐               │
│  │   SAP B1 ERP    │    │   C# AddOn       │               │
│  │   - Módulos     │◄──►│   - Vinculación  │               │
│  │   - Service     │    │   - Gestión      │               │
│  │     Layer       │    │   - Sync         │               │
│  └─────────────────┘    └──────────────────┘               │
│           ▲                       ▲                        │
│           │                       │                        │
│    ┌─────────────────────────────────────────┐             │
│    │         REST API / Service Layer        │             │
│    └─────────────────────────────────────────┘             │
│           ▲                                                │
│           │                                                │
│  ┌─────────────────────────────────────────────────────────┤
│  │              APLICACIÓN OWL (Docker)               │
│  ├─────────────────────────────────────────────────────────┤
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  │ Multi-Cía   │  │ Amortización│  │ Dashboard   │   │
│  │  │ Management  │  │ Tables      │  │ Reports     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │
│  │                                                     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  │ Clientes    │  │ Proveedores │  │ Integración │   │
│  │  │ Module      │  │ Module      │  │ SAP B1      │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │
│  └─────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

#### Frontend (OWL Application)
- **OWL Framework** (Odoo Web Library)
- **JavaScript ES6+**
- **XML Templates**
- **SCSS/CSS3**
- **Chart.js** para visualizaciones

#### Backend Integration
- **Python/FastAPI** para API Gateway
- **SAP Business One Service Layer** (REST API)
- **PostgreSQL/MySQL** para datos locales

#### AddOn SAP B1
- **C# .NET Framework**
- **SAP B1 DI API**
- **SAP B1 UI API**

#### Infraestructura
- **Docker & Docker Compose**
- **Nginx** como proxy reverso
- **Redis** para caché

### Funcionalidades Principales

1. **Gestión Multicompañía**
   - Selector de empresa
   - Configuraciones por compañía
   - Segregación de datos

2. **Tablas de Amortización**
   - Cálculo automático
   - Diferentes métodos (lineal, decreciente, etc.)
   - Gestión de cuotas y pagos

3. **Integración SAP B1**
   - Sincronización de maestros
   - Creación de documentos
   - Consulta de estados

4. **Reportes y Dashboard**
   - Visualización de amortizaciones
   - Estados financieros
   - Alertas y notificaciones

### Estructura de Directorios

```
sap-owl-amortization/
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.owl
│   ├── Dockerfile.api
│   └── nginx.conf
├── owl-app/
│   ├── src/
│   │   ├── components/
│   │   ├── models/
│   │   ├── services/
│   │   └── views/
│   ├── static/
│   └── templates/
├── api-gateway/
│   ├── app/
│   ├── config/
│   └── requirements.txt
├── sap-addon/
│   ├── src/
│   ├── bin/
│   └── SAPAddon.sln
└── docs/
    ├── installation.md
    ├── configuration.md
    └── api-docs.md
```