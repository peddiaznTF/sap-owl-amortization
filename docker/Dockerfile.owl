# owl-app/Dockerfile
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Instalar OWL y dependencias de desarrollo
RUN npm install @odoo/owl webpack webpack-cli webpack-dev-server \
    @babel/core @babel/preset-env babel-loader \
    css-loader style-loader sass sass-loader \
    html-webpack-plugin clean-webpack-plugin

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Cambiar propiedad de archivos
RUN chown -R nextjs:nodejs /app
USER nextjs

# Exponer puerto
EXPOSE 3000

# Comando por defecto
CMD ["npm", "run", "dev"]
