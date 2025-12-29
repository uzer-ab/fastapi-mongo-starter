<div align="center">

# FastAPI MongoDB Starter

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A scalable FastAPI template with MongoDB, JWT authentication, session management, and role-based access control. Built for production with security best practices and comprehensive logging.

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Authentication & Security

- **JWT Dual-Token System**
  - Access tokens (15 min)
  - Refresh tokens (30 days)
- **Argon2 Password Hashing**
- **HttpOnly Cookie Protection**
- **Session Management**
- **Device Fingerprinting**
- **IP Address Tracking**

</td>
<td width="50%">

### 🏗 Architecture & Features

- **Async MongoDB with Beanie ODM**
- **Role-Based Access Control (RBAC)**
- **API Versioning** (`/api/v1`)
- **Pydantic Validation**
- **Comprehensive Logging**
- **Health Check Endpoints**
- **Soft-Delete Pattern**

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB 6.0+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd fastapi-mongo-starter

# 2. Set up environment variables
cp env.example .env

# 3. Edit .env with your configuration
nano .env

# 4. Install dependencies
uv sync

# 5. Run the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Access the API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### 🐳 Docker Setup (Quick Start)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd fastapi-mongo-starter

# 2. Set up environment variables
cp .env.example .env

# 3. Edit .env with your configuration (if needed)
nano .env

# 4. Start with Docker Compose
docker-compose up -d

# 5. Access the API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

The Docker setup includes:

- FastAPI application container
- MongoDB 6.0 container
- Automatic database initialization
- Volume persistence for data
- Network isolation

For detailed Docker setup instructions and troubleshooting, see [DOCKER_SETUP.md](DOCKER_SETUP.md) and [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md).

---

### Environment Configuration

Create a `.env` file with the following variables:

```env
# Required
MONGO_URL=mongodb://localhost:27017
MONGODB_NAME=your_database_name
SECRET_KEY=your-secret-key-min-32-chars

# Optional
HOST=0.0.0.0
PORT=8000
WORKERS=4
ENVIRONMENT=development
```

<details>
<summary><b>Environment Variables Reference</b></summary>

| Variable       | Required | Default           | Description                              |
| -------------- | -------- | ----------------- | ---------------------------------------- |
| `MONGO_URL`    | ✅       | -                 | MongoDB connection string                |
| `MONGODB_NAME` | ✅       | -                 | Database name                            |
| `SECRET_KEY`   | ✅       | auto-generated    | JWT signing key (min 32 chars)           |
| `HOST`         | ❌       | `0.0.0.0`         | Server bind address                      |
| `PORT`         | ❌       | `8000`            | Server port                              |
| `WORKERS`      | ❌       | `cpu_count * 1.4` | Uvicorn workers                          |
| `ENVIRONMENT`  | ❌       | `development`     | Environment (`development`/`production`) |

</details>

---

## 🔑 API Endpoints

### 🏥 Health & Status

```http
GET  /                # Root endpoint
GET  /health          # Basic health check
GET  /ready           # Readiness check (DB connection)
```

### 🔐 Authentication

<table>
<tr>
<th>Endpoint</th>
<th>Method</th>
<th>Description</th>
<th>Auth Required</th>
</tr>
<tr>
<td><code>/api/v1/auth/register</code></td>
<td>POST</td>
<td>Create new user account</td>
<td>❌</td>
</tr>
<tr>
<td><code>/api/v1/auth/login</code></td>
<td>POST</td>
<td>Authenticate and receive tokens</td>
<td>❌</td>
</tr>
<tr>
<td><code>/api/v1/auth/refresh</code></td>
<td>POST</td>
<td>Refresh access token</td>
<td>🍪 Cookie</td>
</tr>
<tr>
<td><code>/api/v1/auth/logout</code></td>
<td>POST</td>
<td>Revoke session and clear tokens</td>
<td>✅ Bearer</td>
</tr>
</table>

### 👤 User Management

<table>
<tr>
<th>Endpoint</th>
<th>Method</th>
<th>Description</th>
<th>Role</th>
</tr>
<tr>
<td><code>/api/v1/user/</code></td>
<td>GET</td>
<td>Get current user profile</td>
<td>USER</td>
</tr>
<tr>
<td><code>/api/v1/user/</code></td>
<td>PUT</td>
<td>Update current user profile</td>
<td>USER</td>
</tr>
<tr>
<td><code>/api/v1/user/</code></td>
<td>DELETE</td>
<td>Delete current user account</td>
<td>USER</td>
</tr>
</table>

### 🛡 Admin Panel

<table>
<tr>
<th>Endpoint</th>
<th>Method</th>
<th>Description</th>
<th>Role</th>
</tr>
<tr>
<td><code>/api/v1/admin/users</code></td>
<td>GET</td>
<td>List all users (paginated)</td>
<td>ADMIN</td>
</tr>
<tr>
<td><code>/api/v1/admin/{user_id}</code></td>
<td>PUT</td>
<td>Update any user</td>
<td>ADMIN</td>
</tr>
<tr>
<td><code>/api/v1/admin/{user_id}</code></td>
<td>DELETE</td>
<td>Delete any user</td>
<td>ADMIN</td>
</tr>
</table>

---

## 📁 Project Structure

```
fastapi-mongo-starter/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── auth.py          # Authentication endpoints
│   │           ├── users.py         # User management
│   │           └── admin.py         # Admin operations
│   │
│   ├── core/
│   │   ├── app_config.py           # FastAPI app configuration
│   │   ├── config.py               # Environment settings
│   │   ├── db.py                   # Database connection
│   │   ├── middleware.py           # Custom middleware
│   │   ├── exception_handlers.py   # Global error handling
│   │   └── health.py               # Health check endpoints
│   │
│   ├── models/
│   │   ├── user.py                 # User database model
│   │   ├── session.py              # Session tracking model
│   │   └── role.py                 # Role & permissions model
│   │
│   ├── schemas/
│   │   ├── auth.py                 # Auth request/response schemas
│   │   └── user.py                 # User data schemas
│   │
│   ├── services/
│   │   └── session_service.py      # Session management logic
│   │
│   ├── utils/
│   │   ├── auth.py                 # JWT utilities
│   │   ├── user_agent.py           # Device fingerprinting
│   │   ├── logging.py              # Logging configuration
│   │   └── formatter.py            # Response formatting
│   │
│   ├── middleware/
│   │   └── http_logger.py          # HTTP request/response logging
│   │
│   ├── dependencies.py             # FastAPI dependencies
│   └── main.py                     # Application entry point
│
├── logs/
│   └── app.log                     # Application logs
├── docker-compose.yml              # Docket compose
├── Dockerfile
├── DOCKER_QUICKSTART.md            # Quik guide to setup docker for project
├── DOCKER_SETUP.md                 # Guide to setup docket for project
├── example.env                     # Environment template
├── pyproject.toml                  # Project dependencies
└── README.md
```

---

## 🏛 Architecture

### Database Models

#### 👤 User Model

```python
{
  "id": "uuid",
  "username": "string (unique, indexed)",
  "email": "string (unique, indexed)",
  "full_name": "string (optional)",
  "password": "string (Argon2 hashed)",
  "role": "Link<Role>",
  "is_active": "boolean",
  "created_at": "datetime"
}
```

#### 🔑 Session Model

```python
{
  "id": "uuid (session_id)",
  "user_id": "uuid",
  "refresh_jti": "uuid (JWT ID for rotation)",
  "device_info": "string (parsed user agent)",
  "ip_address": "string",
  "user_agent": "string (raw)",
  "expires_at": "datetime",
  "is_active": "boolean",
  "created_at": "datetime",
  "last_activity": "datetime"
}
```

#### 🛡 Role Model

```python
{
  "id": "uuid",
  "name": "USER | ADMIN | SUPER_ADMIN",
  "description": "string",
  "permissions": ["string[]"],
  "is_active": "boolean",
  "created_at": "datetime"
}
```

### Token Architecture

<table>
<tr>
<th width="50%">Access Token</th>
<th width="50%">Refresh Token</th>
</tr>
<tr>
<td>

**Storage:** Authorization header
**Lifetime:** 15 minutes
**Claims:**

```json
{
  "uid": "user-id",
  "sid": "session-id",
  "type": "access",
  "exp": "timestamp"
}
```

</td>
<td>

**Storage:** HttpOnly cookie
**Lifetime:** 30 days
**Claims:**

```json
{
  "uid": "user-id",
  "sid": "session-id",
  "jti": "jwt-id",
  "type": "refresh",
  "exp": "timestamp"
}
```

</td>
</tr>
</table>

---

## 🔒 Security Features

### Authentication & Authorization

- ✅ **Argon2 Password Hashing** - Industry-standard, memory-hard hashing algorithm
- ✅ **Automatic Password Rehashing** - Updates passwords to stronger parameters when needed
- ✅ **JWT Dual-Token System** - Separate access and refresh tokens
- ✅ **HttpOnly Cookies** - XSS protection for refresh tokens
- ✅ **Token Rotation** - Unique JTI for each refresh token prevents replay attacks
- ✅ **Session Validation** - Database-backed session verification (not just JWT)
- ✅ **Role-Based Access Control** - Granular permission system with wildcards

### Session Security

- ✅ **Device Fingerprinting** - Track browser, OS, and device type
- ✅ **IP Address Tracking** - Monitor session locations
- ✅ **Session Revocation** - Instantly invalidate sessions
- ✅ **Bulk Session Cleanup** - Revoke all user sessions
- ✅ **Automatic Expiration** - Clean up expired sessions
- ✅ **Soft Delete** - Users marked inactive instead of deleted

---

## 🔄 Authentication Flows

### Registration Flow

```
1. POST /auth/register
   ↓ username/email + password
2. Validate input:
   - Ensure required fields are provided (e.g. username/email, password)
   ↓
3. Check existing user:
   - Search by email OR username
   - Ensure user doesn't already exist
   ↓ (not existing)
4. Hash password (Argon2)
   ↓
5. Create user:
   - Save user data (username/email, hashed password)
   - Assign default role (e.g. "user")
   ↓
6. Return response:
   - Return user data in JSON
```

#### Login → Session Creation Flow

```
1. POST /api/v1/auth/login
   ↓ username/email + password
2. Find user:
   -  Match by (email OR username)
   -  is_active = True
   ↓
3. Verify password (Argon2)
   ↓ (valid)
4. Create Session (DB):
   -  session_id: UUID
   -  refresh_jti: UUID (unique ID for refresh JWT)
   -  device: parsed from User-Agent (e.g. Chrome 120 | Windows 11 | Desktop)
   -  ip_address: request.client.host
   -  is_active: True
   -  expires_at: now + SESSION_TTL
   ↓
5. Create JWT access_token:
   {
     "uid": "user-uuid",
     "sid": "session-uuid",
     "type": "access",
     "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES
   }
   ↓
6. Create JWT refresh_token:
   {
     "uid": "user-uuid",
     "sid": "session-uuid",
     "jti": "refresh-jti-uuid",
     "type": "refresh",
     "exp": now + REFRESH_TOKEN_EXPIRE_DAYS
   }
   ↓
7. Persist Session:
   -  Link session to user
   -  Store refresh_jti / metadata for validation & rotation
   ↓
8. Return tokens:
   -  access_token in JSON response body
   -  refresh_token set as HttpOnly, Secure cookie
```

### Token Refresh Flow

```
1. POST /api/v1/auth/refresh
   ↓
   -  HttpOnly refresh_token cookie (JWT)
2. Decode & validate refresh_token:
   -  Verify signature
   -  Verify type == "refresh"
   -  Verify exp > now
   -  Extract uid, sid, jti
   ↓
3. Find Session:
   -  match by sid (session_id)
   -  is_active = True
   -  expires_at > now
   -  (optionally) jti match if you persist it for rotation
   ↓
4. Security checks:
   -  Verify user still exists and is_active = True
   -  Optionally verify device/IP consistency
   ↓
5. Update session:
   -  last_activity = now
   -  optionally rotate refresh token (new jti, new cookie)
   ↓
6. Create NEW access_token:
   {
     "uid": "user-uuid",
     "sid": "session-uuid",
     "type": "access",
     "exp": now + ACCESS_TOKEN_EXPIRE_MINUTES
   }
   ↓
7. Return:
   -  new access_token in JSON response body
   -  optionally updated refresh_token cookie (if rotating)
```

---

## 📚 API Usage Examples

### Register New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "SecurePass123!",
    "role": "USER"
  }'
```

<details>
<summary><b>Response (201 Created)</b></summary>

```json
{
  "code": 0,
  "message": "User registered successfully",
  "data": {
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": {
      "_id": "d85e6420-53c5-46bf-9938-977748d9d4e3",
      "name": "USER",
      "description": "Regular user with self-service capabilities",
      "permissions": ["user:*"],
      "is_active": true,
      "created_at": "2025-12-27T18:58:43.913000Z"
    },
    "id": "fa0da95f-8ebe-45ac-b32a-9bd6fc4e1e90",
    "is_active": true,
    "created_at": "2025-12-27T19:04:57.690754Z"
  }
}
```

</details>

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

<details>
<summary><b>Response (200 OK)</b></summary>

```json
{
  "code": 0,
  "message": "Login successful",
  "data": {
    "token": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "expires_in": 900,
      "token_type": "bearer"
    },
    "user": {
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": {
        "_id": "d85e6420-53c5-46bf-9938-977748d9d4e3",
        "name": "USER",
        "permissions": ["user:*"],
        "is_active": true
      },
      "id": "fa0da95f-8ebe-45ac-b32a-9bd6fc4e1e90",
      "is_active": true
    }
  }
}
```

</details>

### Get Current User

```bash
curl -X GET "http://localhost:8000/api/v1/user/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Cookie: refresh_token=<REFRESH_TOKEN>"
```

### Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 🛠 Development

### Adding New Features

1. **Create a new router** in `app/api/v1/routers/`

   ```python
   from fastapi import APIRouter

   router = APIRouter(prefix="/your-feature", tags=["your-feature"])

   @router.get("/")
   async def get_items():
       return {"items": []}
   ```

2. **Add schemas** in `app/schemas/your_feature.py`

   ```python
   from pydantic import BaseModel

   class ItemCreate(BaseModel):
       name: str
       description: str
   ```

3. **Create service layer** in `app/services/your_feature_service.py`

   ```python
   class YourFeatureService:
       @staticmethod
       async def create_item(data: dict):
           # Business logic here
           pass
   ```

4. **Register router** in `app/core/app_config.py`

   ```python
   from app.api.v1.routers import your_feature

   app.include_router(
       your_feature.router,
       prefix="/api/v1",
       tags=["your-feature"]
   )
   ```

### Running Tests

```bash
# Install dev dependencies
uv sync --dev

# Run tests with pytest
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code with black
uv run black app/

# Sort imports with isort
uv run isort app/

# Lint with ruff
uv run ruff check app/

# Type checking with mypy
uv run mypy app/
```

---

## 📦 Dependencies

| Package                       | Purpose                  | Version      |
| ----------------------------- | ------------------------ | ------------ |
| **fastapi[standard]**         | Web framework            | Latest       |
| **beanie**                    | MongoDB ODM              | ≥1.25, <1.29 |
| **motor**                     | Async MongoDB driver     | Latest       |
| **pydantic-settings**         | Configuration management | Latest       |
| **python-jose[cryptography]** | JWT encoding/decoding    | ≥3.5.0       |
| **passlib[argon2]**           | Password hashing library | ≥1.7.4       |
| **argon2-cffi**               | Argon2 implementation    | ≥25.1.0      |
| **user-agents**               | User-Agent parsing       | ≥2.2.0       |
| **uvicorn[standard]**         | ASGI web server          | Latest       |
| **python-multipart**          | Form data parsing        | Latest       |
| **pytz**                      | Timezone handling        | ≥2025.2      |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Beanie](https://beanie-odm.dev/) - MongoDB ODM
- [Argon2](https://github.com/P-H-C/phc-winner-argon2) - Password hashing

---

<div align="center">

[Report Bug](https://github.com/uzer-ab/fastapi-mongo-starter/issues) • [Request Feature](https://github.com/uzer-ab/fastapi-mongo-starter/issues)

</div>
