"""
LoL Auto Assistant - Modern UI
Gelişmiş, şık ve tam özellikli League of Legends otomatik kabul/pick/ban aracı
"""

import customtkinter as ctk
import threading
import pystray
from PIL import Image, ImageDraw, ImageTk
import sys
import os
import io
import requests
from typing import Optional

# Import modules
from lcu_connector import LCUConnector, ConnectionState
from bot_logic import LeagueBot
from utils import (
    get_latest_version, get_champion_map, normalize_name,
    get_champion_names, get_champion_image_url, search_champions,
    find_champion_by_name, get_champion_list, get_cached_version
)
from settings import get_settings
from languages import get_language_manager, t
from sounds import get_sound_manager
from spell_tracker import EnemySpellTracker, HotkeyManager, SPELL_COOLDOWNS, SPELL_NAMES_TR, LANE_NAMES

# Set Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Colors
COLORS = {
    'bg_dark': '#0f0f1a',
    'bg_card': '#1a1a2e',
    'bg_card_hover': '#252540',
    'accent': '#6366f1',
    'accent_hover': '#818cf8',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'text': '#f8fafc',
    'text_muted': '#94a3b8',
    'border': '#334155'
}

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LoL Auto Assistant Pro")
        self.geometry("580x850")
        self.minsize(520, 750)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Initialize components
        self.settings = get_settings()
        
        # Initialize language system
        self.lang_manager = get_language_manager()
        saved_lang = self.settings.get('language', 'tr')
        self.lang_manager.set_language(saved_lang)
        
        self.sound_manager = get_sound_manager()
        self.connector = LCUConnector()
        self.bot = LeagueBot(
            self.connector, 
            self.log_message, 
            self.settings,
            self.sound_manager
        )
        self.bot_thread = None
        self.champion_map = {}
        self.champion_names = []
        self.version = None
        
        # Spell Tracker
        self.spell_tracker = EnemySpellTracker(
            on_update=self._update_spell_tracker_ui,
            on_ready=self._on_spell_ready
        )
        self.hotkey_manager = HotkeyManager()
        self._spell_tracker_labels = {}
        
        # Connection state callback
        self.connector.add_state_callback(self.on_connection_state_change)
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._create_header()
        self._create_tabs()
        self._create_log_section()
        self._create_status_bar()

        # System Tray
        self.tray_icon = None
        self.protocol('WM_DELETE_WINDOW', self.on_closing)
        
        # Load saved settings
        self._load_settings()
        
        # Initial data load
        self._load_data()

    # ========== HEADER ==========
    def _create_header(self):
        self.header_frame = ctk.CTkFrame(
            self, 
            corner_radius=0, 
            fg_color=COLORS['bg_card'],
            height=80
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo/Title area
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        self.title_label = ctk.CTkLabel(
            title_frame, 
            text=t('app_title'),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text']
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text=t('subtitle'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        )
        self.subtitle_label.pack(anchor="w")
        
        # Connection Status
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20)
        
        self.connection_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['error']
        )
        self.connection_indicator.pack(side="left", padx=(0, 5))
        
        self.connection_label = ctk.CTkLabel(
            self.status_frame,
            text=t('not_connected'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        )
        self.connection_label.pack(side="left")

    # ========== TABS ==========
    def _create_tabs(self):
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS['bg_dark'],
            segmented_button_fg_color=COLORS['bg_card'],
            segmented_button_selected_color=COLORS['accent'],
            segmented_button_unselected_color=COLORS['bg_card'],
            text_color=COLORS['text']
        )
        self.tabview.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="nsew")
        
        # Add tabs
        self.tab_general = self.tabview.add(t('tab_general'))
        self.tab_champions = self.tabview.add(t('tab_champions'))
        self.tab_spells = self.tabview.add(t('tab_spells'))
        self.tab_stats = self.tabview.add(t('tab_stats'))
        self.tab_settings = self.tabview.add(t('tab_settings'))
        
        self._create_general_tab()
        self._create_champions_tab()
        self._create_spells_tab()
        self._create_stats_tab()
        self._create_settings_tab()

    def _create_general_tab(self):
        self.tab_general.grid_columnconfigure(0, weight=1)
        
        # ====== AUTO ACCEPT SECTION ======
        accept_card = self._create_card(self.tab_general, t('match_settings'))
        accept_card.pack(fill="x", padx=5, pady=5)
        
        # Auto Accept Switch
        accept_row = ctk.CTkFrame(accept_card, fg_color="transparent")
        accept_row.pack(fill="x", padx=15, pady=5)
        
        self.accept_var = ctk.BooleanVar(value=True)
        self.accept_switch = ctk.CTkSwitch(
            accept_row,
            text=t('auto_accept'),
            variable=self.accept_var,
            command=self._on_settings_change,
            progress_color=COLORS['success'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        self.accept_switch.pack(side="left")
        
        # Delay Section
        delay_frame = ctk.CTkFrame(accept_card, fg_color="transparent")
        delay_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.delay_label = ctk.CTkLabel(
            delay_frame,
            text=t('accept_delay', 0),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        )
        self.delay_label.pack(anchor="w")
        
        self.delay_slider = ctk.CTkSlider(
            delay_frame,
            from_=0, to=10,
            number_of_steps=10,
            command=self._update_delay_label,
            progress_color=COLORS['accent'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        self.delay_slider.set(0)
        self.delay_slider.pack(fill="x", pady=(5, 0))
        
        # ====== SOUND SECTION ======
        sound_card = self._create_card(self.tab_general, t('sound_settings'))
        sound_card.pack(fill="x", padx=5, pady=5)
        
        sound_row = ctk.CTkFrame(sound_card, fg_color="transparent")
        sound_row.pack(fill="x", padx=15, pady=10)
        
        self.sound_var = ctk.BooleanVar(value=True)
        self.sound_switch = ctk.CTkSwitch(
            sound_row,
            text=t('sound_notifications'),
            variable=self.sound_var,
            command=self._on_sound_toggle,
            progress_color=COLORS['success'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        self.sound_switch.pack(side="left")
        
        # Test sound button
        self.test_sound_btn = ctk.CTkButton(
            sound_row,
            text=t('test'),
            width=70,
            height=28,
            command=self._test_sound,
            fg_color=COLORS['bg_card_hover'],
            hover_color=COLORS['accent']
        )
        self.test_sound_btn.pack(side="right")
        
        # ====== CONTROLS ======
        controls_frame = ctk.CTkFrame(self.tab_general, fg_color="transparent")
        controls_frame.pack(fill="x", padx=5, pady=15)
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.start_btn = ctk.CTkButton(
            controls_frame,
            text=t('start'),
            command=self._start_bot,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color="#0d9465"
        )
        self.start_btn.grid(row=0, column=0, padx=3, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text=t('stop'),
            command=self._stop_bot,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['error'],
            hover_color="#dc2626",
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=3, sticky="ew")
        
        self.hide_btn = ctk.CTkButton(
            controls_frame,
            text=t('hide'),
            command=self._hide_window,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_card_hover']
        )
        self.hide_btn.grid(row=0, column=2, padx=3, sticky="ew")

    def _create_champions_tab(self):
        self.tab_champions.grid_columnconfigure(0, weight=1)
        
        # ====== AUTO PICK SECTION ======
        pick_card = self._create_card(self.tab_champions, t('auto_pick'))
        pick_card.pack(fill="x", padx=5, pady=5)
        
        # Pick Switch
        pick_row = ctk.CTkFrame(pick_card, fg_color="transparent")
        pick_row.pack(fill="x", padx=15, pady=5)
        
        self.pick_var = ctk.BooleanVar(value=False)
        self.pick_switch = ctk.CTkSwitch(
            pick_row,
            text=t('auto_pick_switch'),
            variable=self.pick_var,
            command=self._on_settings_change,
            progress_color=COLORS['success'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        self.pick_switch.pack(side="left")
        
        # Pick Champions List
        pick_list_frame = ctk.CTkFrame(pick_card, fg_color="transparent")
        pick_list_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            pick_list_frame,
            text=t('pick_champions_hint'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        self.pick_entry = ctk.CTkEntry(
            pick_list_frame,
            placeholder_text=t('pick_placeholder'),
            height=38,
            fg_color=COLORS['bg_dark'],
            border_color=COLORS['border']
        )
        self.pick_entry.pack(fill="x", pady=(5, 0))
        self.pick_entry.bind("<FocusOut>", lambda e: self._on_settings_change())
        
        # ====== AUTO BAN SECTION ======
        ban_card = self._create_card(self.tab_champions, t('auto_ban'))
        ban_card.pack(fill="x", padx=5, pady=5)
        
        # Ban Switch
        ban_row = ctk.CTkFrame(ban_card, fg_color="transparent")
        ban_row.pack(fill="x", padx=15, pady=5)
        
        self.ban_var = ctk.BooleanVar(value=False)
        self.ban_switch = ctk.CTkSwitch(
            ban_row,
            text=t('auto_ban_switch'),
            variable=self.ban_var,
            command=self._on_settings_change,
            progress_color=COLORS['success'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover']
        )
        self.ban_switch.pack(side="left")
        
        # Ban Champions List
        ban_list_frame = ctk.CTkFrame(ban_card, fg_color="transparent")
        ban_list_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            ban_list_frame,
            text=t('ban_champions_hint'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        self.ban_entry = ctk.CTkEntry(
            ban_list_frame,
            placeholder_text=t('ban_placeholder'),
            height=38,
            fg_color=COLORS['bg_dark'],
            border_color=COLORS['border']
        )
        self.ban_entry.pack(fill="x", pady=(5, 0))
        self.ban_entry.bind("<FocusOut>", lambda e: self._on_settings_change())
        
        # ====== INFO BOX ======
        info_frame = ctk.CTkFrame(
            self.tab_champions,
            fg_color=COLORS['bg_card'],
            corner_radius=10
        )
        info_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=t('tip_title'),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['accent']
        ).pack(anchor="w", padx=15, pady=(10, 0))
        
        ctk.CTkLabel(
            info_frame,
            text=t('tip_text'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(5, 10))

    def _create_spells_tab(self):
        """Düşman spell tracker sekmesi"""
        self.tab_spells.grid_columnconfigure(0, weight=1)
        
        # ====== INSTRUCTIONS ======
        info_card = self._create_card(self.tab_spells, t('how_to_use'))
        info_card.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            info_card,
            text=t('spell_instructions'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted'],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(5, 10))
        
        # ====== HOTKEY STATUS ======
        hotkey_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        hotkey_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.hotkey_status_label = ctk.CTkLabel(
            hotkey_frame,
            text=t('hotkey_off'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['warning']
        )
        self.hotkey_status_label.pack(side="left")
        
        self.hotkey_toggle_btn = ctk.CTkButton(
            hotkey_frame,
            text=t('hotkey_enable'),
            width=100,
            height=28,
            command=self._toggle_hotkeys,
            fg_color=COLORS['success'],
            hover_color="#0d9465"
        )
        self.hotkey_toggle_btn.pack(side="right")
        
        # ====== SPELL TRACKER CARDS ======
        tracker_card = self._create_card(self.tab_spells, t('enemy_cooldowns'))
        tracker_card.pack(fill="x", padx=5, pady=5)
        
        # Header row
        header_frame = ctk.CTkFrame(tracker_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(5, 0))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        headers = [t('lane'), t('spell1'), t('status'), t('spell2'), t('status')]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=h,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS['text_muted']
            ).grid(row=0, column=i, padx=2, sticky="ew")
        
        # Lane rows
        spell_options = list(SPELL_COOLDOWNS.keys())
        self._spell_dropdowns = {}
        
        for lane_id in range(1, 6):
            lane_frame = ctk.CTkFrame(tracker_card, fg_color=COLORS['bg_dark'], corner_radius=8)
            lane_frame.pack(fill="x", padx=10, pady=3)
            lane_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            lane_name = LANE_NAMES.get(lane_id, f"Lane {lane_id}")
            
            # Lane name
            ctk.CTkLabel(
                lane_frame,
                text=f"[{lane_id}] {lane_name}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text']
            ).grid(row=0, column=0, padx=5, pady=8, sticky="w")
            
            # Spell 1 dropdown
            spell1_var = ctk.StringVar(value="flash")
            spell1_dropdown = ctk.CTkComboBox(
                lane_frame,
                values=spell_options,
                variable=spell1_var,
                width=85,
                height=28,
                fg_color=COLORS['bg_card'],
                command=lambda v, lid=lane_id: self._on_spell_dropdown_change(lid, 'spell1', v)
            )
            spell1_dropdown.grid(row=0, column=1, padx=2, pady=5)
            self._spell_dropdowns[(lane_id, 'spell1')] = spell1_var
            
            # Spell 1 status
            spell1_status = ctk.CTkLabel(
                lane_frame,
                text="—",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
                width=60
            )
            spell1_status.grid(row=0, column=2, padx=2)
            self._spell_tracker_labels[(lane_id, 'spell1')] = spell1_status
            
            # Spell 2 dropdown
            default_spell2 = {1: 'teleport', 2: 'smite', 3: 'ignite', 4: 'heal', 5: 'ignite'}
            spell2_var = ctk.StringVar(value=default_spell2.get(lane_id, 'ignite'))
            spell2_dropdown = ctk.CTkComboBox(
                lane_frame,
                values=spell_options,
                variable=spell2_var,
                width=85,
                height=28,
                fg_color=COLORS['bg_card'],
                command=lambda v, lid=lane_id: self._on_spell_dropdown_change(lid, 'spell2', v)
            )
            spell2_dropdown.grid(row=0, column=3, padx=2, pady=5)
            self._spell_dropdowns[(lane_id, 'spell2')] = spell2_var
            
            # Spell 2 status
            spell2_status = ctk.CTkLabel(
                lane_frame,
                text="—",
                font=ctk.CTkFont(size=12),
                text_color=COLORS['text_muted'],
                width=60
            )
            spell2_status.grid(row=0, column=4, padx=2)
            self._spell_tracker_labels[(lane_id, 'spell2')] = spell2_status
        
        # ====== CONTROL BUTTONS ======
        btn_frame = ctk.CTkFrame(self.tab_spells, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text=t('reset'),
            width=100,
            height=36,
            command=self._reset_spell_tracker,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_card_hover']
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text=t('start_timer'),
            width=150,
            height=36,
            command=self._start_spell_timer,
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover']
        ).pack(side="right", padx=5)

    def _on_spell_dropdown_change(self, lane_id, slot, value):
        """Spell dropdown değiştiğinde çağrılır"""
        self.spell_tracker.set_spell(lane_id, slot, value)
    
    def _toggle_hotkeys(self):
        """Hotkey'leri aç/kapat"""
        if self.hotkey_manager.is_enabled():
            self.hotkey_manager.stop()
            self.hotkey_status_label.configure(text=t('hotkey_off'), text_color=COLORS['warning'])
            self.hotkey_toggle_btn.configure(text=t('hotkey_enable'), fg_color=COLORS['success'])
            self.log_message(t('msg_hotkeys_disabled'))
        else:
            # Define hotkeys
            hotkeys = {
                'ctrl+1': lambda: self._mark_spell_used(1, 'spell1'),
                'ctrl+2': lambda: self._mark_spell_used(2, 'spell1'),
                'ctrl+3': lambda: self._mark_spell_used(3, 'spell1'),
                'ctrl+4': lambda: self._mark_spell_used(4, 'spell1'),
                'ctrl+5': lambda: self._mark_spell_used(5, 'spell1'),
                'ctrl+6': lambda: self._mark_spell_used(1, 'spell2'),
                'ctrl+7': lambda: self._mark_spell_used(2, 'spell2'),
                'ctrl+8': lambda: self._mark_spell_used(3, 'spell2'),
                'ctrl+9': lambda: self._mark_spell_used(4, 'spell2'),
                'ctrl+0': lambda: self._mark_spell_used(5, 'spell2'),
            }
            
            if self.hotkey_manager.start(hotkeys):
                self.hotkey_status_label.configure(text=t('hotkey_on'), text_color=COLORS['success'])
                self.hotkey_toggle_btn.configure(text=t('hotkey_disable'), fg_color=COLORS['error'])
                self.log_message(t('msg_hotkeys_enabled'))
            else:
                self.log_message(t('msg_hotkey_error'))
    
    def _mark_spell_used(self, lane_id, slot):
        """Bir spell kullanıldığını işaretle (hotkey'den çağrılır)"""
        result = self.spell_tracker.mark_used(lane_id, slot)
        if result:
            lane_name = result['lane_name']
            spell_tr = result['spell_tr']
            cooldown = result['cooldown']
            mins = cooldown // 60
            secs = cooldown % 60
            self.log_message(f"🔴 {lane_name} {spell_tr} KULLANILDI! ({mins}:{secs:02d} cooldown)")
            
            # Ses bildirimi
            if self.sound_manager:
                self.sound_manager.play_notification()
    
    def _reset_spell_tracker(self):
        """Tüm spell tracker'ı sıfırla"""
        self.spell_tracker.reset()
        self._do_update_spell_ui()
        self.log_message(t('msg_spell_reset'))
    
    def _start_spell_timer(self):
        """Zamanlayıcıyı başlat"""
        if hasattr(self, '_spell_timer_running') and self._spell_timer_running:
            self.log_message(t('msg_timer_running'))
            return
        
        self._spell_timer_running = True
        self.spell_tracker.start_timer()
        self._start_ui_update_loop()
        self.log_message(t('msg_timer_started'))
    
    def _start_ui_update_loop(self):
        """Tkinter after ile UI güncelleme döngüsü"""
        if not hasattr(self, '_spell_timer_running') or not self._spell_timer_running:
            return
        
        try:
            self._do_update_spell_ui()
        except Exception as e:
            print(f"UI update error: {e}")
        
        # Her 1 saniyede bir güncelle (after kullanarak)
        if self._spell_timer_running:
            self.after(1000, self._start_ui_update_loop)
    
    def _update_spell_tracker_ui(self):
        """UI'ı güncelle (timer callback) - artık kullanılmıyor, after döngüsü var"""
        pass
    
    def _do_update_spell_ui(self):
        """Ana thread'de UI güncelle"""
        try:
            if not self.winfo_exists():
                return
            
            for lane_id in range(1, 6):
                for slot in ['spell1', 'spell2']:
                    label = self._spell_tracker_labels.get((lane_id, slot))
                    if label and label.winfo_exists():
                        try:
                            status = self.spell_tracker.get_status(lane_id, slot)
                            remaining = status.get('remaining')
                            if remaining is None:
                                label.configure(text="—", text_color=COLORS['text_muted'])
                            elif remaining <= 0:
                                label.configure(text=t('ready'), text_color=COLORS['success'])
                            else:
                                time_str = self.spell_tracker.format_time(remaining)
                                label.configure(text=f"🔴 {time_str}", text_color=COLORS['error'])
                        except Exception:
                            pass
        except Exception as e:
            print(f"Update UI error: {e}")
    
    def _on_spell_ready(self, lane_id, lane_name, spell_name, spell_tr):
        """Bir spell hazır olduğunda çağrılır"""
        try:
            self.after(0, lambda: self._notify_spell_ready(lane_name, spell_tr))
        except Exception:
            pass
    
    def _notify_spell_ready(self, lane_name, spell_tr):
        """Ana thread'de spell hazır bildirimi"""
        self.log_message(f"✅ {lane_name} {spell_tr} HAZIR!")
        if self.sound_manager:
            self.sound_manager.play_success()

    def _create_stats_tab(self):
        self.tab_stats.grid_columnconfigure(0, weight=1)
        
        # Stats Cards
        stats_frame = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        stats_frame.pack(fill="x", padx=5, pady=10)
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Matches Accepted
        self.stat_matches_card = self._create_stat_card(
            stats_frame, "🎮", t('matches_accepted'), "0"
        )
        self.stat_matches_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Champions Picked
        self.stat_picks_card = self._create_stat_card(
            stats_frame, "✨", t('champions_picked'), "0"
        )
        self.stat_picks_card.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Champions Banned
        self.stat_bans_card = self._create_stat_card(
            stats_frame, "🚫", t('champions_banned'), "0"
        )
        self.stat_bans_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Errors
        self.stat_errors_card = self._create_stat_card(
            stats_frame, "⚠️", t('errors'), "0"
        )
        self.stat_errors_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Reset Button
        reset_btn = ctk.CTkButton(
            self.tab_stats,
            text=t('reset_stats'),
            command=self._reset_stats,
            height=40,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_card_hover']
        )
        reset_btn.pack(pady=15)

    def _create_settings_tab(self):
        """Ayarlar sekmesi - Dil ve Geliştirici bilgisi"""
        self.tab_settings.grid_columnconfigure(0, weight=1)
        
        # ====== LANGUAGE SETTINGS ======
        lang_card = self._create_card(self.tab_settings, t('language_settings'))
        lang_card.pack(fill="x", padx=5, pady=5)
        
        lang_row = ctk.CTkFrame(lang_card, fg_color="transparent")
        lang_row.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            lang_row,
            text=t('language') + ":",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text']
        ).pack(side="left")
        
        # Language dropdown
        self.lang_var = ctk.StringVar(value=self.settings.get('language', 'tr'))
        self.lang_dropdown = ctk.CTkComboBox(
            lang_row,
            values=['tr', 'en'],
            variable=self.lang_var,
            width=100,
            height=32,
            fg_color=COLORS['bg_dark'],
            command=self._on_language_change
        )
        self.lang_dropdown.pack(side="right")
        
        # Language info label
        lang_info = ctk.CTkLabel(
            lang_card,
            text=t('language_change_info'),
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted']
        )
        lang_info.pack(anchor="w", padx=15, pady=(0, 10))
        
        # ====== DEVELOPER INFO ======
        dev_card = self._create_card(self.tab_settings, t('developer_info'))
        dev_card.pack(fill="x", padx=5, pady=10)
        
        # Developer info container
        dev_container = ctk.CTkFrame(dev_card, fg_color=COLORS['bg_dark'], corner_radius=10)
        dev_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Developer name
        dev_name_frame = ctk.CTkFrame(dev_container, fg_color="transparent")
        dev_name_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            dev_name_frame,
            text="Syronss",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['accent']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            dev_name_frame,
            text="League of Legends Auto Assistant",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack(anchor="w")
        
        # GitHub Link
        github_frame = ctk.CTkFrame(dev_container, fg_color="transparent")
        github_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            github_frame,
            text="🔗 " + t('github') + ":",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text']
        ).pack(side="left")
        
        github_btn = ctk.CTkButton(
            github_frame,
            text="github.com/Syronss",
            font=ctk.CTkFont(size=11),
            height=28,
            fg_color="transparent",
            text_color=COLORS['accent'],
            hover_color=COLORS['bg_card_hover'],
            command=lambda: self._open_url("https://github.com/Syronss")
        )
        github_btn.pack(side="right")
        
        # Discord
        discord_frame = ctk.CTkFrame(dev_container, fg_color="transparent")
        discord_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(
            discord_frame,
            text="💬 " + t('discord') + ":",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text']
        ).pack(side="left")
        
        discord_label = ctk.CTkLabel(
            discord_frame,
            text="gorkemw.",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['success']
        )
        discord_label.pack(side="right")
        
        # Copy Discord button
        copy_btn = ctk.CTkButton(
            dev_container,
            text="📋 Discord'u Kopyala",
            height=32,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent'],
            command=self._copy_discord_username
        )
        copy_btn.pack(pady=(0, 15))
        
        # Version info
        version_frame = ctk.CTkFrame(self.tab_settings, fg_color=COLORS['bg_card'], corner_radius=10)
        version_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(
            version_frame,
            text="LoL Auto Assistant Pro v1.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        ).pack(pady=10)
    
    def _on_language_change(self, value):
        """Dil değiştirildiğinde ayarları kaydet"""
        self.settings.set('language', value)
        self.lang_manager.set_language(value)
        # Uygulamayı yeniden başlatmadan önce kullanıcıya bilgi ver
        self.log_message(f"🌐 {t('language_change_info')}")
    
    def _open_url(self, url):
        """URL'yi varsayılan tarayıcıda aç"""
        import webbrowser
        webbrowser.open(url)
    
    def _copy_discord_username(self):
        """Discord kullanıcı adını panoya kopyala"""
        self.clipboard_clear()
        self.clipboard_append("gorkemw.")
        self.log_message("📋 Discord kullanıcı adı panoya kopyalandı: gorkemw.")

    def _create_stat_card(self, parent, icon, title, value):
        """Create a statistics card widget"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12
        )
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28)
        ).pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS['text']
        )
        value_label.pack()
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        ).pack(pady=(0, 15))
        
        card.value_label = value_label
        return card

    def _create_card(self, parent, title):
        """Create a styled card frame with title"""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=12
        )
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        return card

    # ========== LOG SECTION ==========
    def _create_log_section(self):
        self.log_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_card'],
            corner_radius=12
        )
        self.log_frame.grid(row=3, column=0, padx=15, pady=5, sticky="nsew")
        
        # Header
        log_header = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(8, 0))
        
        ctk.CTkLabel(
            log_header,
            text=t('log_title'),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text']
        ).pack(side="left")
        
        clear_btn = ctk.CTkButton(
            log_header,
            text=t('clear'),
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            command=self._clear_log,
            fg_color=COLORS['bg_card_hover'],
            hover_color=COLORS['accent']
        )
        clear_btn.pack(side="right")
        
        # Log Box
        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            state="disabled",
            wrap="word",
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=ctk.CTkFont(size=11)
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

    # ========== STATUS BAR ==========
    def _create_status_bar(self):
        self.status_bar = ctk.CTkFrame(
            self,
            height=30,
            fg_color=COLORS['bg_card'],
            corner_radius=0
        )
        self.status_bar.grid(row=4, column=0, sticky="ew")
        
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text=t('ready_status'),
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        )
        self.status_text.pack(side="left", padx=15, pady=5)
        
        self.version_text = ctk.CTkLabel(
            self.status_bar,
            text="v1.0",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_muted']
        )
        self.version_text.pack(side="right", padx=15, pady=5)

    # ========== CALLBACKS & ACTIONS ==========
    def on_connection_state_change(self, state):
        """Called when LCU connection state changes"""
        self.after(0, lambda: self._update_connection_ui(state))
    
    def _update_connection_ui(self, state):
        if state == ConnectionState.CONNECTED:
            self.connection_indicator.configure(text_color=COLORS['success'])
            self.connection_label.configure(text=t('connected'))
        elif state == ConnectionState.CONNECTING:
            self.connection_indicator.configure(text_color=COLORS['warning'])
            self.connection_label.configure(text=t('connecting'))
        else:
            self.connection_indicator.configure(text_color=COLORS['error'])
            self.connection_label.configure(text=t('not_connected'))

    def _update_delay_label(self, value):
        self.delay_label.configure(text=t('accept_delay', int(value)))
        self._on_settings_change()

    def log_message(self, message):
        self.after(0, lambda: self._append_log(message))

    def _append_log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        
        # Update stats UI
        self._update_stats_ui()
    
    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _load_data(self):
        self.log_message(t('msg_starting'))
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        version = get_latest_version()
        if version:
            self.version = version
            self.champion_map = get_champion_map(version)
            self.champion_names = get_champion_names()
            self.after(0, lambda: self.log_message(t('msg_data_updated', version)))
            self.after(0, lambda: self.version_text.configure(text=f"LoL v{version}"))
        else:
            self.after(0, lambda: self.log_message(t('msg_data_error')))

    def _get_champ_ids_from_text(self, text):
        """Parse comma-separated champion names and return list of IDs"""
        if not text.strip():
            return []
        
        names = [n.strip() for n in text.split(',') if n.strip()]
        ids = []
        
        for name in names:
            champ = find_champion_by_name(name)
            if champ:
                ids.append(champ['key'])
        
        return ids

    def _on_settings_change(self, *args):
        """Called when any setting changes"""
        settings = {
            'enable_auto_accept': self.accept_var.get(),
            'accept_delay': self.delay_slider.get(),
            'enable_auto_ban': self.ban_var.get(),
            'enable_auto_pick': self.pick_var.get(),
            'enable_sound': self.sound_var.get()
        }
        self.bot.update_settings(settings)
        self._save_settings()

    def _on_sound_toggle(self):
        self.sound_manager.set_enabled(self.sound_var.get())
        self._on_settings_change()
    
    def _test_sound(self):
        self.sound_manager.play_match_found()

    def _save_settings(self):
        """Save current settings to file"""
        self.settings.update({
            'enable_auto_accept': self.accept_var.get(),
            'accept_delay': int(self.delay_slider.get()),
            'enable_auto_ban': self.ban_var.get(),
            'enable_auto_pick': self.pick_var.get(),
            'enable_sound': self.sound_var.get(),
            'ban_champions': [n.strip() for n in self.ban_entry.get().split(',') if n.strip()],
            'pick_champions': [n.strip() for n in self.pick_entry.get().split(',') if n.strip()]
        })

    def _load_settings(self):
        """Load settings from file"""
        self.accept_var.set(self.settings.get('enable_auto_accept', True))
        self.delay_slider.set(self.settings.get('accept_delay', 0))
        self._update_delay_label(self.settings.get('accept_delay', 0))
        self.ban_var.set(self.settings.get('enable_auto_ban', False))
        self.pick_var.set(self.settings.get('enable_auto_pick', False))
        self.sound_var.set(self.settings.get('enable_sound', True))
        
        # Load champion lists
        ban_champs = self.settings.get('ban_champions', [])
        pick_champs = self.settings.get('pick_champions', [])
        
        if ban_champs:
            self.ban_entry.insert(0, ', '.join(ban_champs))
        if pick_champs:
            self.pick_entry.insert(0, ', '.join(pick_champs))
        
        self.sound_manager.set_enabled(self.sound_var.get())

    def _start_bot(self):
        # Validate and get champion IDs
        settings = {}
        
        if self.pick_var.get():
            pick_ids = self._get_champ_ids_from_text(self.pick_entry.get())
            if not pick_ids:
                self.log_message(t('msg_no_pick_champion'))
            else:
                settings['pick_champion_ids'] = pick_ids
                self.log_message(t('msg_pick_list', len(pick_ids)))

        if self.ban_var.get():
            ban_ids = self._get_champ_ids_from_text(self.ban_entry.get())
            if not ban_ids:
                self.log_message(t('msg_no_ban_champion'))
            else:
                settings['ban_champion_ids'] = ban_ids
                self.log_message(t('msg_ban_list', len(ban_ids)))
        
        # Update bot settings
        self._on_settings_change()
        self.bot.update_settings(settings)
        
        # Start bot thread
        self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
        self.bot_thread.start()
        
        # Update UI
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.pick_entry.configure(state="disabled")
        self.ban_entry.configure(state="disabled")
        self.status_text.configure(text=t('bot_running'))

    def _stop_bot(self):
        self.bot.stop()
        if self.bot_thread:
            self.bot_thread.join(timeout=1)
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.pick_entry.configure(state="normal")
        self.ban_entry.configure(state="normal")
        self.status_text.configure(text=t('ready_status'))

    def _update_stats_ui(self):
        """Update statistics display"""
        stats = self.bot.get_stats()
        self.stat_matches_card.value_label.configure(text=str(stats['matches_accepted']))
        self.stat_picks_card.value_label.configure(text=str(stats['champions_picked']))
        self.stat_bans_card.value_label.configure(text=str(stats['champions_banned']))
        self.stat_errors_card.value_label.configure(text=str(stats['errors']))
    
    def _reset_stats(self):
        self.bot.reset_stats()
        self._update_stats_ui()
        self.log_message(t('msg_stats_reset'))

    # ========== TRAY & WINDOW ==========
    def on_closing(self):
        self._save_settings()
        self._stop_bot()
        self._spell_timer_running = False  # UI güncelleme döngüsünü durdur
        self.hotkey_manager.stop()
        self.spell_tracker.stop_timer()
        self.destroy()
        os._exit(0)

    def _hide_window(self):
        self.withdraw()
        if not self.tray_icon:
            image = self._create_icon_image()
            menu = (
                pystray.MenuItem(t('show'), self._show_window),
                pystray.MenuItem(t('exit'), self._quit_app)
            )
            self.tray_icon = pystray.Icon("lol_auto", image, "LoL Auto Assistant", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_window(self, icon, item):
        self.after(0, self.deiconify)
        icon.stop()
        self.tray_icon = None

    def _quit_app(self, icon, item):
        self._save_settings()
        self._stop_bot()
        icon.stop()
        self.destroy()
        os._exit(0)

    def _create_icon_image(self):
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw gradient-like circle
        draw.ellipse([4, 4, 60, 60], fill=COLORS['accent'])
        draw.ellipse([12, 12, 52, 52], fill=COLORS['bg_card'])
        
        # Draw play symbol
        points = [(26, 20), (26, 44), (46, 32)]
        draw.polygon(points, fill=COLORS['accent'])
        
        return image


if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
