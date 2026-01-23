"""
Language Manager - Çoklu dil desteği
Türkçe ve İngilizce dil desteği
"""

# Türkçe Metinler
TR = {
    # Header
    'app_title': '⚡ LoL Auto Assistant',
    'subtitle': 'Modern • Hızlı • Güvenilir',
    'connected': 'Bağlı',
    'connecting': 'Bağlanıyor...',
    'not_connected': 'Bağlantı Yok',
    
    # Tabs
    'tab_general': '⚙️ Genel',
    'tab_champions': '🏆 Şampiyonlar',
    'tab_spells': '⏱️ Spell Tracker',
    'tab_stats': '📊 İstatistikler',
    'tab_settings': '⚙️ Ayarlar',
    
    # General Tab
    'match_settings': '🎮 Maç Eşleştirme',
    'auto_accept': 'Otomatik Kabul Et',
    'accept_delay': 'Kabul Gecikmesi: {0} sn',
    'sound_settings': '🔊 Ses Ayarları',
    'sound_notifications': 'Ses Bildirimleri',
    'test': '🔔 Test',
    'start': '▶️ BAŞLAT',
    'stop': '⏹️ DURDUR',
    'hide': '👁️ GİZLE',
    
    # Champions Tab
    'auto_pick': '✨ Otomatik Seçim (Pick)',
    'auto_pick_switch': 'Otomatik Seç',
    'pick_champions_hint': 'Öncelik sırasına göre şampiyonlar (virgülle ayırın):',
    'pick_placeholder': 'Örn: Yasuo, Yone, Zed',
    'auto_ban': '🚫 Otomatik Yasaklama (Ban)',
    'auto_ban_switch': 'Otomatik Yasakla',
    'ban_champions_hint': 'Öncelik sırasına göre yasaklanacak şampiyonlar:',
    'ban_placeholder': 'Örn: Shaco, Teemo, Yuumi',
    'tip_title': '💡 İpucu',
    'tip_text': 'Birden fazla şampiyon ekleyebilirsiniz.\nİlk uygun olan otomatik seçilir/yasaklanır.',
    
    # Spells Tab
    'how_to_use': '⌨️ Nasıl Kullanılır',
    'spell_instructions': (
        'Oyun içinde rakip spell attığını gördüğünde:\n'
        '• Ctrl+1 → Top Flash    • Ctrl+6 → Top Spell2\n'
        '• Ctrl+2 → Jungle Flash  • Ctrl+7 → Jungle Spell2\n'
        '• Ctrl+3 → Mid Flash     • Ctrl+8 → Mid Spell2\n'
        '• Ctrl+4 → ADC Flash    • Ctrl+9 → ADC Spell2\n'
        '• Ctrl+5 → Support Flash • Ctrl+0 → Support Spell2'
    ),
    'hotkey_off': 'Hotkey: Kapalı',
    'hotkey_on': 'Hotkey: Aktif ✓',
    'hotkey_enable': 'Hotkey Aç',
    'hotkey_disable': 'Hotkey Kapat',
    'enemy_cooldowns': '⏱️ Düşman Cooldown\'ları',
    'reset': '🔄 Sıfırla',
    'start_timer': '▶️ Zamanlayıcı Başlat',
    'lane': 'Lane',
    'spell1': 'Spell 1',
    'spell2': 'Spell 2',
    'status': 'Durum',
    'ready': '✅ HAZIR',
    
    # Stats Tab
    'matches_accepted': 'Kabul Edilen Maç',
    'champions_picked': 'Seçilen Şampiyon',
    'champions_banned': 'Yasaklanan Şampiyon',
    'errors': 'Hata',
    'reset_stats': '🔄 İstatistikleri Sıfırla',
    
    # Log
    'log_title': '📋 İşlem Kayıtları',
    'clear': 'Temizle',
    
    # Status Bar
    'ready_status': 'Hazır',
    'bot_running': 'Bot çalışıyor...',
    
    # Tray
    'show': 'Göster',
    'exit': 'Çıkış',
    
    # Messages
    'msg_starting': '🔄 Sistem başlatılıyor...',
    'msg_data_updated': '✅ Veriler güncellendi (v{0}). Hazır.',
    'msg_data_error': '❌ Veri hatası! İnternet bağlantısını kontrol edin.',
    'msg_no_pick_champion': '⚠️ Pick için geçerli şampiyon bulunamadı!',
    'msg_pick_list': '📋 Pick listesi: {0} şampiyon',
    'msg_no_ban_champion': '⚠️ Ban için geçerli şampiyon bulunamadı!',
    'msg_ban_list': '📋 Ban listesi: {0} şampiyon',
    'msg_stats_reset': '📊 İstatistikler sıfırlandı.',
    'msg_hotkeys_disabled': '⌨️ Hotkey\'ler kapatıldı.',
    'msg_hotkeys_enabled': '⌨️ Hotkey\'ler aktif! Ctrl+1-5: Spell1, Ctrl+6-0: Spell2',
    'msg_hotkey_error': '❌ Hotkey başlatılamadı. \'keyboard\' modülü yüklü mü?',
    'msg_spell_used': '🔴 {0} {1} KULLANILDI! ({2}:{3:02d} cooldown)',
    'msg_spell_reset': '🔄 Spell tracker sıfırlandı.',
    'msg_timer_running': '⏱️ Zamanlayıcı zaten çalışıyor.',
    'msg_timer_started': '⏱️ Spell zamanlayıcı başlatıldı.',
    'msg_spell_ready': '✅ {0} {1} HAZIR!',
    
    # Developer
    'developer_info': '👨‍💻 Geliştirici',
    'github': 'GitHub',
    'discord': 'Discord',
    
    # Settings
    'language_settings': '🌐 Dil Ayarları',
    'language': 'Dil',
    'turkish': 'Türkçe',
    'english': 'English',
    'language_change_info': 'Dil değişikliği uygulamayı yeniden başlatmadan sonra etkinleşir.',
}

# İngilizce Metinler
EN = {
    # Header
    'app_title': '⚡ LoL Auto Assistant',
    'subtitle': 'Modern • Fast • Reliable',
    'connected': 'Connected',
    'connecting': 'Connecting...',
    'not_connected': 'Not Connected',
    
    # Tabs
    'tab_general': '⚙️ General',
    'tab_champions': '🏆 Champions',
    'tab_spells': '⏱️ Spell Tracker',
    'tab_stats': '📊 Statistics',
    'tab_settings': '⚙️ Settings',
    
    # General Tab
    'match_settings': '🎮 Match Settings',
    'auto_accept': 'Auto Accept',
    'accept_delay': 'Accept Delay: {0} sec',
    'sound_settings': '🔊 Sound Settings',
    'sound_notifications': 'Sound Notifications',
    'test': '🔔 Test',
    'start': '▶️ START',
    'stop': '⏹️ STOP',
    'hide': '👁️ HIDE',
    
    # Champions Tab
    'auto_pick': '✨ Auto Pick',
    'auto_pick_switch': 'Auto Pick',
    'pick_champions_hint': 'Champions by priority (comma separated):',
    'pick_placeholder': 'Ex: Yasuo, Yone, Zed',
    'auto_ban': '🚫 Auto Ban',
    'auto_ban_switch': 'Auto Ban',
    'ban_champions_hint': 'Champions to ban by priority:',
    'ban_placeholder': 'Ex: Shaco, Teemo, Yuumi',
    'tip_title': '💡 Tip',
    'tip_text': 'You can add multiple champions.\nThe first available one will be picked/banned.',
    
    # Spells Tab
    'how_to_use': '⌨️ How to Use',
    'spell_instructions': (
        'When you see an enemy use a spell in game:\n'
        '• Ctrl+1 → Top Flash    • Ctrl+6 → Top Spell2\n'
        '• Ctrl+2 → Jungle Flash  • Ctrl+7 → Jungle Spell2\n'
        '• Ctrl+3 → Mid Flash     • Ctrl+8 → Mid Spell2\n'
        '• Ctrl+4 → ADC Flash    • Ctrl+9 → ADC Spell2\n'
        '• Ctrl+5 → Support Flash • Ctrl+0 → Support Spell2'
    ),
    'hotkey_off': 'Hotkey: Off',
    'hotkey_on': 'Hotkey: Active ✓',
    'hotkey_enable': 'Enable Hotkey',
    'hotkey_disable': 'Disable Hotkey',
    'enemy_cooldowns': '⏱️ Enemy Cooldowns',
    'reset': '🔄 Reset',
    'start_timer': '▶️ Start Timer',
    'lane': 'Lane',
    'spell1': 'Spell 1',
    'spell2': 'Spell 2',
    'status': 'Status',
    'ready': '✅ READY',
    
    # Stats Tab
    'matches_accepted': 'Matches Accepted',
    'champions_picked': 'Champions Picked',
    'champions_banned': 'Champions Banned',
    'errors': 'Errors',
    'reset_stats': '🔄 Reset Statistics',
    
    # Log
    'log_title': '📋 Activity Log',
    'clear': 'Clear',
    
    # Status Bar
    'ready_status': 'Ready',
    'bot_running': 'Bot is running...',
    
    # Tray
    'show': 'Show',
    'exit': 'Exit',
    
    # Messages
    'msg_starting': '🔄 System starting...',
    'msg_data_updated': '✅ Data updated (v{0}). Ready.',
    'msg_data_error': '❌ Data error! Check your internet connection.',
    'msg_no_pick_champion': '⚠️ No valid champion found for pick!',
    'msg_pick_list': '📋 Pick list: {0} champions',
    'msg_no_ban_champion': '⚠️ No valid champion found for ban!',
    'msg_ban_list': '📋 Ban list: {0} champions',
    'msg_stats_reset': '📊 Statistics reset.',
    'msg_hotkeys_disabled': '⌨️ Hotkeys disabled.',
    'msg_hotkeys_enabled': '⌨️ Hotkeys active! Ctrl+1-5: Spell1, Ctrl+6-0: Spell2',
    'msg_hotkey_error': '❌ Could not start hotkeys. Is \'keyboard\' module installed?',
    'msg_spell_used': '🔴 {0} {1} USED! ({2}:{3:02d} cooldown)',
    'msg_spell_reset': '🔄 Spell tracker reset.',
    'msg_timer_running': '⏱️ Timer is already running.',
    'msg_timer_started': '⏱️ Spell timer started.',
    'msg_spell_ready': '✅ {0} {1} READY!',
    
    # Developer
    'developer_info': '👨‍💻 Developer',
    'github': 'GitHub',
    'discord': 'Discord',
    
    # Settings
    'language_settings': '🌐 Language Settings',
    'language': 'Language',
    'turkish': 'Türkçe',
    'english': 'English',
    'language_change_info': 'Language change will take effect after restarting the app.',
}

# Dil haritalama
LANGUAGES = {
    'tr': TR,
    'en': EN
}

class LanguageManager:
    """Dil yönetimi sınıfı"""
    
    def __init__(self):
        self.current_lang = 'en'
        self._strings = LANGUAGES['en']
    
    def set_language(self, lang_code):
        """Dili değiştir"""
        if lang_code in LANGUAGES:
            self.current_lang = lang_code
            self._strings = LANGUAGES[lang_code]
    
    def get(self, key, *args):
        """Çeviri al"""
        text = self._strings.get(key, key)
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError):
                return text
        return text
    
    def get_language(self):
        """Mevcut dil kodunu döndür"""
        return self.current_lang

# Global instance
_lang_manager = None

def get_language_manager():
    """Global dil yöneticisini al"""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager

def t(key, *args):
    """Kısa çeviri fonksiyonu"""
    return get_language_manager().get(key, *args)
