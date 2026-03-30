import subprocess
import logging
from AppKit import NSPasteboard, NSWorkspace
from typing import Optional
from logging_setup import log_debug, log_info, log_warning, log_error


def get_selected_text(logger) -> Optional[str]:
    """Get selected text using macOS native APIs"""
    log_info(logger, "Attempting to get selected text...")
    try:
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        app_name = active_app.localizedName()
        log_debug(logger, f"Active application: {app_name}")

        script = f"""
        tell application "{app_name}"
            try
                set theSelection to (get selection)
                if theSelection is not "" then
                    return theSelection
                end if
            end try
        end tell

        tell application "System Events"
            keystroke "c" using command down
            delay 0.3
            return (the clipboard as text)
        end tell
        """

        process = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        selected_text = process.stdout.strip()

        if selected_text:
            log_debug(logger, f"Successfully got selected text: {repr(selected_text)}")
            return selected_text

        pasteboard = NSPasteboard.generalPasteboard()
        clipboard_text = pasteboard.stringForType_("public.utf8-plain-text")
        if clipboard_text:
            log_debug(logger, f"Fallback to clipboard text: {repr(clipboard_text)}")
            return clipboard_text

        log_warning(logger, "No text could be retrieved")
        return None
    except Exception as e:
        log_error(logger, f"Error getting selected text: {e}", e)
        return None
