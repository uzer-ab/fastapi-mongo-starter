# FastAPI Template (MongoDB)

Production-ready FastAPI template with MongoDB (Beanie ODM), JWT authentication, session management, admin panel, and comprehensive logging.

## Features

- **Async MongoDB** with Beanie ODM (User/Session models with refresh tokens)
- **JWT Authentication** (15min access + 30Days refresh tokens)
- **Session Management** (device fingerprinting, IP tracking, bulk revocation)
- **Role-based Access** (USER/ADMIN with `require_admin` dependency)
- **API Versioning** (`/api/v1/` with APIRouter)
- **Pydantic Validation** (schemas for requests/responses)

## 📁 Directory Structure

```
├── app
│   ├── api
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── __init__.py
│   │       └── routers
│   │           ├── admin.py
│   │           ├── auth.py
│   │           ├── __init__.py
│   │           └── users.py
│   ├── core
│   │   ├── app_config.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── exception_handlers.py
│   │   ├── health.py
│   │   ├── __init__.py
│   │   └── middleware.py
│   ├── dependencies.py
│   ├── __init__.py
│   ├── main.py
│   ├── middleware
│   │   └── http_logger.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── role.py
│   │   ├── session.py
│   │   └── user.py
│   ├── schemas
│   │   ├── auth.py
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services
│   │   └── session_service.py
│   └── utils
│       ├── auth.py
│       ├── formatter.py
│       ├── logging.py
│       └── user_agent.py
├── example.env
├── LICENSE
├── logs
│   └── app.log
├── pyproject.toml
├── README.md
└── uv.lock
```

## 🚀 Quick Start

1. **Copy environment**: `cp example.env .env`
2. **Edit `.env`**:

```
   - MONGO_URL=
   - MONGODB_NAME=
   - SECRET_KEY=
   - HOST=0.0.0.0
   - PORT=8000
   - WORKERS=4
   - ENVIRONMENT="devlopment"
```

3. **Install dependencies**: `uv sync`

4. **Run server**: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`

5. **Open docs**: - Swagger: `http://localhost:8000/docs`

## 🔑 API Endpoints

### Root

```
GET  /health                      # health check
GET  /ready                       # readiness check
GET  /                            # root endpoint
```

### Authentication

```
POST /api/v1/auth/register     # username + email + password → create new user
POST /api/v1/auth/login        # email/username + password → access & refresh tokens
POST /api/v1/auth/refresh      # refresh_token → new access
POST /api/v1/auth/logout       # Bearer token → revoke session
```

### User

```
GET /api/v1/user/              # read current user (Bearer token)
PUT /api/v1/user/              # update current user (Bearer token)
DELETE /api/v1/user/           # delete current user (Bearer token)
```

### Admin

```
GET /api/v1/admin/users?page=1&size=10      # list all users (admin, Bearer token, pagination)
PUT /api/v1/admin/{user_id}                 # update specific user by ID (admin, Bearer token)
DELETE /api/v1/admin/{user_id}              # delete specific user by ID (admin, Bearer token)
```

## 🛠 Environment Variables

| Variable       | Required | Default       | Description                 |
| -------------- | -------- | ------------- | --------------------------- |
| `MONGO_URL`    | ✅       | -             | MongoDB connection string   |
| `MONGODB_NAME` | ✅       | -             | Database name               |
| `SECRET_KEY`   | ✅       | auto-gen      | JWT signing key (32+ chars) |
| `HOST`         | ❌       | `0.0.0.0`     | Bind address                |
| `PORT`         | ❌       | `8000`        | Server port                 |
| `WORKERS`      | ❌       | `cpu*1.4`     | Uvicorn workers             |
| `ENVIRONMENT`  | ❌       | `development` | Project Environment         |

## 🏗 Development Workflow

1. **Add new router**: `app/api/v1/routers/new_feature.py`
2. **Mount in main.py**: `app.include_router(new_feature.router, prefix="/api/v1/new", tags=["new"])`
3. **Add schemas**: `app/schemas/new_feature.py`
4. **Add service**: `app/services/new_feature_service.py`

## 📦 Dependencies (pyproject.toml)

```
[project]
name = "fastapi-app"
version = "0.1.0"
description = "FastAPI template with MongoDB + Beanie"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]",
    "beanie>=1.25,<1.29.0",
    "motor",
    "pydantic-settings",
    "python-multipart",
    "uvicorn[standard]",
    "python-jose[cryptography]>=3.5.0",
    "argon2-cffi>=25.1.0",
    "passlib[argon2]>=1.7.4",
    "user-agents>=2.2.0",
    "pytz>=2025.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]
```

| Package                   | Purpose               | Version        |
| ------------------------- | --------------------- | -------------- |
| fastapi[standard]         | Web framework         | Latest         |
| beanie                    | MongoDB ODM           | `≥1.25, <1.29` |
| motor                     | Async MongoDB         | Latest         |
| pydantic-settings         | Config management     | Latest         |
| python-jose[cryptography] | JWT tokens            | `≥3.5.0`       |
| passlib[argon2]           | Password hashing      | `≥1.7.4`       |
| argon2-cffi               | Argon2 implementation | `≥25.1.0`      |
| user-agents               | Device fingerprinting | `≥2.2.0`       |
| uvicorn[standard]         | ASGI server           | Latest         |
| python-multipart          | Form data parsing     | Latest         |
| pytz                      | Timezone handling     | `≥2025.2`      |

## 🔒 Security Features

- **Argon2** password hashing with automatic rehashing
- **Dual JWT tokens** (access + refresh) with hybrid storage
- **Session validation** (DB + token double-check)
- **Device fingerprinting** (browser/OS/IP)
- **Soft-delete** users + auto-session cleanup
- **Role-based access control** (RBAC)
- **Refresh token rotation** with JTI tracking
- **HttpOnly cookies** for refresh tokens
- **Bearer authentication** for access tokens

## Token Architecture

### Access Token

- **Storage**: Bearer token in Authorization header
- **Lifetime**: Short-lived (typically 15 minutes)
- **Claims**: `uid` (user ID), `sid` (session ID), `type: "access"`
- **Purpose**: Authorizes API requests

### Refresh Token

- **Storage**: HttpOnly cookie (XSS protection)
- **Lifetime**: Long-lived (typically 7-30 days)
- **Claims**: `uid`, `sid`, `jti` (JWT ID for rotation), `type: "refresh"`
- **Purpose**: Issues new access tokens without re-authentication

## Security Mechanisms

**Token Rotation**
The implementation uses `jti` (JWT ID) in refresh tokens to enable token rotation, where each refresh operation invalidates the old token and issues a new one, preventing replay attacks.

**Multi-Layer Validation**
The logout endpoint accepts tokens from multiple sources (Authorization header or cookie), ensuring users can log out even if one token type is compromised.

**Session Tracking**
Both tokens share the same `sid` (session ID), allowing server-side session revocation and tracking across devices using the device fingerprinting data.

**Defense in Depth**

- HttpOnly cookies prevent XSS token theft
- Bearer tokens enable mobile/API client support
- Database session validation catches compromised tokens
- IP and user-agent tracking detects suspicious activity

## 🧪 User Creation Payload & Route

### Create User

#### Curl

```
curl --location 'http://127.0.0.1:8000/api/v1/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{
  "username": "talha",
  "email": "talha@example.com",
  "full_name": "Talha",
  "password": "12345"
}'
```

#### Response (201 Created)

```
{
    "code": 0,
    "message": "User registered successfully",
    "data": {
        "username": "talha",
        "email": "talha@example.com",
        "full_name": "Talha",
        "role": {
            "_id": "d85e6420-53c5-46bf-9938-977748d9d4e3",
            "name": "USER",
            "description": "Regular user with self-service capabilities",
            "permissions": [
                "user:*"
            ],
            "is_active": true,
            "created_at": "2025-12-27T18:58:43.913000Z"
        },
        "id": "fa0da95f-8ebe-45ac-b32a-9bd6fc4e1e90",
        "is_active": true,
        "created_at": "2025-12-27T19:04:57.690754Z"
    }
}

```

### Login User

#### Curl

```
curl --location 'http://127.0.0.1:8000/api/v1/auth/login' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email": "talha@example.com",
  "password": "12345"
}'
```

#### Response (200 OK)

```
{
    "code": 0,
    "message": "Login successful",
    "data": {
        "token": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJmYTBkYTk1Zi04ZWJlLTQ1YWMtYjMyYS05YmQ2ZmM0ZTFlOTAiLCJzaWQiOiI1OWEyYzI2Ni05NGUyLTQzYmMtYjlhNC1mNDRmOWQzNTQzNWEiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY2ODY2MTMzfQ.tl1CGdKTh_3S37Cx0aDVwHtxKtbH8XqR9Qa55QysEIY",
            "expires_in": 900,
            "token_type": "bearer"
        },
        "user": {
            "username": "talha",
            "email": "talha@example.com",
            "full_name": "Talha",
            "role": {
                "_id": "d85e6420-53c5-46bf-9938-977748d9d4e3",
                "name": "USER",
                "description": "Regular user with self-service capabilities",
                "permissions": [
                    "user:*"
                ],
                "is_active": true,
                "created_at": "2025-12-27T18:58:43.913000Z"
            },
            "id": "fa0da95f-8ebe-45ac-b32a-9bd6fc4e1e90",
            "is_active": true,
            "created_at": "2025-12-27T19:04:57.690000Z"
        }
    }
}

```

### Refresh Token

#### Curl

```
curl --location --request POST 'http://127.0.0.1:8000/api/v1/auth/refresh' \
--header 'Cookie: refresh_token= Bearer <ACCESS_TOKEN>'
```

#### Response (200 OK)

```
{
    "code": 0,
    "message": "Token refreshed successfully",
    "data": {
        "token": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI2YWJjY2RlNC1kMzA2LTQ1NDItOTg4Mi1hYmU0MmNlMTRkZDEiLCJzaWQiOiJkMmM2MTk4NC1jZGNkLTQ5ODgtYmVkNS1iZjBmOTY0MTFkOTMiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY2ODY2MDIyfQ.zsfplOVfnwwt31zTwAaemm2QWgoTd-9mg4tC7eVUf6E",
            "expires_in": 900,
            "token_type": "bearer"
        }
    }
}
```

## 🔄 Session & User Workflow

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
