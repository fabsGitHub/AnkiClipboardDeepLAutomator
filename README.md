# AnkiClipboardDeepLAutomator

A Python automation tool that translates selected text using DeepL and instantly creates Anki flashcards via a customizable hotkey.

> ✨ **New:** Automatic dependency installation and cross-platform support!

---

## 📖 Introduction

**AnkiClipboardDeepLAutomator** streamlines language learning by eliminating manual steps between reading, translating, and saving vocabulary. With a single hotkey, selected text is copied, translated via DeepL, and stored directly as an Anki card.

---

## 📚 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Automatic Dependency Installation](#-automatic-dependency-installation)
- [CPU Optimization](#-cpu-optimization)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🚀 Features

- 📋 Automatically copies selected text
- 🌍 Translates text using the DeepL API
- 🧠 Creates Anki flashcards instantly
- ⌨️ Hotkey-triggered workflow (`Cmd + E` / `Ctrl + E`)
- 🔔 System notifications with sound feedback
- 🔧 Automatic dependency detection and installation
- 🌐 Cross-platform compatibility (macOS, Windows, Linux)

---

## 📦 Requirements

Ensure the following are installed:

- Python 3.9+
- Anki (running in the background)
- AnkiConnect plugin
  👉 https://ankiweb.net/shared/info/2036732292

---

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/fabsGitHub/AnkiClipboardDeepLAutomator.git
cd AnkiClipboardDeepLAutomator
```

### 2. (Optional) Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

#### Automatic Installation (currently not working)

```bash
python3 main.py
```

#### Manual Installation

```bash
pip install requests python-dotenv deepl pynput pygame
```

#### Platform-Specific Dependencies

- **macOS**

  ```bash
  pip install pyobjc
  ```

- **Windows**

  ```bash
  pip install win10toast
  ```

- **Linux (optional notifications)**

  ```bash
  pip install notify-send
  ```

---

## ⚙️ Configuration

### 1. Create `.env` File

```env
AUTH_KEY=your_deepl_api_key_here
```

### 2. Configure `config.json`

```json
{
  "logging": {
    "level": "WARNING",
    "file_level": "DEBUG",
    "console_level": "WARNING"
  },
  "deepl": {
    "auth_key_env": "AUTH_KEY",
    "source_lang": "EN",
    "target_lang": "DE",
    "model_type": "prefer_quality_optimized"
  },
  "anki": {
    "connect_url": "http://localhost:8765",
    "deck_name": "english",
    "model_name": "Basic"
  },
  "hotkeys": {
    "trigger": {
      "cmd": true,
      "key": "e"
    }
  }
}
```

---

## ▶️ Usage

1. Launch **Anki**
2. Ensure **AnkiConnect** is enabled
3. Start the script:

```bash
python3 main.py
```

4. Select any text
5. Press:

- **macOS:** `Cmd + E`
- **Windows/Linux:** `Ctrl + E`

### ✅ Result

The selected text will be:

- Copied
- Translated via DeepL
- Saved as a new Anki card

### 🛑 Exit

```bash
Ctrl + C
```

---

## 📁 Project Structure

```text
.
├── install_dependencies.py (currently not working)
├── main.py
├── config.json
├── .env
├── requirements.txt
├── logging_setup.py
├── notification_handler.py
├── text_selection.py
├── anki_connection.py
├── key_handler.py
├── anki_automator.log
└── notification_sound.mp3
```

---

## 📁 Shell Script & launchd agent

### Automatically Start Anki and Anki-Listener on macOS Login
To automatically start Anki and your Anki-Listener script when you log in to your macOS user account, you can use a shell script and a launchd agent. This guide will walk you through the setup process.

### Prerequisites

Ensure that Anki is installed on your system.
Ensure that your Python script (main.py) is located in your project directory.
Make sure Python is installed and the correct version is referenced in the script.

Step 1: Customize the Script
Replace the placeholders in the script with your actual paths:

`/path/to/your/AnkiClipboardDeepLAutomator/` with the path to your project directory.
`/path/to/your/python3` with the path to your Python executable.

Here is the script with placeholders:
```bash
#!/bin/bash

# Start Anki
open -a Anki

# Wait for Anki to start
sleep 5

# Change to the project directory
cd /path/to/your/AnkiClipboardDeepLAutomator/

# Create a launchd service if it doesn't exist
PLIST_FILE=~/Library/LaunchAgents/com.user.ankilistener.plist

if [ ! -f "$PLIST_FILE" ]; then
    cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.ankilistener</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>-c</string>
        <string>cd /path/to/your/AnkiClipboardDeepLAutomator/ && /path/to/your/python3 main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardOutPath</key>
    <string>/path/to/your/AnkiClipboardDeepLAutomator/output.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/your/AnkiClipboardDeepLAutomator/error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\$PATH</string>
    </dict>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
EOF
    echo "Creating launchd service..."
else
    echo "launchd service already exists."
fi

# Load the launchd service
if ! launchctl list | grep -q com.user.ankilistener; then
    launchctl unload "$PLIST_FILE" 2>/dev/null
    launchctl load "$PLIST_FILE"
    echo "Loading launchd service..."
else
    echo "launchd service is already running."
fi
```

Step 2: Save the Script
Save the script to a file, for example, *start_anki_listener.sh*, in your project directory.

Step 3: Make the Script Executable
Open Terminal and navigate to your project directory. Make the script executable:

```bash
chmod +x /path/to/your/start_anki_listener.sh
```

Step 4: Add the Script as a Login Item

Open *System Preferences > Users & Groups > Login Items*.
Click the *+ button*.
Navigate to the location where you saved *start_anki_listener.sh* and select it.
Ensure the checkbox next to the script is checked to allow it to run at login.

### Troubleshooting

Permissions: Ensure that the script and the Python script are executable.
Paths: Double-check that all paths in the script are correct.
Logs: Check the log files for any error messages.

### Important Notes

Replace Paths: Make sure to replace all placeholders (`/path/to/your/...`) with the actual paths to your project directory and Python executable.
Python Version: Ensure that the path to the Python version is correct.
Permissions: Ensure that script files are executable (`chmod +x /path/to/your/start_anki_listener.sh`).

---

## ⚠️ Troubleshooting

### ❌ Cannot Connect to Anki

- Ensure Anki is running
- Verify AnkiConnect is installed and enabled
- Check `connect_url` in `config.json`

### ❌ DeepL Errors

- Confirm API key in `.env`
- Verify DeepL account status
- Check internet connection

### ❌ Missing Dependencies

- Run:

  ```bash
  python3 -m pip install xyz
  ```

### ❌ Hotkey Not Working

- Grant accessibility permissions to your terminal/app
- Verify hotkey configuration in `config.json`

---

## 🤝 Contributing

Contributions are welcome!

- Open an issue for discussion before major changes
- Submit pull requests with clear descriptions

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 📧 Support

For help or questions:

- Check GitHub Issues

---
