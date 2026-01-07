# Authentication Setup Guide

Configure Google OAuth authentication for your RAG application using Streamlit Cloud's built-in authentication.

## Overview

RAG Starter Kit Pro uses Google OAuth for simple, secure authentication:
- Sign in with Google account
- No password management required
- Automatic session handling
- Easy to enable/disable

## Enabling Authentication

### Option 1: Environment Variable

Set in your `.env` file or environment:
```bash
AUTH_ENABLED=true
```

### Option 2: Streamlit Secrets

Add to `.streamlit/secrets.toml`:
```toml
AUTH_ENABLED = true
```

### Option 3: Session State

Set programmatically:
```python
st.session_state.auth_enabled = True
```

## Streamlit Cloud Deployment (Recommended)

When deploying to Streamlit Cloud, Google OAuth is handled automatically:

### Setup Steps

1. **Deploy your app** to [Streamlit Cloud](https://share.streamlit.io)

2. **Go to App Settings**
   - Click the menu (⋮) on your deployed app
   - Select "Settings"

3. **Enable Viewer Authentication**
   - Go to "Sharing" section
   - Enable "Viewer authentication"
   - Select "Google" as the identity provider

4. **Configure Allowed Users** (Optional)
   - Add specific email addresses to allow
   - Or allow all users from specific domains
   - Example: `@yourcompany.com`

5. **Save Settings**
   - Authentication is now active
   - Users must sign in with Google to access

### How It Works

When a user visits your app:

1. They see a Google sign-in page
2. After authentication, `st.user` contains their info:
   - `st.user.email` - User's email address
   - `st.user.name` - User's display name (if available)

3. The app checks authentication status automatically

## Local Development

For local development, you have two options:

### Option 1: Disable Authentication

```bash
# .env
AUTH_ENABLED=false
```

This allows full access without sign-in during development.

### Option 2: Use Streamlit Auth Testing

Run with authentication testing:
```bash
streamlit run app.py --server.auth=mock
```

## User Information

### Getting Current User

```python
from components.auth import get_current_user

user = get_current_user()
if user:
    print(f"Welcome, {user['name']}")
    print(f"Email: {user['email']}")
```

### User Object Structure

```python
{
    "email": "user@example.com",
    "name": "User Name",
    "role": "user"
}
```

## Session Management

### Check Authentication Status

```python
from components.auth import check_authentication

if check_authentication():
    # User is authenticated
    render_main_app()
else:
    # Show login page
    render_auth()
```

### Logout

```python
from components.auth import logout

# Log out the current user
logout()
st.rerun()
```

## User Menu

The app includes a sidebar user menu that shows:
- User's name
- User's email
- Logout button

```python
from components.auth import render_user_menu

# Render in sidebar
render_user_menu()
```

## Role-Based Access Control

While Google OAuth doesn't provide roles directly, you can implement role management:

### Define Admin Emails

```python
ADMIN_EMAILS = [
    "admin@yourcompany.com",
    "owner@yourcompany.com"
]

def get_user_role(email):
    if email in ADMIN_EMAILS:
        return "admin"
    return "user"
```

### Check Roles

```python
from components.auth import require_role

if require_role("admin"):
    render_admin_panel()
else:
    st.warning("Admin access required")
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AUTH_ENABLED | false | Enable/disable authentication |

### Streamlit Cloud Settings

| Setting | Description |
|---------|-------------|
| Viewer authentication | Enable Google sign-in requirement |
| Allowed users | Specific email addresses to allow |
| Allowed domains | Email domains to allow (e.g., @company.com) |

## Security Best Practices

### 1. Use HTTPS

Streamlit Cloud automatically provides HTTPS. For self-hosted deployments, ensure you configure SSL/TLS.

### 2. Restrict Access

Configure allowed users or domains in Streamlit Cloud settings rather than allowing all Google users.

### 3. Monitor Access

Check your Streamlit Cloud dashboard for:
- Active sessions
- Login attempts
- User activity

### 4. Keep Auth Enabled in Production

```toml
# Production .streamlit/secrets.toml
AUTH_ENABLED = true
```

## Troubleshooting

### "Authentication not working locally"

Local development doesn't have access to Streamlit Cloud's OAuth. Options:
- Set `AUTH_ENABLED=false` for local testing
- Deploy to Streamlit Cloud for full OAuth testing

### "User not being recognized"

Ensure your app checks `st.user`:
```python
if hasattr(st, 'user') and st.user.email:
    # User is authenticated
    pass
```

### "Can't access after login"

Check that:
1. Your email is in the allowed users list (if configured)
2. Your domain is in the allowed domains (if configured)
3. AUTH_ENABLED is set correctly

### "Session keeps expiring"

Streamlit Cloud sessions have a default timeout. Users need to:
- Keep the app tab active
- Re-authenticate after long periods of inactivity

## Migration from Password Auth

If you're migrating from the previous password-based authentication:

1. **Remove old user database** - No longer needed
2. **Update AUTH_ENABLED** - Set to `true`
3. **Deploy to Streamlit Cloud** - Configure Google OAuth
4. **Notify users** - They'll now sign in with Google

The new system is simpler:
- No passwords to manage
- No user registration required
- Automatic security updates from Google
- Single sign-on if users are already logged into Google

## Summary

| Feature | Description |
|---------|-------------|
| Authentication | Google OAuth via Streamlit Cloud |
| Configuration | Single `AUTH_ENABLED` setting |
| User Info | Email and name from Google account |
| Roles | Implement based on email addresses |
| Sessions | Managed automatically by Streamlit |
