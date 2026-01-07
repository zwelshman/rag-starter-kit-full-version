"""
Authentication & User Management Component
Provides Google OAuth authentication using Streamlit's built-in OAuth support.
"""

import streamlit as st
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("rag_app.components.auth")


def init_auth_state():
    """Initialize authentication session state."""
    if 'auth_enabled' not in st.session_state:
        st.session_state.auth_enabled = False
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None


def check_authentication() -> bool:
    """
    Check if user is authenticated via Google OAuth.

    Returns:
        True if authenticated, False otherwise
    """
    init_auth_state()

    # If auth is not enabled, always return True
    if not st.session_state.get('auth_enabled', False):
        return True

    # Check if user is logged in via Streamlit's user API
    if hasattr(st, 'user') and st.user.email:
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "email": st.user.email,
            "name": getattr(st.user, 'name', st.user.email.split('@')[0]),
            "role": "user",
        }
        logger.info(f"User authenticated via Google OAuth: {st.user.email}")
        return True

    # Fallback: check session state
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user."""
    init_auth_state()

    # Try to get user from Streamlit's user API first
    if hasattr(st, 'user') and st.user.email:
        return {
            "email": st.user.email,
            "name": getattr(st.user, 'name', st.user.email.split('@')[0]),
            "role": "user",
        }

    return st.session_state.get('current_user')


def logout():
    """Log out the current user."""
    init_auth_state()
    user = st.session_state.current_user
    username = user.get('email') if user else 'unknown'
    st.session_state.authenticated = False
    st.session_state.current_user = None
    logger.info(f"User logged out: {username}")


def render_auth():
    """Render the authentication UI for Google OAuth."""
    init_auth_state()

    st.title("Welcome to RAG Starter Kit Pro")

    st.markdown("""
    ### Sign in to continue

    This application requires authentication. Please sign in with your Google account to access all features.
    """)

    # Show login button that redirects to Google OAuth
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <p style="color: #666; margin-bottom: 20px;">
                Click the button below to sign in with Google
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Streamlit Cloud automatically handles OAuth - show instructions
        st.info("""
        **To enable Google OAuth:**

        1. Deploy this app to Streamlit Cloud
        2. Go to your app settings
        3. Enable "Viewer authentication"
        4. Select "Google" as the identity provider
        5. Configure allowed email domains (optional)

        The login will appear automatically when configured.
        """)

        st.markdown("---")
        st.caption("For local development, set `AUTH_ENABLED=false` in your environment.")


def render_user_menu():
    """Render user menu in sidebar."""
    init_auth_state()

    user = get_current_user()
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{user.get('name', 'User')}**")
        st.sidebar.caption(f"{user.get('email', '')}")

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
    if user.get('role') == 'admin':
        return True

    return user.get('role') == required_role


def get_user_settings() -> Dict[str, Any]:
    """Get settings for the current user."""
    init_auth_state()
    user = st.session_state.current_user

    if not user:
        return {}

    # Load user settings from session or default
    email = user.get('email', 'default')
    settings_key = f"user_settings_{email}"
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
        email = user.get('email', 'default')
        settings_key = f"user_settings_{email}"
        st.session_state[settings_key] = settings
        logger.info(f"Settings saved for user: {email}")
