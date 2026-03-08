"""
Listener Panel for Music Player Application.
Provides interface for listeners to browse and play music.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QLineEdit, QComboBox,
    QMessageBox, QScrollArea, QSlider, QGridLayout,
    QSizePolicy, QSplitter, QStackedWidget
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QPixmap
from typing import Dict, Any, List, Optional
from pathlib import Path


class SongCard(QFrame):
    """Card widget to display a song with cover art and details."""
    
    play_requested = pyqtSignal(dict)  # Emits song data dict
    details_requested = pyqtSignal(dict)  # Emits song data dict for details page
    
    def __init__(self, song_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.song_data = song_data
        self.setObjectName("songCard")
        self.setFixedSize(220, 280)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Cover Art (clickable for details)
        self.cover_label = QLabel()
        self.cover_label.setObjectName("coverLabel")
        self.cover_label.setFixedSize(196, 160)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cover_path = self.song_data.get('cover_art_path')
        if cover_path and Path(cover_path).exists():
            pixmap = QPixmap(cover_path)
            self.cover_label.setPixmap(pixmap.scaled(
                196, 160,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.cover_label.setText("🎵")
            self.cover_label.setStyleSheet("font-size: 48px; background-color: #0f3460; border-radius: 8px; color: #4ecdc4;")
        
        # Make cover clickable for details
        self.cover_label.mousePressEvent = lambda e: self.details_requested.emit(self.song_data)
        
        layout.addWidget(self.cover_label)
        
        # Title (clickable for details)
        title = self.song_data.get('title', 'Unknown Title')
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_label.mousePressEvent = lambda e: self.details_requested.emit(self.song_data)
        layout.addWidget(self.title_label)
        
        # Artist
        artist = self.song_data.get('display_name') or self.song_data.get('artist_name', 'Unknown Artist')
        artist_label = QLabel(artist)
        artist_label.setObjectName("cardArtist")
        artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(artist_label)
        
        # Genre badge
        genre = self.song_data.get('genre', '')
        if genre:
            genre_label = QLabel(genre)
            genre_label.setObjectName("cardGenre")
            genre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(genre_label)
        
        # Play button overlay
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("cardPlayBtn")
        self.play_btn.setFixedSize(50, 50)
        self.play_btn.clicked.connect(lambda: self.play_requested.emit(self.song_data))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)


class ArtistCard(QFrame):
    """Card widget to display an artist."""
    
    artist_selected = pyqtSignal(int)  # Emits artist_id
    
    def __init__(self, artist_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.artist_data = artist_data
        self.setObjectName("artistCard")
        self.setFixedSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Artist name
        name = self.artist_data.get('display_name') or self.artist_data.get('username', 'Unknown')
        name_label = QLabel(name)
        name_label.setObjectName("artistName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Genre if available
        genre = self.artist_data.get('genre')
        if genre:
            genre_label = QLabel(genre)
            genre_label.setObjectName("artistGenre")
            genre_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(genre_label)
        
        # Song count
        count = self.artist_data.get('song_count', 0)
        count_label = QLabel(f"{count} song{'s' if count != 1 else ''}")
        count_label.setObjectName("artistCount")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(count_label)
        
        # Click handler
        self.mousePressEvent = lambda e: self.artist_selected.emit(self.artist_data['id'])


class ListenerPanel(QWidget):
    """Listener panel widget for listener-specific functionality."""
    
    # Signal to logout
    logout_requested = pyqtSignal()
    
    def __init__(self, db_manager, user_info: Dict[str, Any], parent=None):
        """Initialize the listener panel.
        
        Args:
            db_manager: DatabaseManager instance.
            user_info: Dictionary containing logged-in listener's info.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_info = user_info
        self.profile_data = None
        self.all_songs: List[Dict[str, Any]] = []
        self.filtered_songs: List[Dict[str, Any]] = []
        self.artists: List[Dict[str, Any]] = []
        self.current_artist_filter: Optional[int] = None
        self.current_song: Optional[Dict[str, Any]] = None
        
        # Initialize Media Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        self._setup_ui()
        self._apply_styles()
        self._load_profile()
        self._load_songs()
        self._load_artists()
        
        # Connect player signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
    
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
        
        subtitle = QLabel("Listener Dashboard")
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
        
        role_label = QLabel("Listener")
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
        
        # --- Stacked Widget for different views ---
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Main Browse View (Artists + Songs)
        self.browse_widget = QWidget()
        browse_layout = QHBoxLayout(self.browse_widget)
        browse_layout.setContentsMargins(0, 0, 0, 0)
        browse_layout.setSpacing(0)
        
        # Content Splitter (Artists on left, Songs on right)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setObjectName("contentSplitter")
        
        # --- Artists Section (Left Sidebar) ---
        artists_widget = QWidget()
        artists_widget.setObjectName("artistsWidget")
        artists_layout = QVBoxLayout(artists_widget)
        artists_layout.setContentsMargins(20, 20, 20, 20)
        artists_layout.setSpacing(15)
        
        artists_header = QLabel("🎤 Artists")
        artists_header.setObjectName("sidebarHeader")
        artists_layout.addWidget(artists_header)
        
        # Clear filter button
        self.clear_filter_btn = QPushButton("Show All Songs")
        self.clear_filter_btn.setObjectName("clearFilterBtn")
        self.clear_filter_btn.clicked.connect(self._clear_artist_filter)
        self.clear_filter_btn.setVisible(False)
        artists_layout.addWidget(self.clear_filter_btn)
        
        # Artists scroll area
        artists_scroll = QScrollArea()
        artists_scroll.setWidgetResizable(True)
        artists_scroll.setObjectName("artistsScroll")
        artists_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.artists_container = QWidget()
        self.artists_layout = QVBoxLayout(self.artists_container)
        self.artists_layout.setContentsMargins(0, 0, 0, 0)
        self.artists_layout.setSpacing(10)
        self.artists_layout.addStretch()
        
        artists_scroll.setWidget(self.artists_container)
        artists_layout.addWidget(artists_scroll)
        
        content_splitter.addWidget(artists_widget)
        content_splitter.setStretchFactor(0, 0)
        
        # --- Songs Section (Right Main Area) ---
        songs_widget = QWidget()
        songs_widget.setObjectName("songsWidget")
        songs_layout = QVBoxLayout(songs_widget)
        songs_layout.setContentsMargins(30, 20, 30, 20)
        songs_layout.setSpacing(20)
        
        # Songs header with filter info
        songs_header_layout = QHBoxLayout()
        
        self.songs_title = QLabel("🎵 All Songs")
        self.songs_title.setObjectName("sectionLabel")
        songs_header_layout.addWidget(self.songs_title)
        
        songs_header_layout.addStretch()
        
        self.song_count_label = QLabel("0 songs")
        self.song_count_label.setObjectName("countLabel")
        songs_header_layout.addWidget(self.song_count_label)
        
        songs_layout.addLayout(songs_header_layout)
        
        # Songs scroll area with grid
        songs_scroll = QScrollArea()
        songs_scroll.setWidgetResizable(True)
        songs_scroll.setObjectName("songsScroll")
        songs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.songs_container = QWidget()
        self.songs_grid = QGridLayout(self.songs_container)
        self.songs_grid.setContentsMargins(0, 0, 0, 0)
        self.songs_grid.setSpacing(25)
        self.songs_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        songs_scroll.setWidget(self.songs_container)
        songs_layout.addWidget(songs_scroll)
        
        content_splitter.addWidget(songs_widget)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([250, 750])  # Initial sizes
        
        browse_layout.addWidget(content_splitter)
        self.content_stack.addWidget(self.browse_widget)
        
        # --- Song Details Page ---
        self.details_widget = QWidget()
        self.details_widget.setObjectName("detailsWidget")
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(40, 30, 40, 30)
        details_layout.setSpacing(20)
        
        # Back button
        back_btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Browse")
        self.back_btn.setObjectName("backButton")
        self.back_btn.clicked.connect(self._show_browse_view)
        back_btn_layout.addWidget(self.back_btn)
        back_btn_layout.addStretch()
        details_layout.addLayout(back_btn_layout)
        
        # Large cover image
        self.details_cover = QLabel()
        self.details_cover.setObjectName("detailsCover")
        self.details_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_cover.setMinimumHeight(350)
        details_layout.addWidget(self.details_cover, 1)
        
        # Song info
        info_layout = QVBoxLayout()
        self.details_title = QLabel("Song Title")
        self.details_title.setObjectName("detailsTitle")
        self.details_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.details_title)
        
        self.details_artist = QLabel("Artist Name")
        self.details_artist.setObjectName("detailsArtist")
        self.details_artist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.details_artist)
        
        self.details_genre = QLabel("Genre")
        self.details_genre.setObjectName("detailsGenre")
        self.details_genre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.details_genre)
        
        details_layout.addLayout(info_layout)
        
        # Playback controls
        controls_layout = QVBoxLayout()
        
        # Progress slider
        slider_layout = QHBoxLayout()
        self.details_current_time = QLabel("0:00")
        self.details_current_time.setObjectName("detailsTimeLabel")
        slider_layout.addWidget(self.details_current_time)
        
        self.details_slider = QSlider(Qt.Orientation.Horizontal)
        self.details_slider.setObjectName("detailsSlider")
        self.details_slider.setRange(0, 0)
        self.details_slider.sliderMoved.connect(self._seek_position)
        self.details_slider.sliderPressed.connect(self._slider_pressed)
        self.details_slider.sliderReleased.connect(self._slider_released)
        slider_layout.addWidget(self.details_slider, 1)
        
        self.details_total_time = QLabel("0:00")
        self.details_total_time.setObjectName("detailsTimeLabel")
        slider_layout.addWidget(self.details_total_time)
        
        controls_layout.addLayout(slider_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(20)
        
        self.details_prev_btn = QPushButton("⏮")
        self.details_prev_btn.setObjectName("detailsControlBtn")
        self.details_prev_btn.setFixedSize(50, 50)
        
        self.details_play_btn = QPushButton("▶")
        self.details_play_btn.setObjectName("detailsPlayBtn")
        self.details_play_btn.setFixedSize(70, 70)
        self.details_play_btn.clicked.connect(self._toggle_playback)
        
        self.details_stop_btn = QPushButton("⏹")
        self.details_stop_btn.setObjectName("detailsControlBtn")
        self.details_stop_btn.setFixedSize(50, 50)
        self.details_stop_btn.clicked.connect(self._stop_playback)
        
        btn_layout.addWidget(self.details_prev_btn)
        btn_layout.addWidget(self.details_play_btn)
        btn_layout.addWidget(self.details_stop_btn)
        
        controls_layout.addLayout(btn_layout)
        details_layout.addLayout(controls_layout)
        
        # Play from details button
        play_from_details_layout = QHBoxLayout()
        play_from_details_layout.addStretch()
        self.play_from_details_btn = QPushButton("▶ Play This Song")
        self.play_from_details_btn.setObjectName("playFromDetailsBtn")
        self.play_from_details_btn.clicked.connect(self._play_from_details)
        play_from_details_layout.addWidget(self.play_from_details_btn)
        play_from_details_layout.addStretch()
        details_layout.addLayout(play_from_details_layout)
        
        details_layout.addStretch()
        self.content_stack.addWidget(self.details_widget)
        
        main_layout.addWidget(self.content_stack, 1)
        
        # --- Full-Screen Player Overlay ---
        self.fullscreen_widget = QFrame(self)
        self.fullscreen_widget.setObjectName("fullscreenWidget")
        self.fullscreen_widget.setGeometry(0, 0, self.width(), self.height())
        self.fullscreen_widget.setVisible(False)
        self.fullscreen_widget.raise_()
        
        fullscreen_layout = QVBoxLayout(self.fullscreen_widget)
        fullscreen_layout.setContentsMargins(0, 0, 0, 0)
        fullscreen_layout.setSpacing(0)
        
        # Close button
        close_layout = QHBoxLayout()
        self.close_fullscreen_btn = QPushButton("✕ Close")
        self.close_fullscreen_btn.setObjectName("closeFullscreenBtn")
        self.close_fullscreen_btn.clicked.connect(self._hide_fullscreen)
        close_layout.addStretch()
        close_layout.addWidget(self.close_fullscreen_btn)
        fullscreen_layout.addLayout(close_layout)
        
        # Large cover in fullscreen
        self.fullscreen_cover = QLabel()
        self.fullscreen_cover.setObjectName("fullscreenCover")
        self.fullscreen_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fullscreen_layout.addWidget(self.fullscreen_cover, 1)
        
        # Fullscreen info
        fs_info_layout = QVBoxLayout()
        self.fullscreen_title = QLabel("Song Title")
        self.fullscreen_title.setObjectName("fullscreenTitle")
        self.fullscreen_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fs_info_layout.addWidget(self.fullscreen_title)
        
        self.fullscreen_artist = QLabel("Artist")
        self.fullscreen_artist.setObjectName("fullscreenArtist")
        self.fullscreen_artist.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fs_info_layout.addWidget(self.fullscreen_artist)
        
        fullscreen_layout.addLayout(fs_info_layout)
        
        # Fullscreen controls
        fs_controls = QVBoxLayout()
        
        # Progress
        fs_slider_layout = QHBoxLayout()
        self.fullscreen_current = QLabel("0:00")
        self.fullscreen_current.setObjectName("fullscreenTime")
        fs_slider_layout.addWidget(self.fullscreen_current)
        
        self.fullscreen_slider = QSlider(Qt.Orientation.Horizontal)
        self.fullscreen_slider.setObjectName("fullscreenSlider")
        self.fullscreen_slider.sliderMoved.connect(self._seek_position)
        self.fullscreen_slider.sliderPressed.connect(self._slider_pressed)
        self.fullscreen_slider.sliderReleased.connect(self._slider_released)
        fs_slider_layout.addWidget(self.fullscreen_slider, 1)
        
        self.fullscreen_total = QLabel("0:00")
        self.fullscreen_total.setObjectName("fullscreenTime")
        fs_slider_layout.addWidget(self.fullscreen_total)
        
        fs_controls.addLayout(fs_slider_layout)
        
        # Buttons
        fs_btn_layout = QHBoxLayout()
        fs_btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fs_btn_layout.setSpacing(30)
        
        self.fullscreen_prev = QPushButton("⏮")
        self.fullscreen_prev.setObjectName("fsControlBtn")
        self.fullscreen_prev.setFixedSize(60, 60)
        
        self.fullscreen_play = QPushButton("▶")
        self.fullscreen_play.setObjectName("fsPlayBtn")
        self.fullscreen_play.setFixedSize(90, 90)
        self.fullscreen_play.clicked.connect(self._toggle_playback)
        
        self.fullscreen_stop = QPushButton("⏹")
        self.fullscreen_stop.setObjectName("fsControlBtn")
        self.fullscreen_stop.setFixedSize(60, 60)
        self.fullscreen_stop.clicked.connect(self._stop_playback)
        
        fs_btn_layout.addWidget(self.fullscreen_prev)
        fs_btn_layout.addWidget(self.fullscreen_play)
        fs_btn_layout.addWidget(self.fullscreen_stop)
        
        fs_controls.addLayout(fs_btn_layout)
        fullscreen_layout.addLayout(fs_controls)
        
        fullscreen_layout.addSpacing(40)
        
        # --- Fixed Player Bar at Bottom ---
        self.player_bar = QFrame()
        self.player_bar.setObjectName("playerBar")
        self.player_bar.setFixedHeight(100)
        self.player_bar.setVisible(False)  # Hidden until music starts
        
        player_layout = QHBoxLayout(self.player_bar)
        player_layout.setContentsMargins(20, 10, 20, 10)
        player_layout.setSpacing(20)
        
        # Thumbnail (clickable for fullscreen)
        self.player_thumbnail = QLabel("🎵")
        self.player_thumbnail.setObjectName("playerThumbnail")
        self.player_thumbnail.setFixedSize(70, 70)
        self.player_thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_thumbnail.setCursor(Qt.CursorShape.PointingHandCursor)
        self.player_thumbnail.mousePressEvent = lambda e: self._show_fullscreen()
        player_layout.addWidget(self.player_thumbnail)
        
        # Song info
        info_layout = QVBoxLayout()
        self.player_title = QLabel("No song playing")
        self.player_title.setObjectName("playerTitle")
        self.player_artist = QLabel("")
        self.player_artist.setObjectName("playerArtist")
        info_layout.addWidget(self.player_title)
        info_layout.addWidget(self.player_artist)
        player_layout.addLayout(info_layout, 1)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setObjectName("playerControlBtn")
        self.prev_btn.setFixedSize(40, 40)
        
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setObjectName("playerMainBtn")
        self.play_pause_btn.setFixedSize(55, 55)
        self.play_pause_btn.clicked.connect(self._toggle_playback)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("playerControlBtn")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.clicked.connect(self._stop_playback)
        
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.play_pause_btn)
        btn_layout.addWidget(self.stop_btn)
        
        controls_layout.addLayout(btn_layout)
        
        # Progress slider
        slider_layout = QHBoxLayout()
        self.current_time = QLabel("0:00")
        self.current_time.setObjectName("timeLabel")
        slider_layout.addWidget(self.current_time)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self._seek_position)
        self.progress_slider.sliderPressed.connect(self._slider_pressed)
        self.progress_slider.sliderReleased.connect(self._slider_released)
        slider_layout.addWidget(self.progress_slider, 1)
        
        self.total_time = QLabel("0:00")
        self.total_time.setObjectName("timeLabel")
        slider_layout.addWidget(self.total_time)
        
        controls_layout.addLayout(slider_layout)
        player_layout.addLayout(controls_layout, 2)
        
        main_layout.addWidget(self.player_bar)
    
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
                color: #ffe66d;
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
            
            /* Artists Sidebar */
            QWidget#artistsWidget {
                background-color: #16213e;
                border-right: 1px solid #0f3460;
            }
            
            QLabel#sidebarHeader {
                font-size: 20px;
                font-weight: bold;
                color: #e0e0e0;
                padding-bottom: 10px;
                border-bottom: 1px solid #0f3460;
            }
            
            QPushButton#clearFilterBtn {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            
            QPushButton#clearFilterBtn:hover {
                background-color: #5de0d6;
            }
            
            /* Artist Card */
            QFrame#artistCard {
                background-color: #1a1a2e;
                border-radius: 10px;
                border: 1px solid #0f3460;
                padding: 5px;
            }
            
            QFrame#artistCard:hover {
                background-color: #0f3460;
                border: 1px solid #4ecdc4;
            }
            
            QLabel#artistName {
                font-size: 15px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#artistGenre {
                font-size: 12px;
                color: #4ecdc4;
            }
            
            QLabel#artistCount {
                font-size: 11px;
                color: #808080;
            }
            
            /* Songs Section */
            QLabel#sectionLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e0e0e0;
            }
            
            QLabel#countLabel {
                font-size: 14px;
                color: #808080;
            }
            
            /* Song Card */
            QFrame#songCard {
                background-color: #16213e;
                border-radius: 12px;
                border: 1px solid #0f3460;
            }
            
            QFrame#songCard:hover {
                background-color: #1a2642;
                border: 1px solid #e94560;
            }
            
            QLabel#cardTitle {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#cardArtist {
                font-size: 12px;
                color: #b0b0b0;
            }
            
            QLabel#cardGenre {
                font-size: 11px;
                color: #4ecdc4;
                background-color: #0f3460;
                padding: 3px 10px;
                border-radius: 10px;
            }
            
            QPushButton#cardPlayBtn {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            
            QPushButton#cardPlayBtn:hover {
                background-color: #ff6b6b;
            }
            
            /* Player Bar */
            QFrame#playerBar {
                background-color: #16213e;
                border-top: 2px solid #0f3460;
            }
            
            QLabel#playerThumbnail {
                font-size: 32px;
                background-color: #0f3460;
                border-radius: 8px;
            }
            
            QLabel#playerTitle {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#playerArtist {
                font-size: 13px;
                color: #b0b0b0;
            }
            
            QPushButton#playerControlBtn {
                background-color: transparent;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 20px;
                font-size: 16px;
            }
            
            QPushButton#playerControlBtn:hover {
                background-color: #0f3460;
                color: #ffffff;
            }
            
            QPushButton#playerMainBtn {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 27px;
                font-size: 20px;
            }
            
            QPushButton#playerMainBtn:hover {
                background-color: #ff6b6b;
            }
            
            QLabel#timeLabel {
                font-size: 12px;
                color: #808080;
                font-family: monospace;
            }
            
            QSlider#progressSlider::groove:horizontal {
                background: #0f3460;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#progressSlider::handle:horizontal {
                background: #e94560;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider#progressSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 3px;
            }
            
            /* Scroll Areas */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QSplitter::handle {
                background-color: #0f3460;
            }
            
            QSplitter::handle:horizontal {
                width: 2px;
            }
            /* Details Page Styles */
            QWidget#detailsWidget {
                background-color: #1a1a2e;
            }
            
            QPushButton#backButton {
                background-color: transparent;
                color: #4ecdc4;
                border: 1px solid #4ecdc4;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            
            QPushButton#backButton:hover {
                background-color: #4ecdc4;
                color: #1a1a2e;
            }
            
            QLabel#detailsCover {
                background-color: #0f3460;
                border-radius: 12px;
            }
            
            QLabel#detailsTitle {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#detailsArtist {
                font-size: 18px;
                color: #b0b0b0;
            }
            
            QLabel#detailsGenre {
                font-size: 14px;
                color: #4ecdc4;
                background-color: #0f3460;
                padding: 5px 15px;
                border-radius: 15px;
            }
            
            QLabel#detailsTimeLabel {
                font-size: 12px;
                color: #808080;
                font-family: monospace;
            }
            
            QSlider#detailsSlider::groove:horizontal {
                background: #0f3460;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#detailsSlider::handle:horizontal {
                background: #e94560;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider#detailsSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 3px;
            }
            
            QPushButton#detailsControlBtn {
                background-color: transparent;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                border-radius: 25px;
                font-size: 18px;
            }
            
            QPushButton#detailsControlBtn:hover {
                background-color: #0f3460;
                color: #ffffff;
            }
            
            QPushButton#detailsPlayBtn {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 35px;
                font-size: 24px;
            }
            
            QPushButton#detailsPlayBtn:hover {
                background-color: #ff6b6b;
            }
            
            QPushButton#playFromDetailsBtn {
                background-color: #4ecdc4;
                color: #1a1a2e;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            
            QPushButton#playFromDetailsBtn:hover {
                background-color: #5de0d6;
            }
            
            /* Fullscreen Styles */
            QFrame#fullscreenWidget {
                background-color: #0d0d1a;
            }
            
            QPushButton#closeFullscreenBtn {
                background-color: transparent;
                color: #e0e0e0;
                border: 1px solid #e94560;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                margin: 20px;
            }
            
            QPushButton#closeFullscreenBtn:hover {
                background-color: #e94560;
                color: white;
            }
            
            QLabel#fullscreenCover {
                background-color: transparent;
            }
            
            QLabel#fullscreenTitle {
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLabel#fullscreenArtist {
                font-size: 24px;
                color: #b0b0b0;
            }
            
            QLabel#fullscreenTime {
                font-size: 14px;
                color: #808080;
                font-family: monospace;
            }
            
            QSlider#fullscreenSlider::groove:horizontal {
                background: #0f3460;
                height: 8px;
                border-radius: 4px;
            }
            
            QSlider#fullscreenSlider::handle:horizontal {
                background: #e94560;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            
            QSlider#fullscreenSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 4px;
            }
            
            QPushButton#fsControlBtn {
                background-color: transparent;
                color: #e0e0e0;
                border: 2px solid #0f3460;
                border-radius: 30px;
                font-size: 20px;
            }
            
            QPushButton#fsControlBtn:hover {
                background-color: #0f3460;
                color: #ffffff;
            }
            
            QPushButton#fsPlayBtn {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 45px;
                font-size: 28px;
            }
            
            QPushButton#fsPlayBtn:hover {
                background-color: #ff6b6b;
            }
        """)
    
    def _load_profile(self):
        """Load listener profile from database."""
        self.profile_data = self.db_manager.get_user_profile(
            self.user_info['id'], 
            'listener'
        )
        
        if self.profile_data:
            display_name = self.profile_data.get('display_name', '') or self.user_info['username']
            # Update welcome label
            self.findChild(QLabel, "welcomeLabel").setText(f"Welcome, {display_name}")
    
    def _load_songs(self):
        """Load all songs from database."""
        self.all_songs = self.db_manager.get_all_songs()
        self.filtered_songs = self.all_songs.copy()
        self._update_songs_grid()
    
    def _load_artists(self):
        """Load all artists from database."""
        self.artists = self.db_manager.get_all_artists()
        self._update_artists_list()
    
    def _update_artists_list(self):
        """Update the artists sidebar."""
        # Clear existing
        while self.artists_layout.count() > 1:  # Keep the stretch
            item = self.artists_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Add artist cards
        for artist in self.artists:
            card = ArtistCard(artist)
            card.artist_selected.connect(self._filter_by_artist)
            self.artists_layout.insertWidget(self.artists_layout.count() - 1, card)
    
    def _update_songs_grid(self):
        """Update the songs grid display."""
        # Clear existing cards
        while self.songs_grid.count():
            item = self.songs_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Update count
        count = len(self.filtered_songs)
        self.song_count_label.setText(f"{count} song{'s' if count != 1 else ''}")
        
        # Add song cards
        row = 0
        col = 0
        max_cols = 3
        
        for song in self.filtered_songs:
            card = SongCard(song)
            card.play_requested.connect(self._play_song)
            card.details_requested.connect(self._show_song_details)
            self.songs_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _filter_by_artist(self, artist_id: int):
        """Filter songs by selected artist."""
        self.current_artist_filter = artist_id
        self.clear_filter_btn.setVisible(True)
        
        # Find artist name
        artist_name = "Unknown Artist"
        for artist in self.artists:
            if artist['id'] == artist_id:
                artist_name = artist.get('display_name') or artist.get('username')
                break
        
        self.songs_title.setText(f"🎵 Songs by {artist_name}")
        
        # Filter songs
        self.filtered_songs = [
            song for song in self.all_songs 
            if song.get('artist_id') == artist_id or song.get('artist_id') == str(artist_id)
        ]
        self._update_songs_grid()
    
    def _clear_artist_filter(self):
        """Clear artist filter and show all songs."""
        self.current_artist_filter = None
        self.clear_filter_btn.setVisible(False)
        self.songs_title.setText("🎵 All Songs")
        self.filtered_songs = self.all_songs.copy()
        self._update_songs_grid()
    
    def _play_song(self, song_data: Dict[str, Any]):
        """Play a song."""
        self.current_song = song_data
        file_path = song_data.get('file_path')
        
        if not file_path:
            QMessageBox.warning(self, "Error", "No audio file available for this song.")
            return
        
        path = Path(file_path)
        if not path.exists():
            QMessageBox.warning(self, "Error", f"Audio file not found: {file_path}")
            return
        
        # Show player bar
        self.player_bar.setVisible(True)
        
        # Update player info
        self.player_title.setText(song_data.get('title', 'Unknown Title'))
        artist = song_data.get('display_name') or song_data.get('artist_name', 'Unknown Artist')
        self.player_artist.setText(artist)
        
        # Update thumbnail
        cover_path = song_data.get('cover_art_path')
        if cover_path and Path(cover_path).exists():
            pixmap = QPixmap(cover_path)
            self.player_thumbnail.setPixmap(pixmap.scaled(
                70, 70,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.player_thumbnail.setText("🎵")
            self.player_thumbnail.setStyleSheet("font-size: 32px; background-color: #0f3460; border-radius: 8px;")
        
        # Set source and play
        url = QUrl.fromLocalFile(str(path.absolute()))
        self.player.setSource(url)
        self.player.play()
    
    def _toggle_playback(self):
        """Toggle play/pause."""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_pause_btn.setText("▶")
        else:
            self.player.play()
            self.play_pause_btn.setText("⏸")
    
    def _stop_playback(self):
        """Stop playback."""
        self.player.stop()
        self.play_pause_btn.setText("▶")
        self.progress_slider.setValue(0)
        self.current_time.setText("0:00")
    
    def _on_position_changed(self, position):
        """Handle position change."""
        if not hasattr(self, '_slider_dragging') or not self._slider_dragging:
            self.progress_slider.setValue(position)
            self.details_slider.setValue(position)
            self.fullscreen_slider.setValue(position)
        
        time_str = self._format_time(position)
        self.current_time.setText(time_str)
        self.details_current_time.setText(time_str)
        self.fullscreen_current.setText(time_str)
    
    def _on_duration_changed(self, duration):
        """Handle duration change."""
        self.progress_slider.setRange(0, duration)
        self.details_slider.setRange(0, duration)
        self.fullscreen_slider.setRange(0, duration)
        
        time_str = self._format_time(duration)
        self.total_time.setText(time_str)
        self.details_total_time.setText(time_str)
        self.fullscreen_total.setText(time_str)
    
    def _on_state_changed(self, state):
        """Handle playback state change."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setText("⏸")
            self.details_play_btn.setText("⏸")
            self.fullscreen_play.setText("⏸")
        else:
            self.play_pause_btn.setText("▶")
            self.details_play_btn.setText("▶")
            self.fullscreen_play.setText("▶")
    
    def _seek_position(self, position):
        """Seek to position."""
        self.player.setPosition(position)
    
    def _slider_pressed(self):
        """Slider pressed."""
        self._slider_dragging = True
    
    def _slider_released(self):
        """Slider released."""
        self._slider_dragging = False
        self.player.setPosition(self.progress_slider.value())
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds to MM:SS."""
        seconds = (ms // 1000) % 60
        minutes = (ms // 60000)
        return f"{minutes}:{seconds:02d}"
    
    def _show_song_details(self, song_data: Dict[str, Any]):
        """Show the song details page."""
        self.current_song = song_data
        
        # Update details view
        cover_path = song_data.get('cover_art_path')
        if cover_path and Path(cover_path).exists():
            pixmap = QPixmap(cover_path)
            self.details_cover.setPixmap(pixmap.scaled(
                400, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.details_cover.setText("🎵")
            self.details_cover.setStyleSheet("font-size: 120px; background-color: #0f3460; border-radius: 12px; color: #4ecdc4;")
        
        self.details_title.setText(song_data.get('title', 'Unknown Title'))
        artist = song_data.get('display_name') or song_data.get('artist_name', 'Unknown Artist')
        self.details_artist.setText(artist)
        self.details_genre.setText(song_data.get('genre', ''))
        
        # Switch to details view
        self.content_stack.setCurrentWidget(self.details_widget)
    
    def _show_browse_view(self):
        """Return to the browse view."""
        self.content_stack.setCurrentWidget(self.browse_widget)
    
    def _play_from_details(self):
        """Play the current song from details view."""
        if self.current_song:
            self._play_song(self.current_song)
    
    def _show_fullscreen(self):
        """Show the fullscreen player."""
        if not self.current_song:
            return
        
        # Update fullscreen info
        cover_path = self.current_song.get('cover_art_path')
        if cover_path and Path(cover_path).exists():
            pixmap = QPixmap(cover_path)
            self.fullscreen_cover.setPixmap(pixmap.scaled(
                self.width() - 100, self.height() - 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.fullscreen_cover.setText("🎵")
            self.fullscreen_cover.setStyleSheet("font-size: 200px; color: #4ecdc4;")
        
        self.fullscreen_title.setText(self.current_song.get('title', 'Unknown Title'))
        artist = self.current_song.get('display_name') or self.current_song.get('artist_name', 'Unknown Artist')
        self.fullscreen_artist.setText(artist)
        
        # Show fullscreen widget
        self.fullscreen_widget.setGeometry(0, 0, self.width(), self.height())
        self.fullscreen_widget.setVisible(True)
        self.fullscreen_widget.raise_()
    
    def _hide_fullscreen(self):
        """Hide the fullscreen player."""
        self.fullscreen_widget.setVisible(False)
    
    def resizeEvent(self, event):
        """Handle resize to update fullscreen geometry."""
        super().resizeEvent(event)
        if self.fullscreen_widget.isVisible():
            self.fullscreen_widget.setGeometry(0, 0, self.width(), self.height())
        
        # Update fullscreen cover if visible
        if self.fullscreen_widget.isVisible() and self.current_song:
            cover_path = self.current_song.get('cover_art_path')
            if cover_path and Path(cover_path).exists():
                pixmap = QPixmap(cover_path)
                self.fullscreen_cover.setPixmap(pixmap.scaled(
                    self.width() - 100, self.height() - 300,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
    
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
            self.player.stop()
            self.logout_requested.emit()
