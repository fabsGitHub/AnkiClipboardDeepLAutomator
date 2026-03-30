import platform
import subprocess
import os  # Wichtig: os-Modul importieren
import logging
from typing import Optional
from logging_setup import log_debug, log_info, log_error


def show_notification(logger, message: str, title: str = "Anki Translator"):
    """Show a notification using the appropriate method for the current OS."""
    log_info(logger, f"Showing notification: {title} - {message}")
    try:
        if platform.system() == "Darwin":
            log_debug(logger, "Using macOS notification system")
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script])
        elif platform.system() == "Windows":
            log_debug(logger, "Using Windows notification system")
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=10)
        else:
            log_debug(logger, "Using Linux notification system")
            subprocess.run(["notify-send", title, message])
    except Exception as e:
        log_error(logger, f"Failed to show notification: {e}", e)


def play_sound(logger):
    """Play a notification sound."""
    log_info(logger, "Playing notification sound...")
    sound_file = os.path.join(os.path.dirname(__file__), "notification_sound.mp3")

    try:
        import pygame

        if not pygame.mixer.get_init():
            pygame.mixer.init()
            log_debug(logger, "Initialized pygame mixer")

        sound = pygame.mixer.Sound(sound_file)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))
        log_debug(logger, "Sound played successfully")
    except Exception as e:
        log_error(logger, f"Pygame sound playback failed: {e}", e)

        try:
            if platform.system() == "Darwin":
                log_debug(logger, "Using macOS fallback sound")
                subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"])
            elif platform.system() == "Windows":
                log_debug(logger, "Using Windows fallback sound")
                import winsound

                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            else:
                log_debug(logger, "Using Linux fallback sound")
                subprocess.run(
                    ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"]
                )
            log_debug(logger, "Fallback sound played successfully")
        except Exception as e:
            log_error(logger, f"Platform-specific sound playback failed: {e}", e)
