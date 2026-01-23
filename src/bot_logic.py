"""
Bot Logic - League of Legends otomatik işlemler
Multi-champion listesi, istatistikler ve ses bildirimleri
Doğrulanmış ban/pick sistemi
"""

import time
import threading

class LeagueBot:
    def __init__(self, connector, log_callback=None, settings=None, sound_manager=None):
        self.connector = connector
        self.log_callback = log_callback
        self.settings = settings
        self.sound_manager = sound_manager
        self.is_running = False
        
        # Settings
        self.enable_auto_accept = True
        self.accept_delay = 0.0
        
        self.enable_auto_ban = False
        self.ban_champion_ids = []  # List for priority ban
        
        self.enable_auto_pick = False
        self.pick_champion_ids = []  # List for priority pick
        
        self.enable_sound = True
        
        # Statistics
        self.stats = {
            'matches_accepted': 0,
            'champions_banned': 0,
            'champions_picked': 0,
            'errors': 0
        }
        
        # State tracking to prevent duplicate actions
        self._last_action_completed = set()
        self._action_lock = threading.Lock()
        
        # Pending actions - track actions we're actively trying to complete
        self._pending_actions = {}  # action_id -> {'type': 'ban'/'pick', 'champion_id': id, 'attempts': 0}
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def update_settings(self, settings):
        """
        Updates bot settings dynamically.
        settings: dict containing keys like 'enable_auto_accept', 'ban_champion_ids', etc.
        """
        if 'enable_auto_accept' in settings:
            self.enable_auto_accept = settings['enable_auto_accept']
        if 'accept_delay' in settings:
            self.accept_delay = float(settings['accept_delay'])
            
        if 'enable_auto_ban' in settings:
            self.enable_auto_ban = settings['enable_auto_ban']
        if 'ban_champion_id' in settings:
            # Single ID (legacy) - convert to list
            self.ban_champion_ids = [settings['ban_champion_id']]
        if 'ban_champion_ids' in settings:
            self.ban_champion_ids = list(settings['ban_champion_ids'])
            
        if 'enable_auto_pick' in settings:
            self.enable_auto_pick = settings['enable_auto_pick']
        if 'pick_champion_id' in settings:
            # Single ID (legacy) - convert to list
            self.pick_champion_ids = [settings['pick_champion_id']]
        if 'pick_champion_ids' in settings:
            self.pick_champion_ids = list(settings['pick_champion_ids'])
        
        if 'enable_sound' in settings:
            self.enable_sound = settings['enable_sound']

    def get_stats(self):
        """Returns a copy of current statistics"""
        return dict(self.stats)
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'matches_accepted': 0,
            'champions_banned': 0,
            'champions_picked': 0,
            'errors': 0
        }

    def start(self):
        self.is_running = True
        self._last_action_completed.clear()
        self._pending_actions.clear()
        self.log("🚀 Bot servisi başlatıldı.")
        
        # Start auto-reconnect on connector
        if hasattr(self.connector, 'start_auto_reconnect'):
            self.connector.start_auto_reconnect()
        
        while self.is_running:
            if not self.connector.connected:
                if self.connector.connect():
                    self.log("✅ League Client'a bağlanıldı!")
                else:
                    time.sleep(2)
                    continue
            
            try:
                if self.enable_auto_accept:
                    self.auto_accept()
                
                # Check champ select only if pick or ban is enabled
                if self.enable_auto_ban or self.enable_auto_pick:
                    self.handle_champ_select()
                    
            except Exception as e:
                self.log(f"❌ Hata: {e}")
                self.stats['errors'] += 1
            
            time.sleep(1)
        
        # Stop auto-reconnect when bot stops
        if hasattr(self.connector, 'stop_auto_reconnect'):
            self.connector.stop_auto_reconnect()

    def stop(self):
        self.is_running = False
        self._pending_actions.clear()
        self.log("⏹️ Bot durduruldu.")

    def auto_accept(self):
        # Check matchmaking status
        response = self.connector.request("GET", "/lol-matchmaking/v1/ready-check")
        if response and response.status_code == 200:
            data = response.json()
            state = data.get("state")
            player_response = data.get("playerResponse")
            
            # Only accept if InProgress and we haven't already accepted
            if state == "InProgress" and player_response == "None":
                # Play sound notification
                if self.enable_sound and self.sound_manager:
                    self.sound_manager.play_match_found()
                
                if self.accept_delay > 0:
                    self.log(f"🎮 Maç bulundu! {int(self.accept_delay)} sn bekleniyor...")
                    time.sleep(self.accept_delay)
                
                self.log("✅ Maç kabul ediliyor...")
                accept_response = self.connector.request("POST", "/lol-matchmaking/v1/ready-check/accept")
                
                if accept_response and accept_response.status_code in [200, 204]:
                    self.stats['matches_accepted'] += 1
                    if self.sound_manager and self.enable_sound:
                        self.sound_manager.play_success()

    def handle_champ_select(self):
        # Check champ select session
        session_response = self.connector.request("GET", "/lol-champ-select/v1/session")
        if not session_response or session_response.status_code != 200:
            # Not in champ select, clear action tracking
            self._last_action_completed.clear()
            self._pending_actions.clear()
            return

        session = session_response.json()
        
        # Get local summoner info
        summoner_response = self.connector.request("GET", "/lol-summoner/v1/current-summoner")
        if not summoner_response or summoner_response.status_code != 200:
            return
            
        summoner_id = summoner_response.json().get("summonerId")
        
        # Find local player's cellId
        local_cell_id = -1
        for team_member in session.get("myTeam", []):
            if team_member.get("summonerId") == summoner_id:
                local_cell_id = team_member.get("cellId")
                break
        
        if local_cell_id == -1:
            return

        # Get list of banned champions in this session
        banned_champion_ids = set()
        for action_group in session.get("actions", []):
            for action in action_group:
                if action.get("type") == "ban" and action.get("completed"):
                    champ_id = action.get("championId")
                    if champ_id:
                        banned_champion_ids.add(str(champ_id))
        
        # Get list of picked champions in this session
        picked_champion_ids = set()
        for team_member in session.get("myTeam", []) + session.get("theirTeam", []):
            champ_id = team_member.get("championId")
            if champ_id:
                picked_champion_ids.add(str(champ_id))

        # Iterate through actions
        actions = session.get("actions", [])
        for action_group in actions:
            for action in action_group:
                action_id = action.get("id")
                action_type = action.get("type")
                is_my_action = action.get("actorCellId") == local_cell_id
                is_in_progress = action.get("isInProgress", False)
                is_completed = action.get("completed", False)
                
                # Check if this action just got completed (was pending, now completed)
                if action_id in self._pending_actions and is_completed:
                    pending = self._pending_actions.pop(action_id)
                    self.log(f"✅ {pending['type'].upper()} DOĞRULANDI! (ID: {pending['champion_id']})")
                    if self.sound_manager and self.enable_sound:
                        self.sound_manager.play_success()
                    
                    # Update stats
                    if pending['type'] == 'ban':
                        self.stats['champions_banned'] += 1
                    else:
                        self.stats['champions_picked'] += 1
                    
                    with self._action_lock:
                        self._last_action_completed.add(action_id)
                    continue
                
                # Check if action belongs to me and is in progress
                if is_my_action and is_in_progress and not is_completed:
                    
                    # Skip if already confirmed completed
                    with self._action_lock:
                        if action_id in self._last_action_completed:
                            continue
                    
                    # Handle Ban
                    if action_type == "ban" and self.enable_auto_ban:
                        champion_id = self._get_available_champion(
                            self.ban_champion_ids, 
                            banned_champion_ids
                        )
                        if champion_id:
                            self._attempt_action(action_id, champion_id, "ban")
                        return
                        
                    # Handle Pick
                    if action_type == "pick" and self.enable_auto_pick:
                        # For pick, exclude both banned and already picked
                        unavailable = banned_champion_ids | picked_champion_ids
                        champion_id = self._get_available_champion(
                            self.pick_champion_ids, 
                            unavailable
                        )
                        if champion_id:
                            self._attempt_action(action_id, champion_id, "pick")
                        return

    def _attempt_action(self, action_id, champion_id, action_type):
        """
        Attempt to complete an action (ban/pick).
        Will keep retrying until verified complete.
        """
        # Check if we're already working on this action
        if action_id in self._pending_actions:
            pending = self._pending_actions[action_id]
            pending['attempts'] += 1
            
            # Log retry attempts
            if pending['attempts'] % 3 == 0:  # Log every 3rd attempt
                self.log(f"🔄 {action_type.upper()} yeniden deneniyor... (Deneme: {pending['attempts']})")
        else:
            # First attempt
            self._pending_actions[action_id] = {
                'type': action_type,
                'champion_id': champion_id,
                'attempts': 1
            }
            emoji = "🚫" if action_type == "ban" else "✨"
            self.log(f"{emoji} Şampiyon {action_type} yapılıyor (ID: {champion_id})...")
        
        # Step 1: First, hover over the champion (select without confirming)
        hover_body = {
            "championId": int(champion_id)
        }
        self.connector.request("PATCH", f"/lol-champ-select/v1/session/actions/{action_id}", hover_body)
        
        # Small delay to ensure the hover is registered
        time.sleep(0.3)
        
        # Step 2: Now confirm the action
        confirm_body = {
            "championId": int(champion_id),
            "completed": True
        }
        resp = self.connector.request("PATCH", f"/lol-champ-select/v1/session/actions/{action_id}", confirm_body)
        
        # We don't trust the response - we verify by checking if action.completed becomes True
        # This will be checked in the next iteration of handle_champ_select

    def _get_available_champion(self, priority_list, unavailable_set):
        """
        Get the first available champion from the priority list that isn't unavailable.
        Returns champion ID or None.
        """
        for champ_id in priority_list:
            if str(champ_id) not in unavailable_set:
                return champ_id
        return None

    def _complete_action(self, action_id, champion_id):
        """Complete a ban or pick action. Returns True on success."""
        body = {
            "championId": int(champion_id),
            "completed": True
        }
        resp = self.connector.request("PATCH", f"/lol-champ-select/v1/session/actions/{action_id}", body)
        if resp and resp.status_code in [200, 204]:
            self.log("✅ İşlem başarılı!")
            if self.sound_manager and self.enable_sound:
                self.sound_manager.play_success()
            return True
        else:
            self.log("⚠️ İşlem başarısız olabilir.")
            return False
