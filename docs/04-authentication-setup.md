# Authentication Setup Guide

Configure user authentication and access control for your RAG application.

## Overview

RAG Starter Kit Pro includes a built-in authentication system with:
- User registration and login
- Role-based access control
- Session management
- Brute force protection

## Enabling Authentication

### 1. Enable in Configuration

```python
# In app.py
st.session_state.auth_enabled = True
```

Or via environment variable:
```toml
AUTH_ENABLED = "true"
```

### 2. Configure Secret Key

```toml
# .streamlit/secrets.toml
SECRET_KEY = "your-secure-random-key-here"
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Default Users

The system comes with default users for testing:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | admin |
| user | user123 | user |

**Important:** Change these in production!

## User Management

### Adding Users Programmatically

```python
from components.auth import register_user

register_user(
    username="newuser",
    password="securepassword",
    name="New User",
    email="user@example.com",
    role="user"
)
```

### User Roles

| Role | Permissions |
|------|-------------|
| admin | Full access, user management |
| user | Standard access |
| viewer | Read-only access |

### Role-Based Access Control

```python
from components.auth import require_role

if require_role("admin"):
    # Admin-only functionality
    render_admin_panel()
else:
    st.warning("Admin access required")
```

## Session Management

### Session Configuration

```python
from utils.session_manager import SessionManager
from datetime import timedelta

# Create session manager with custom timeout
session_mgr = SessionManager(timeout=timedelta(hours=8))
```

### Session Operations

```python
# Create session
session_id = session_mgr.create_session(user_id, data)

# Get session data
data = session_mgr.get_session(session_id)

# Update session
session_mgr.update_session(session_id, {"key": "value"})

# Extend session
session_mgr.extend_session(session_id)

# Destroy session
session_mgr.destroy_session(session_id)
```

## Security Features

### Brute Force Protection

- Account lockout after 5 failed attempts
- 5-minute lockout period
- Automatic reset after successful login

### Password Requirements

Recommended password policy:
- Minimum 8 characters
- Mix of uppercase/lowercase
- At least one number
- At least one special character

Implement custom validation:
```python
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number"
    return True, "Password is valid"
```

## Database Backend

### Default: Session State

By default, users are stored in Streamlit session state (not persistent).

### Production: Database

For production, implement a database backend:

```python
import sqlite3

class UserDatabase:
    def __init__(self, db_path="users.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                name TEXT,
                email TEXT,
                role TEXT,
                created_at TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, username, password_hash, name, email, role):
        self.conn.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, name, email, role, datetime.now())
        )
        self.conn.commit()

    def get_user(self, username):
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()
```

## OAuth Integration

### Google OAuth (Example)

```python
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id='your-client-id',
    client_secret='your-client-secret',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid email profile'},
)
```

## Audit Logging

Track authentication events:

```python
import logging

auth_logger = logging.getLogger("auth")

def log_auth_event(event_type, username, success, details=None):
    auth_logger.info(f"{event_type} | user={username} | success={success} | {details}")
```

## Troubleshooting

### "Session Expired"
- Sessions timeout after 24 hours by default
- User needs to log in again
- Consider extending session timeout

### "Account Locked"
- Wait 5 minutes
- Or reset via admin panel
- Check for brute force attacks

### "Password Reset Not Working"
- Implement email-based reset
- Provide admin reset option
- Log password reset attempts

## Best Practices

1. **Use HTTPS** in production
2. **Implement password hashing** (bcrypt recommended)
3. **Enable session timeouts**
4. **Log all authentication events**
5. **Implement account recovery**
6. **Use secure session tokens**
7. **Validate all user input**
