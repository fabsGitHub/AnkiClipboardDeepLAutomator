# AnkiClipboardDeepLAutomator

A Python script that automatically translates selected text using DeepL and saves it as a card in Anki—via a hotkey.

## Note

The app has currently only been tested on macOS!

---

## 🚀 Features

- 📋 Automatically copies selected text
- 🌍 Translates using the DeepL API
- 🧠 Adds a card directly to Anki
- ⌨️ Hotkey-controlled (`Cmd + E`)
- 🔔 System notifications & sound
- 📝 Logging with rotating logs

---

## 📦 Requirements

Make sure the following is installed:

- Python 3.8+
- Anki (must be running)
- AnkiConnect plugin
  👉 https://ankiweb.net/shared/info/2036732292

---

## 📥 Installation

### 1. Clone the repository or download the files

```bash
git clone <https://github.com/fabsGitHub/AnkiClipboardDeepLAutomator>
cd AnkiClipboardDeepLAutomator
```

---

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

---

### 3. Install dependencies

```bash
pip install pyperclip requests pygame python-dotenv deepl pynput
```

Additionally on Windows:

```bash
pip install win10toast
```

---

### 4. Create a `.env` file

```env
DEEPL_API_KEY=your_deepl_api_key
```

---

### 5. Adjust `config.json`

```json
{
  “deepl”: {
    “auth_key_env”: “DEEPL_API_KEY”,
    “source_lang”: “EN”,
    “target_lang”: “DE”,
    “model_type”: “general”
  },
  “anki”: {
    “connect_url”: “http://localhost:8765”,
    “deck_name”: “Default”,
    “model_name”: “Basic”
  },
  “hotkeys”: {
    “trigger”: {
      “key”: “e”
    }
  }
}
```

---

## ▶️ Usage

1. Launch **Anki**
2. Make sure **AnkiConnect is active**
3. Run the script:

```bash
python ankilistener.py
```

4. Select some text
5. Press:

```bash
Cmd + E   (macOS)
```

👉 The text will be:

- copied
- translated
- saved as an Anki card

---

## 🛑 Exit

```bash
Ctrl + C
```

---

## ⚓ Project Structure

```
.
├── ankilistener.py
├── config.json
├── .env
├── output.log
├── notification_sound.mp3
```

---

## ⚠️ Notes

- Anki **must be running**
- AnkiConnect must be active
- The hotkey works globally
- On Linux, install `notify-send` if necessary

---

## 🧩 Troubleshooting

**❌ Connection to Anki fails**

- Is Anki running?
- Is AnkiConnect installed?

**❌ DeepL error**

- Is the API key correct?
- Is `.env` loaded?

---

## 📜 License

MIT License
