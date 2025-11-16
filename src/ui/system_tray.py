"""
System tray integration for Email Drafting Tool.
Provides quick access and background operation.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


class SystemTrayManager(QObject):
    """Manages system tray icon and interactions."""

    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.init_tray()

    def init_tray(self):
        """Initialize system tray icon."""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)

        # Try to set icon (fallback to default if not found)
        try:
            # You can replace this with a custom icon file
            self.tray_icon.setIcon(QIcon.fromTheme("mail-unread"))
        except:
            logger.warning("Could not load tray icon")

        # Create context menu
        menu = QMenu()

        # Show/Hide window action
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_window_requested.emit)
        menu.addAction(show_action)

        hide_action = QAction("Hide Window", self)
        hide_action.triggered.connect(self.hide_window_requested.emit)
        menu.addAction(hide_action)

        menu.addSeparator()

        # Refresh emails action
        refresh_action = QAction("Refresh Emails", self)
        refresh_action.triggered.connect(self.refresh_requested.emit)
        menu.addAction(refresh_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        # Set menu
        self.tray_icon.setContextMenu(menu)

        # Handle tray icon activation (click)
        self.tray_icon.activated.connect(self.on_tray_activated)

        # Show tray icon
        self.tray_icon.show()

        logger.info("System tray initialized")

    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        from PyQt6.QtWidgets import QSystemTrayIcon

        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - toggle window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.show_window_requested.emit()

    def show_message(self, title: str, message: str, duration: int = 3000):
        """Show notification message."""
        if self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                duration
            )

    def update_tooltip(self, tooltip: str):
        """Update tray icon tooltip."""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
