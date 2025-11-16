"""
Main entry point for the Email Drafting & Refinement Tool.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.utils.auth import get_auth_manager
from src.services.graph_service import get_graph_service
from src.services.db_service import get_db_service
from src.services.cache_service import get_cache_service
from src.models.email import Email


def setup_logging():
    """Configure application logging."""
    settings = get_settings()

    # Create logs directory if it doesn't exist
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Email Drafting Tool - Starting")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")
    logger.info("=" * 80)

    return logger


def check_requirements():
    """Check that all required settings are configured."""
    settings = get_settings()
    logger = logging.getLogger(__name__)

    missing = []

    # Check Azure credentials
    if not settings.AZURE_CLIENT_ID or settings.AZURE_CLIENT_ID == "your_client_id_here":
        missing.append("AZURE_CLIENT_ID")

    # Check AI credentials
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY.startswith("your_"):
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        logger.error("Missing required configuration:")
        for item in missing:
            logger.error(f"  - {item}")
        logger.error("\nPlease update your .env file with the required credentials.")
        logger.error("See SETUP_GUIDE.md for instructions.")
        return False

    logger.info("Configuration check passed")
    return True


def initialize_services(logger):
    """Initialize all core services."""
    settings = get_settings()

    print("\n" + "=" * 80)
    print("Email Drafting Tool - Phase 1 Implementation")
    print("=" * 80)

    # Initialize database
    print("\n[1/4] Initializing database...")
    logger.info("Initializing database service")
    db_service = get_db_service()
    stats = db_service.get_email_stats()
    print(f"  ✓ Database initialized")
    print(f"    - Total emails in DB: {stats['total_emails']}")
    print(f"    - Inbox: {stats['total_inbox']}, Sent: {stats['total_sent']}")

    # Initialize cache
    print("\n[2/4] Initializing cache...")
    logger.info("Initializing cache service")
    cache_service = get_cache_service()
    cache_stats = cache_service.get_stats()
    print(f"  ✓ Cache initialized")
    print(f"    - Cached entries: {cache_stats.get('total_entries', 0)}")

    # Authenticate with Microsoft
    print("\n[3/4] Authenticating with Microsoft Graph API...")
    logger.info("Starting Microsoft authentication")
    auth_manager = get_auth_manager()

    if auth_manager.is_authenticated():
        print("  ✓ Already authenticated")
    else:
        print("  ! Authentication required")
        token = auth_manager.get_token()
        if not token:
            print("  ✗ Authentication failed!")
            return False

    # Get user info
    graph_service = get_graph_service()
    user_info = graph_service.get_user_info()

    if user_info:
        print(f"  ✓ Authenticated as: {user_info.get('displayName')} ({user_info.get('mail')})")
        logger.info(f"Authenticated as {user_info.get('mail')}")
    else:
        print("  ✗ Failed to get user info")
        return False

    return True


def fetch_and_store_emails(logger):
    """Fetch emails from Microsoft Graph and store in database."""
    settings = get_settings()
    graph_service = get_graph_service()
    db_service = get_db_service()

    print("\n[4/4] Fetching emails from Microsoft Outlook...")

    # Fetch inbox emails
    print("  - Fetching inbox emails...")
    inbox_emails = graph_service.fetch_emails(
        folder="inbox",
        max_results=settings.MAX_EMAILS_PER_FETCH
    )

    if inbox_emails:
        # Convert and store
        email_objects = [Email.from_graph_api(e, email_type="inbox") for e in inbox_emails]
        saved_count = db_service.save_emails_batch(email_objects)
        print(f"    ✓ Fetched {len(inbox_emails)} inbox emails ({saved_count} new)")
    else:
        print("    ! No inbox emails found")

    # Fetch sent emails (for style learning)
    print("  - Fetching sent emails for style learning...")
    sent_emails = graph_service.fetch_sent_emails(
        max_results=min(50, settings.INITIAL_STYLE_LEARNING_EMAILS)
    )

    if sent_emails:
        email_objects = [Email.from_graph_api(e, email_type="sent") for e in sent_emails]
        saved_count = db_service.save_emails_batch(email_objects)
        print(f"    ✓ Fetched {len(sent_emails)} sent emails ({saved_count} new)")
    else:
        print("    ! No sent emails found")

    return True


def display_summary(logger):
    """Display application status summary."""
    settings = get_settings()
    db_service = get_db_service()

    stats = db_service.get_email_stats()
    sender_stats = db_service.get_sender_stats()

    print("\n" + "=" * 80)
    print("INITIALIZATION COMPLETE")
    print("=" * 80)

    print("\n📊 Current Status:")
    print(f"  - Total emails in database: {stats['total_emails']}")
    print(f"  - Inbox emails: {stats['total_inbox']}")
    print(f"  - Sent emails: {stats['total_sent']}")
    print(f"  - Unread emails: {stats['total_unread']}")
    print(f"  - Sender profiles: {sender_stats['total_senders']}")

    print("\n⚙️  Configuration:")
    print(f"  - Database: {settings.DATABASE_PATH}")
    print(f"  - Cache: {settings.CACHE_DIR}")
    print(f"  - Logs: {settings.LOG_FILE}")

    print("\n✅ Phase 1 Complete:")
    print("  [✓] Microsoft Graph authentication")
    print("  [✓] Database setup and initialization")
    print("  [✓] Email fetching and storage")
    print("  [✓] Cache service")

    print("\n🔜 Next Steps:")
    print("  • Phase 2: AI Integration & Style Learning")
    print("    - Implement Claude API service")
    print("    - Analyze sent emails to learn your writing style")
    print("    - Build sender-specific profiles")
    print("    - Generate first draft response")
    print("\n  • Phase 3: Desktop UI Development")
    print("    - Build PyQt6 main window")
    print("    - Add system tray integration")
    print("    - Implement global hotkeys")

    print("\n💡 Try running the app again to fetch more emails!")
    print("   Or continue to Phase 2 implementation.")
    print("=" * 80 + "\n")


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging()
    settings = get_settings()

    try:
        # Check configuration
        if not check_requirements():
            logger.error("Configuration incomplete. Exiting.")
            print("\n❌ Configuration Error:")
            print("   Please set up your .env file with required credentials.")
            print("   See SETUP_GUIDE.md for detailed instructions.\n")
            return 1

        logger.info("All requirements met")

        # Phase 1: Initialize services
        if not initialize_services(logger):
            logger.error("Service initialization failed")
            return 1

        # Fetch and store emails
        if not fetch_and_store_emails(logger):
            logger.error("Email fetching failed")
            return 1

        # Display summary
        display_summary(logger)

        logger.info("Application completed successfully")
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        print(f"\n\n❌ Fatal Error: {e}")
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
