"""
code/alert/telegram_alert.py
──────────────────────────────
Telegram bot alert for accident detection.

Only called when a track passes the THRESHOLD_ACCIDENT reliability
threshold AND EfficientNet classifies severity as MINOR or SEVERE.

Author  : Trọng Nghĩa
"""

from __future__ import annotations

import numpy as np

# TODO: from telegram import Bot  (python-telegram-bot >= 20.0)


class TelegramAlert:
    """
    Sends formatted alerts to a Telegram chat.

    Usage:
        alert = TelegramAlert(token='...', chat_id='...')
        await alert.send(severity, frame, location)
    """

    def __init__(self, token: str, chat_id: str) -> None:
        # TODO: self.bot = Bot(token=token)
        # TODO: self.chat_id = chat_id
        # TODO: add rate-limiting state (avoid spam on repeated FPs)
        raise NotImplementedError

    async def send(
        self,
        severity,          # Severity enum
        frame: np.ndarray, # frame to attach as photo
        location: str = "Camera 01",
    ) -> None:
        """
        Send an alert message with a snapshot.

        Rate limit: do NOT send more than 1 alert per N seconds
                    for the same camera. (TODO: implement)
        """
        # TODO: format message text
        # TODO: encode frame as JPEG bytes
        # TODO: self.bot.send_photo(chat_id, photo, caption)
        raise NotImplementedError
