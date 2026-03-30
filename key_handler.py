import threading
from pynput.keyboard import Key
from typing import List, Callable
from logging_setup import log_debug, log_info, log_error


def on_press(
    key, logger, hotkeys_config: dict, cmd_pressed: List[bool], e_pressed: List[bool]
):
    """Called when a key is pressed."""
    current_thread = threading.current_thread()
    log_debug(
        logger, f"on_press called in thread: {current_thread.name} for key: {key}"
    )

    try:
        if key == Key.cmd:
            cmd_pressed[0] = True
            log_info(logger, "Cmd key pressed")
        elif hasattr(key, "char") and key.char == hotkeys_config["trigger"]["key"]:
            e_pressed[0] = True
            log_info(logger, f"Trigger key '{key.char}' pressed")
    except AttributeError as e:
        log_error(logger, f"AttributeError for key: {key}", e)


def on_release(
    key,
    logger,
    hotkeys_config: dict,
    cmd_pressed: List[bool],
    e_pressed: List[bool],
    action_in_progress: List[bool],
    action_lock: threading.Lock,
    on_cmd_e: Callable,
):
    """Called when a key is released."""
    current_thread = threading.current_thread()
    log_debug(
        logger, f"on_release called in thread: {current_thread.name} for key: {key}"
    )

    try:
        if key == Key.cmd:
            cmd_pressed[0] = False
            log_info(logger, "Cmd key released")

            if e_pressed[0]:
                with action_lock:
                    if not action_in_progress[0]:
                        action_in_progress[0] = True
                        threading.Thread(target=on_cmd_e).start()
            e_pressed[0] = False
        elif hasattr(key, "char") and key.char == hotkeys_config["trigger"]["key"]:
            e_pressed[0] = False
            log_info(logger, f"Trigger key '{key.char}' released")
    except AttributeError as e:
        log_error(logger, f"AttributeError for key: {key}", e)
