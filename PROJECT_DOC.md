# Django WebSocket Backend Project Documentation

## Table of Contents
1. Project Overview
2. Project Setup & Structure
3. Dockerfile: Line-by-Line Explanation
4. docker-compose.yml: Line-by-Line Explanation
5. Nginx Configuration: Line-by-Line Explanation
6. Gunicorn Setup: Line-by-Line Explanation
7. Installed Packages & Their Purpose
8. WebSocket Setup (Django Channels)
9. WSGI vs ASGI: How the Project Works
10. Notes on PostgreSQL Usage
11. Using the Realtime App for Generic WebSocket Events

---

## 1. Project Overview
This project is a production-ready Django backend featuring:
- Django Channels for WebSocket support
- Django REST Framework (DRF) for REST APIs
- JWT authentication for secure endpoints and WebSocket connections
- Real-time chat app example
- Dockerized deployment with Nginx reverse proxy, Daphne (ASGI), Gunicorn (WSGI), and Redis for Channels backend

---

## 2. Project Setup & Structure
- **backend/**: Django project settings, ASGI/WSGI entrypoints, URLs
- **chat/**: Django app for chat functionality (consumers, routing, models)
- **Dockerfile**: Builds the backend image
- **docker-compose.yml**: Orchestrates backend, wsgi, redis, nginx
- **nginx.conf**: Nginx reverse proxy config
- **requirements.txt**: Python dependencies
- **Makefile**: Useful commands for development
- **api.http**: Local API test requests (ignored in git)

---

## 3. Dockerfile: Line-by-Line Explanation
```
FROM python:3.11-slim
```
- Use a minimal Python 3.11 image for smaller size and security.

```
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
```
- Prevents Python from writing .pyc files and enables unbuffered output for logs.

```
WORKDIR /code
```
- Sets the working directory inside the container.

```
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
```
- Copies requirements and installs all dependencies.

```
COPY . .
```
- Copies the entire project into the container.

```
CMD ["/bin/bash"]
```
- Default command (overridden by docker-compose for each service).

---

## 4. docker-compose.yml: Line-by-Line Explanation
- **version: '3.9'**: Compose file format version.
- **services:**
  - **backend:**
    - Builds from Dockerfile.
    - Runs Daphne (ASGI server) for WebSocket and API endpoints.
    - Depends on redis.
    - Exposes port 8000 (internal).
  - **wsgi:**
    - Runs Gunicorn (WSGI server) for admin/static endpoints.
    - Shares the same code as backend.
    - Exposes port 8001 (internal).
  - **redis:**
    - Official Redis image for Channels backend.
    - Exposes port 6379 (internal).
  - **nginx:**
    - Uses nginx.conf for reverse proxy.
    - Depends on backend, wsgi.
    - Exposes port 80 (external for host access).
- **volumes:**
  - Mounts static/media for persistence.

---

## 5. Nginx Configuration: Line-by-Line Explanation
- **worker_processes 1;**: One worker (sufficient for dev/small prod).
- **events { worker_connections 1024; }**: Max connections per worker.
- **http { ... }**: Main HTTP config block.
- **upstream backend { ... }**: Defines ASGI backend (Daphne, port 8000).
- **upstream wsgi { ... }**: Defines WSGI backend (Gunicorn, port 8001).
- **server { ... }**: Main server block.
  - **listen 80;**: Listens on port 80.
  - **location /ws/ { ... }**: Proxies WebSocket traffic to Daphne (ASGI).
  - **location /api/ { ... }**: Proxies API traffic to Daphne (ASGI).
  - **location /static/ { ... }**: Serves static files directly.
  - **location /media/ { ... }**: Serves media files directly.
  - **location / { ... }**: All other traffic (admin, etc.) proxied to Gunicorn (WSGI).

---

## 6. Gunicorn Setup: Line-by-Line Explanation
- **gunicorn backend.wsgi:application --bind 0.0.0.0:8001**
  - Runs Gunicorn, binding to all interfaces on port 8001.
  - Uses Django's WSGI entrypoint for HTTP (not WebSocket) traffic.

---

## 7. Installed Packages & Their Purpose
- **Django**: Main web framework.
- **djangorestframework**: REST API support.
- **djangorestframework-simplejwt**: JWT authentication for DRF and WebSocket.
- **channels**: Adds ASGI/WebSocket support to Django.
- **channels-redis**: Redis backend for Channels (group messaging, scaling).
- **drf-spectacular**: OpenAPI schema and Swagger UI for DRF.
- **gunicorn**: WSGI HTTP server for Django (admin, static, etc.).
- **daphne**: ASGI server for Django Channels (WebSocket, API).
- **redis**: Python client for Redis (used by Channels backend).
- **psycopg2** (optional): PostgreSQL driver (if you switch from SQLite to Postgres).

---

## 8. WebSocket Setup (Django Channels)
- **channels** is added to `INSTALLED_APPS`.
- **ASGI application** is set in `backend/asgi.py`.
- **chat/routing.py** defines WebSocket URL routing.
- **chat/consumers.py** implements `AsyncWebsocketConsumer` for chat logic.
- **Redis** is used as the channel layer backend for group messaging and scaling.
- **JWT authentication** is performed in the consumer's `connect` method, extracting the token from the query string.
- **Nginx** proxies `/ws/` traffic to Daphne (ASGI), which handles WebSocket connections.

---

## 9. WSGI vs ASGI: How the Project Works
- **ASGI (Daphne):**
  - Handles all `/ws/` (WebSocket) and `/api/` (REST API) traffic.
  - Supports long-lived connections and async features.
  - Uses Redis for channel layer (group messaging, scaling).
- **WSGI (Gunicorn):**
  - Handles all other HTTP traffic (e.g., Django admin, static files fallback).
  - Synchronous, traditional Django HTTP server.
- **Nginx** routes requests to the correct backend based on URL.

---

## 10. Notes on PostgreSQL Usage
- The default setup uses SQLite for simplicity.
- For production, it is recommended to use PostgreSQL:
  - Install `psycopg2` in `requirements.txt`.
  - Update `DATABASES` in `backend/settings.py` to use PostgreSQL.
  - Add a `postgres` service to `docker-compose.yml` and configure environment variables.
- PostgreSQL is more robust and scalable for production workloads.

---

## 11. Using the Realtime App for Generic WebSocket Events

The `realtime` app provides a generic WebSocket interface for any Django app in this project to push real-time data to the frontend, eliminating the need for REST API polling.

### How It Works
- The frontend opens a persistent WebSocket connection to `/ws/realtime/?token=<jwt>` after user login.
- The backend can send data to the frontend at any time (e.g., on model save, signal, or background task) using the `notify_user` function in `realtime/notification.py`.
- The frontend receives updates instantly, without any user interaction or polling.

### Example Usage
**Backend:**
```python
from realtime.notification import notify_user

def some_backend_event(user_id):
    data = {"type": "notification", "message": "You have a new message!"}
    notify_user(user_id, data)
```

**Frontend:**
- Open a WebSocket connection once (e.g., when the app loads):
  ```js
  const ws = new WebSocket("ws://localhost/ws/realtime/?token=YOUR_JWT_TOKEN");
  ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle the real-time event (e.g., show notification)
  };
  // Optionally, add reconnect logic if needed
  ```

### Best Practices
- Keep the WebSocket connection open as long as the user is active in your app.
- Use the connection for all real-time updates (notifications, status, etc.).
- Backend can trigger `notify_user()` from any app, view, signal, or background task.
- No special always-on channel is needed; the persistent WebSocket connection is the live channel.

### Benefits
- Decouples real-time delivery from REST APIs.
- Reduces server load by eliminating polling.
- Enables instant UI updates for any backend event.

---

For further details, see the code comments and configuration files in the repository.
