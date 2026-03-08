"""
Database module for Music Player Application.
Handles SQLite database connection and user management.
"""

import sqlite3
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any


class DatabaseManager:
    """Manages SQLite database operations for the Music Player application."""
    
    DB_NAME = "music_player.db"
    
    # Pre-defined admin credentials
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"  # In production, use environment variables
    ADMIN_EMAIL = "admin@musicplayer.com"
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection and create tables if needed.
        
        Args:
            db_path: Optional custom path for the database file.
        """
        if db_path:
            self.db_path = db_path
        else:
            # Store database in user's home directory for persistence
            home = Path.home()
            app_dir = home / ".music_player"
            app_dir.mkdir(exist_ok=True)
            self.db_path = str(app_dir / self.DB_NAME)
        
        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
        self._ensure_admin_exists()
    
    def _connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def _create_tables(self) -> None:
        """Create necessary database tables."""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'artist', 'listener')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Artists additional info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artist_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                stage_name TEXT,
                bio TEXT,
                genre TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Listeners additional info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listener_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                display_name TEXT,
                preferred_genre TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Songs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                artist_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration INTEGER,
                file_path TEXT,
                cover_art_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (artist_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Migration: Add cover_art_path if it doesn't exist
        cursor.execute("PRAGMA table_info(songs)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'cover_art_path' not in columns:
            cursor.execute("ALTER TABLE songs ADD COLUMN cover_art_path TEXT")
        
        self.connection.commit()
    
    def _ensure_admin_exists(self) -> None:
        """Ensure the pre-defined admin account exists."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (self.ADMIN_USERNAME,))
        
        if not cursor.fetchone():
            password_hash = self._hash_password(self.ADMIN_PASSWORD)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, 'admin')
            ''', (self.ADMIN_USERNAME, self.ADMIN_EMAIL, password_hash))
            self.connection.commit()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256.
        
        Args:
            password: Plain text password.
            
        Returns:
            Hashed password string.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user info if valid.
        
        Args:
            username: Username to verify.
            password: Password to verify.
            
        Returns:
            User info dictionary if credentials are valid, None otherwise.
        """
        cursor = self.connection.cursor()
        password_hash = self._hash_password(password)
        
        cursor.execute('''
            SELECT id, username, email, role, created_at, last_login
            FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Update last login time
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user['id'],))
            self.connection.commit()
            
            return dict(user)
        
        return None
    
    def register_user(self, username: str, email: str, password: str, 
                      role: str, **extra_fields) -> Tuple[bool, str]:
        """Register a new user.
        
        Args:
            username: Desired username.
            email: User's email address.
            password: User's password.
            role: User role ('artist' or 'listener').
            **extra_fields: Additional profile fields.
            
        Returns:
            Tuple of (success, message).
        """
        if role == 'admin':
            return False, "Cannot create admin accounts through registration."
        
        if role not in ('artist', 'listener'):
            return False, "Invalid role specified."
        
        cursor = self.connection.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists."
        
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Email already registered."
        
        password_hash = self._hash_password(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            
            # Create profile record based on role
            if role == 'artist':
                cursor.execute('''
                    INSERT INTO artist_profiles (user_id, stage_name, bio, genre)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, 
                      extra_fields.get('stage_name', username),
                      extra_fields.get('bio', ''),
                      extra_fields.get('genre', '')))
            else:  # listener
                cursor.execute('''
                    INSERT INTO listener_profiles (user_id, display_name, preferred_genre)
                    VALUES (?, ?, ?)
                ''', (user_id,
                      extra_fields.get('display_name', username),
                      extra_fields.get('preferred_genre', '')))
            
            self.connection.commit()
            return True, "Registration successful!"
            
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Registration failed: {str(e)}"
    
    def get_user_profile(self, user_id: int, role: str) -> Optional[Dict[str, Any]]:
        """Get user profile information.
        
        Args:
            user_id: User's ID.
            role: User's role.
            
        Returns:
            Profile information dictionary or None.
        """
        cursor = self.connection.cursor()
        
        if role == 'artist':
            cursor.execute('''
                SELECT u.*, ap.stage_name, ap.bio, ap.genre
                FROM users u
                LEFT JOIN artist_profiles ap ON u.id = ap.user_id
                WHERE u.id = ?
            ''', (user_id,))
        elif role == 'listener':
            cursor.execute('''
                SELECT u.*, lp.display_name, lp.preferred_genre
                FROM users u
                LEFT JOIN listener_profiles lp ON u.id = lp.user_id
                WHERE u.id = ?
            ''', (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin panel).
        
        Returns:
            List of user dictionaries.
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT id, username, email, role, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete a user (admin only).
        
        Args:
            user_id: ID of user to delete.
            
        Returns:
            Tuple of (success, message).
        """
        cursor = self.connection.cursor()
        
        # Prevent deleting admin account
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found."
        
        if user['role'] == 'admin':
            return False, "Cannot delete admin accounts."
        
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.connection.commit()
            return True, "User deleted successfully."
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Delete failed: {str(e)}"
    
    def update_user_profile(self, user_id: int, role: str, **fields) -> Tuple[bool, str]:
        """Update user profile information.
        
        Args:
            user_id: User's ID.
            role: User's role.
            **fields: Fields to update.
            
        Returns:
            Tuple of (success, message).
        """
        cursor = self.connection.cursor()
        
        try:
            if role == 'artist':
                valid_fields = ['stage_name', 'bio', 'genre']
                update_fields = {k: v for k, v in fields.items() if k in valid_fields}
                
                if update_fields:
                    set_clause = ', '.join(f"{k} = ?" for k in update_fields.keys())
                    values = list(update_fields.values()) + [user_id]
                    cursor.execute(f'''
                        UPDATE artist_profiles SET {set_clause} WHERE user_id = ?
                    ''', values)
                    
            elif role == 'listener':
                valid_fields = ['display_name', 'preferred_genre']
                update_fields = {k: v for k, v in fields.items() if k in valid_fields}
                
                if update_fields:
                    set_clause = ', '.join(f"{k} = ?" for k in update_fields.keys())
                    values = list(update_fields.values()) + [user_id]
                    cursor.execute(f'''
                        UPDATE listener_profiles SET {set_clause} WHERE user_id = ?
                    ''', values)
            
            self.connection.commit()
            return True, "Profile updated successfully."
            
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Update failed: {str(e)}"
    
    # ==================== Song Management ====================
    
    def add_song(self, artist_id: int, title: str, genre: str, 
                 duration: Optional[int] = None, file_path: Optional[str] = None,
                 cover_art_path: Optional[str] = None) -> Tuple[bool, str]:
        """Add a new song for an artist.
        
        Args:
            artist_id: ID of the artist uploading the song.
            title: Song title.
            genre: Song genre.
            duration: Optional duration in seconds.
            file_path: Optional path to the song file.
            cover_art_path: Optional path to the cover art image.
            
        Returns:
            Tuple of (success, message).
        """
        cursor = self.connection.cursor()
        
        # Verify user is an artist
        cursor.execute("SELECT role FROM users WHERE id = ?", (artist_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found."
        
        if user['role'] != 'artist':
            return False, "Only artists can upload songs."
        
        try:
            cursor.execute('''
                INSERT INTO songs (artist_id, title, genre, duration, file_path, cover_art_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (artist_id, title, genre, duration, file_path, cover_art_path))
            
            self.connection.commit()
            return True, "Song added successfully!"
            
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Failed to add song: {str(e)}"
    
    def get_artist_songs(self, artist_id: int) -> List[Dict[str, Any]]:
        """Get all songs by a specific artist.
        
        Args:
            artist_id: ID of the artist.
            
        Returns:
            List of song dictionaries.
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT s.*, u.username as artist_name
            FROM songs s
            JOIN users u ON s.artist_id = u.id
            WHERE s.artist_id = ?
            ORDER BY s.created_at DESC
        ''', (artist_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_songs(self) -> List[Dict[str, Any]]:
        """Get all songs (for admin/listener browsing).
        
        Returns:
            List of song dictionaries with artist info.
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT s.*, u.username as artist_name,
                   COALESCE(ap.stage_name, u.username) as display_name
            FROM songs s
            JOIN users u ON s.artist_id = u.id
            LEFT JOIN artist_profiles ap ON u.id = ap.user_id
            ORDER BY s.created_at DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_songs_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Get all songs of a specific genre.
        
        Args:
            genre: Genre to filter by.
            
        Returns:
            List of song dictionaries.
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT s.*, u.username as artist_name,
                   COALESCE(ap.stage_name, u.username) as display_name
            FROM songs s
            JOIN users u ON s.artist_id = u.id
            LEFT JOIN artist_profiles ap ON u.id = ap.user_id
            WHERE s.genre = ?
            ORDER BY s.created_at DESC
        ''', (genre,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_song(self, song_id: int, artist_id: int) -> Tuple[bool, str]:
        """Delete a song (only by the artist who owns it).
        
        Args:
            song_id: ID of the song to delete.
            artist_id: ID of the artist attempting to delete.
            
        Returns:
            Tuple of (success, message).
        """
        cursor = self.connection.cursor()
        
        # Verify song belongs to this artist
        cursor.execute("SELECT id FROM songs WHERE id = ? AND artist_id = ?", (song_id, artist_id))
        song = cursor.fetchone()
        
        if not song:
            return False, "Song not found or you don't have permission to delete it."
        
        try:
            cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
            self.connection.commit()
            return True, "Song deleted successfully."
            
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Delete failed: {str(e)}"
    
    def update_song(self, song_id: int, artist_id: int, **fields) -> Tuple[bool, str]:
        """Update song information.
        
        Args:
            song_id: ID of the song to update.
            artist_id: ID of the artist attempting to update.
            **fields: Fields to update (title, genre, duration, file_path).
            
        Returns:
            Tuple of (success, message).
        """
        cursor = self.connection.cursor()
        
        # Verify song belongs to this artist
        cursor.execute("SELECT id FROM songs WHERE id = ? AND artist_id = ?", (song_id, artist_id))
        song = cursor.fetchone()
        
        if not song:
            return False, "Song not found or you don't have permission to update it."
        
        valid_fields = ['title', 'genre', 'duration', 'file_path']
        update_fields = {k: v for k, v in fields.items() if k in valid_fields}
        
        if not update_fields:
            return False, "No valid fields to update."
        
        try:
            set_clause = ', '.join(f"{k} = ?" for k in update_fields.keys())
            values = list(update_fields.values()) + [song_id]
            cursor.execute(f'''
                UPDATE songs SET {set_clause} WHERE id = ?
            ''', values)
            
            self.connection.commit()
            return True, "Song updated successfully."
            
        except sqlite3.Error as e:
            self.connection.rollback()
            return False, f"Update failed: {str(e)}"
    
    def get_song_count_by_artist(self, artist_id: int) -> int:
        """Get the number of songs uploaded by an artist.
        
        Args:
            artist_id: ID of the artist.
            
        Returns:
            Number of songs.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM songs WHERE artist_id = ?", (artist_id,))
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def get_all_artists(self) -> List[Dict[str, Any]]:
        """Get all artists with their song counts.
        
        Returns:
            List of artist dictionaries with profile info and song count.
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at,
                   COALESCE(ap.stage_name, u.username) as display_name,
                   ap.genre, ap.bio,
                   (SELECT COUNT(*) FROM songs WHERE artist_id = u.id) as song_count
            FROM users u
            LEFT JOIN artist_profiles ap ON u.id = ap.user_id
            WHERE u.role = 'artist'
            ORDER BY display_name ASC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
