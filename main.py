#!/usr/bin/env python3
import requests
import json
import os
import time
from dotenv import load_dotenv
from pynput.keyboard import Key, Listener
import signal
import threading
import sys
from typing import Optional, Dict, Any

from logging_setup import setup_logging, log_debug, log_info, log_warning, log_error
from notification_handler import show_notification, play_sound
from text_selection import get_selected_text
from anki_connection import Connection
from key_handler import on_press, on_release


def create_on_cmd_e_handler(
    logger,
    deepl_config: Dict[str, Any],
    anki_config: Dict[str, Any],
    hotkeys_config: Dict[str, Any],
    last_trigger_time: list,
    action_in_progress: list,
):
    """Create a handler function for the hotkey action."""

    def on_cmd_e():
        """Handle the hotkey action in a separate thread."""
        current_thread = threading.current_thread()
        log_info(logger, f"on_cmd_e called in thread: {current_thread.name}")

        current_time = time.time()
        if current_time - last_trigger_time[0] < 1:  # trigger_delay
            log_debug(logger, "Ignoring duplicate trigger")
            action_in_progress[0] = False
            return

        last_trigger_time[0] = current_time

        try:
            log_info(logger, "Hotkey pressed, starting translation process...")
            selected_text = get_selected_text(logger)

            if not selected_text:
                log_warning(logger, "No text selected or failed to copy text")
                show_notification(
                    logger, "No text selected or failed to copy text", "⚠️ No Text"
                )
                return

            log_debug(logger, f"Selected Text: {repr(selected_text)}")

            cn = Connection(logger, deepl_config, anki_config)
            translation = cn._translate(selected_text, deepl_config["target_lang"])
            if translation is None:
                log_error(logger, "Translation failed")
                return

            log_debug(logger, f"Translation: {repr(translation)}")

            result = cn._invoke(
                action="addNote",
                note={
                    "deckName": anki_config["deck_name"],
                    "modelName": anki_config["model_name"],
                    "fields": {
                        "Front": selected_text,
                        "Back": translation,
                    },
                    "options": {"closeAfterAdding": True},
                },
            )

            if result is not None:
                log_info(logger, f"Note created successfully! Note ID: {result}")
                play_sound(logger)

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            log_error(logger, error_msg, e)
            show_notification(logger, error_msg, "❌ Error")
        finally:
            action_in_progress[0] = False
            log_debug(logger, "Action completed, releasing lock")

    return on_cmd_e


def main():
    logger = setup_logging()

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

    # Use lists to allow modification in nested functions
    cmd_pressed = [False]
    e_pressed = [False]
    last_trigger_time = [0]
    action_in_progress = [False]
    action_lock = threading.Lock()

    # Create the on_cmd_e handler function
    on_cmd_e_handler = create_on_cmd_e_handler(
        logger,
        deepl_config,
        anki_config,
        hotkeys_config,
        last_trigger_time,
        action_in_progress,
    )

    # Define the callback functions with proper closures
    def wrapped_on_press(key):
        on_press(key, logger, hotkeys_config, cmd_pressed, e_pressed)

    def wrapped_on_release(key):
        on_release(
            key,
            logger,
            hotkeys_config,
            cmd_pressed,
            e_pressed,
            action_in_progress,
            action_lock,
            on_cmd_e_handler,
        )

    listener = Listener(on_press=wrapped_on_press, on_release=wrapped_on_release)

    try:
        listener.start()
        log_info(logger, "Listener started. Press CTRL+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_info(logger, "Script stopped by user")
    except Exception as e:
        log_error(logger, f"Unexpected error: {e}", e)
    finally:
        if listener.running:
            listener.stop()
        listener.join()
        log_info(logger, "Script terminated")
        print("\nScript stopped by user. Goodbye!")


if __name__ == "__main__":
    main()
