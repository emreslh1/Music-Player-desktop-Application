"""
Login Screen for Music Player Application.
Provides user authentication interface.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QMessageBox,
    QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class LoginScreen(QWidget):
    """Login screen widget for user authentication."""
    
    # Signals
    login_successful = pyqtSignal(dict)  # Emits user info on successful login
    switch_to_register = pyqtSignal()  # Signal to switch to registration screen
    
    def __init__(self, db_manager, parent=None):
        """Initialize the login screen.
        
        Args:
            db_manager: DatabaseManager instance for authentication.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Set up the user interface with improved spacing."""
        # Main layout with generous margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(0)
        
        # Add vertical spacer at top for centering
        main_layout.addSpacerItem(
            QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        
        # Center container
        center_widget = QFrame()
        center_widget.setObjectName("loginContainer")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(0)
        center_layout.setContentsMargins(60, 50, 60, 50)
        
        # Title with icon
        title_label = QLabel("🎵")
        title_label.setObjectName("titleIcon")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title_label)
        
        center_layout.addSpacing(15)
        
        # App name
        app_name_label = QLabel("Music Player")
        app_name_label.setObjectName("appNameLabel")
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(app_name_label)
        
        center_layout.addSpacing(8)
        
        # Subtitle
        subtitle_label = QLabel("Welcome Back!")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(subtitle_label)
        
        # Spacing before form
        center_layout.addSpacing(45)
        
        # Username section
        username_label = QLabel("Username")
        username_label.setObjectName("inputLabel")
        center_layout.addWidget(username_label)
        
        center_layout.addSpacing(12)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setObjectName("usernameInput")
        self.username_input.setMinimumHeight(50)
        self.username_input.returnPressed.connect(self._attempt_login)
        center_layout.addWidget(self.username_input)
        
        # Spacing between inputs
        center_layout.addSpacing(30)
        
        # Password section
        password_label = QLabel("Password")
        password_label.setObjectName("inputLabel")
        center_layout.addWidget(password_label)
        
        center_layout.addSpacing(12)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("passwordInput")
        self.password_input.setMinimumHeight(50)
        self.password_input.returnPressed.connect(self._attempt_login)
        center_layout.addWidget(self.password_input)
        
        # Spacing before button
        center_layout.addSpacing(40)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setObjectName("loginButton")
        self.login_button.setMinimumHeight(55)
        self.login_button.clicked.connect(self._attempt_login)
        center_layout.addWidget(self.login_button)
        
        # Spacing before register link
        center_layout.addSpacing(35)
        
        # Register link section
        register_layout = QHBoxLayout()
        register_layout.setSpacing(8)
        register_layout.addStretch()
        
        register_text = QLabel("Don't have an account?")
        register_text.setObjectName("registerText")
        register_layout.addWidget(register_text)
        
        self.register_link = QPushButton("Sign Up")
        self.register_link.setObjectName("registerLink")
        self.register_link.setFlat(True)
        self.register_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_link.clicked.connect(self.switch_to_register.emit)
        register_layout.addWidget(self.register_link)
        
        register_layout.addStretch()
        center_layout.addLayout(register_layout)
        
        # Add center widget to main layout with size constraints
        center_widget.setMinimumWidth(480)
        center_widget.setMaximumWidth(520)
        main_layout.addWidget(center_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add vertical spacer at bottom
        main_layout.addSpacerItem(
            QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        
        # Set focus to username input
        self.username_input.setFocus()
    
    def _apply_styles(self):
        """Apply stylesheet to the widget with improved aesthetics."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
            
            QFrame#loginContainer {
                background-color: #16213e;
                border-radius: 20px;
                border: 1px solid #0f3460;
            }
            
            QLabel#titleIcon {
                font-size: 48px;
            }
            
            QLabel#appNameLabel {
                font-size: 32px;
                font-weight: bold;
                color: #e94560;
                letter-spacing: 1px;
            }
            
            QLabel#subtitleLabel {
                font-size: 16px;
                color: #8a8a8a;
                font-weight: 300;
            }
            
            QLabel#inputLabel {
                font-size: 14px;
                color: #c0c0c0;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            
            QLineEdit {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 15px;
                color: #ffffff;
                selection-background-color: #e94560;
            }
            
            QLineEdit:focus {
                border: 2px solid #e94560;
                background-color: #0d2940;
            }
            
            QLineEdit::placeholder {
                color: #6a6a6a;
            }
            
            QPushButton#loginButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            
            QPushButton#loginButton:hover {
                background-color: #ff6b6b;
            }
            
            QPushButton#loginButton:pressed {
                background-color: #c73e54;
            }
            
            QLabel#registerText {
                color: #7a7a7a;
                font-size: 14px;
            }
            
            QPushButton#registerLink {
                color: #e94560;
                font-size: 14px;
                font-weight: 600;
                text-decoration: none;
                background: transparent;
                border: none;
                padding: 0px;
            }
            
            QPushButton#registerLink:hover {
                color: #ff6b6b;
            }
        """)
    
    def _attempt_login(self):
        """Attempt to log in with provided credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username:
            self._show_error("Please enter your username.")
            self.username_input.setFocus()
            return
        
        if not password:
            self._show_error("Please enter your password.")
            self.password_input.setFocus()
            return
        
        # Verify credentials
        user_info = self.db_manager.verify_user(username, password)
        
        if user_info:
            self._clear_inputs()
            self.login_successful.emit(user_info)
        else:
            self._show_error("Invalid username or password.")
            self.password_input.clear()
            self.password_input.setFocus()
    
    def _show_error(self, message: str):
        """Show an error message box.
        
        Args:
            message: Error message to display.
        """
        QMessageBox.warning(self, "Login Error", message)
    
    def _clear_inputs(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.password_input.clear()
    
    def reset(self):
        """Reset the login screen to initial state."""
        self._clear_inputs()
        self.username_input.setFocus()
