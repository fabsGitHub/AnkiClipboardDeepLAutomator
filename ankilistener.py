import pyperclip
import requests
import json
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
from dotenv import load_dotenv
import deepl
from pynput.keyboard import Key, Controller, Listener
import platform
import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler

print("""
-----------------------------------------
AnkiClipboardDeepLAutomator - v1.0
Dieses Skript übersetzt markierten Text mit DeepL und fügt ihn als Karte in Anki ein.

Voraussetzungen:
- Anki muss lokal auf deinem Computer installiert und gestartet sein.
- Ein Ankideck muss erstellt sein und in config.json hinterlegt sein.
- Das AnkiConnect-Plugin muss in Anki installiert und aktiviert sein.
  (Installationsanleitung: https://ankiweb.net/shared/info/2036732292)

Verwendung:
1. Starte Anki und stelle sicher, dass AnkiConnect aktiviert ist.
2. Starte dieses Skript.
3. Markiere den Text, den du übersetzen möchtest.
4. Drücke `Cmd + E` (oder deine konfigurierte Tastenkombination).
5. Die Übersetzung wird automatisch als Karte in deinem Anki-Deck gespeichert.

Exit the script with `Ctrl + C`.
-----------------------------------------
""")

# Configure logging
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler = RotatingFileHandler(
    "output.log",
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5,  # Maximal 5 Log-Dateien behalten
    encoding="utf-8",
)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


def log_message(message, level=logging.INFO):
    """Log a message with the specified level."""
    if level == logging.INFO:
        logger.info(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.CRITICAL:
        logger.critical(message)


# Load the DeepL API key from the .env file
load_dotenv()

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

deepl_config = config["deepl"]
anki_config = config["anki"]
hotkeys_config = config["hotkeys"]


def show_notification(message, title="Anki Translator"):
    """Show a notification using the appropriate method for the current OS."""
    if platform.system() == "Darwin":  # macOS
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])
    elif platform.system() == "Windows":  # Windows
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10)
    else:  # Linux and others
        try:
            subprocess.run(["notify-send", title, message])
        except FileNotFoundError:
            log_message(f"Notification could not be shown: {message}", logging.ERROR)


def play_sound():
    """Play a notification sound using the most reliable method for the current platform."""
    sound_file = os.path.join(os.path.dirname(__file__), "notification_sound.mp3")

    # Try pygame first (cross-platform)
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))
        return
    except Exception as e:
        log_message(f"Pygame sound playback failed: {e}", logging.ERROR)

    # Fallback: Platform-specific methods
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"])
        elif platform.system() == "Windows":  # Windows
            import winsound

            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        else:  # Linux
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"]
            )
    except Exception as e:
        log_message(f"Platform-specific sound playback failed: {e}", logging.ERROR)


class Connection:
    def __init__(self):
        self.session = requests.Session()
        self.translate = self._translate
        self.request = self._request
        self.invoke = self._invoke

    def _translate(self, text, language):
        """Translate the text using the DeepL API."""
        try:
            deepl_client = deepl.DeepLClient(os.environ[deepl_config["auth_key_env"]])
            result = deepl_client.translate_text(
                text,
                source_lang=deepl_config["source_lang"],
                target_lang=language,
                model_type=deepl_config["model_type"],
            )
            return result.text
        except Exception as e:
            error_msg = f"DeepL Translation Error: {str(e)}"
            log_message(error_msg, logging.ERROR)
            show_notification(error_msg, "❌ DeepL Error")
            return None

    @staticmethod
    def _request(action, **params):
        return {"action": action, "params": params, "version": 6}

    def _invoke(self, action, **params):
        """Send a request to AnkiConnect."""
        requestJson = json.dumps(self._request(action, **params)).encode("utf-8")
        try:
            response = self.session.post(
                anki_config["connect_url"], requestJson, timeout=5
            )
            jsonResponse = response.json()

            if len(jsonResponse) != 2:
                error_msg = "Response has an unexpected number of fields"
                log_message(error_msg, logging.ERROR)
                show_notification(error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)
            if "error" not in jsonResponse:
                error_msg = "Response is missing required error field"
                log_message(error_msg, logging.ERROR)
                show_notification(error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)
            if "result" not in jsonResponse:
                error_msg = "Response is missing required result field"
                log_message(error_msg, logging.ERROR)
                show_notification(error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)
            if jsonResponse["error"] is not None:
                if jsonResponse["error"].startswith(
                    "cannot create note because it is a duplicate"
                ):
                    msg = "Note already exists and was not recreated."
                    log_message(msg, logging.INFO)
                    show_notification(msg, "ℹ️ AnkiConnect Info")
                    return None
                error_msg = jsonResponse["error"]
                log_message(f"AnkiConnect Error: {error_msg}", logging.ERROR)
                show_notification(error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)
            return jsonResponse["result"]
        except requests.exceptions.ConnectionError:
            error_msg = """
            ❌ Error: Could not connect to AnkiConnect.
            Please make sure:
            1. Anki is running.
            2. The AnkiConnect add-on is installed and enabled in Anki.
            3. AnkiConnect is properly configured and running on port 8765.
            You can install AnkiConnect from: https://foosoft.net/projects/anki-connect/
            """
            log_message(error_msg, logging.ERROR)
            show_notification(
                "Could not connect to AnkiConnect. Check if Anki is running and AnkiConnect is enabled.",
                "❌ AnkiConnect Error",
            )
            return None
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to AnkiConnect: {e}"
            log_message(error_msg, logging.ERROR)
            show_notification(error_msg, "❌ AnkiConnect Error")
            return None


def copy_selected_text():
    """Copy the selected text to the clipboard and return it."""
    old_clipboard = pyperclip.paste()

    ctrl = Controller()
    ctrl.press(Key.cmd)
    ctrl.press("c")
    ctrl.release("c")
    ctrl.release(Key.cmd)

    max_attempts = 3
    for _ in range(max_attempts):
        time.sleep(0.3)
        current_clipboard = pyperclip.paste()
        if current_clipboard != old_clipboard and current_clipboard.strip():
            return current_clipboard.strip()

    error_msg = "Could not copy the selected text. Please try again."
    log_message(error_msg, logging.ERROR)
    show_notification(error_msg, "❌ Clipboard Error")
    return None


def on_cmd_e():
    """Triggered when the configured hotkey is pressed."""
    selected_text = copy_selected_text()
    if not selected_text:
        return

    log_message(f"Selected Text: {selected_text}")

    try:
        cn = Connection()
        translation = cn.translate(selected_text, deepl_config["target_lang"])
        if translation is None:
            return

        log_message(f"Translation: {translation}")

        result = cn.invoke(
            action="addNote",
            note={
                "deckName": anki_config["deck_name"],
                "modelName": anki_config["model_name"],
                "fields": {
                    "Front": selected_text,
                    "Back": translation,
                },
                "options": {
                    "closeAfterAdding": True,
                },
            },
        )
        if result is not None:
            log_message(f"Note created successfully! Note ID: {result}")
            play_sound()
            show_notification(f"Übersetzung: {translation}", "✅")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log_message(error_msg, logging.ERROR)
        show_notification(error_msg, "❌ Error")


# Global variable to store the status of the cmd key
cmd_pressed = False


def on_press(key):
    """Called when a key is pressed."""
    global cmd_pressed
    try:
        if key == Key.cmd:
            cmd_pressed = True
        elif (
            hasattr(key, "char")
            and key.char == hotkeys_config["trigger"]["key"]
            and cmd_pressed
        ):
            on_cmd_e()
    except AttributeError:
        pass


def on_release(key):
    """Called when a key is released."""
    global cmd_pressed
    if key == Key.cmd:
        cmd_pressed = False


def main():
    log_message(
        f"Script is running. Press `Cmd + {hotkeys_config['trigger']['key']}` to translate the selected text and save it to Anki."
    )
    log_message("Exit the script with `Ctrl + C`.")

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
