from datetime import datetime
from enum import auto, Enum
from pathlib import Path
from typing import Optional, Any, Tuple

from gi.repository import Notify
from pyee import BaseEventEmitter


class NotificationEvent(Enum):
    CLOSED = auto()
    LEFT_BUTTON_CLICKED = auto()
    RIGHT_BUTTON_CLICKED = auto()


class NotificationButton(Enum):
    LEFT = 'left'
    RIGHT = 'right'


ButtonCaptionsType = Tuple[
    str,  # left
    str,  # right
]


class Notification:
    """
    Create notification with the specified urgency, message, icon.
    Add buttons and listenable events for notification closing / buttons clicking
    """
    __notification_button_to_event_map = {
        NotificationButton.LEFT.value: NotificationEvent.LEFT_BUTTON_CLICKED.value,
        NotificationButton.RIGHT.value: NotificationEvent.RIGHT_BUTTON_CLICKED.value,
    }

    def __init__(self,
                 title: str,
                 message: str,
                 icon: Path,
                 urgency: Optional[Notify.Urgency] = None,
                 listen_closed_event: bool = False) -> None:
        self.__raw_notification = Notify.Notification.new(title, message, str(icon))

        if urgency is not None:
            self.__raw_notification.set_urgency(urgency)

        self.last_shown: Optional[datetime] = None

        self.event = BaseEventEmitter()

        if listen_closed_event:
            self.__raw_notification.connect('closed', self.__on_closed)

    def __on_closed(self, notification: Notify.Notification) -> None:
        self.event.emit(NotificationEvent.CLOSED.value)

    def __on_button_clicked(self, notification: Notify.Notification, action_id: str, arg: Any) -> None:
        event = self.__notification_button_to_event_map[action_id]

        # TODO: send self to handler as an argument
        self.event.emit(event)

    def add_buttons(self, button_captions: ButtonCaptionsType) -> None:
        """Add two active buttons to notification - left and right"""
        left, right = button_captions

        self.__raw_notification.add_action(
            NotificationButton.LEFT.value,
            left,
            self.__on_button_clicked,
            None
        )

        self.__raw_notification.add_action(
            NotificationButton.RIGHT.value,
            right,
            self.__on_button_clicked,
            None
        )

    def show(self) -> None:
        self.__raw_notification.show()

        self.last_shown = datetime.now()
