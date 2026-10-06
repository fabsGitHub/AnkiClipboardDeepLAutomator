import requests
import json
import os
import deepl
from typing import Optional, Dict, Any
from logging_setup import log_debug, log_info, log_error
from notification_handler import show_notification


class Connection:
    def __init__(
        self, logger, deepl_config: Dict[str, Any], anki_config: Dict[str, Any]
    ):
        self.session = requests.Session()
        self.logger = logger
        self.deepl_config = deepl_config
        self.anki_config = anki_config
        log_info(self.logger, "Connection object initialized")

    def _translate(self, text: str, language: str) -> Optional[str]:
        """Translate the text using the DeepL API."""
        log_info(self.logger, f"Sending {len(text)} characters to DeepL.")
        try:
            deepl_client = deepl.DeepLClient(
                os.environ[self.deepl_config["auth_key_env"]]
            )
            result = deepl_client.translate_text(
                text,
                source_lang=self.deepl_config["source_lang"],
                target_lang=language,
                model_type=self.deepl_config["model_type"],
            )
            log_debug(self.logger, f"DeepL returned {len(result.text)} characters.")
            return result.text
        except Exception as e:
            error_msg = "DeepL translation failed; response details were omitted to protect selected text."
            log_error(self.logger, error_msg)
            show_notification(self.logger, error_msg, "❌ DeepL Error")
            return None

    @staticmethod
    def _request(action: str, **params) -> dict:
        return {"action": action, "params": params, "version": 6}

    def _invoke(self, action: str, **params) -> Optional[int]:
        """Send a request to AnkiConnect."""
        log_info(self.logger, f"Invoking AnkiConnect action: {action}")
        request_json = json.dumps(self._request(action, **params)).encode("utf-8")
        log_debug(self.logger, f"AnkiConnect request prepared for action: {action}")

        try:
            response = self.session.post(
                self.anki_config["connect_url"], request_json, timeout=5
            )
            json_response = response.json()

            if len(json_response) != 2:
                error_msg = "Response has an unexpected number of fields"
                log_error(self.logger, error_msg)
                show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)

            if "error" not in json_response:
                error_msg = "Response is missing required error field"
                log_error(self.logger, error_msg)
                show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)

            if "result" not in json_response:
                error_msg = "Response is missing required result field"
                log_error(self.logger, error_msg)
                show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
                raise Exception(error_msg)

            translation = params["note"]["fields"]["Back"]

            if json_response["error"] is not None:
                if json_response["error"].startswith(
                    "cannot create note because it is a duplicate"
                ):
                    msg = "Note already exists and was not recreated."
                    log_info(self.logger, msg)
                    show_notification(
                        self.logger, f"Translation: {translation}", "ℹ️ Already saved"
                    )
                    return None
                else:
                    error_msg = "AnkiConnect rejected the note request."
                    log_error(self.logger, error_msg)
                    show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
                    raise Exception(error_msg)
            else:
                success_msg = (
                    f"Note created successfully! Note ID: {json_response['result']}"
                )
                log_info(self.logger, success_msg)
                show_notification(
                    self.logger, f"Translation: {translation}", "✅ Anki Note Saved!"
                )
                return json_response["result"]

        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to AnkiConnect." 
            log_error(self.logger, error_msg)
            show_notification(
                self.logger,
                "Could not connect to AnkiConnect. Check if Anki is running and AnkiConnect is enabled.",
                "❌ AnkiConnect Error",
            )
            return None
        except requests.exceptions.RequestException:
            error_msg = "AnkiConnect request failed; response details were omitted."
            log_error(self.logger, error_msg)
            show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
            return None
        except Exception:
            error_msg = "AnkiConnect action failed; payload and exception details were omitted."
            log_error(self.logger, error_msg)
            show_notification(self.logger, error_msg, "❌ AnkiConnect Error")
            return None
