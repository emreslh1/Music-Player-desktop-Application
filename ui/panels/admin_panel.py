"""
Admin Panel for Music Player Application.
Provides interface for administrators to manage users.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, List


class AdminPanel(QWidget):
    """Admin panel widget for managing users."""
    
    # Signal to logout
    logout_requested = pyqtSignal()
    
    def __init__(self, db_manager, user_info: Dict[str, Any], parent=None):
        """Initialize the admin panel.
        
        Args:
            db_manager: DatabaseManager instance.
            user_info: Dictionary containing logged-in admin's info.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_info = user_info
        self.users: List[Dict[str, Any]] = []
        self._setup_ui()
        self._apply_styles()
        self._load_users()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(70)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 10, 30, 10)
        
        # Left side - Logo and title
        left_layout = QVBoxLayout()
        
        title = QLabel("🎵 Music Player")
        title.setObjectName("appTitle")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Admin Dashboard")
        subtitle.setObjectName("appSubtitle")
        left_layout.addWidget(subtitle)
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        
        # Right side - User info and logout
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        welcome_label = QLabel(f"Welcome, {self.user_info['username']}")
        welcome_label.setObjectName("welcomeLabel")
        right_layout.addWidget(welcome_label)
        
        role_label = QLabel("Administrator")
        role_label.setObjectName("roleLabel")
        right_layout.addWidget(role_label)
        
        header_layout.addLayout(right_layout)
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setFixedSize(80, 35)
        self.logout_button.clicked.connect(self._logout)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Users List Section
        users_header_layout = QHBoxLayout()
        
        users_title = QLabel("👥 User Management")
        users_title.setObjectName("sectionTitle")
        users_header_layout.addWidget(users_title)
        
        users_header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh List")
        refresh_btn.setObjectName("actionButton")
        refresh_btn.setFixedSize(120, 35)
        refresh_btn.clicked.connect(self._load_users)
        users_header_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(users_header_layout)
        
        # Users Table
        self.users_table = QTableWidget()
        self.users_table.setObjectName("usersTable")
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role", "Joined Date", "Actions"])
        
        # Configure header resizing
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.users_table.setColumnWidth(3, 100)
        self.users_table.setColumnWidth(4, 150)
        self.users_table.setColumnWidth(5, 100)
        
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.verticalHeader().setVisible(False)
        
        content_layout.addWidget(self.users_table)
        
        main_layout.addWidget(content)
    
    def _apply_styles(self):
        """Apply stylesheet to the widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QFrame#header {
                background-color: #16213e;
                border-bottom: 1px solid #0f3460;
            }
            
            QLabel#appTitle {
                font-size: 20px;
                font-weight: bold;
                color: #e94560;
            }
            
            QLabel#appSubtitle {
                font-size: 12px;
                color: #808080;
            }
            
            QLabel#welcomeLabel {
                font-size: 14px;
                font-weight: bold;
                color: #e0e0e0;
            }
            
            QLabel#roleLabel {
                font-size: 11px;
                color: #4ecdc4;
            }
            
            QLabel#sectionTitle {
                font-size: 24px;
                font-weight: bold;
                color: #e0e0e0;
            }
            
            QPushButton#logoutButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            
            QPushButton#logoutButton:hover {
                background-color: #ff6b6b;
            }
            
            QPushButton#actionButton {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            
            QPushButton#actionButton:hover {
                background-color: #5de0d6;
            }
            
            QTableWidget {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 10px;
                gridline-color: #0f3460;
                font-size: 14px;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #0f3460;
            }
            
            QTableWidget::item:selected {
                background-color: #e94560;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #0f3460;
                color: #e0e0e0;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#deleteButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            
            QPushButton#deleteButton:hover {
                background-color: #ff6b6b;
            }
            
            QPushButton#deleteButton:disabled {
                background-color: #2a2a40;
                color: #606060;
            }
        """)
    
    def _load_users(self):
        """Load all users from database."""
        self.users = self.db_manager.get_all_users()
        self._update_users_table()
    
    def _update_users_table(self):
        """Update the users table with current data."""
        self.users_table.setRowCount(len(self.users))
        
        for row, user in enumerate(self.users):
            # ID
            id_item = QTableWidgetItem(str(user['id']))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_table.setItem(row, 0, id_item)
            
            # Username
            username_item = QTableWidgetItem(user['username'])
            self.users_table.setItem(row, 1, username_item)
            
            # Email
            email_item = QTableWidgetItem(user['email'])
            self.users_table.setItem(row, 2, email_item)
            
            # Role
            role_item = QTableWidgetItem(user['role'].capitalize())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_table.setItem(row, 3, role_item)
            
            # Joined Date
            created = user['created_at']
            if created and 'T' in created:
                created = created.split('T')[0]
            date_item = QTableWidgetItem(created or 'N/A')
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_table.setItem(row, 4, date_item)
            
            # Actions (Delete button)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("deleteButton")
            
            # Disable deleting self or other admins (if we implement multiple admins)
            if user['role'] == 'admin':
                delete_btn.setEnabled(False)
                delete_btn.setToolTip("Cannot delete admin users")
            else:
                delete_btn.clicked.connect(lambda checked, uid=user['id']: self._delete_user(uid))
            
            actions_layout.addWidget(delete_btn)
            self.users_table.setCellWidget(row, 5, actions_widget)
            
            # Set row height
            self.users_table.setRowHeight(row, 50)
    
    def _delete_user(self, user_id: int):
        """Delete a user after confirmation.
        
        Args:
            user_id: ID of user to delete.
        """
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this user?\nThis will also delete their profile and any uploaded songs.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_user(user_id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self._load_users()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def _logout(self):
        """Handle logout request."""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
