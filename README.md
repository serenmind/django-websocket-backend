# Django WebSocket Backend Example

This project is a production-ready Django backend with:
- Django Channels (WebSocket support)
- Django REST Framework (DRF)
- JWT authentication
- Real-time chat app example
- Docker, Docker Compose, Nginx reverse proxy

## Features
- JWT-protected WebSocket endpoints
- REST API with OpenAPI docs (drf-spectacular)
- Healthcheck endpoint for Docker/Nginx
- Supports both ASGI (Daphne) and WSGI (Gunicorn)
- Redis for Channels backend

## Quick Start

1. **Clone the repo**
2. **Build and run with Docker Compose:**
   ```sh
   docker-compose up --build
   ```
3. **Access:**
   - API: http://localhost/api/
   - OpenAPI docs: http://localhost/api/schema/swagger-ui/
   - WebSocket: ws://localhost/ws/chat/<room_name>/?token=<jwt>
   - Admin: http://localhost/admin/

## Usage

- See `api.http` for example API requests (obtain/refresh JWT, test protected endpoints)
- Use a WebSocket client (browser, websocat, wscat, etc.) to connect to chat rooms
- Example WebSocket URL:
  ```
  ws://localhost/ws/chat/room1/?token=<your_access_token>
  ```
- Send messages as JSON:
  ```json
  {"message": "Hello, world!"}
  ```

## Development
- See `Makefile` for useful commands (shell, migrate, createsuperuser, etc.)
- Static/media files are handled via Docker and Nginx

## Production
- Nginx proxies /ws/ and /api/ to ASGI, all else to WSGI
- (Add your own healthcheck endpoint if needed for Docker/Nginx)
- Use strong secrets and HTTPS in production

## License
MIT
