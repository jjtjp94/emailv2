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


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging()

    try:
        # Check configuration
        if not check_requirements():
            logger.error("Configuration incomplete. Exiting.")
            return 1

        logger.info("All requirements met")

        # TODO: Phase 1 - Initialize services
        # - Microsoft Graph authentication
        # - Database setup
        # - Cache initialization

        # TODO: Phase 2 - Style learning
        # - Fetch sent emails
        # - Analyze writing style
        # - Build sender profiles

        # TODO: Phase 3 - Launch UI
        # - Create main window
        # - Setup system tray
        # - Initialize hotkeys

        logger.info("Application initialized successfully")
        logger.info("Ready to draft emails!")

        # For now, just print success message
        print("\n" + "=" * 80)
        print("Email Drafting Tool - Development Version")
        print("=" * 80)
        print("\nConfiguration loaded successfully!")
        print(f"Database: {settings.DATABASE_PATH}")
        print(f"Cache: {settings.CACHE_DIR}")
        print(f"Logs: {settings.LOG_FILE}")
        print("\nNext steps:")
        print("1. Complete Phase 1: Microsoft Graph authentication")
        print("2. Setup database schema")
        print("3. Implement email fetching")
        print("\nSee PROJECT_PLAN.md for full implementation roadmap.")
        print("=" * 80)

        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
