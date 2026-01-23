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

* **Spell Tracker:** Track enemy summoner spell cooldowns.
* Hotkey support (Ctrl+1-5 and Ctrl+6-0)
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

2. Create a virtual environment (recommended):

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

This software is not endorsed by **Riot Games** and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends.

**League of Legends** and **Riot Games** are trademarks or registered trademarks of Riot Games, Inc.

Use this tool at your own risk. Be cautious about account security.

---

<p align="center">
Made by <a href="[https://github.com/Syronss](https://github.com/Syronss)">Syronss</a>
</p>
