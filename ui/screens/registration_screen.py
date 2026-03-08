"""
Registration Screen for Music Player Application.
Provides user registration interface for Artists and Listeners.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy,
    QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class RegistrationScreen(QWidget):
    """Registration screen widget for new user signup."""
    
    # Signals
    registration_successful = pyqtSignal(dict)  # Emits user info on successful registration
    switch_to_login = pyqtSignal()  # Signal to switch back to login screen
    
    # Available music genres
    GENRES = [
        "Pop", "Rock", "Hip Hop", "R&B", "Jazz", 
        "Classical", "Electronic", "Country", "Latin",
        "Indie", "Metal", "Blues", "Folk", "Other"
    ]
    
    def __init__(self, db_manager, parent=None):
        """Initialize the registration screen.
        
        Args:
            db_manager: DatabaseManager instance for registration.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Set up the user interface with expanded, readable form fields."""
        # Main layout with generous margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for smaller screens (or just to handle overflow)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("registerScroll")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # The content widget inside the scroll area
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        
        # Use a layout that fills the space but keeps things readable
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        # Large margins to give that "distributed widely" feel
        content_layout.setContentsMargins(100, 60, 100, 60)
        
        # --- Header Section ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        title_icon = QLabel("🎵")
        title_icon.setObjectName("titleIcon")
        title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_icon)
        
        title_label = QLabel("Create Account")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Join our music community!")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(40)
        
        # --- Form Section ---
        # We will use a grid layout for some fields to spread them out
        # or just a wide vertical layout. Let's use a wide vertical layout
        # but limit width slightly so it's not absurdly wide on 4k screens,
        # but much wider than a "box".
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(30)
        
        # Account Type
        type_label = QLabel("I am a:")
        type_label.setObjectName("sectionHeader")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(type_label)
        
        type_layout = QHBoxLayout()
        type_layout.setSpacing(50)
        type_layout.addStretch()
        
        self.artist_radio = QRadioButton("Artist")
        self.artist_radio.setObjectName("artistRadio")
        self.artist_radio.setChecked(True)
        self.artist_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.artist_radio.toggled.connect(self._on_account_type_changed)
        
        self.listener_radio = QRadioButton("Listener")
        self.listener_radio.setObjectName("listenerRadio")
        self.listener_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.account_type_group = QButtonGroup(self)
        self.account_type_group.addButton(self.artist_radio, 0)
        self.account_type_group.addButton(self.listener_radio, 1)
        
        type_layout.addWidget(self.artist_radio)
        type_layout.addWidget(self.listener_radio)
        type_layout.addStretch()
        form_layout.addLayout(type_layout)
        
        form_layout.addSpacing(20)
        
        # Credentials
        creds_label = QLabel("Login Details")
        creds_label.setObjectName("sectionHeader")
        form_layout.addWidget(creds_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(60)
        self.username_input.returnPressed.connect(self._attempt_registration)
        form_layout.addWidget(self.username_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setMinimumHeight(60)
        self.email_input.returnPressed.connect(self._attempt_registration)
        form_layout.addWidget(self.email_input)
        
        # Passwords side by side
        pass_layout = QHBoxLayout()
        pass_layout.setSpacing(20)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(60)
        self.password_input.returnPressed.connect(self._attempt_registration)
        pass_layout.addWidget(self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(60)
        self.confirm_password_input.returnPressed.connect(self._attempt_registration)
        pass_layout.addWidget(self.confirm_password_input)
        
        form_layout.addLayout(pass_layout)
        
        form_layout.addSpacing(20)
        
        # Profile Details
        profile_label = QLabel("Profile Details")
        profile_label.setObjectName("sectionHeader")
        form_layout.addWidget(profile_label)
        
        # Artist Fields
        self.artist_fields = QWidget()
        artist_layout = QVBoxLayout(self.artist_fields)
        artist_layout.setContentsMargins(0, 0, 0, 0)
        artist_layout.setSpacing(25)
        
        self.stage_name_input = QLineEdit()
        self.stage_name_input.setPlaceholderText("Stage Name (Optional)")
        self.stage_name_input.setMinimumHeight(60)
        artist_layout.addWidget(self.stage_name_input)
        
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(self.GENRES)
        self.genre_combo.setMinimumHeight(60)
        artist_layout.addWidget(self.genre_combo)
        
        form_layout.addWidget(self.artist_fields)
        
        # Listener Fields
        self.listener_fields = QWidget()
        listener_layout = QVBoxLayout(self.listener_fields)
        listener_layout.setContentsMargins(0, 0, 0, 0)
        listener_layout.setSpacing(25)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Display Name (Optional)")
        self.display_name_input.setMinimumHeight(60)
        listener_layout.addWidget(self.display_name_input)
        
        self.pref_genre_combo = QComboBox()
        self.pref_genre_combo.addItems(self.GENRES)
        self.pref_genre_combo.setMinimumHeight(60)
        listener_layout.addWidget(self.pref_genre_combo)
        
        self.listener_fields.hide()
        form_layout.addWidget(self.listener_fields)
        
        # Add form layout to content
        # Constrain width slightly but keep it wide (e.g. 800px or 1000px max)
        center_form_layout = QHBoxLayout()
        center_form_layout.addStretch()
        
        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setMaximumWidth(900)  # Wide but not infinite
        center_form_layout.addWidget(form_container, stretch=2)
        
        center_form_layout.addStretch()
        content_layout.addLayout(center_form_layout)
        
        content_layout.addSpacing(50)
        
        # --- Footer ---
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(30)
        
        self.register_button = QPushButton("Create Account")
        self.register_button.setObjectName("registerButton")
        self.register_button.setMinimumHeight(70)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self._attempt_registration)
        self.register_button.setMaximumWidth(400)
        
        btn_center = QHBoxLayout()
        btn_center.addStretch()
        btn_center.addWidget(self.register_button)
        btn_center.addStretch()
        footer_layout.addLayout(btn_center)
        
        login_layout = QHBoxLayout()
        login_layout.setSpacing(10)
        login_layout.addStretch()
        
        login_text = QLabel("Already have an account?")
        login_text.setObjectName("loginText")
        login_layout.addWidget(login_text)
        
        self.login_link = QPushButton("Sign In")
        self.login_link.setObjectName("loginLink")
        self.login_link.setFlat(True)
        self.login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_link.clicked.connect(self.switch_to_login.emit)
        login_layout.addWidget(self.login_link)
        
        login_layout.addStretch()
        footer_layout.addLayout(login_layout)
        
        content_layout.addLayout(footer_layout)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Set focus
        self.username_input.setFocus()
    
    def _apply_styles(self):
        """Apply stylesheet to the widget with expanded, open styling."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
            
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QWidget#contentWidget {
                background-color: #1a1a2e;
            }
            
            QLabel#titleIcon {
                font-size: 64px;
            }
            
            QLabel#titleLabel {
                font-size: 42px;
                font-weight: bold;
                color: #e94560;
                letter-spacing: 2px;
            }
            
            QLabel#subtitleLabel {
                font-size: 20px;
                color: #8a8a8a;
                font-weight: 300;
            }
            
            QLabel#sectionHeader {
                font-size: 18px;
                color: #4ecdc4;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 10px;
                margin-top: 10px;
            }
            
            QLineEdit {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 15px;
                padding: 15px 25px;
                font-size: 18px;
                color: #ffffff;
                selection-background-color: #e94560;
            }
            
            QLineEdit:focus {
                border: 2px solid #e94560;
                background-color: #1a2642;
            }
            
            QLineEdit::placeholder {
                color: #606070;
                font-size: 18px;
            }
            
            QRadioButton {
                color: #e0e0e0;
                font-size: 20px;
                spacing: 15px;
                padding: 10px;
                font-weight: 500;
            }
            
            QRadioButton::indicator {
                width: 28px;
                height: 28px;
                border-radius: 14px;
                border: 3px solid #0f3460;
                background-color: #16213e;
            }
            
            QRadioButton::indicator:checked {
                background-color: #e94560;
                border: 3px solid #e94560;
            }
            
            QRadioButton::indicator:hover {
                border: 3px solid #4ecdc4;
            }
            
            QComboBox {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 15px;
                padding: 15px 25px;
                font-size: 18px;
                color: #ffffff;
            }
            
            QComboBox:focus {
                border: 2px solid #e94560;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 50px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 10px solid #4ecdc4;
                margin-right: 20px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 10px;
                selection-background-color: #e94560;
                color: #ffffff;
                padding: 10px;
                font-size: 16px;
            }
            
            QPushButton#registerButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 35px;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
            }
            
            QPushButton#registerButton:hover {
                background-color: #ff6b6b;
                margin-top: -2px;
            }
            
            QPushButton#registerButton:pressed {
                background-color: #c73e54;
                margin-top: 2px;
            }
            
            QLabel#loginText {
                color: #8a8a8a;
                font-size: 16px;
            }
            
            QPushButton#loginLink {
                color: #4ecdc4;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 5px;
            }
            
            QPushButton#loginLink:hover {
                color: #7edcd6;
                text-decoration: underline;
            }
        """)
    
    def _on_account_type_changed(self):
        """Handle account type radio button change."""
        if self.artist_radio.isChecked():
            self.artist_fields.show()
            self.listener_fields.hide()
        else:
            self.artist_fields.hide()
            self.listener_fields.show()
    
    def _attempt_registration(self):
        """Attempt to register a new user."""
        # Get values
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Determine account type
        is_artist = self.artist_radio.isChecked()
        role = 'artist' if is_artist else 'listener'
        
        # Validate inputs
        if not username:
            self._show_error("Please enter a username.")
            self.username_input.setFocus()
            return
        
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters.")
            self.username_input.setFocus()
            return
        
        if not email:
            self._show_error("Please enter your email.")
            self.email_input.setFocus()
            return
        
        if not self._is_valid_email(email):
            self._show_error("Please enter a valid email address.")
            self.email_input.setFocus()
            return
        
        if not password:
            self._show_error("Please enter a password.")
            self.password_input.setFocus()
            return
        
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            self.password_input.setFocus()
            return
        
        if password != confirm_password:
            self._show_error("Passwords do not match.")
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return
        
        # Get role-specific fields
        extra_fields = {}
        if is_artist:
            stage_name = self.stage_name_input.text().strip()
            if stage_name:
                extra_fields['stage_name'] = stage_name
            extra_fields['genre'] = self.genre_combo.currentText()
        else:
            display_name = self.display_name_input.text().strip()
            if display_name:
                extra_fields['display_name'] = display_name
            extra_fields['preferred_genre'] = self.pref_genre_combo.currentText()
        
        # Attempt registration
        success, message = self.db_manager.register_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra_fields
        )
        
        if success:
            # Get the newly registered user's info
            user_info = self.db_manager.verify_user(username, password)
            if user_info:
                self._clear_inputs()
                QMessageBox.information(self, "Success", 
                    f"Account created successfully! Welcome, {username}!")
                self.registration_successful.emit(user_info)
        else:
            self._show_error(message)
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email string to validate.
            
        Returns:
            True if email format is valid.
        """
        # Simple email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _show_error(self, message: str):
        """Show an error message box.
        
        Args:
            message: Error message to display.
        """
        QMessageBox.warning(self, "Registration Error", message)
    
    def _clear_inputs(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.stage_name_input.clear()
        self.display_name_input.clear()
        self.genre_combo.setCurrentIndex(0)
        self.pref_genre_combo.setCurrentIndex(0)
        self.artist_radio.setChecked(True)
    
    def reset(self):
        """Reset the registration screen to initial state."""
        self._clear_inputs()
        self.username_input.setFocus()
