#!/usr/bin/env python3
import json
import os
import time
from dotenv import load_dotenv
from pynput.keyboard import Key, Listener
import signal
import threading
import sys
from typing import Dict, Any

from logging_setup import setup_logging, log_debug, log_info, log_warning, log_error
from notification_handler import show_notification, play_sound
from text_selection import get_selected_text
from anki_connection import Connection


class HotkeyManager:
    def __init__(
        self,
        logger,
        deepl_config: Dict[str, Any],
        anki_config: Dict[str, Any],
        hotkeys_config: Dict[str, Any],
    ):
        self.logger = logger
        self.deepl_config = deepl_config
        self.anki_config = anki_config
        self.hotkeys_config = hotkeys_config
        self.cmd_pressed = False
        self.e_pressed = False
        self.last_trigger_time = 0
        self.action_in_progress = False
        self.action_lock = threading.Lock()
        self.listener = None
        self.trigger_key = hotkeys_config["trigger"]["key"]

    def on_cmd_e(self):
        """Handle the hotkey action in a separate thread."""
        current_thread = threading.current_thread()
        log_info(self.logger, f"on_cmd_e called in thread: {current_thread.name}")

        current_time = time.time()
        if current_time - self.last_trigger_time < 1:  # trigger_delay
            log_debug(self.logger, "Ignoring duplicate trigger")
            self.action_in_progress = False
            return

        self.last_trigger_time = current_time

        try:
            log_info(self.logger, "Hotkey pressed, starting translation process...")
            selected_text = get_selected_text(self.logger)

            if not selected_text:
                log_warning(self.logger, "No text selected or failed to copy text")
                show_notification(
                    self.logger, "No text selected or failed to copy text", "⚠️ No Text"
                )
                return

            log_debug(self.logger, f"Selected Text: {repr(selected_text)}")

            cn = Connection(self.logger, self.deepl_config, self.anki_config)
            translation = cn._translate(selected_text, self.deepl_config["target_lang"])
            if translation is None:
                log_error(self.logger, "Translation failed")
                return

            log_debug(self.logger, f"Translation: {repr(translation)}")

            result = cn._invoke(
                action="addNote",
                note={
                    "deckName": self.anki_config["deck_name"],
                    "modelName": self.anki_config["model_name"],
                    "fields": {
                        "Front": selected_text,
                        "Back": translation,
                    },
                    "options": {"closeAfterAdding": True},
                },
            )

            if result is not None:
                log_info(self.logger, f"Note created successfully! Note ID: {result}")
                play_sound(self.logger)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            log_error(self.logger, error_msg, e)
            show_notification(self.logger, error_msg, "❌ Error")
        finally:
            self.action_in_progress = False
            log_debug(self.logger, "Action completed, releasing lock")

    def on_press(self, key):
        """Called when a key is pressed."""
        current_thread = threading.current_thread()
        log_debug(
            self.logger,
            f"on_press called in thread: {current_thread.name} for key: {key}",
        )

        try:
            if key == Key.cmd:
                self.cmd_pressed = True
                log_info(self.logger, "Cmd key pressed")
            elif hasattr(key, "char") and key.char == self.trigger_key:
                self.e_pressed = True
                log_info(self.logger, f"Trigger key '{key.char}' pressed")
        except AttributeError as e:
            log_error(self.logger, f"AttributeError for key: {key}", e)

    def on_release(self, key):
        """Called when a key is released."""
        current_thread = threading.current_thread()
        log_debug(
            self.logger,
            f"on_release called in thread: {current_thread.name} for key: {key}",
        )

        try:
            if key == Key.cmd:
                self.cmd_pressed = False
                log_info(self.logger, "Cmd key released")

                if self.e_pressed:
                    with self.action_lock:
                        if not self.action_in_progress:
                            self.action_in_progress = True
                            threading.Thread(target=self.on_cmd_e).start()
                self.e_pressed = False
            elif hasattr(key, "char") and key.char == self.trigger_key:
                self.e_pressed = False
                log_info(self.logger, f"Trigger key '{key.char}' released")

                # Check if Cmd is still pressed
                if self.cmd_pressed and not self.action_in_progress:
                    with self.action_lock:
                        if not self.action_in_progress:
                            self.action_in_progress = True
                            threading.Thread(target=self.on_cmd_e).start()
        except AttributeError as e:
            log_error(self.logger, f"AttributeError for key: {key}", e)

    def start(self):
        """Start the keyboard listener."""
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        log_info(self.logger, "Listener started. Press CTRL+C to exit.")

    def stop(self):
        """Stop the keyboard listener."""
        if self.listener and self.listener.running:
            self.listener.stop()
            self.listener.join()
            log_info(self.logger, "Listener stopped.")


def main():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Setup logging with configuration
    logger = setup_logging(config)
    
    def handle_signal(sig, frame):
        log_info(logger, "Script stopped by user (Ctrl+C)")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)

    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    load_dotenv()

    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        deepl_config = config["deepl"]
        anki_config = config["anki"]
        hotkeys_config = config["hotkeys"]
        log_info(logger, "Configuration loaded successfully")
    except Exception as e:
        log_error(logger, f"Failed to load configuration: {e}", e)
        sys.exit(1)

    log_info(
        logger, f"Main function started in thread: {threading.current_thread().name}"
    )
    log_info(logger, "Script started")
    log_info(
        logger,
        f"Press Cmd + {hotkeys_config['trigger']['key']} to translate selected text",
    )

    hotkey_manager = HotkeyManager(logger, deepl_config, anki_config, hotkeys_config)

    try:
        hotkey_manager.start()
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        log_info(logger, "Script stopped by user")
    except Exception as e:
        log_error(logger, f"Unexpected error: {e}", e)
    finally:
        hotkey_manager.stop()
        log_info(logger, "Script terminated")
        print("\nScript stopped by user. Goodbye!")


if __name__ == "__main__":
    main()
