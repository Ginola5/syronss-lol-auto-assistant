"""
LCU Connector - League Client API bağlantısı
Auto-reconnect ve connection state callbacks
"""

import psutil
import requests
import base64
import urllib3
import threading
import time

# Suppress insecure request warnings (since LCU uses self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ConnectionState:
    """Connection state enum"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class LCUConnector:
    def __init__(self):
        self.port = None
        self.auth_token = None
        self.connected = False
        self.base_url = None
        self.headers = None
        
        # Callbacks
        self._state_callbacks = []
        self._current_state = ConnectionState.DISCONNECTED
        
        # Auto-reconnect
        self._auto_reconnect = True
        self._reconnect_interval = 2
        self._reconnect_thread = None
        self._stop_reconnect = threading.Event()
        
        # Health check
        self._last_health_check = 0
        self._health_check_interval = 5
    
    @property
    def state(self):
        return self._current_state
    
    def add_state_callback(self, callback):
        """Add a callback for connection state changes. Callback receives (new_state)"""
        if callback not in self._state_callbacks:
            self._state_callbacks.append(callback)
    
    def remove_state_callback(self, callback):
        """Remove a state callback"""
        if callback in self._state_callbacks:
            self._state_callbacks.remove(callback)
    
    def _notify_state_change(self, new_state):
        """Notify all callbacks of state change"""
        if new_state != self._current_state:
            self._current_state = new_state
            for callback in self._state_callbacks:
                try:
                    callback(new_state)
                except Exception as e:
                    print(f"State callback error: {e}")

    def connect(self):
        """
        Attempts to find the LeagueClientUx process and extract credentials.
        """
        self._notify_state_change(ConnectionState.CONNECTING)
        
        try:
            for proc in psutil.process_iter(['name', 'cmdline']):
                # Windows usually runs LeagueClientUx.exe
                if proc.info['name'] in ['LeagueClientUx.exe', 'LeagueClientUx']:
                    cmdline = proc.info['cmdline']
                    if not cmdline:
                        continue
                    
                    port = None
                    token = None
                    
                    for arg in cmdline:
                        if arg.startswith('--app-port='):
                            port = arg.split('=')[1]
                        elif arg.startswith('--remoting-auth-token='):
                            token = arg.split('=')[1]
                    
                    if port and token:
                        self.port = port
                        self.auth_token = token
                        self.base_url = f"https://127.0.0.1:{self.port}"
                        auth_str = f"riot:{self.auth_token}"
                        b64_auth = base64.b64encode(auth_str.encode()).decode()
                        self.headers = {
                            "Authorization": f"Basic {b64_auth}",
                            "Content-Type": "application/json"
                        }
                        
                        # Verify connection with a test request
                        if self._verify_connection():
                            self.connected = True
                            self._notify_state_change(ConnectionState.CONNECTED)
                            return True
                        
        except Exception as e:
            print(f"Connection error: {e}")
            self._notify_state_change(ConnectionState.ERROR)
        
        self.connected = False
        self._notify_state_change(ConnectionState.DISCONNECTED)
        return False
    
    def _verify_connection(self):
        """Verify the connection is working with a simple API call"""
        try:
            url = f"{self.base_url}/lol-summoner/v1/current-summoner"
            response = requests.get(url, headers=self.headers, verify=False, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def disconnect(self):
        """Manually disconnect"""
        self.connected = False
        self.port = None
        self.auth_token = None
        self.base_url = None
        self.headers = None
        self._notify_state_change(ConnectionState.DISCONNECTED)
    
    def start_auto_reconnect(self, interval=2):
        """Start auto-reconnect in background"""
        self._reconnect_interval = interval
        self._stop_reconnect.clear()
        
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return
        
        self._reconnect_thread = threading.Thread(target=self._auto_reconnect_loop, daemon=True)
        self._reconnect_thread.start()
    
    def stop_auto_reconnect(self):
        """Stop auto-reconnect"""
        self._stop_reconnect.set()
        if self._reconnect_thread:
            self._reconnect_thread.join(timeout=1)
    
    def _auto_reconnect_loop(self):
        """Background loop for auto-reconnection"""
        while not self._stop_reconnect.is_set():
            if not self.connected:
                self.connect()
            else:
                # Health check
                current_time = time.time()
                if current_time - self._last_health_check > self._health_check_interval:
                    self._last_health_check = current_time
                    if not self._verify_connection():
                        self.connected = False
                        self._notify_state_change(ConnectionState.DISCONNECTED)
            
            self._stop_reconnect.wait(self._reconnect_interval)
    
    def health_check(self):
        """Perform a health check on the connection"""
        if not self.connected:
            return False
        return self._verify_connection()

    def request(self, method, endpoint, data=None):
        """
        Generic request wrapper for LCU API.
        """
        if not self.connected:
            return None
        
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, verify=False, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, verify=False, timeout=5)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, verify=False, timeout=5)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, verify=False, timeout=5)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, verify=False, timeout=5)
            else:
                return None
            
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as e:
            print(f"Connection lost ({endpoint}): {e}")
            self.connected = False
            self._notify_state_change(ConnectionState.DISCONNECTED)
            return None
        except Exception as e:
            print(f"Request error ({endpoint}): {e}")
            return None
    
    def get_current_summoner(self):
        """Get current logged in summoner info"""
        response = self.request("GET", "/lol-summoner/v1/current-summoner")
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_gameflow_phase(self):
        """Get current gameflow phase (Lobby, ChampSelect, InProgress, etc.)"""
        response = self.request("GET", "/lol-gameflow/v1/gameflow-phase")
        if response and response.status_code == 200:
            return response.json()
        return None
