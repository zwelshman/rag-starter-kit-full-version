"""
Session Manager
Advanced session management for multi-user environments.
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
import uuid

logger = logging.getLogger("rag_app.utils.session_manager")


class SessionManager:
    """
    Manages user sessions with persistence and expiration.
    """

    DEFAULT_TIMEOUT = timedelta(hours=24)

    def __init__(self, timeout: Optional[timedelta] = None):
        """
        Initialize session manager.

        Args:
            timeout: Session timeout duration (default: 24 hours)
        """
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._init_storage()

    def _init_storage(self):
        """Initialize session storage."""
        if 'session_storage' not in st.session_state:
            st.session_state.session_storage = {}
        if 'session_metadata' not in st.session_state:
            st.session_state.session_metadata = {}

    def create_session(self, user_id: str, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a user.

        Args:
            user_id: User identifier
            data: Optional initial session data

        Returns:
            Session ID
        """
        self._init_storage()

        session_id = self._generate_session_id(user_id)

        st.session_state.session_storage[session_id] = data or {}
        st.session_state.session_metadata[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.timeout).isoformat(),
        }

        logger.info(f"Session created for user {user_id}: {session_id[:8]}...")
        return session_id

    def _generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID."""
        unique_string = f"{user_id}:{datetime.now().isoformat()}:{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if expired/not found
        """
        self._init_storage()

        if session_id not in st.session_state.session_storage:
            return None

        # Check expiration
        metadata = st.session_state.session_metadata.get(session_id, {})
        expires_at = datetime.fromisoformat(metadata.get("expires_at", datetime.now().isoformat()))

        if datetime.now() > expires_at:
            self.destroy_session(session_id)
            return None

        # Update last access
        st.session_state.session_metadata[session_id]["last_access"] = datetime.now().isoformat()

        return st.session_state.session_storage[session_id]

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            data: Data to update

        Returns:
            True if successful, False otherwise
        """
        self._init_storage()

        if session_id not in st.session_state.session_storage:
            return False

        st.session_state.session_storage[session_id].update(data)
        st.session_state.session_metadata[session_id]["last_access"] = datetime.now().isoformat()

        return True

    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was destroyed, False if not found
        """
        self._init_storage()

        if session_id in st.session_state.session_storage:
            del st.session_state.session_storage[session_id]
            if session_id in st.session_state.session_metadata:
                del st.session_state.session_metadata[session_id]
            logger.info(f"Session destroyed: {session_id[:8]}...")
            return True
        return False

    def get_user_sessions(self, user_id: str) -> list:
        """
        Get all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of session IDs
        """
        self._init_storage()

        sessions = []
        for session_id, metadata in st.session_state.session_metadata.items():
            if metadata.get("user_id") == user_id:
                sessions.append(session_id)
        return sessions

    def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        self._init_storage()

        expired = []
        now = datetime.now()

        for session_id, metadata in st.session_state.session_metadata.items():
            expires_at = datetime.fromisoformat(metadata.get("expires_at", now.isoformat()))
            if now > expires_at:
                expired.append(session_id)

        for session_id in expired:
            self.destroy_session(session_id)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        return len(expired)

    def extend_session(self, session_id: str, duration: Optional[timedelta] = None) -> bool:
        """
        Extend session expiration.

        Args:
            session_id: Session identifier
            duration: Extension duration (default: session timeout)

        Returns:
            True if successful, False otherwise
        """
        self._init_storage()

        if session_id not in st.session_state.session_metadata:
            return False

        extension = duration or self.timeout
        new_expiry = datetime.now() + extension
        st.session_state.session_metadata[session_id]["expires_at"] = new_expiry.isoformat()

        return True

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata.

        Args:
            session_id: Session identifier

        Returns:
            Session metadata or None
        """
        self._init_storage()
        return st.session_state.session_metadata.get(session_id)


# Convenience functions for Streamlit
def get_current_session() -> Optional[Dict[str, Any]]:
    """Get the current user's session data."""
    if 'current_session_id' not in st.session_state:
        return None

    manager = SessionManager()
    return manager.get_session(st.session_state.current_session_id)


def save_to_session(key: str, value: Any) -> bool:
    """Save a value to the current session."""
    if 'current_session_id' not in st.session_state:
        return False

    manager = SessionManager()
    return manager.update_session(
        st.session_state.current_session_id,
        {key: value}
    )


def get_from_session(key: str, default: Any = None) -> Any:
    """Get a value from the current session."""
    session = get_current_session()
    if session is None:
        return default
    return session.get(key, default)
