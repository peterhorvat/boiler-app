# Boiler App

A modern full-stack web application boilerplate with Django REST Framework backend and Nuxt 3 frontend, fully containerized with Docker.

## 🚀 Features

### Backend (Django)
- ✅ Django 5.0 with Django REST Framework
- ✅ JWT Authentication with refresh tokens
- ✅ PostgreSQL database
- ✅ Redis caching and Celery task queue
- ✅ Custom User model
- ✅ CORS configuration
- ✅ Production-ready settings
- ✅ Security headers and HTTPS support

### Frontend (Nuxt 3)
- ✅ Nuxt 3 with Vue 3 Composition API
- ✅ Pinia state management
- ✅ Tailwind CSS for styling
- ✅ Axios HTTP client with interceptors
- ✅ JWT token management
- ✅ Authentication middleware
- ✅ Responsive design

### DevOps
- ✅ Docker and Docker Compose
- ✅ Production and development environments
- ✅ Nginx reverse proxy with SSL
- ✅ Automated deployment scripts
- ✅ Database backup and restore
- ✅ Health checks and monitoring

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd boiler
   ```

2. **Copy environment file:**
   ```bash
   cp .env.local .env
   ```

3. **Start development environment:**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Django Admin: http://localhost:8000/admin

### Production Deployment

1. **Prepare the server:**
   ```bash
   ./scripts/setup.sh
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

3. **Deploy:**
   ```bash
   ./scripts/deploy.sh
   ```

## 📁 Project Structure

```
boiler/
├── backend/                 # Django backend
│   ├── core/               # Django project settings
│   ├── apps/               # Django applications
│   │   ├── authentication/ # Auth endpoints
│   │   └── users/          # User management
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend Docker image
├── frontend/               # Nuxt 3 frontend
│   ├── components/        # Vue components
│   ├── layouts/           # Layout components
│   ├── pages/             # Route pages
│   ├── stores/            # Pinia stores
│   ├── middleware/        # Route middleware
│   ├── plugins/           # Nuxt plugins
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend Docker image
├── nginx/                 # Nginx configuration
├── scripts/               # Deployment scripts
├── docker-compose.yml     # Development environment
├── docker-compose.prod.yml # Production environment
└── README.md
```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable/disable debug mode
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `REDIS_PASSWORD`: Redis password
- `DOMAIN`: Your domain name
- `CORS_ALLOWED_ORIGINS`: Allowed CORS origins

### SSL Configuration

For production, place your SSL certificates in `nginx/ssl/`:
- `fullchain.pem`: SSL certificate chain
- `privkey.pem`: Private key

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

### API Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/change-password/` - Change password
- `GET /api/users/me/` - Get user profile

### Frontend Authentication
- Automatic token refresh
- Protected routes with middleware
- Persistent authentication state
- Secure cookie storage

## 🔄 Development Workflow

### Adding New Features

1. **Backend (Django):**
   - Create new apps in `backend/apps/`
   - Add models, serializers, views
   - Configure URLs
   - Run migrations

2. **Frontend (Nuxt):**
   - Add pages in `pages/`
   - Create components in `components/`
   - Add store logic in `stores/`
   - Configure routes and middleware

### Database Management

```bash
# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate

# Access database shell
docker-compose exec db psql -U postgres -d boiler_db
```

### Monitoring and Logs

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Monitor services
docker-compose ps
```

## 🗄️ Backup and Restore

### Create Backup
```bash
./scripts/backup.sh
```

### Restore from Backup
```bash
./scripts/restore.sh backups/boiler_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🔒 Security Features

- JWT token authentication with refresh
- HTTPS enforcement in production
- Security headers (HSTS, XSS protection, etc.)
- CORS configuration
- Rate limiting (Nginx)
- SQL injection protection (Django ORM)
- XSS protection (Vue.js)
- CSRF protection
- Secure cookie settings

## 🧪 Testing

### Backend Tests
```bash
docker-compose exec backend python manage.py test
```

### Frontend Tests
```bash
docker-compose exec frontend npm run test
```

## 📈 Performance Optimization

- Nginx gzip compression
- Static file caching
- Database connection pooling
- Redis caching
- Image optimization
- Code splitting (Nuxt)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed description

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Nuxt 3 Documentation](https://nuxt.com/)
- [Vue 3 Documentation](https://vuejs.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Tailwind CSS](https://tailwindcss.com/)