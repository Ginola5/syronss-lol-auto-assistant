"""
Spell Tracker - Düşman Summoner Spell Takibi
Global hotkey ile spell kullanımını işaretleme ve cooldown takibi
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable

# Summoner spell cooldowns (saniye cinsinden)
SPELL_COOLDOWNS = {
    'flash': 300,       # 5 dakika
    'ignite': 180,      # 3 dakika
    'heal': 240,        # 4 dakika
    'barrier': 180,     # 3 dakika
    'exhaust': 210,     # 3.5 dakika
    'ghost': 210,       # 3.5 dakika
    'cleanse': 210,     # 3.5 dakika
    'teleport': 360,    # 6 dakika
    'smite': 90,        # 1.5 dakika (15 saniye charge)
}

# Türkçe spell isimleri
SPELL_NAMES_TR = {
    'flash': 'Flash',
    'ignite': 'Tutuştur',
    'heal': 'İyileştir',
    'barrier': 'Bariyer',
    'exhaust': 'Bitkinlik',
    'ghost': 'Hayalet',
    'cleanse': 'Arındır',
    'teleport': 'Işınlan',
    'smite': 'Çarp',
}

# Lane/Pozisyon isimleri
LANE_NAMES = {
    1: 'Top',
    2: 'Jungle', 
    3: 'Mid',
    4: 'ADC',
    5: 'Support'
}

LANE_NAMES_TR = {
    1: 'Üst',
    2: 'Orman',
    3: 'Orta',
    4: 'ADC',
    5: 'Destek'
}


class EnemySpellTracker:
    """
    Düşman spell kullanımını takip eden sınıf.
    Her düşman için 2 spell slot'u var (D ve F).
    """
    
    def __init__(self, on_update: Optional[Callable] = None, on_ready: Optional[Callable] = None):
        """
        on_update: Her güncelleme olduğunda çağrılacak callback
        on_ready: Bir spell hazır olduğunda çağrılacak callback (lane, spell_name)
        """
        self.on_update = on_update
        self.on_ready = on_ready
        
        # Her lane için spell durumu
        self._tracked_spells: Dict[int, dict] = {}
        
        # Default spell assignments (tahmin)
        self._default_spells = {
            1: {'spell1': 'flash', 'spell2': 'teleport'},    # Top
            2: {'spell1': 'flash', 'spell2': 'smite'},       # Jungle
            3: {'spell1': 'flash', 'spell2': 'ignite'},      # Mid
            4: {'spell1': 'flash', 'spell2': 'heal'},        # ADC
            5: {'spell1': 'flash', 'spell2': 'ignite'},      # Support
        }
        
        # Background timer thread
        self._running = False
        self._timer_thread = None
        self._lock = threading.RLock()  # RLock kullanıyoruz, reentrant olsun
        
        # Initialize tracking for all lanes
        self._init_spells()
    
    def _init_spells(self):
        """Spell'leri başlat"""
        self._tracked_spells = {}
        for lane_id in range(1, 6):
            self._tracked_spells[lane_id] = {
                'spell1': {
                    'name': self._default_spells[lane_id]['spell1'],
                    'used_at': None,
                    'ready_at': None,
                    'notified': False
                },
                'spell2': {
                    'name': self._default_spells[lane_id]['spell2'],
                    'used_at': None,
                    'ready_at': None,
                    'notified': False
                }
            }
    
    def reset(self):
        """Tüm takibi sıfırla"""
        with self._lock:
            self._init_spells()
        self._notify_update()
    
    def set_spell(self, lane_id: int, slot: str, spell_name: str):
        """
        Bir lane için spell ayarla.
        lane_id: 1-5 (Top, Jungle, Mid, ADC, Support)
        slot: 'spell1' veya 'spell2'
        spell_name: 'flash', 'ignite', etc.
        """
        spell_name = spell_name.lower()
        if spell_name not in SPELL_COOLDOWNS:
            return False
        
        with self._lock:
            if lane_id in self._tracked_spells and slot in self._tracked_spells[lane_id]:
                self._tracked_spells[lane_id][slot]['name'] = spell_name
                self._tracked_spells[lane_id][slot]['used_at'] = None
                self._tracked_spells[lane_id][slot]['ready_at'] = None
                self._tracked_spells[lane_id][slot]['notified'] = False
        
        self._notify_update()
        return True
    
    def mark_used(self, lane_id: int, slot: str = 'spell1'):
        """
        Bir spell'in kullanıldığını işaretle.
        lane_id: 1-5
        slot: 'spell1' veya 'spell2' (default: spell1 = genellikle flash)
        """
        with self._lock:
            if lane_id not in self._tracked_spells:
                return None
            
            spell_data = self._tracked_spells[lane_id].get(slot)
            if not spell_data:
                return None
            
            spell_name = spell_data['name']
            cooldown = SPELL_COOLDOWNS.get(spell_name, 300)
            
            now = datetime.now()
            spell_data['used_at'] = now
            spell_data['ready_at'] = now + timedelta(seconds=cooldown)
            spell_data['notified'] = False
            
            result = {
                'lane': lane_id,
                'lane_name': LANE_NAMES.get(lane_id, f'Lane {lane_id}'),
                'spell': spell_name,
                'spell_tr': SPELL_NAMES_TR.get(spell_name, spell_name),
                'cooldown': cooldown,
                'ready_at': spell_data['ready_at']
            }
        
        self._notify_update()
        return result
    
    def _get_remaining_internal(self, spell_data) -> Optional[int]:
        """İç kullanım için kalan süreyi hesapla (lock olmadan)"""
        if not spell_data or not spell_data.get('ready_at'):
            return None
        remaining = (spell_data['ready_at'] - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def get_remaining_time(self, lane_id: int, slot: str = 'spell1') -> Optional[int]:
        """
        Kalan süreyi saniye olarak döndür.
        None = hiç kullanılmadı veya hazır
        """
        with self._lock:
            if lane_id not in self._tracked_spells:
                return None
            spell_data = self._tracked_spells[lane_id].get(slot)
            return self._get_remaining_internal(spell_data)
    
    def is_ready(self, lane_id: int, slot: str = 'spell1') -> bool:
        """Spell hazır mı?"""
        remaining = self.get_remaining_time(lane_id, slot)
        return remaining is None or remaining <= 0
    
    def get_status(self, lane_id: int, slot: str = 'spell1') -> dict:
        """Bir spell'in durumunu döndür"""
        with self._lock:
            if lane_id not in self._tracked_spells:
                return {'name': 'unknown', 'name_tr': '', 'remaining': None, 'is_ready': True}
            
            spell_data = self._tracked_spells[lane_id].get(slot, {})
            remaining = self._get_remaining_internal(spell_data)
            
            return {
                'name': spell_data.get('name', 'unknown'),
                'name_tr': SPELL_NAMES_TR.get(spell_data.get('name', ''), spell_data.get('name', '')),
                'remaining': remaining,
                'is_ready': remaining is None or remaining <= 0,
                'used_at': spell_data.get('used_at'),
                'ready_at': spell_data.get('ready_at')
            }
    
    def get_all_status(self) -> dict:
        """Tüm lane'lerin durumunu döndür"""
        result = {}
        with self._lock:
            for lane_id in range(1, 6):
                spell1_data = self._tracked_spells[lane_id].get('spell1', {})
                spell2_data = self._tracked_spells[lane_id].get('spell2', {})
                
                remaining1 = self._get_remaining_internal(spell1_data)
                remaining2 = self._get_remaining_internal(spell2_data)
                
                result[lane_id] = {
                    'lane_name': LANE_NAMES.get(lane_id),
                    'lane_name_tr': LANE_NAMES_TR.get(lane_id),
                    'spell1': {
                        'name': spell1_data.get('name', 'unknown'),
                        'remaining': remaining1,
                        'is_ready': remaining1 is None or remaining1 <= 0
                    },
                    'spell2': {
                        'name': spell2_data.get('name', 'unknown'),
                        'remaining': remaining2,
                        'is_ready': remaining2 is None or remaining2 <= 0
                    }
                }
        return result
    
    def format_time(self, seconds: Optional[int]) -> str:
        """Süreyi MM:SS formatına çevir"""
        if seconds is None or seconds <= 0:
            return "HAZIR"
        
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    def start_timer(self):
        """Arka plan zamanlayıcısını başlat"""
        if self._running:
            return
        
        self._running = True
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()
    
    def stop_timer(self):
        """Zamanlayıcıyı durdur"""
        self._running = False
        if self._timer_thread:
            try:
                self._timer_thread.join(timeout=2)
            except:
                pass
            self._timer_thread = None
    
    def _timer_loop(self):
        """Her saniye durumu kontrol et ve hazır olan spell'leri bildir"""
        while self._running:
            try:
                ready_notifications = []
                
                with self._lock:
                    for lane_id in range(1, 6):
                        for slot in ['spell1', 'spell2']:
                            spell_data = self._tracked_spells[lane_id].get(slot, {})
                            
                            # Eğer kullanılmış ve henüz bildirilmemişse
                            if spell_data.get('ready_at') and not spell_data.get('notified'):
                                remaining = self._get_remaining_internal(spell_data)
                                
                                if remaining is not None and remaining <= 0:
                                    spell_data['notified'] = True
                                    spell_name = spell_data.get('name', 'unknown')
                                    
                                    # Callback için hazırla (lock dışında çağıracağız)
                                    ready_notifications.append((
                                        lane_id, 
                                        LANE_NAMES.get(lane_id),
                                        spell_name,
                                        SPELL_NAMES_TR.get(spell_name, spell_name)
                                    ))
                
                # Callback'leri lock dışında çağır
                for notification in ready_notifications:
                    if self.on_ready:
                        try:
                            self.on_ready(*notification)
                        except Exception as e:
                            print(f"on_ready callback error: {e}")
                
                # UI güncelle
                self._notify_update()
                
            except Exception as e:
                print(f"Timer error: {e}")
            
            time.sleep(1)
    
    def _notify_update(self):
        """UI güncellemesi için callback çağır"""
        if self.on_update:
            try:
                self.on_update()
            except Exception:
                pass


class HotkeyManager:
    """Global hotkey yöneticisi"""
    
    def __init__(self):
        self._keyboard = None
        self._hotkeys = {}
        self._enabled = False
        self._lock = threading.Lock()
    
    def start(self, hotkey_callbacks: dict):
        """
        Hotkey'leri başlat.
        hotkey_callbacks: {'ctrl+1': callback_func, ...}
        """
        with self._lock:
            if self._enabled:
                return True
            
            try:
                import keyboard
                self._keyboard = keyboard
                
                for hotkey, callback in hotkey_callbacks.items():
                    try:
                        keyboard.add_hotkey(hotkey, callback, suppress=False)
                        self._hotkeys[hotkey] = callback
                    except Exception as e:
                        print(f"Hotkey ekleme hatası ({hotkey}): {e}")
                
                self._enabled = True
                return True
            except ImportError:
                print("keyboard modülü yüklenemedi. 'pip install keyboard' komutunu çalıştırın.")
                return False
            except Exception as e:
                print(f"Hotkey hatası: {e}")
                return False
    
    def stop(self):
        """Tüm hotkey'leri kaldır"""
        with self._lock:
            if not self._enabled:
                return
            
            if self._keyboard:
                try:
                    for hotkey in list(self._hotkeys.keys()):
                        try:
                            self._keyboard.remove_hotkey(hotkey)
                        except:
                            pass
                    self._hotkeys.clear()
                except Exception:
                    pass
            
            self._enabled = False
    
    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled
