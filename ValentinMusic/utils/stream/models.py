from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueueItem:
    title: str
    dur: str
    streamtype: str
    by: str
    user_id: int
    chat_id: int
    file: str
    vidid: str
    thumb: str | None = None
    seconds: int = 0
    played: int = 0
    mystic: Any = None
    markup: str = ""
    old_dur: str | None = None
    old_second: int = 0
    speed_path: str | None = None
    speed: float = 1.0

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "dur": self.dur,
            "streamtype": self.streamtype,
            "by": self.by,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "file": self.file,
            "vidid": self.vidid,
            "thumb": self.thumb,
            "seconds": self.seconds,
            "played": self.played,
        }
