"""
Main window UI for Email Drafting Tool.
PyQt6-based desktop interface with email list, preview, and draft editor.
"""

import logging
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QTextEdit, QPushButton, QLabel,
    QComboBox, QLineEdit, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon

from src.services.db_service import get_db_service
from src.services.draft_generator import get_draft_generator, REFINEMENT_PRESETS
from src.services.graph_service import get_graph_service
from src.models.email import Email
from src.models.draft import Draft

logger = logging.getLogger(__name__)


class DraftGenerationWorker(QThread):
    """Background worker for generating drafts."""

    finished = pyqtSignal(object)  # Draft object or None
    error = pyqtSignal(str)  # Error message

    def __init__(self, email: Email, target_length: str = "medium",
                 target_formality: Optional[str] = None,
                 additional_instructions: str = ""):
        super().__init__()
        self.email = email
        self.target_length = target_length
        self.target_formality = target_formality
        self.additional_instructions = additional_instructions

    def run(self):
        """Generate draft in background thread."""
        try:
            draft_generator = get_draft_generator()
            draft = draft_generator.generate_draft_for_email(
                email=self.email,
                target_length=self.target_length,
                target_formality=self.target_formality,
                additional_instructions=self.additional_instructions
            )
            self.finished.emit(draft)
        except Exception as e:
            logger.exception(f"Draft generation error: {e}")
            self.error.emit(str(e))


class RefinementWorker(QThread):
    """Background worker for refining drafts."""

    finished = pyqtSignal(object)  # Refined Draft object or None
    error = pyqtSignal(str)  # Error message

    def __init__(self, draft: Draft, refinement_type: str, custom_instruction: str = ""):
        super().__init__()
        self.draft = draft
        self.refinement_type = refinement_type
        self.custom_instruction = custom_instruction

    def run(self):
        """Refine draft in background thread."""
        try:
            draft_generator = get_draft_generator()
            refined_draft = draft_generator.refine_draft(
                draft=self.draft,
                refinement_type=self.refinement_type,
                custom_instruction=self.custom_instruction
            )
            self.finished.emit(refined_draft)
        except Exception as e:
            logger.exception(f"Draft refinement error: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.db_service = get_db_service()
        self.current_email: Optional[Email] = None
        self.current_draft: Optional[Draft] = None
        self.draft_worker: Optional[DraftGenerationWorker] = None
        self.refinement_worker: Optional[RefinementWorker] = None

        self.init_ui()
        self.load_emails()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_emails)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes

        logger.info("Main window initialized")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Email Drafting Tool")
        self.setGeometry(100, 100, 1400, 900)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left pane: Email list
        left_pane = self.create_email_list_pane()
        splitter.addWidget(left_pane)

        # Middle pane: Email detail
        middle_pane = self.create_email_detail_pane()
        splitter.addWidget(middle_pane)

        # Right pane: Draft editor
        right_pane = self.create_draft_editor_pane()
        splitter.addWidget(right_pane)

        # Set initial sizes (30%, 30%, 40%)
        splitter.setSizes([400, 400, 600])

        main_layout.addWidget(splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar("Ready")

    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        refresh_action = QAction("&Refresh Emails", self)
        refresh_action.setShortcut("Ctrl+R")
        refresh_action.triggered.connect(self.refresh_emails)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Draft menu
        draft_menu = menubar.addMenu("&Draft")

        generate_action = QAction("&Generate Draft", self)
        generate_action.setShortcut("Ctrl+D")
        generate_action.triggered.connect(self.generate_draft)
        draft_menu.addAction(generate_action)

        copy_action = QAction("&Copy to Clipboard", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_draft_to_clipboard)
        draft_menu.addAction(copy_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_email_list_pane(self) -> QWidget:
        """Create the email list pane."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        # Header
        header = QLabel("📧 Inbox")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Filter dropdown
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Show:")
        self.email_filter = QComboBox()
        self.email_filter.addItems(["Unread", "All Inbox", "Sent"])
        self.email_filter.currentTextChanged.connect(self.filter_emails)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.email_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Email list
        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.on_email_selected)
        layout.addWidget(self.email_list)

        # Email count label
        self.email_count_label = QLabel("0 emails")
        self.email_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.email_count_label)

        return pane

    def create_email_detail_pane(self) -> QWidget:
        """Create the email detail pane."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        # Header
        header = QLabel("📨 Email Details")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Email metadata
        self.email_subject_label = QLabel("Subject: ")
        self.email_subject_label.setWordWrap(True)
        self.email_subject_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.email_subject_label)

        self.email_from_label = QLabel("From: ")
        layout.addWidget(self.email_from_label)

        self.email_date_label = QLabel("Date: ")
        layout.addWidget(self.email_date_label)

        # Separator
        layout.addWidget(QLabel("─" * 50))

        # Email content
        self.email_content = QTextEdit()
        self.email_content.setReadOnly(True)
        layout.addWidget(self.email_content)

        return pane

    def create_draft_editor_pane(self) -> QWidget:
        """Create the draft editor pane."""
        pane = QWidget()
        layout = QVBoxLayout(pane)

        # Header
        header = QLabel("✍️ Draft Response")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Draft controls
        controls_group = QGroupBox("Draft Controls")
        controls_layout = QVBoxLayout()

        # Generation options
        gen_layout = QHBoxLayout()

        gen_layout.addWidget(QLabel("Length:"))
        self.length_combo = QComboBox()
        self.length_combo.addItems(["Short", "Medium", "Long"])
        self.length_combo.setCurrentText("Medium")
        gen_layout.addWidget(self.length_combo)

        gen_layout.addWidget(QLabel("Tone:"))
        self.formality_combo = QComboBox()
        self.formality_combo.addItems(["Auto", "Casual", "Professional", "Formal"])
        gen_layout.addWidget(self.formality_combo)

        gen_layout.addStretch()
        controls_layout.addLayout(gen_layout)

        # Generate button
        self.generate_btn = QPushButton("🤖 Generate Draft")
        self.generate_btn.clicked.connect(self.generate_draft)
        self.generate_btn.setMinimumHeight(40)
        controls_layout.addWidget(self.generate_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        controls_layout.addWidget(self.progress_bar)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Refinement controls
        refine_group = QGroupBox("Refinement Options")
        refine_layout = QVBoxLayout()

        # Quick refinement buttons (2 rows)
        refine_row1 = QHBoxLayout()
        self.concise_btn = QPushButton("✂️ Make Concise")
        self.concise_btn.clicked.connect(lambda: self.refine_draft("concise"))
        refine_row1.addWidget(self.concise_btn)

        self.detailed_btn = QPushButton("📝 Add Details")
        self.detailed_btn.clicked.connect(lambda: self.refine_draft("detailed"))
        refine_row1.addWidget(self.detailed_btn)

        self.formal_btn = QPushButton("👔 More Formal")
        self.formal_btn.clicked.connect(lambda: self.refine_draft("formal"))
        refine_row1.addWidget(self.formal_btn)

        refine_layout.addLayout(refine_row1)

        refine_row2 = QHBoxLayout()
        self.casual_btn = QPushButton("😊 More Casual")
        self.casual_btn.clicked.connect(lambda: self.refine_draft("casual"))
        refine_row2.addWidget(self.casual_btn)

        self.grammar_btn = QPushButton("✓ Fix Grammar")
        self.grammar_btn.clicked.connect(lambda: self.refine_draft("grammar"))
        refine_row2.addWidget(self.grammar_btn)

        self.bullets_btn = QPushButton("• Add Bullets")
        self.bullets_btn.clicked.connect(lambda: self.refine_draft("bullets"))
        refine_row2.addWidget(self.bullets_btn)

        refine_layout.addLayout(refine_row2)

        # Custom instruction
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom:"))
        self.custom_instruction = QLineEdit()
        self.custom_instruction.setPlaceholderText("Enter custom refinement instruction...")
        custom_layout.addWidget(self.custom_instruction)

        self.custom_refine_btn = QPushButton("Apply")
        self.custom_refine_btn.clicked.connect(lambda: self.refine_draft("custom"))
        custom_layout.addWidget(self.custom_refine_btn)

        refine_layout.addLayout(custom_layout)

        refine_group.setLayout(refine_layout)
        layout.addWidget(refine_group)

        # Draft editor
        self.draft_editor = QTextEdit()
        self.draft_editor.setPlaceholderText("Draft will appear here...\n\nSelect an email and click 'Generate Draft' to begin.")
        layout.addWidget(self.draft_editor)

        # Draft info
        self.draft_info_label = QLabel("")
        self.draft_info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.draft_info_label)

        # Action buttons
        action_layout = QHBoxLayout()

        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_draft_to_clipboard)
        action_layout.addWidget(self.copy_btn)

        self.create_in_outlook_btn = QPushButton("📧 Create Draft in Outlook")
        self.create_in_outlook_btn.clicked.connect(self.create_draft_in_outlook)
        action_layout.addWidget(self.create_in_outlook_btn)

        layout.addLayout(action_layout)

        # Initially disable refinement buttons
        self.set_refinement_buttons_enabled(False)

        return pane

    def load_emails(self, filter_type: str = "Unread"):
        """Load emails into the list."""
        self.email_list.clear()

        try:
            if filter_type == "Unread":
                emails = self.db_service.get_emails_by_type("inbox", limit=100, unread_only=True)
            elif filter_type == "All Inbox":
                emails = self.db_service.get_emails_by_type("inbox", limit=100)
            elif filter_type == "Sent":
                emails = self.db_service.get_emails_by_type("sent", limit=100)
            else:
                emails = []

            for email in emails:
                item = QListWidgetItem()

                # Format display text
                sender = email.sender_name or email.sender_email
                subject = email.subject or "(No Subject)"
                date_str = ""

                if email.received_datetime:
                    date = email.received_datetime
                    if date.date() == datetime.now().date():
                        date_str = date.strftime("%H:%M")
                    else:
                        date_str = date.strftime("%b %d")

                # Bold unread emails
                if not email.is_read and filter_type != "Sent":
                    text = f"● {sender}\n  {subject}\n  {date_str}"
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                else:
                    text = f"  {sender}\n  {subject}\n  {date_str}"

                item.setText(text)
                item.setData(Qt.ItemDataRole.UserRole, email.id)  # Store email ID

                self.email_list.addItem(item)

            # Update count
            self.email_count_label.setText(f"{len(emails)} email(s)")
            self.update_status_bar(f"Loaded {len(emails)} emails")

        except Exception as e:
            logger.error(f"Failed to load emails: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load emails: {e}")

    def filter_emails(self, filter_type: str):
        """Filter emails based on selection."""
        self.load_emails(filter_type)

    def on_email_selected(self, item: QListWidgetItem):
        """Handle email selection."""
        email_id = item.data(Qt.ItemDataRole.UserRole)

        # Load email from database
        with self.db_service.get_session() as session:
            email = session.query(Email).filter_by(id=email_id).first()

            if email:
                self.current_email = email
                self.display_email(email)

                # Check if draft exists
                existing_draft = self.db_service.get_latest_draft_for_email(email.message_id)
                if existing_draft:
                    self.display_draft(existing_draft)

    def display_email(self, email: Email):
        """Display email details."""
        subject = email.subject or "(No Subject)"
        sender = f"{email.sender_name} <{email.sender_email}>" if email.sender_name else email.sender_email

        date_str = ""
        if email.received_datetime:
            date_str = email.received_datetime.strftime("%Y-%m-%d %H:%M")
        elif email.sent_datetime:
            date_str = email.sent_datetime.strftime("%Y-%m-%d %H:%M")

        self.email_subject_label.setText(f"Subject: {subject}")
        self.email_from_label.setText(f"From: {sender}")
        self.email_date_label.setText(f"Date: {date_str}")

        # Display body (prefer plain text)
        from src.utils.text_processing import clean_email_text
        content = clean_email_text(email.body_html, email.body_text)
        self.email_content.setPlainText(content)

    def display_draft(self, draft: Draft):
        """Display draft in editor."""
        self.current_draft = draft
        self.draft_editor.setPlainText(draft.body_content)

        info = f"Version {draft.draft_version} | {draft.tokens_used} tokens"
        if draft.target_length:
            info += f" | {draft.target_length.capitalize()} length"
        if draft.target_formality:
            info += f" | {draft.target_formality.capitalize()} tone"

        self.draft_info_label.setText(info)
        self.set_refinement_buttons_enabled(True)

    def generate_draft(self):
        """Generate draft for current email."""
        if not self.current_email:
            QMessageBox.warning(self, "No Email Selected", "Please select an email first.")
            return

        # Get parameters
        length = self.length_combo.currentText().lower()
        formality_text = self.formality_combo.currentText().lower()
        formality = None if formality_text == "auto" else formality_text

        # Disable button and show progress
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.update_status_bar("Generating draft...")

        # Start worker thread
        self.draft_worker = DraftGenerationWorker(
            email=self.current_email,
            target_length=length,
            target_formality=formality
        )
        self.draft_worker.finished.connect(self.on_draft_generated)
        self.draft_worker.error.connect(self.on_draft_error)
        self.draft_worker.start()

    def on_draft_generated(self, draft: Optional[Draft]):
        """Handle draft generation completion."""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if draft:
            self.display_draft(draft)
            self.update_status_bar(f"Draft generated ({draft.tokens_used} tokens used)")
        else:
            QMessageBox.warning(self, "Generation Failed", "Failed to generate draft.")
            self.update_status_bar("Draft generation failed")

    def on_draft_error(self, error_msg: str):
        """Handle draft generation error."""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Draft generation error:\n{error_msg}")
        self.update_status_bar("Draft generation error")

    def refine_draft(self, refinement_type: str):
        """Refine current draft."""
        if not self.current_draft:
            QMessageBox.warning(self, "No Draft", "Generate a draft first.")
            return

        custom_instruction = ""
        if refinement_type == "custom":
            custom_instruction = self.custom_instruction.text()
            if not custom_instruction:
                QMessageBox.warning(self, "No Instruction", "Enter a custom instruction.")
                return

        # Disable buttons and show progress
        self.set_refinement_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.update_status_bar("Refining draft...")

        # Start worker thread
        self.refinement_worker = RefinementWorker(
            draft=self.current_draft,
            refinement_type=refinement_type,
            custom_instruction=custom_instruction
        )
        self.refinement_worker.finished.connect(self.on_draft_refined)
        self.refinement_worker.error.connect(self.on_refinement_error)
        self.refinement_worker.start()

    def on_draft_refined(self, refined_draft: Optional[Draft]):
        """Handle draft refinement completion."""
        self.set_refinement_buttons_enabled(True)
        self.progress_bar.setVisible(False)

        if refined_draft:
            self.display_draft(refined_draft)
            self.update_status_bar(f"Draft refined (version {refined_draft.draft_version})")
            self.custom_instruction.clear()
        else:
            QMessageBox.warning(self, "Refinement Failed", "Failed to refine draft.")
            self.update_status_bar("Draft refinement failed")

    def on_refinement_error(self, error_msg: str):
        """Handle draft refinement error."""
        self.set_refinement_buttons_enabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Draft refinement error:\n{error_msg}")
        self.update_status_bar("Draft refinement error")

    def set_refinement_buttons_enabled(self, enabled: bool):
        """Enable/disable refinement buttons."""
        self.concise_btn.setEnabled(enabled)
        self.detailed_btn.setEnabled(enabled)
        self.formal_btn.setEnabled(enabled)
        self.casual_btn.setEnabled(enabled)
        self.grammar_btn.setEnabled(enabled)
        self.bullets_btn.setEnabled(enabled)
        self.custom_refine_btn.setEnabled(enabled)
        self.copy_btn.setEnabled(enabled)
        self.create_in_outlook_btn.setEnabled(enabled)

    def copy_draft_to_clipboard(self):
        """Copy draft to clipboard."""
        if not self.current_draft:
            QMessageBox.warning(self, "No Draft", "Generate a draft first.")
            return

        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.draft_editor.toPlainText())

        self.update_status_bar("Draft copied to clipboard")
        QMessageBox.information(self, "Copied", "Draft copied to clipboard!")

    def create_draft_in_outlook(self):
        """Create draft in Outlook via Graph API."""
        if not self.current_draft or not self.current_email:
            QMessageBox.warning(self, "No Draft", "Generate a draft first.")
            return

        try:
            graph_service = get_graph_service()
            draft_content = self.draft_editor.toPlainText()

            # Create draft reply in Outlook
            outlook_draft = graph_service.create_draft_reply(
                email_id=self.current_email.message_id,
                body_content=draft_content,
                content_type="Text"
            )

            if outlook_draft:
                QMessageBox.information(
                    self,
                    "Success",
                    "Draft created in Outlook!\n\nOpen Outlook to view and send."
                )
                self.update_status_bar("Draft created in Outlook")

                # Mark draft as used
                draft_generator = get_draft_generator()
                draft_generator.mark_draft_used(self.current_draft.id, was_edited=False)
            else:
                QMessageBox.warning(self, "Failed", "Failed to create draft in Outlook.")

        except Exception as e:
            logger.exception(f"Failed to create draft in Outlook: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create draft:\n{e}")

    def refresh_emails(self):
        """Refresh emails from Microsoft Graph."""
        self.update_status_bar("Refreshing emails...")

        try:
            graph_service = get_graph_service()

            # Fetch new emails
            inbox_emails = graph_service.fetch_emails(folder="inbox", max_results=20)

            if inbox_emails:
                email_objects = [Email.from_graph_api(e, email_type="inbox") for e in inbox_emails]
                saved_count = self.db_service.save_emails_batch(email_objects)

                # Reload list
                current_filter = self.email_filter.currentText()
                self.load_emails(current_filter)

                self.update_status_bar(f"Refreshed: {saved_count} new email(s)")
            else:
                self.update_status_bar("No new emails")

        except Exception as e:
            logger.exception(f"Failed to refresh emails: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh emails:\n{e}")
            self.update_status_bar("Refresh failed")

    def update_status_bar(self, message: str):
        """Update status bar message."""
        self.status_bar.showMessage(message)

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Email Drafting Tool",
            "Email Drafting & Refinement Tool\n\n"
            "Version 0.1.0\n\n"
            "AI-powered email drafting with style learning and sender adaptation.\n\n"
            "Features:\n"
            "• Learns your writing style from sent emails\n"
            "• Adapts tone per sender automatically\n"
            "• One-click draft refinements\n"
            "• Direct Outlook integration\n\n"
            "Built with Python, PyQt6, and Claude AI"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up workers
        if self.draft_worker and self.draft_worker.isRunning():
            self.draft_worker.terminate()
            self.draft_worker.wait()

        if self.refinement_worker and self.refinement_worker.isRunning():
            self.refinement_worker.terminate()
            self.refinement_worker.wait()

        event.accept()
