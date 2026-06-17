# Vidra Backend

Este es un proyecto backend desarrollado en **Flask** que proporciona una API RESTful para gestionar descargas (basado en `yt-dlp`). Permite iniciar descargas, inspeccionar y seleccionar elementos de una lista de reproducción, consultar registros (logs) y suscribirse a actualizaciones en tiempo real mediante Server-Sent Events (SSE).

Está diseñado para estar listo para producción utilizando **Waitress** y cuenta con un sistema de autenticación por Token.

## 🚀 Características Principales

- **Gestión de Descargas**: Iniciar, monitorear y consultar información de descargas.
- **Soporte para Listas de Reproducción**: Inspecciona una URL y selecciona qué entradas específicas descargar.
- **Eventos en Tiempo Real (SSE)**: Suscripción a los cambios (deltas) de las descargas en tiempo real.
- **Autenticación Segura**: Protección de endpoints mediante Bearer Token en entornos de producción.
- **Servidor de Producción**: Integración nativa con Waitress para manejar múltiples hilos.

## ⚙️ Variables de Entorno

El proyecto es altamente configurable a través de variables de entorno, lo que lo hace ideal para despliegues con Docker o contenedores similares.

| Variable    | Descripción                                                                                                             | Valor por Defecto    |
| :---------- | :---------------------------------------------------------------------------------------------------------------------- | :------------------- |
| `APP_ENV`   | Entorno de ejecución (`development` o `production`). Si es `production`, activa la validación de tokens y usa Waitress. | `development`        |
| `API_TOKEN` | Token de seguridad para las peticiones HTTP.                                                                            | `SUPER_SECRET_TOKEN` |
| `HOST`      | Dirección IP donde correrá el servidor.                                                                                 | `0.0.0.0`            |
| `PORT`      | Puerto donde correrá el servidor.                                                                                       | `5000`               |
| `LOGS_PATH` | Directorio para almacenar los logs.                                                                                     | `./temp/logs`        |
| `DATA_PATH` | Directorio para configuraciones persistentes (ej. yt-dlp).                                                              | `./temp/data`        |
| `TEMP_PATH` | Directorio para archivos temporales y caché.                                                                            | `./temp/temp`        |

## 🛠️ Instalación y Ejecución

1. **Clonar el repositorio:**

   ```bash
    git clone [https://github.com/chomusuke-mk/vidra-backend.git](https://github.com/chomusuke-mk/vidra-backend.git)
    cd vidra-backend
   ```

2. **Crear un entorno virtual (Recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**

   Nota: Asegúrate de tener `yt-dlp` y `yt-dlp-ejs` instalados globalmente o disponibles en tu PATH, ya que el proyecto los utiliza para las descargas.

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el proyecto:**

   _Para desarrollo:_

   ```bash
   export APP_ENV=development
   python src/main.py
   ```

   _Para producción:_

   ```bash
   export APP_ENV=production
   export API_TOKEN=TU_TOKEN_SECRETO
   python src/main.py
   ```

   _(En producción, la API levantará Waitress en 2 hilos y exigirá el `API_TOKEN` en las cabeceras)._

## 📖 Referencia de la API

_Nota: Todos los endpoints (excepto `/` y `/favicon.ico`) requieren autenticación cuando `APP_ENV=production`. Debes enviar el token en la cabecera HTTP:_
`Authorization: Bearer SUPER_SECRET_TOKEN`

### 1. Health Check

Comprueba si la API está funcionando.

- **GET** `/`
- **Respuesta Exitosa:** `200 OK`

  ```json
  { "status": "ok" }
  ```

### 2. Añadir Descarga

Inicia una nueva descarga.

- **POST** `/downloads`
- **Body (JSON):**

  ```json
  {
    "url": "https://www.youtube.com/watch?v=ejemplo",
    "options": {}
  }
  ```

- **Respuesta Exitosa:** `201 Created`

  ```json
  {
    "message": "Download added successfully",
    "id": "abc-123-xyz"
  }
  ```

### 3. Obtener Información de la Descarga

Obtiene el estado o metadatos de una descarga específica.

- **GET** `/downloads?id={download_id}`
- **Respuesta Exitosa:** `200 OK` (Retorna un objeto JSON con los detalles).

### 4. Consultar Logs

Obtiene los logs de texto plano de una descarga.

- **GET** `/logs?id={download_id}`
- **Respuesta Exitosa:** `200 OK` (Content-Type: `text/plain`).

### 5. Seleccionar Entradas (Playlists)

Si la URL pertenece a una lista de reproducción y requiere selección de elementos.

- **GET** `/select-entries?id={download_id}`
  Retorna la lista de entradas disponibles.
- **POST** `/select-entries?id={download_id}`
  Envía las entradas que el usuario ha seleccionado para descargar.
  - **Body (JSON):**

    ```json
    {
      "entries": [1, 3, 5]
    }
    ```

### 6. Suscribirse a Actualizaciones (SSE)

Abre una conexión persistente (Server-Sent Events) para recibir el progreso en tiempo real.

- **GET** `/subscribe?id={download_id}&everything=false`
- **Respuesta Exitosa:** `200 OK` (Content-Type: `text/event-stream`).

### 7. Control de Descarga (En desarrollo)

Permite pausar, reanudar, cancelar o reintentar una descarga. _(Actualmente no implementado - 501)._

- **PATCH** `/downloads?id={download_id}&action={pause|resume|cancel|retry}`

## 🔒 Notas de Seguridad y Certificados

El código inyecta y utiliza la ruta de certificados de certifi directamente en el entorno (SSL_CERT_FILE y REQUESTS_CA_BUNDLE). Esto asegura que las librerías subyacentes encargadas de las peticiones HTTP no tengan problemas con validaciones SSL en contenedores o entornos minimalistas.
