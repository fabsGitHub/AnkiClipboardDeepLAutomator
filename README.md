# AnkiClipboardDeepLAutomator

A macOS keyboard workflow that sends selected text to DeepL and creates forward and reverse Anki notes through AnkiConnect.

## What it does

- Reads selected text with macOS accessibility and clipboard APIs.
- Sends the selection to DeepL for translation.
- Creates two notes in Anki through the local AnkiConnect service.
- Can optionally attach speech audio from Google Translate Text-to-Speech.

This is a personal productivity tool and learning project. It is currently macOS-only because it uses AppKit, AppleScript, and the macOS Command key.

## Requirements

- macOS with Python 3.9 or later.
- Anki running locally with the AnkiConnect add-on enabled.
- A DeepL API key.
- macOS Accessibility and Automation permissions for the terminal or Python process that runs the tool.

## Setup

```bash
git clone https://github.com/fabsGitHub/AnkiClipboardDeepLAutomator.git
cd AnkiClipboardDeepLAutomator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add your DeepL API key to .env as AUTH_KEY. The file is excluded from Git. Do not paste API keys into config.json, commit history, logs, or issue reports.

## Configure

Edit config.json to choose the DeepL source and target languages, Anki deck and note model, character limit, and hotkey key. The default trigger is Command plus period. The Command key is currently fixed by the macOS listener.

Audio is disabled by default. To enable it, set anki.include_audio to true and choose anki.audio_lang. When enabled, Anki retrieves speech audio from Google Translate Text-to-Speech; the selected phrase is sent to that service. The query is URL-encoded, but it remains third-party data sharing.

## Use

1. Start Anki and make sure AnkiConnect is available at http://localhost:8765.
2. Activate the virtual environment and run:

```bash
python3 main.py
```

3. Select a phrase in another application and press Command plus the configured trigger key.
4. The app creates a forward and a reverse card in the configured deck.

## Data and privacy

- Selected text and the resulting translation are sent to DeepL and then to the local AnkiConnect instance because those transfers are required for the workflow.
- Audio requests to Google Translate are disabled unless explicitly enabled in config.json.
- Logs contain operational events and character counts, not selected text, translations, request bodies, or response bodies.
- Desktop notifications may display a translation so the result is visible to the user; notification contents are not written to the application log.
- Keep .env private and rotate a key immediately if it was ever committed or shared.

## Project structure

- main.py handles the hotkey workflow.
- anki_connection.py calls DeepL and AnkiConnect.
- text_selection.py reads selected text using macOS APIs.
- notification_handler.py displays desktop feedback.
- config.json contains non-secret preferences.
- applescript_utils.py escapes strings before embedding them in AppleScript.
- requirements.txt defines Python dependencies for manual environment setup.
- .env.example documents the required secret variable without a key value.

## License

This project is distributed under the MIT License; see LICENSE.