"""
Artist Panel for Music Player Application.
Provides interface for artists to manage their profile and upload songs.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QLineEdit, QTextEdit,
    QComboBox, QMessageBox, QSpacerItem, QSizePolicy,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QDialog, QDialogButtonBox, QFileDialog,
    QGridLayout, QSlider, QStyle
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QPixmap, QIcon, QAction
from typing import Dict, Any, List
from pathlib import Path


class SongCard(QFrame):
    """Widget to display song info in a card format."""
    
    play_requested = pyqtSignal(str)  # Emits file path
    delete_requested = pyqtSignal(int)  # Emits song ID
    
    def __init__(self, song_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.song_data = song_data
        self.setObjectName("songCard")
        self.setFixedSize(200, 280)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Cover Art
        self.cover_label = QLabel()
        self.cover_label.setObjectName("coverLabel")
        self.cover_label.setFixedSize(180, 180)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet("background-color: #0f3460; border-radius: 8px;")
        
        cover_path = self.song_data.get('cover_art_path')
        if cover_path and Path(cover_path).exists():
            pixmap = QPixmap(cover_path)
            self.cover_label.setPixmap(pixmap.scaled(
                180, 180, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.cover_label.setText("🎵")
            self.cover_label.setStyleSheet("font-size: 64px; background-color: #0f3460; border-radius: 8px; color: #4ecdc4;")
            
        layout.addWidget(self.cover_label)
        
        # Title
        title = self.song_data.get('title', 'Unknown Title')
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Genre
        genre = self.song_data.get('genre', 'Unknown Genre')
        genre_label = QLabel(genre)
        genre_label.setObjectName("cardGenre")
        genre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(genre_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("cardPlayBtn")
        self.play_btn.setFixedSize(30, 30)
        self.play_btn.clicked.connect(lambda: self.play_requested.emit(self.song_data.get('file_path')))
        
        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setObjectName("cardDeleteBtn")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.song_data.get('id')))
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)


class AddSongDialog(QDialog):
    """Dialog for adding a new song with file selection and genre."""
    
    GENRES = [
        "Pop", "Rock", "Hip Hop", "R&B", "Jazz", 
        "Classical", "Electronic", "Country", "Latin",
        "Indie", "Metal", "Blues", "Folk", "Other"
    ]
    
    def __init__(self, parent=None):
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle("Upload New Song")
        self.setMinimumWidth(500)
        self.selected_file_path = None
        self.selected_cover_path = None
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Set up the dialog UI with file selection."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(18)
        
        # Title
        title = QLabel("🎵 Upload New Song")
        title.setObjectName("dialogTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # --- MP3 File Selection ---
        file_section_label = QLabel("Select MP3 File")
        file_section_label.setObjectName("sectionLabel")
        layout.addWidget(file_section_label)
        
        # File selection row
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Click 'Browse' to select an MP3 file...")
        self.file_path_input.setMinimumHeight(45)
        self.file_path_input.setReadOnly(True)
        file_layout.addWidget(self.file_path_input)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("browseButton")
        self.browse_button.setFixedSize(100, 45)
        self.browse_button.clicked.connect(self._browse_file)
        file_layout.addWidget(self.browse_button)
        
        layout.addLayout(file_layout)
        
        # Selected file info
        self.file_info_label = QLabel("")
        self.file_info_label.setObjectName("fileInfoLabel")
        self.file_info_label.setWordWrap(True)
        layout.addWidget(self.file_info_label)
        
        # --- Cover Art Selection ---
        cover_section_label = QLabel("Select Cover Art (Optional)")
        cover_section_label.setObjectName("sectionLabel")
        layout.addWidget(cover_section_label)
        
        # Cover selection row
        cover_layout = QHBoxLayout()
        cover_layout.setSpacing(10)
        
        self.cover_path_input = QLineEdit()
        self.cover_path_input.setPlaceholderText("Click 'Browse' to select an image...")
        self.cover_path_input.setMinimumHeight(45)
        self.cover_path_input.setReadOnly(True)
        cover_layout.addWidget(self.cover_path_input)
        
        self.browse_cover_button = QPushButton("Browse")
        self.browse_cover_button.setObjectName("browseButton")
        self.browse_cover_button.setFixedSize(100, 45)
        self.browse_cover_button.clicked.connect(self._browse_cover)
        cover_layout.addWidget(self.browse_cover_button)
        
        layout.addLayout(cover_layout)
        
        # --- Details ---
        # Song title
        title_label = QLabel("Song Title")
        title_label.setObjectName("fieldLabel")
        layout.addWidget(title_label)
        
        self.song_title_input = QLineEdit()
        self.song_title_input.setPlaceholderText("Enter the song title")
        self.song_title_input.setMinimumHeight(45)
        layout.addWidget(self.song_title_input)
        
        # Genre selection
        genre_label = QLabel("Genre")
        genre_label.setObjectName("fieldLabel")
        layout.addWidget(genre_label)
        
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(self.GENRES)
        self.genre_combo.setMinimumHeight(45)
        layout.addWidget(self.genre_combo)
        
        # Duration (optional)
        duration_label = QLabel("Duration (optional)")
        duration_label.setObjectName("fieldLabel")
        layout.addWidget(duration_label)
        
        duration_layout = QHBoxLayout()
        
        self.duration_minutes = QLineEdit()
        self.duration_minutes.setPlaceholderText("Min")
        self.duration_minutes.setMinimumHeight(45)
        self.duration_minutes.setMaximumWidth(80)
        duration_layout.addWidget(self.duration_minutes)
        
        colon_label = QLabel(":")
        colon_label.setObjectName("colonLabel")
        colon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        duration_layout.addWidget(colon_label)
        
        self.duration_seconds = QLineEdit()
        self.duration_seconds.setPlaceholderText("Sec")
        self.duration_seconds.setMinimumHeight(45)
        self.duration_seconds.setMaximumWidth(80)
        duration_layout.addWidget(self.duration_seconds)
        
        duration_layout.addStretch()
        layout.addLayout(duration_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        button_box.accepted.connect(self._accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _apply_styles(self):
        """Apply styles to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #16213e;
            }
            
            QLabel#dialogTitle {
                font-size: 22px;
                font-weight: bold;
                color: #e94560;
            }
            
            QLabel#sectionLabel {
                font-size: 15px;
                color: #4ecdc4;
                font-weight: 600;
            }
            
            QLabel#fieldLabel {
                font-size: 14px;
                color: #c0c0c0;
                font-weight: 500;
            }
            
            QLabel#colonLabel {
                font-size: 20px;
                color: #707070;
                font-weight: bold;
            }
            
            QLabel#fileInfoLabel {
                font-size: 12px;
                color: #6a9b6a;
                padding: 5px;
            }
            
            QLineEdit {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
            
            QLineEdit:read-only {
                background-color: #0a2540;
                color: #a0a0a0;
            }
            
            QLineEdit::placeholder {
                color: #6a6a6a;
            }
            
            QComboBox {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 35px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #4ecdc4;
                margin-right: 12px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #0f3460;
                selection-background-color: #e94560;
                color: #ffffff;
            }
            
            QPushButton#browseButton {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#browseButton:hover {
                background-color: #5de0d6;
            }
            
            QPushButton {
                background-color: #0f3460;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1a3a5c;
            }
            
            QPushButton:pressed {
                background-color: #0d2940;
            }
        """)
    
    def _browse_file(self):
        """Open file dialog to select an MP3 file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MP3 File",
            "",
            "MP3 Files (*.mp3);;All Files (*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_input.setText(file_path)
            
            # Extract filename and set as default title
            path = Path(file_path)
            filename = path.stem  # Filename without extension
            if not self.song_title_input.text().strip():
                self.song_title_input.setText(filename)
            
            # Show file info
            file_size = path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            self.file_info_label.setText(f"✓ Selected: {path.name} ({size_mb:.2f} MB)")
    
    def _browse_cover(self):
        """Open file dialog to select a cover image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Art",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.selected_cover_path = file_path
            self.cover_path_input.setText(file_path)
            
    def _accept(self):
        """Validate and accept the dialog."""
        # Check if file is selected
        if not self.selected_file_path:
            QMessageBox.warning(self, "Error", "Please select an MP3 file to upload.")
            return
        
        title = self.song_title_input.text().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a song title.")
            return
        
        self.accept()
    
    def get_song_data(self) -> Dict[str, Any]:
        """Get the entered song data including file path.
        
        Returns:
            Dictionary with song title, genre, duration, file path, and cover path.
        """
        title = self.song_title_input.text().strip()
        genre = self.genre_combo.currentText()
        
        # Parse duration
        duration = None
        try:
            minutes = int(self.duration_minutes.text()) if self.duration_minutes.text() else 0
            seconds = int(self.duration_seconds.text()) if self.duration_seconds.text() else 0
            if minutes > 0 or seconds > 0:
                duration = minutes * 60 + seconds
        except ValueError:
            pass
        
        return {
            'title': title,
            'genre': genre,
            'duration': duration,
            'file_path': self.selected_file_path,
            'cover_art_path': self.selected_cover_path
        }


class ArtistPanel(QWidget):
    """Artist panel widget for artist-specific functionality."""
    
    # Signal to logout
    logout_requested = pyqtSignal()
    
    # Available genres
    GENRES = [
        "Pop", "Rock", "Hip Hop", "R&B", "Jazz", 
        "Classical", "Electronic", "Country", "Latin",
        "Indie", "Metal", "Blues", "Folk", "Other"
    ]
    
    def __init__(self, db_manager, user_info: Dict[str, Any], parent=None):
        """Initialize the artist panel.
        
        Args:
            db_manager: DatabaseManager instance.
            user_info: Dictionary containing logged-in artist's info.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_info = user_info
        self.profile_data = None
        self.songs: List[Dict[str, Any]] = []
        
        # Initialize Media Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)  # Set default volume to 70%
        self.player.errorOccurred.connect(self._on_player_error)
        
        self._setup_ui()
        self._apply_styles()
        self._load_profile()
        self._load_songs()
    
    def _on_player_error(self):
        """Handle media player errors."""
        error_msg = self.player.errorString()
        QMessageBox.warning(self, "Playback Error", f"Error playing media: {error_msg}")

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
        
        subtitle = QLabel("Artist Dashboard")
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
        
        role_label = QLabel("Artist")
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
        
        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("contentScroll")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 25, 30, 25)
        content_layout.setSpacing(25)
        
        # Profile section
        profile_frame = QFrame()
        profile_frame.setObjectName("profileFrame")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setContentsMargins(30, 25, 30, 25)
        profile_layout.setSpacing(18)
        
        # Profile header
        profile_header = QLabel("🎤 Artist Profile")
        profile_header.setObjectName("sectionLabel")
        profile_layout.addWidget(profile_header)
        
        # Stage name
        stage_name_layout = QHBoxLayout()
        stage_name_label = QLabel("Stage Name:")
        stage_name_label.setObjectName("fieldLabel")
        stage_name_label.setFixedWidth(130)
        stage_name_layout.addWidget(stage_name_label)
        
        self.stage_name_input = QLineEdit()
        self.stage_name_input.setPlaceholderText("Your stage/artist name")
        self.stage_name_input.setMinimumHeight(42)
        stage_name_layout.addWidget(self.stage_name_input)
        
        profile_layout.addLayout(stage_name_layout)
        
        # Genre
        genre_layout = QHBoxLayout()
        genre_label = QLabel("Primary Genre:")
        genre_label.setObjectName("fieldLabel")
        genre_label.setFixedWidth(130)
        genre_layout.addWidget(genre_label)
        
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(self.GENRES)
        self.genre_combo.setMinimumHeight(42)
        genre_layout.addWidget(self.genre_combo)
        
        profile_layout.addLayout(genre_layout)
        
        # Bio
        bio_label = QLabel("Bio:")
        bio_label.setObjectName("fieldLabel")
        profile_layout.addWidget(bio_label)
        
        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Tell us about yourself and your music...")
        self.bio_input.setMaximumHeight(100)
        profile_layout.addWidget(self.bio_input)
        
        # Save profile button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        self.save_profile_btn = QPushButton("💾 Save Profile")
        self.save_profile_btn.setObjectName("saveButton")
        self.save_profile_btn.setFixedSize(160, 42)
        self.save_profile_btn.clicked.connect(self._save_profile)
        save_layout.addWidget(self.save_profile_btn)
        
        profile_layout.addLayout(save_layout)
        
        content_layout.addWidget(profile_frame)
        
        # Songs section
        songs_frame = QFrame()
        songs_frame.setObjectName("songsFrame")
        songs_layout = QVBoxLayout(songs_frame)
        songs_layout.setContentsMargins(30, 25, 30, 25)
        songs_layout.setSpacing(18)
        
        # Songs header with upload button
        songs_header_layout = QHBoxLayout()
        
        songs_header = QLabel("🎵 My Songs")
        songs_header.setObjectName("sectionLabel")
        songs_header_layout.addWidget(songs_header)
        
        songs_header_layout.addStretch()
        
        # Song count label
        self.song_count_label = QLabel("0 songs")
        self.song_count_label.setObjectName("songCountLabel")
        songs_header_layout.addWidget(self.song_count_label)
        
        songs_layout.addLayout(songs_header_layout)
        
        # Upload button
        upload_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("➕ Upload New Song")
        self.upload_btn.setObjectName("uploadButton")
        self.upload_btn.setFixedSize(180, 45)
        self.upload_btn.clicked.connect(self._show_upload_dialog)
        upload_layout.addWidget(self.upload_btn)
        
        upload_layout.addStretch()
        songs_layout.addLayout(upload_layout)
        
        # Songs table/grid
        self.songs_container = QWidget()
        self.songs_grid = QGridLayout(self.songs_container)
        self.songs_grid.setSpacing(20)
        self.songs_grid.setContentsMargins(0, 0, 0, 0)
        # Align top-left
        self.songs_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        songs_layout.addWidget(self.songs_container)
        
        content_layout.addWidget(songs_frame)
        
        # Add stretch at bottom
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)
        
        # --- Player Controls ---
        player_frame = QFrame()
        player_frame.setObjectName("playerFrame")
        player_frame.setFixedHeight(90)
        player_layout = QHBoxLayout(player_frame)
        player_layout.setContentsMargins(20, 10, 20, 10)
        
        # Now Playing Info
        info_layout = QVBoxLayout()
        self.playing_title = QLabel("Not Playing")
        self.playing_title.setObjectName("playingTitle")
        self.playing_artist = QLabel("")
        self.playing_artist.setObjectName("playingArtist")
        info_layout.addWidget(self.playing_title)
        info_layout.addWidget(self.playing_artist)
        player_layout.addLayout(info_layout, 1)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.setObjectName("controlButton")
        self.stop_btn.clicked.connect(self._stop_playback)
        
        self.play_pause_btn = QPushButton("⏯")
        self.play_pause_btn.setFixedSize(50, 50)
        self.play_pause_btn.setObjectName("playPauseButton")
        self.play_pause_btn.clicked.connect(self._toggle_playback)
        
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.play_pause_btn)
        
        controls_layout.addLayout(btn_layout)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("progressSlider")
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self._set_position)
        self.slider.sliderPressed.connect(self._slider_pressed)
        self.slider.sliderReleased.connect(self._slider_released)
        controls_layout.addWidget(self.slider)
        
        player_layout.addLayout(controls_layout, 2)
        
        # Volume/Time (Placeholder for symmetry or volume)
        vol_layout = QHBoxLayout()
        vol_layout.addStretch()
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("timeLabel")
        vol_layout.addWidget(self.time_label)
        player_layout.addLayout(vol_layout, 1)
        
        main_layout.addWidget(player_frame)
        
        # Player connections
        self.player.positionChanged.connect(self._position_changed)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.playbackStateChanged.connect(self._player_state_changed)
        
        self.is_slider_pressed = False
    
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
            
            QScrollArea#contentScroll {
                border: none;
                background-color: #1a1a2e;
            }
            
            QFrame#profileFrame, QFrame#songsFrame {
                background-color: #16213e;
                border-radius: 12px;
                border: 1px solid #0f3460;
            }
            
            QLabel#sectionLabel {
                font-size: 18px;
                font-weight: bold;
                color: #e0e0e0;
            }
            
            QLabel#fieldLabel {
                font-size: 14px;
                color: #b0b0b0;
                font-weight: 500;
            }
            
            QLabel#songCountLabel {
                font-size: 14px;
                color: #4ecdc4;
                font-weight: 500;
            }
            
            QLineEdit {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 2px solid #e94560;
            }
            
            QLineEdit::placeholder {
                color: #6a6a6a;
            }
            
            QTextEdit {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QTextEdit:focus {
                border: 2px solid #e94560;
            }
            
            QComboBox {
                background-color: #0f3460;
                border: 2px solid #1a1a2e;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QComboBox:focus {
                border: 2px solid #e94560;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #4ecdc4;
                margin-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #16213e;
                border: 2px solid #0f3460;
                selection-background-color: #4ecdc4;
                color: #ffffff;
            }
            
            QPushButton#saveButton {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#saveButton:hover {
                background-color: #5de0d6;
            }
            
            QPushButton#uploadButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton#uploadButton:hover {
                background-color: #ff6b6b;
            }
            
            QTableWidget {
                background-color: #0f3460;
                border: 1px solid #1a1a2e;
                border-radius: 10px;
                gridline-color: #1a1a2e;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1a1a2e;
            }
            
            QTableWidget::item:selected {
                background-color: #e94560;
            }
            
            QHeaderView::section {
                background-color: #16213e;
                color: #e0e0e0;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            
            QPushButton#deleteButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 12px;
            }
            
            QPushButton#deleteButton:hover {
                background-color: #ff6b6b;
            }
            
            /* Song Card Styles */
            QFrame#songCard {
                background-color: #16213e;
                border-radius: 12px;
                border: 1px solid #0f3460;
            }
            
            QFrame#songCard:hover {
                border: 1px solid #e94560;
                background-color: #1a2642;
            }
            
            QLabel#cardTitle {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#cardGenre {
                font-size: 12px;
                color: #b0b0b0;
            }
            
            QPushButton#cardPlayBtn {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border-radius: 15px;
                font-weight: bold;
            }
            
            QPushButton#cardPlayBtn:hover {
                background-color: #5de0d6;
            }
            
            QPushButton#cardDeleteBtn {
                background-color: #e94560;
                color: white;
                border-radius: 15px;
            }
            
            QPushButton#cardDeleteBtn:hover {
                background-color: #ff6b6b;
            }
            
            /* Player Controls Styles */
            QFrame#playerFrame {
                background-color: #16213e;
                border-top: 1px solid #0f3460;
            }
            
            QLabel#playingTitle {
                font-size: 16px;
                font-weight: bold;
                color: #e94560;
            }
            
            QLabel#playingArtist {
                font-size: 12px;
                color: #b0b0b0;
            }
            
            QPushButton#controlButton {
                background-color: transparent;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 20px;
                font-size: 18px;
            }
            
            QPushButton#controlButton:hover {
                background-color: #0f3460;
                color: #ffffff;
            }
            
            QPushButton#playPauseButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            
            QPushButton#playPauseButton:hover {
                background-color: #ff6b6b;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #0f3460;
                height: 8px;
                background: #0f3460;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #4ecdc4;
                border: 1px solid #4ecdc4;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QLabel#timeLabel {
                color: #b0b0b0;
                font-family: monospace;
            }
        """)
    
    def _load_profile(self):
        """Load artist profile from database."""
        self.profile_data = self.db_manager.get_user_profile(
            self.user_info['id'], 
            'artist'
        )
        
        if self.profile_data:
            # Populate fields
            stage_name = self.profile_data.get('stage_name', '') or self.user_info['username']
            self.stage_name_input.setText(stage_name)
            
            genre = self.profile_data.get('genre', 'Pop')
            index = self.genre_combo.findText(genre)
            if index >= 0:
                self.genre_combo.setCurrentIndex(index)
            
            bio = self.profile_data.get('bio', '')
            self.bio_input.setPlainText(bio or '')
    
    def _load_songs(self):
        """Load artist's songs from database."""
        self.songs = self.db_manager.get_artist_songs(self.user_info['id'])
        self._update_songs_grid()
    
    def _update_songs_grid(self):
        """Update the songs grid with current data."""
        self.song_count_label.setText(f"{len(self.songs)} song{'s' if len(self.songs) != 1 else ''}")
        
        # Clear existing items
        while self.songs_grid.count():
            item = self.songs_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Add cards
        row = 0
        col = 0
        max_cols = 4  # Adjust based on window width if needed
        
        for song in self.songs:
            card = SongCard(song)
            card.play_requested.connect(self._play_song)
            card.delete_requested.connect(self._delete_song)
            
            self.songs_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _play_song(self, file_path: str):
        """Play the selected song file.
        
        Args:
            file_path: Path to the MP3 file.
        """
        if not file_path:
            return
            
        path = Path(file_path)
        if not path.exists():
            QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            return
        
        # Update UI info
        # Find song info for display
        for song in self.songs:
            if song.get('file_path') == file_path:
                self.playing_title.setText(song.get('title', 'Unknown'))
                self.playing_artist.setText(song.get('artist_name', self.user_info['username']))
                break
        
        # Set source and play
        url = QUrl.fromLocalFile(str(path.absolute()))
        self.player.setSource(url)
        self.player.play()
        self.play_pause_btn.setText("⏸")
    
    def _stop_playback(self):
        """Stop playback."""
        self.player.stop()
        self.play_pause_btn.setText("▶")
        self.playing_title.setText("Not Playing")
        self.playing_artist.setText("")
        self.slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        
    def _toggle_playback(self):
        """Toggle play/pause."""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_pause_btn.setText("▶")
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
            self.play_pause_btn.setText("⏸")
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            # If stopped and has source, play. If no source, do nothing.
            if self.player.source().isValid():
                self.player.play()
                self.play_pause_btn.setText("⏸")

    def _position_changed(self, position):
        """Handle player position change."""
        if not self.is_slider_pressed:
            self.slider.setValue(position)
        self._update_time_label(position, self.player.duration())

    def _duration_changed(self, duration):
        """Handle player duration change."""
        self.slider.setRange(0, duration)
        self._update_time_label(self.player.position(), duration)

    def _set_position(self, position):
        """Set player position from slider."""
        self.player.setPosition(position)

    def _slider_pressed(self):
        """Handle slider pressed event."""
        self.is_slider_pressed = True

    def _slider_released(self):
        """Handle slider released event."""
        self.is_slider_pressed = False
        self.player.setPosition(self.slider.value())

    def _update_time_label(self, position, duration):
        """Update the time label."""
        def format_time(ms):
            seconds = (ms // 1000) % 60
            minutes = (ms // 60000)
            return f"{minutes:02d}:{seconds:02d}"
        
        self.time_label.setText(f"{format_time(position)} / {format_time(duration)}")

    def _player_state_changed(self, state):
        """Handle player state changes."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setText("▶")
            
    def _save_profile(self):
        """Save profile changes to database."""
        stage_name = self.stage_name_input.text().strip()
        genre = self.genre_combo.currentText()
        bio = self.bio_input.toPlainText().strip()
        
        success, message = self.db_manager.update_user_profile(
            self.user_info['id'],
            'artist',
            stage_name=stage_name,
            genre=genre,
            bio=bio
        )
        
        if success:
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self._load_profile()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def _show_upload_dialog(self):
        """Show the upload song dialog with file selection."""
        dialog = AddSongDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            song_data = dialog.get_song_data()
            
            if song_data['title'] and song_data.get('file_path'):
                success, message = self.db_manager.add_song(
                    artist_id=self.user_info['id'],
                    title=song_data['title'],
                    genre=song_data['genre'],
                    duration=song_data.get('duration'),
                    file_path=song_data.get('file_path'),
                    cover_art_path=song_data.get('cover_art_path')
                )
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    self._load_songs()
                else:
                    QMessageBox.warning(self, "Error", message)
            else:
                QMessageBox.warning(self, "Error", "Failed to get song data.")
    
    def _delete_song(self, song_id: int):
        """Delete a song after confirmation.
        
        Args:
            song_id: ID of the song to delete.
        """
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this song?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db_manager.delete_song(song_id, self.user_info['id'])
            
            if success:
                QMessageBox.information(self, "Success", message)
                self._load_songs()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def _logout(self):
        """Handle logout button click."""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
