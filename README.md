# Zero-Knowledge Encrypted Storage Backend

A secure, zero-knowledge encrypted file storage API built with FastAPI and Supabase. This backend provides client-side encryption capabilities where the server never has access to unencrypted data.

## 🔐 Security Features

- **Zero-Knowledge Architecture**: Server never sees plaintext data or encryption keys
- **Client-Side Encryption**: All encryption/decryption happens on the client
- **JWT Authentication**: Secure token-based authentication
- **Row Level Security (RLS)**: Database-level access control
- **Rate Limiting**: Protection against abuse and DDoS
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Configurable cross-origin resource sharing

## 🏗️ Architecture

```
Frontend (Client-side encryption) 
    ↓ (Encrypted data + metadata)
FastAPI Backend (API Layer)
    ↓ (Encrypted storage)
Supabase (Database + Storage)
```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── config/
│   ├── database.py        # Supabase connection
│   ├── storage.py         # Supabase storage config
│   └── settings.py        # App settings
├── models/
│   ├── user.py           # User Pydantic models
│   ├── file.py           # File Pydantic models
│   └── auth.py           # Auth models
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── files.py          # File management routes
│   ├── user.py           # User profile routes
│   └── health.py         # Health check routes
├── services/
│   ├── auth_service.py   # Auth business logic
│   ├── file_service.py   # File business logic
│   ├── storage_service.py # Storage operations
│   └── user_service.py   # User operations
├── middleware/
│   ├── auth.py           # JWT verification
│   ├── rate_limit.py     # Rate limiting
│   └── error_handler.py  # Error handling
├── utils/
│   ├── jwt.py            # JWT utilities
│   ├── validators.py     # Input validation
│   └── responses.py      # API responses
├── sql/
│   ├── 01_create_tables.sql # Database schema
│   ├── 02_rls_policies.sql  # Security policies
│   ├── 03_storage_setup.sql # Storage bucket setup
│   └── README.md         # Database setup guide
└── tests/
    ├── conftest.py       # Test configuration
    ├── test_auth.py      # Auth endpoint tests
    ├── test_files.py     # File endpoint tests
    └── test_user.py      # User endpoint tests
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
```

Required environment variables:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
```

### 3. Database Setup

Follow the [SQL Setup Guide](sql/README.md) to configure your Supabase database.

### 4. Run the Server

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication

All endpoints except registration, login, and health checks require authentication:
```
Authorization: Bearer <jwt-token>
```

### Endpoints Overview

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh token
- `GET /auth/verify` - Verify token

#### File Management
- `POST /files/upload` - Upload encrypted file
- `GET /files` - List user files (paginated)
- `GET /files/{file_id}` - Get file metadata
- `GET /files/{file_id}/download` - Get download URL
- `DELETE /files/{file_id}` - Soft delete file
- `DELETE /files/{file_id}/permanent` - Hard delete file

#### User Profile
- `GET /user/profile` - Get user profile
- `GET /user/storage` - Get storage statistics
- `PATCH /user/password` - Change password

#### System
- `GET /health` - Health check
- `GET /stats` - System statistics

### Example Requests

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password_hash": "client-side-hashed-password",
    "salt": "random-salt-from-client"
  }'
```

#### Upload File
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@encrypted-file.enc" \
  -F "encrypted_filename=base64-encrypted-name" \
  -F "encrypted_metadata={\"encrypted_size\":\"...\",\"encrypted_type\":\"...\"}" \
  -F "file_size=1048576"
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | ZeroKnowledgeStorage | No |
| `APP_VERSION` | Version | 1.0.0 | No |
| `ENVIRONMENT` | Environment | development | No |
| `DEBUG` | Debug mode | True | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `SUPABASE_URL` | Supabase project URL | - | Yes |
| `SUPABASE_KEY` | Supabase anon key | - | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service key | - | Yes |
| `JWT_SECRET_KEY` | JWT secret key | - | Yes |
| `JWT_ALGORITHM` | JWT algorithm | HS256 | No |
| `JWT_EXPIRATION_MINUTES` | Token expiry | 60 | No |
| `STORAGE_BUCKET_NAME` | Storage bucket | encrypted-files | No |
| `MAX_FILE_SIZE_MB` | Max file size | 50 | No |
| `DEFAULT_STORAGE_LIMIT_GB` | Storage limit | 5 | No |
| `BCRYPT_ROUNDS` | Password hashing rounds | 12 | No |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | 60 | No |
| `ALLOWED_ORIGINS` | CORS origins | http://localhost:3000 | No |

### Rate Limits

- **Login attempts**: 5 per 15 minutes per IP
- **File uploads**: 20 per hour per user
- **File downloads**: 100 per hour per user
- **API requests**: 1000 per hour per user
- **Registration**: 3 per hour per IP

## 🔒 Security Best Practices

### Client-Side Requirements
- All encryption/decryption must happen on the client
- Never send unencrypted data or keys to the server
- Use strong encryption (AES-256-GCM recommended)
- Generate unique salts for each user
- Hash passwords client-side before transmission

### Server-Side Security
- JWT tokens expire after 1 hour (configurable)
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- Row Level Security (RLS) in database
- CORS protection
- Secure headers

### Deployment Security
- Use HTTPS in production
- Set strong JWT secret key (min 32 characters)
- Regular security updates
- Monitor access logs
- Backup and disaster recovery plan

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env
```

### Production Considerations

- Use a production WSGI server (uvicorn with gunicorn)
- Set up reverse proxy (nginx)
- Configure SSL/TLS certificates
- Monitor with logging and metrics
- Set up health checks and alerts
- Regular backups
- Security scanning

## 📊 Monitoring

### Health Checks
- Database connectivity
- Storage accessibility
- API response times
- Error rates

### Metrics to Monitor
- Request rates and latencies
- Error rates by endpoint
- Storage usage per user
- Active user sessions
- File upload/download patterns

### Logging
- All API requests and responses
- Authentication attempts
- File operations
- Error conditions
- Security events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the [SQL Setup Guide](sql/README.md) for database issues
2. Review the API documentation
3. Check the test files for usage examples
4. Create an issue on GitHub

## 🔄 API Versioning

Current API version: `v1`

Base URL: `/api/v1`

Breaking changes will increment the major version number.