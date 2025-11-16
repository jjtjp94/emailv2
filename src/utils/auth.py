"""
Authentication utilities for Microsoft Graph API.
Handles OAuth 2.0 device code flow and token management.
"""

import json
import logging
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import msal
from msal import PublicClientApplication

from src.config import get_settings

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages Microsoft Graph API authentication using device code flow."""

    # Keyring service name for storing tokens
    KEYRING_SERVICE = "EmailDraftingTool"
    KEYRING_USERNAME = "microsoft_graph_token"

    def __init__(self):
        self.settings = get_settings()
        self.app: Optional[PublicClientApplication] = None
        self._token_cache = None
        self._init_msal_app()

    def _init_msal_app(self):
        """Initialize MSAL Public Client Application."""
        # Token cache file
        cache_file = self.settings.CACHE_DIR / "msal_token_cache.json"

        # Load existing cache if available
        self._token_cache = msal.SerializableTokenCache()
        if cache_file.exists():
            try:
                self._token_cache.deserialize(cache_file.read_text())
                logger.info("Loaded existing token cache")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {e}")

        # Create MSAL app
        self.app = PublicClientApplication(
            client_id=self.settings.AZURE_CLIENT_ID,
            authority=self.settings.AZURE_AUTHORITY,
            token_cache=self._token_cache
        )

        logger.info(f"Initialized MSAL app with client ID: {self.settings.AZURE_CLIENT_ID[:8]}...")

    def _save_cache(self):
        """Save token cache to file."""
        if self._token_cache and self._token_cache.has_state_changed:
            cache_file = self.settings.CACHE_DIR / "msal_token_cache.json"
            try:
                cache_file.write_text(self._token_cache.serialize())
                logger.debug("Saved token cache")
            except Exception as e:
                logger.error(f"Failed to save token cache: {e}")

    def get_token(self) -> Optional[str]:
        """
        Get a valid access token. Tries to get from cache first, then prompts for auth.

        Returns:
            Access token string, or None if authentication fails
        """
        # Try to get token silently from cache
        accounts = self.app.get_accounts()

        if accounts:
            logger.info(f"Found {len(accounts)} cached account(s)")
            # Try to get token silently for the first account
            result = self.app.acquire_token_silent(
                scopes=self.settings.AZURE_SCOPES,
                account=accounts[0]
            )

            if result and "access_token" in result:
                logger.info("Successfully acquired token silently")
                self._save_cache()
                return result["access_token"]
            else:
                logger.info("Silent token acquisition failed, need interactive auth")
        else:
            logger.info("No cached accounts found")

        # If silent acquisition failed, use device code flow
        return self._authenticate_device_code()

    def _authenticate_device_code(self) -> Optional[str]:
        """
        Authenticate using device code flow (interactive).

        Returns:
            Access token string, or None if authentication fails
        """
        logger.info("Starting device code flow authentication")

        try:
            flow = self.app.initiate_device_flow(scopes=self.settings.AZURE_SCOPES)

            if "user_code" not in flow:
                logger.error("Failed to create device flow")
                return None

            # Display instructions to user
            print("\n" + "=" * 80)
            print("MICROSOFT AUTHENTICATION REQUIRED")
            print("=" * 80)
            print(flow["message"])
            print("=" * 80)
            print("\nWaiting for authentication...")

            # Wait for the user to authenticate
            result = self.app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                logger.info("Device code authentication successful")
                self._save_cache()

                # Also save to keyring as backup
                self._save_token_to_keyring(result)

                print("\n✓ Authentication successful!")
                print("=" * 80 + "\n")

                return result["access_token"]
            else:
                error = result.get("error_description", result.get("error", "Unknown error"))
                logger.error(f"Device code authentication failed: {error}")
                print(f"\n✗ Authentication failed: {error}\n")
                return None

        except Exception as e:
            logger.exception(f"Exception during device code authentication: {e}")
            return None

    def _save_token_to_keyring(self, token_response: Dict[str, Any]):
        """Save token response to system keyring as backup."""
        try:
            token_data = {
                "access_token": token_response.get("access_token"),
                "refresh_token": token_response.get("refresh_token"),
                "expires_at": (datetime.now() + timedelta(seconds=token_response.get("expires_in", 3600))).isoformat(),
                "scope": " ".join(self.settings.AZURE_SCOPES)
            }
            keyring.set_password(
                self.KEYRING_SERVICE,
                self.KEYRING_USERNAME,
                json.dumps(token_data)
            )
            logger.debug("Saved token to system keyring")
        except Exception as e:
            logger.warning(f"Failed to save token to keyring: {e}")

    def clear_cache(self):
        """Clear all cached authentication data."""
        logger.info("Clearing authentication cache")

        # Clear MSAL cache file
        cache_file = self.settings.CACHE_DIR / "msal_token_cache.json"
        if cache_file.exists():
            cache_file.unlink()
            logger.info("Deleted token cache file")

        # Clear keyring
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            logger.info("Deleted token from keyring")
        except keyring.errors.PasswordDeleteError:
            pass  # Token wasn't in keyring
        except Exception as e:
            logger.warning(f"Failed to delete token from keyring: {e}")

        # Reinitialize MSAL app
        self._init_msal_app()
        print("Authentication cache cleared. Please authenticate again.")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated (has valid cached token)."""
        accounts = self.app.get_accounts()
        if not accounts:
            return False

        # Try to get token silently
        result = self.app.acquire_token_silent(
            scopes=self.settings.AZURE_SCOPES,
            account=accounts[0]
        )

        return result is not None and "access_token" in result

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get basic user information from Microsoft Graph.

        Returns:
            User info dict with displayName, mail, userPrincipalName, etc.
        """
        import requests

        token = self.get_token()
        if not token:
            return None

        headers = {"Authorization": f"Bearer {token}"}

        try:
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None


# Global instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create the global AuthManager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


def get_access_token() -> Optional[str]:
    """Convenience function to get access token."""
    return get_auth_manager().get_token()


def clear_auth_cache():
    """Convenience function to clear authentication cache."""
    get_auth_manager().clear_cache()
