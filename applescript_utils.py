"""Helpers for safely embedding values in AppleScript string literals."""


def escape_applescript_string(value: str) -> str:
    slash = chr(92)
    return (
        value.replace(slash, slash + slash)
        .replace('"', slash + '"')
        .replace(chr(13), slash + "r")
        .replace(chr(10), slash + "n")
    )