"""
Sound System - Windows ses bildirimleri
Maç bulunduğunda ve diğer olaylarda ses çalar
"""

import threading
import winsound

class SoundManager:
    """Manages sound notifications"""
    
    # Windows system sounds
    SOUND_MATCH_FOUND = "SystemExclamation"
    SOUND_SUCCESS = "SystemAsterisk"
    SOUND_ERROR = "SystemHand"
    SOUND_NOTIFICATION = "SystemNotification"
    
    # Custom beep frequencies
    BEEP_MATCH_FOUND = [(800, 200), (1000, 200), (1200, 300)]
    BEEP_SUCCESS = [(600, 150), (800, 150)]
    BEEP_ERROR = [(400, 300)]
    
    def __init__(self):
        self.enabled = True
        self._lock = threading.Lock()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sounds"""
        with self._lock:
            self.enabled = enabled
    
    def _play_async(self, sound_func, *args):
        """Play sound in background thread"""
        if not self.enabled:
            return
        threading.Thread(target=sound_func, args=args, daemon=True).start()
    
    def play_system_sound(self, sound_name: str):
        """Play a Windows system sound"""
        def _play():
            try:
                winsound.PlaySound(sound_name, winsound.SND_ALIAS | winsound.SND_ASYNC)
            except Exception:
                pass
        self._play_async(_play)
    
    def play_beep_sequence(self, sequence: list):
        """Play a sequence of beeps [(frequency, duration), ...]"""
        def _play():
            try:
                for freq, duration in sequence:
                    winsound.Beep(freq, duration)
            except Exception:
                pass
        self._play_async(_play)
    
    def play_match_found(self):
        """Play sound when match is found"""
        self.play_beep_sequence(self.BEEP_MATCH_FOUND)
    
    def play_success(self):
        """Play success sound"""
        self.play_beep_sequence(self.BEEP_SUCCESS)
    
    def play_error(self):
        """Play error sound"""
        self.play_beep_sequence(self.BEEP_ERROR)
    
    def play_notification(self):
        """Play notification sound"""
        self.play_system_sound(self.SOUND_NOTIFICATION)


# Global sound manager instance
_sound_instance = None

def get_sound_manager():
    """Get the global sound manager instance"""
    global _sound_instance
    if _sound_instance is None:
        _sound_instance = SoundManager()
    return _sound_instance
