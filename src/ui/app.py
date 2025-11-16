"""
Desktop application launcher for Email Drafting Tool.
Initializes PyQt6 application and main window.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.config import get_settings
from src.ui.main_window import MainWindow
from src.ui.system_tray import SystemTrayManager
from src.utils.auth import get_auth_manager

logger = logging.getLogger(__name__)


class EmailDraftingApp:
    """Main application controller."""

    def __init__(self):
        self.app: QApplication = None
        self.main_window: MainWindow = None
        self.system_tray: SystemTrayManager = None
        self.settings = get_settings()

    def setup_logging(self):
        """Configure logging for GUI app."""
        log_file = Path(self.settings.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        logger.info("=" * 80)
        logger.info("Email Drafting Tool (GUI) - Starting")
        logger.info("=" * 80)

    def check_authentication(self) -> bool:
        """Check if user is authenticated with Microsoft."""
        auth_manager = get_auth_manager()

        if not auth_manager.is_authenticated():
            # Show authentication dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Microsoft Authentication Required")
            msg.setInformativeText(
                "You need to authenticate with your Microsoft account to use this application.\n\n"
                "Click OK to start the authentication process."
            )
            msg.setWindowTitle("Authentication Required")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

            if msg.exec() == QMessageBox.StandardButton.Ok:
                # Run authentication in background (would need proper implementation)
                # For now, show instructions
                instructions = QMessageBox()
                instructions.setIcon(QMessageBox.Icon.Information)
                instructions.setText("Please authenticate via terminal")
                instructions.setInformativeText(
                    "Please run the following command in a terminal to authenticate:\n\n"
                    "python src/main.py\n\n"
                    "Then restart this application."
                )
                instructions.setWindowTitle("Authentication Instructions")
                instructions.exec()
                return False
            else:
                return False

        return True

    def run(self):
        """Run the application."""
        try:
            # Setup logging
            self.setup_logging()

            # Create Qt Application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Email Drafting Tool")
            self.app.setOrganizationName("EmailDrafter")

            # Set application-wide style
            self.app.setStyle("Fusion")

            # Check authentication
            if not self.check_authentication():
                logger.warning("Authentication check failed")
                return 1

            # Create main window
            logger.info("Creating main window")
            self.main_window = MainWindow()

            # Create system tray
            logger.info("Creating system tray")
            self.system_tray = SystemTrayManager(self.app)

            # Connect system tray signals
            self.system_tray.show_window_requested.connect(self.show_window)
            self.system_tray.hide_window_requested.connect(self.hide_window)
            self.system_tray.refresh_requested.connect(self.main_window.refresh_emails)
            self.system_tray.quit_requested.connect(self.quit_application)

            # Update tray tooltip
            self.system_tray.update_tooltip("Email Drafting Tool")

            # Show main window
            self.main_window.show()

            logger.info("Application started successfully")

            # Run event loop
            return self.app.exec()

        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            return 0
        except Exception as e:
            logger.exception(f"Fatal error: {e}")
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application error:\n{e}\n\nCheck logs for details."
            )
            return 1

    def show_window(self):
        """Show main window."""
        if self.main_window:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()

    def hide_window(self):
        """Hide main window."""
        if self.main_window:
            self.main_window.hide()

    def quit_application(self):
        """Quit the application."""
        if self.app:
            self.app.quit()


def main():
    """Entry point for GUI application."""
    app = EmailDraftingApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
