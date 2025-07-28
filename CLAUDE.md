# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack web application boilerplate with Django REST Framework backend and Nuxt 3 frontend, fully containerized with Docker. It features JWT authentication, PostgreSQL database, Redis caching, and Celery task queue.

## Development Commands

### Docker Development Environment
```bash
# Start all services
docker-compose up -d

# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create Django superuser
docker-compose exec backend python manage.py createsuperuser

# Create new Django migrations
docker-compose exec backend python manage.py makemigrations

# Run Django tests
docker-compose exec backend python manage.py test

# Access Django shell
docker-compose exec backend python manage.py shell

# Access PostgreSQL database
docker-compose exec db psql -U postgres -d boiler_db

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Frontend Development
```bash
# Development server (inside container)
docker-compose exec frontend npm run dev

# Build for production
docker-compose exec frontend npm run build

# Generate static site
docker-compose exec frontend npm run generate

# Run tests
docker-compose exec frontend npm run test
```

### Backend Development
```bash
# Run Django development server (inside container)
docker-compose exec backend python manage.py runserver 0.0.0.0:8000

# Run Celery worker
docker-compose exec backend celery -A core worker --loglevel=info

# Monitor Celery tasks
docker-compose exec backend celery -A core flower
```

## Architecture Overview

### Backend Architecture (Django)
- **Custom User Model**: Uses email as username field (`apps.users.User`)
- **JWT Authentication**: SimpleJWT with access/refresh token rotation
- **App Structure**: Modular apps in `backend/apps/` (users, authentication, websockets)
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session storage and Celery broker
- **Task Queue**: Celery for background processing
- **WebSockets**: Django Channels with Redis channel layer for real-time communication
- **ASGI**: Daphne server for handling both HTTP and WebSocket connections
- **API**: RESTful API with DRF pagination (20 items per page)

### Frontend Architecture (Nuxt 3)
- **SPA Mode**: Server-side rendering disabled (`ssr: false`)
- **State Management**: Pinia stores for authentication and app state
- **HTTP Client**: Axios with automatic JWT token handling and refresh
- **WebSocket Client**: Composables for real-time communication (`useWebSocket`, `useNotifications`, `useChat`)
- **Authentication**: Cookie-based token storage with automatic refresh
- **Styling**: Tailwind CSS with custom components
- **Route Protection**: Middleware for authenticated/guest routes

### Authentication Flow
1. Login/Register returns JWT access + refresh tokens
2. Tokens stored in secure cookies (httpOnly for production)
3. Axios interceptor adds Bearer token to requests
4. Automatic token refresh on 401 responses
5. Redirect to login on refresh failure

### Key Files and Their Purposes
- `backend/core/settings.py`: Django configuration with environment-based settings
- `backend/apps/users/models.py`: Custom User model with email authentication
- `frontend/stores/auth.ts`: Pinia authentication store with token management
- `frontend/plugins/api.client.ts`: Axios configuration with interceptors
- `frontend/middleware/auth.ts` & `guest.ts`: Route protection middleware
- `docker-compose.yml`: Development environment services
- `docker-compose.prod.yml`: Production environment services

### Environment Variables
Key variables defined in `.env` file:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Development mode toggle
- `DB_*`: Database connection settings
- `REDIS_URL`: Redis connection string
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS
- `API_BASE_URL`: Frontend API endpoint configuration

### Database Schema
- Custom User model extends AbstractUser with email as primary field
- Additional fields: `is_verified`, `created_at`, `updated_at`
- Uses PostgreSQL with migrations in `backend/apps/*/migrations/`

### API Endpoints
- `/api/auth/register/` - User registration
- `/api/auth/login/` - User login
- `/api/auth/refresh/` - Token refresh
- `/api/auth/logout/` - User logout
- `/api/auth/change-password/` - Password change
- `/api/users/me/` - Current user profile

### WebSocket Endpoints
- `ws/notifications/{user_id}/` - Real-time notifications for specific user
- `ws/chat/{room_name}/` - Real-time chat for specific room
- Authentication via JWT token in query string: `?token=ACCESS_TOKEN`

### Deployment
- Production uses `docker-compose.prod.yml` with Nginx reverse proxy
- Scripts in `scripts/` directory: `setup.sh`, `deploy.sh`, `backup.sh`, `restore.sh`
- SSL certificates go in `nginx/ssl/` directory
- Static files served by WhiteNoise in Django