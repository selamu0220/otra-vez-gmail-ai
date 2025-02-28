# Gmail Assistant

Asistente para gestionar correos electrónicos de Gmail basado en instrucciones en lenguaje natural. Esta aplicación te permite autenticarte con Gmail, generar borradores de correos electrónicos y enviarlos.

## Características

- Autenticación con OAuth2 de Google
- Generación de emails basados en instrucciones en lenguaje natural
- Envío de emails a través de la API de Gmail
- Interfaz de usuario moderna y fácil de usar

## Estructura del Proyecto

El proyecto está dividido en dos partes principales:

### Cliente (React + TypeScript)

- Interfaz de usuario para interactuar con el asistente
- Componentes modulares para cada funcionalidad
- Hooks personalizados para la lógica de negocio
- Servicios para comunicación con el backend

### Servidor (Node.js + Express)

- API REST para manejar las peticiones del cliente
- Integración con la API de Gmail usando googleapis
- Servicios modulares para autenticación y manejo de emails

## Requisitos Previos

- Node.js (versión 14 o superior)
- Cuenta de Google y credenciales de OAuth2
  - Necesitas crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
  - Configurar el consentimiento de OAuth
  - Crear credenciales de OAuth2

## Configuración

1. Clona el repositorio
2. Configura las variables de entorno:
   - Copia `.env.example` a `.env` en la carpeta `server`
   - Añade tus credenciales de Google

### Backend

```bash
cd gmail-assistant/server
npm install
cp .env.example .env  # Edita este archivo con tus credenciales
npm run dev
```

### Frontend

```bash
cd gmail-assistant/client
npm install
npm start
```

## Uso

1. Abre la aplicación en tu navegador (http://localhost:3000 por defecto)
2. Haz clic en "Conectar Gmail" y autoriza la aplicación
3. Escribe tus instrucciones para generar un email
4. Revisa y edita el borrador generado
5. Envía el email

## Tecnologías Utilizadas

- **Frontend**: React, TypeScript, Axios
- **Backend**: Node.js, Express, Googleapis
- **Autenticación**: OAuth2

## Basado en

Este proyecto es una adaptación de un workflow original desarrollado con la biblioteca AbacusAI, que ha sido convertido para funcionar como una aplicación web completa. 