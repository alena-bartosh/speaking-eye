import logging
from typing import Callable, Optional

from gi.repository import GLib, GObject


class Timer:
    def __init__(self, name: str,
                 handler: Callable[[], None],
                 interval_ms: int,
                 repeat: bool,
                 logger: logging.Logger) -> None:
        self.name = name
        self.handler = handler
        self.interval_ms = interval_ms
        self.repeat = repeat
        self.timer_id: Optional[int] = None
        self.is_started = False

        self.logger = logger

    def start(self) -> None:
        if self.is_started:
            self.logger.debug(f'Timer [{self.name}] has already started, thus will not start again')
            return

        self.timer_id = GLib.timeout_add(self.interval_ms, self.__internal_handler)
        self.is_started = True

    def stop(self) -> None:
        if not self.is_started:
            self.logger.debug(f'Timer [{self.name}] is not started, thus will not stop')
            return

        GObject.source_remove(self.timer_id)
        self.timer_id = None
        self.is_started = False

    def __internal_handler(self) -> bool:
        self.handler()

        if not self.repeat:
            self.is_started = False

        return self.repeat
