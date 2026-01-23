"""
Settings Manager - JSON tabanlı ayar yönetimi
Thread-safe ayar kaydetme/yükleme
"""

import json
import os
import threading
from pathlib import Path

class SettingsManager:
    """Thread-safe settings manager with JSON persistence"""
    
    DEFAULT_SETTINGS = {
        # Auto Accept
        'enable_auto_accept': True,
        'accept_delay': 0,
        
        # Auto Ban
        'enable_auto_ban': False,
        'ban_champions': [],  # List of champion names for priority ban
        
        # Auto Pick
        'enable_auto_pick': False,
        'pick_champions': [],  # List of champion names for priority pick
        
        # Sound
        'enable_sound': True,
        'sound_volume': 100,
        
        # Hotkeys
        'hotkey_toggle': 'ctrl+shift+l',
        'enable_hotkeys': False,
        
        # Statistics
        'stats_matches_accepted': 0,
        'stats_champions_banned': 0,
        'stats_champions_picked': 0,
        
        # UI
        'window_geometry': '550x750',
        'always_on_top': False,
        
        # Advanced
        'reconnect_interval': 2,
        'polling_interval': 1,
        
        # Language
        'language': 'en',  # 'tr' or 'en'
    }
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            # Default to user's AppData
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = Path(appdata) / 'LoLAutoAssistant'
        else:
            config_dir = Path(config_dir)
        
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / 'settings.json'
        self.log_file = config_dir / 'app.log'
        
        self._settings = dict(self.DEFAULT_SETTINGS)
        self._lock = threading.RLock()
        
        self.load()
    
    def load(self):
        """Load settings from JSON file"""
        with self._lock:
            try:
                if self.config_file.exists():
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                        # Merge with defaults (keeps new keys from defaults)
                        self._settings = {**self.DEFAULT_SETTINGS, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
                self._settings = dict(self.DEFAULT_SETTINGS)
    
    def save(self):
        """Save current settings to JSON file"""
        with self._lock:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._settings, f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value (thread-safe)"""
        with self._lock:
            return self._settings.get(key, default)
    
    def set(self, key, value, auto_save=True):
        """Set a setting value (thread-safe)"""
        with self._lock:
            self._settings[key] = value
            if auto_save:
                self.save()
    
    def update(self, updates: dict, auto_save=True):
        """Update multiple settings at once (thread-safe)"""
        with self._lock:
            self._settings.update(updates)
            if auto_save:
                self.save()
    
    def get_all(self):
        """Get a copy of all settings"""
        with self._lock:
            return dict(self._settings)
    
    def reset(self):
        """Reset all settings to defaults"""
        with self._lock:
            self._settings = dict(self.DEFAULT_SETTINGS)
            self.save()
    
    def increment_stat(self, stat_key):
        """Increment a statistics counter"""
        with self._lock:
            if stat_key in self._settings:
                self._settings[stat_key] += 1
                self.save()


# Global settings instance
_settings_instance = None

def get_settings():
    """Get the global settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
