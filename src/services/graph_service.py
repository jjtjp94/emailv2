"""
Microsoft Graph API service for email operations.
Handles fetching emails, creating drafts, and managing Outlook data.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import get_settings
from src.utils.auth import get_access_token

logger = logging.getLogger(__name__)


class GraphService:
    """Service for interacting with Microsoft Graph API."""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.settings = get_settings()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization token."""
        token = get_access_token()
        if not token:
            raise Exception("Failed to get access token")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Make a request to Microsoft Graph API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body for POST/PATCH requests
            timeout: Request timeout in seconds

        Returns:
            Response JSON or None if request failed
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                json=json_data,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {method} {endpoint}: {e}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {method} {endpoint}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error for {method} {endpoint}: {e}")
            raise

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user's profile information."""
        logger.info("Fetching user profile")
        return self._make_request("GET", "/me")

    def fetch_emails(
        self,
        folder: str = "inbox",
        max_results: int = 20,
        filter_query: Optional[str] = None,
        select_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails from a specific folder.

        Args:
            folder: Folder name (inbox, sentitems, drafts, etc.)
            max_results: Maximum number of emails to fetch
            filter_query: OData filter query (e.g., "isRead eq false")
            select_fields: Specific fields to retrieve

        Returns:
            List of email dictionaries
        """
        logger.info(f"Fetching up to {max_results} emails from {folder}")

        # Build endpoint
        if folder.lower() == "inbox":
            endpoint = "/me/mailFolders/inbox/messages"
        elif folder.lower() == "sentitems":
            endpoint = "/me/mailFolders/sentitems/messages"
        elif folder.lower() == "drafts":
            endpoint = "/me/mailFolders/drafts/messages"
        else:
            endpoint = f"/me/mailFolders/{folder}/messages"

        # Build query parameters
        params = {
            "$top": min(max_results, 100),  # Graph API max is 100 per request
            "$orderby": "receivedDateTime DESC"
        }

        if filter_query:
            params["$filter"] = filter_query

        if select_fields:
            params["$select"] = ",".join(select_fields)

        try:
            emails = []
            next_link = None

            while len(emails) < max_results:
                if next_link:
                    # Use next link for pagination
                    response = self.session.get(
                        next_link,
                        headers=self._get_headers(),
                        timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                else:
                    # Initial request
                    data = self._make_request("GET", endpoint, params=params)

                if not data or "value" not in data:
                    break

                batch = data["value"]
                emails.extend(batch)

                # Check for more pages
                next_link = data.get("@odata.nextLink")
                if not next_link or len(batch) == 0:
                    break

                # Don't exceed max_results
                if len(emails) >= max_results:
                    emails = emails[:max_results]
                    break

            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails

        except Exception as e:
            logger.error(f"Failed to fetch emails from {folder}: {e}")
            return []

    def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific email by its ID.

        Args:
            email_id: The email message ID

        Returns:
            Email dictionary or None
        """
        logger.info(f"Fetching email {email_id}")
        try:
            return self._make_request("GET", f"/me/messages/{email_id}")
        except Exception as e:
            logger.error(f"Failed to fetch email {email_id}: {e}")
            return None

    def fetch_sent_emails(
        self,
        max_results: int = 200,
        days_back: int = 365
    ) -> List[Dict[str, Any]]:
        """
        Fetch sent emails for style learning.

        Args:
            max_results: Maximum number of sent emails to fetch
            days_back: How many days back to search

        Returns:
            List of sent email dictionaries
        """
        logger.info(f"Fetching up to {max_results} sent emails from last {days_back} days")

        # Calculate date filter
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        filter_query = f"sentDateTime ge {start_date}"

        return self.fetch_emails(
            folder="sentitems",
            max_results=max_results,
            filter_query=filter_query
        )

    def fetch_unread_emails(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Fetch unread emails from inbox."""
        logger.info(f"Fetching up to {max_results} unread emails")
        return self.fetch_emails(
            folder="inbox",
            max_results=max_results,
            filter_query="isRead eq false"
        )

    def fetch_email_thread(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all emails in a conversation thread.

        Args:
            conversation_id: The conversation ID

        Returns:
            List of emails in the thread, ordered by date
        """
        logger.info(f"Fetching thread for conversation {conversation_id}")

        filter_query = f"conversationId eq '{conversation_id}'"

        # Fetch from all folders (inbox, sent, drafts)
        all_emails = []

        for folder in ["inbox", "sentitems"]:
            emails = self.fetch_emails(
                folder=folder,
                max_results=100,
                filter_query=filter_query
            )
            all_emails.extend(emails)

        # Sort by received/sent date
        all_emails.sort(key=lambda x: x.get("receivedDateTime", x.get("sentDateTime", "")))

        logger.info(f"Found {len(all_emails)} emails in thread")
        return all_emails

    def create_draft_reply(
        self,
        email_id: str,
        body_content: str,
        content_type: str = "HTML"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a draft reply to an email.

        Args:
            email_id: The email to reply to
            body_content: The reply content
            content_type: "HTML" or "Text"

        Returns:
            Created draft dictionary or None
        """
        logger.info(f"Creating draft reply for email {email_id}")

        endpoint = f"/me/messages/{email_id}/createReply"

        try:
            # First, create the draft
            draft = self._make_request("POST", endpoint)

            if not draft or "id" not in draft:
                logger.error("Failed to create draft reply")
                return None

            draft_id = draft["id"]

            # Update the draft with our content
            update_endpoint = f"/me/messages/{draft_id}"
            update_data = {
                "body": {
                    "contentType": content_type,
                    "content": body_content
                }
            }

            updated_draft = self._make_request("PATCH", update_endpoint, json_data=update_data)

            logger.info(f"Created draft reply with ID: {draft_id}")
            return updated_draft

        except Exception as e:
            logger.error(f"Failed to create draft reply: {e}")
            return None

    def create_new_draft(
        self,
        to_recipients: List[str],
        subject: str,
        body_content: str,
        cc_recipients: Optional[List[str]] = None,
        content_type: str = "HTML"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new draft email.

        Args:
            to_recipients: List of recipient email addresses
            subject: Email subject
            body_content: Email body
            cc_recipients: Optional CC recipients
            content_type: "HTML" or "Text"

        Returns:
            Created draft dictionary or None
        """
        logger.info(f"Creating new draft to {', '.join(to_recipients)}")

        endpoint = "/me/messages"

        # Build recipient objects
        to_list = [{"emailAddress": {"address": addr}} for addr in to_recipients]
        cc_list = [{"emailAddress": {"address": addr}} for addr in (cc_recipients or [])]

        draft_data = {
            "subject": subject,
            "body": {
                "contentType": content_type,
                "content": body_content
            },
            "toRecipients": to_list
        }

        if cc_list:
            draft_data["ccRecipients"] = cc_list

        try:
            draft = self._make_request("POST", endpoint, json_data=draft_data)
            logger.info(f"Created new draft with ID: {draft.get('id')}")
            return draft
        except Exception as e:
            logger.error(f"Failed to create new draft: {e}")
            return None

    def send_draft(self, draft_id: str) -> bool:
        """
        Send a draft email.

        Args:
            draft_id: The draft message ID

        Returns:
            True if sent successfully, False otherwise
        """
        logger.info(f"Sending draft {draft_id}")

        endpoint = f"/me/messages/{draft_id}/send"

        try:
            self._make_request("POST", endpoint)
            logger.info(f"Successfully sent draft {draft_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send draft {draft_id}: {e}")
            return False

    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read."""
        endpoint = f"/me/messages/{email_id}"
        try:
            self._make_request("PATCH", endpoint, json_data={"isRead": True})
            return True
        except Exception as e:
            logger.error(f"Failed to mark email {email_id} as read: {e}")
            return False

    def search_emails_by_sender(
        self,
        sender_email: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for emails from a specific sender across all folders.

        Args:
            sender_email: Sender's email address
            max_results: Maximum results to return

        Returns:
            List of emails from the sender
        """
        logger.info(f"Searching emails from {sender_email}")

        filter_query = f"from/emailAddress/address eq '{sender_email}'"

        emails = []

        # Search in inbox and sent items
        for folder in ["inbox", "sentitems"]:
            batch = self.fetch_emails(
                folder=folder,
                max_results=max_results,
                filter_query=filter_query
            )
            emails.extend(batch)

            if len(emails) >= max_results:
                break

        logger.info(f"Found {len(emails)} emails from {sender_email}")
        return emails[:max_results]


# Global instance
_graph_service: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    """Get or create the global GraphService instance."""
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
