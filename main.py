"""
Main Application Entry Point for Music Player Desktop Application.
Handles application initialization, navigation, and authentication flow.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from database import DatabaseManager
from ui.screens import LoginScreen, RegistrationScreen
from ui.panels import AdminPanel, ArtistPanel, ListenerPanel


class MusicPlayerApp(QMainWindow):
    """Main application window managing navigation between screens."""
    
    # Window dimensions
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Current user info
        self.current_user = None
        
        # Set up the main window
        self._setup_window()
        self._setup_widgets()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure the main window properties."""
        self.setWindowTitle("Music Player")
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))
        self.resize(1100, 750)
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QScrollBar:vertical {
                background-color: #16213e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #0f3460;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #e94560;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #16213e;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #0f3460;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #e94560;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
    
    def _setup_widgets(self):
        """Set up the stacked widget for navigation."""
        # Create stacked widget for screen navigation
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.login_screen = LoginScreen(self.db_manager)
        self.registration_screen = RegistrationScreen(self.db_manager)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.login_screen)        # Index 0
        self.stacked_widget.addWidget(self.registration_screen)  # Index 1
        
        # Panel widgets (created dynamically on login)
        self.admin_panel = None
        self.artist_panel = None
        self.listener_panel = None
        
        # Show login screen by default
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def _connect_signals(self):
        """Connect signals from screens to handlers."""
        # Login screen signals
        self.login_screen.login_successful.connect(self._on_login_success)
        self.login_screen.switch_to_register.connect(self._show_registration)
        
        # Registration screen signals
        self.registration_screen.registration_successful.connect(self._on_registration_success)
        self.registration_screen.switch_to_login.connect(self._show_login)
    
    def _show_login(self):
        """Switch to login screen."""
        self.login_screen.reset()
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def _show_registration(self):
        """Switch to registration screen."""
        self.registration_screen.reset()
        self.stacked_widget.setCurrentWidget(self.registration_screen)
    
    def _on_login_success(self, user_info: dict):
        """Handle successful login.
        
        Args:
            user_info: Dictionary containing user information.
        """
        self.current_user = user_info
        self._navigate_to_panel(user_info['role'])
    
    def _on_registration_success(self, user_info: dict):
        """Handle successful registration.
        
        Args:
            user_info: Dictionary containing user information.
        """
        self.current_user = user_info
        self._navigate_to_panel(user_info['role'])
    
    def _navigate_to_panel(self, role: str):
        """Navigate to the appropriate panel based on user role.
        
        Args:
            role: User's role ('admin', 'artist', or 'listener').
        """
        # Remove existing panel if any
        self._clear_panels()
        
        # Create and add the appropriate panel
        if role == 'admin':
            self.admin_panel = AdminPanel(self.db_manager, self.current_user)
            self.admin_panel.logout_requested.connect(self._logout)
            self.stacked_widget.addWidget(self.admin_panel)
            self.stacked_widget.setCurrentWidget(self.admin_panel)
            
        elif role == 'artist':
            self.artist_panel = ArtistPanel(self.db_manager, self.current_user)
            self.artist_panel.logout_requested.connect(self._logout)
            self.stacked_widget.addWidget(self.artist_panel)
            self.stacked_widget.setCurrentWidget(self.artist_panel)
            
        elif role == 'listener':
            self.listener_panel = ListenerPanel(self.db_manager, self.current_user)
            self.listener_panel.logout_requested.connect(self._logout)
            self.stacked_widget.addWidget(self.listener_panel)
            self.stacked_widget.setCurrentWidget(self.listener_panel)
    
    def _clear_panels(self):
        """Remove existing panel widgets."""
        if self.admin_panel:
            self.stacked_widget.removeWidget(self.admin_panel)
            self.admin_panel.deleteLater()
            self.admin_panel = None
        
        if self.artist_panel:
            self.stacked_widget.removeWidget(self.artist_panel)
            self.artist_panel.deleteLater()
            self.artist_panel = None
        
        if self.listener_panel:
            self.stacked_widget.removeWidget(self.listener_panel)
            self.listener_panel.deleteLater()
            self.listener_panel = None
    
    def _logout(self):
        """Handle user logout."""
        self.current_user = None
        self._clear_panels()
        self._show_login()
    
    def closeEvent(self, event):
        """Handle application close event.
        
        Args:
            event: Close event.
        """
        # Close database connection
        if self.db_manager:
            self.db_manager.close()
        
        event.accept()


def main():
    """Main entry point for the application."""
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Music Player")
    app.setOrganizationName("MusicPlayer")
    
    # Create and show main window
    window = MusicPlayerApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
