# ⚡ LoL Auto Assistant

A modern, stylish, and advanced **League of Legends** automation tool. It automatically accepts matches, picks your desired champion, or bans unwanted ones.

## ✨ Features

### 🎮 Core Features

* **Auto Accept:** Automatically accepts the match when found.
* Delay setting (0-10 seconds)
* Sound notification


* **Auto Pick:** Automatically picks your designated champion.
* Multi-champion list support (picks based on priority order)


* **Auto Ban:** Automatically bans your designated champion.
* Multi-champion list support



### 🔥 Advanced Features

* **Spell Tracker:** Track enemy summoner spell cooldowns with hotkey support.
* Real-time cooldown display
* "Spell Ready" sound notification


* **System Tray:** Runs in the background (minimize to tray).
* **Multi-Language Support:** **Full support for Turkish (Türkçe)** and English.
* **Statistics:** Track accepted matches, picked/banned champions.
* **Save Settings:** Automatically remembers your preferences.

## 📋 Requirements

* **Windows** Operating System
* **Python 3.8+**
* League of Legends Client

## 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/Syronss/syronss-lol-auto-assistant.git
cd syronss-lol-auto-assistant

```

2. Create a virtual environment (optional):
> **Tip:** It's recommended to use a virtual environment to avoid package conflicts
```bash
python -m venv .venv
.venv\Scripts\activate

```

3. Install the required libraries:

```bash
pip install -r requirements.txt

```

## 💻 Usage
To start the application:

```bash
python src/main.py

```
> ⚠️ **Important:** Ensure all dependencies are installed before running (see Installation).
(Dont forget Install the required libraries in Installation section 3)
### ⌨️ Hotkeys (Spell Tracker)

| Hotkey | Function |
| --- | --- |
| `Ctrl+1` | Top Flash used |
| `Ctrl+2` | Jungle Flash used |
| `Ctrl+3` | Mid Flash used |
| `Ctrl+4` | ADC Flash used |
| `Ctrl+5` | Support Flash used |
| `Ctrl+6` | Top Spell2 used |
| `Ctrl+7` | Jungle Spell2 used |
| `Ctrl+8` | Mid Spell2 used |
| `Ctrl+9` | ADC Spell2 used |
| `Ctrl+0` | Support Spell2 used |

## 📦 Build EXE

To create a single executable file (.exe):

```bash
pyinstaller --noconfirm --onefile --windowed --name "LoLAutoAssistant" --paths "src" --add-data "src;src" --hidden-import "customtkinter" src/main.py

```

## 📁 Project Structure

```
syronss-lol-auto-assistant/
├── src/
│   ├── main.py           # Main application and UI
│   ├── bot_logic.py      # Bot logic (auto accept/pick/ban)
│   ├── lcu_connector.py  # League Client API connection
│   ├── spell_tracker.py  # Enemy spell tracking
│   ├── languages.py      # Multi-language support
│   ├── settings.py       # Settings management
│   ├── sounds.py         # Sound notifications
│   └── utils.py          # Utility functions
├── requirements.txt
├── LICENSE
└── README.md

```

## 🤝 Contributing

1. Fork this repository
2. Create a Feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [Apache License 2.0](https://www.google.com/search?q=LICENSE).

**Important:** If you create derivative works using this project, you are **required** to provide reference to the original project.

## 👨‍💻 Developer

**Syronss**

* GitHub: [@Syronss](https://github.com/Syronss)
* Discord: `gorkemw.`
## ⚠️ Disclaimer

### About This Project
This is an **independent, open-source project** created by the community. It is not affiliated with, endorsed by, or sponsored by Riot Games.

**League of Legends®** and **Riot Games** are trademarks or registered trademarks of Riot Games, Inc.

### How It Works
This tool uses Riot's **official League Client API (LCU)** - the same API that the League client uses internally. All features work through legitimate, publicly documented endpoints.

**What this tool does:**
- Automates match acceptance for convenience
- Helps with champion selection/banning
- Tracks enemy summoner spell cooldowns

**What this tool does NOT do:**
- Modify game files or memory
- Provide unfair advantages in gameplay
- Automate in-game actions or decisions
- Access your account credentials

### Use Responsibly
This tool is designed as a quality-of-life helper and complies with Riot's developer guidelines. However:
- Always ensure your usage follows [Riot's Terms of Service](https://www.riotgames.com/en/terms-of-service)
- Use at your own discretion - the developer is not responsible for any account issues
- When in doubt, check Riot's policies on third-party tools

### No Warranty
This software is provided "as is" without guarantees. While we strive for safety and compliance, use responsibly and stay informed about Riot's policies.

---

**Questions?** Contact Riot Games support for clarification on their third-party application policies.
---

<p align="center">
Made by <a href="[https://github.com/Syronss](https://github.com/Syronss)">Syronss</a>
</p>
