"""
Authentication & User Management Component
Provides user authentication, session management, and access control.
"""

import streamlit as st
import hashlib
import hmac
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger("rag_app.components.auth")


# Default users for demo (in production, use a proper database)
DEFAULT_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "Administrator",
        "role": "admin",
        "email": "admin@example.com",
    },
    "user": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "name": "Demo User",
        "role": "user",
        "email": "user@example.com",
    },
}


def init_auth_state():
    """Initialize authentication session state."""
    if 'auth_enabled' not in st.session_state:
        st.session_state.auth_enabled = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'lockout_until' not in st.session_state:
        st.session_state.lockout_until = None
    if 'users_db' not in st.session_state:
        st.session_state.users_db = DEFAULT_USERS.copy()


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hmac.compare_digest(hash_password(password), password_hash)


def check_authentication() -> bool:
    """Check if user is authenticated."""
    init_auth_state()
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user."""
    init_auth_state()
    return st.session_state.get('current_user')


def login(username: str, password: str) -> bool:
    """
    Attempt to log in a user.

    Args:
        username: Username to authenticate
        password: Password to verify

    Returns:
        True if login successful, False otherwise
    """
    init_auth_state()

    # Check lockout
    if st.session_state.lockout_until:
        if datetime.now() < st.session_state.lockout_until:
            remaining = (st.session_state.lockout_until - datetime.now()).seconds
            logger.warning(f"Login attempt during lockout: {username}")
            st.error(f"Account locked. Try again in {remaining} seconds.")
            return False
        else:
            st.session_state.lockout_until = None
            st.session_state.login_attempts = 0

    users = st.session_state.users_db
    if username in users:
        user = users[username]
        if verify_password(password, user['password_hash']):
            st.session_state.authenticated = True
            st.session_state.current_user = {
                "username": username,
                "name": user['name'],
                "role": user['role'],
                "email": user['email'],
                "login_time": datetime.now().isoformat(),
            }
            st.session_state.login_attempts = 0
            logger.info(f"User logged in: {username}")
            return True

    # Failed login
    st.session_state.login_attempts += 1
    logger.warning(f"Failed login attempt for: {username} (attempt {st.session_state.login_attempts})")

    # Lockout after 5 failed attempts
    if st.session_state.login_attempts >= 5:
        st.session_state.lockout_until = datetime.now() + timedelta(minutes=5)
        st.error("Too many failed attempts. Account locked for 5 minutes.")
    else:
        st.error("Invalid username or password.")

    return False


def logout():
    """Log out the current user."""
    init_auth_state()
    username = st.session_state.current_user.get('username') if st.session_state.current_user else 'unknown'
    st.session_state.authenticated = False
    st.session_state.current_user = None
    logger.info(f"User logged out: {username}")


def register_user(username: str, password: str, name: str, email: str, role: str = "user") -> bool:
    """
    Register a new user.

    Args:
        username: Unique username
        password: Password (will be hashed)
        name: Display name
        email: Email address
        role: User role (default: user)

    Returns:
        True if registration successful, False otherwise
    """
    init_auth_state()

    if username in st.session_state.users_db:
        return False

    st.session_state.users_db[username] = {
        "password_hash": hash_password(password),
        "name": name,
        "role": role,
        "email": email,
        "created_at": datetime.now().isoformat(),
    }

    logger.info(f"New user registered: {username}")
    return True


def render_auth():
    """Render the authentication UI."""
    init_auth_state()

    st.title("🔐 Authentication Required")
    st.markdown("Please log in to access the RAG Starter Kit Pro.")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        render_login_form()

    with tab2:
        render_register_form()


def render_login_form():
    """Render the login form."""
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if username and password:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
            else:
                st.warning("Please enter both username and password.")

    st.markdown("---")
    st.markdown("**Demo Credentials:**")
    st.code("Username: admin | Password: admin123\nUsername: user | Password: user123")


def render_register_form():
    """Render the registration form."""
    with st.form("register_form"):
        st.subheader("Create Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register", use_container_width=True)

        if submitted:
            if not all([username, email, name, password, confirm_password]):
                st.warning("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                if register_user(username, password, name, email):
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username already exists.")


def render_user_menu():
    """Render user menu in sidebar."""
    init_auth_state()

    if st.session_state.authenticated and st.session_state.current_user:
        user = st.session_state.current_user
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 {user['name']}**")
        st.sidebar.caption(f"Role: {user['role']}")

        if st.sidebar.button("Logout", use_container_width=True):
            logout()
            st.rerun()


def require_role(required_role: str) -> bool:
    """
    Check if current user has the required role.

    Args:
        required_role: Role required for access

    Returns:
        True if user has required role, False otherwise
    """
    init_auth_state()

    if not st.session_state.authenticated:
        return False

    user = st.session_state.current_user
    if not user:
        return False

    # Admin has all permissions
    if user['role'] == 'admin':
        return True

    return user['role'] == required_role


def get_user_settings() -> Dict[str, Any]:
    """Get settings for the current user."""
    init_auth_state()
    user = st.session_state.current_user

    if not user:
        return {}

    # Load user settings from session or default
    settings_key = f"user_settings_{user['username']}"
    if settings_key not in st.session_state:
        st.session_state[settings_key] = {
            "theme": "light",
            "notifications": True,
            "default_model": "claude-sonnet-4-5",
            "default_vector_store": "chromadb",
        }

    return st.session_state[settings_key]


def save_user_settings(settings: Dict[str, Any]):
    """Save settings for the current user."""
    init_auth_state()
    user = st.session_state.current_user

    if user:
        settings_key = f"user_settings_{user['username']}"
        st.session_state[settings_key] = settings
        logger.info(f"Settings saved for user: {user['username']}")
