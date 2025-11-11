from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
import enum

if TYPE_CHECKING:
    from .events import EventHandlerType
    EventCallBackAndArgs = tuple[EventHandlerType | None, tuple[Any, ...], dict[str, Any]]

# maybe use strings
class BorderPos(enum.Enum):
    TOP_LEFT     = 0
    BOTTOM_LEFT  = 1
    TOP_CENTER   = 2
    BOTTOM_CENTER= 3
    TOP_RIGHT    = 4
    BOTTOM_RIGHT = 5

class TkTuiBase(ABC):
    __subs_for_mouse_event: dict[WidgetBase, EventCallBackAndArgs]
    __subs_for_key_event: dict[WidgetBase, EventCallBackAndArgs]

    @abstractmethod
    def __new__(cls) -> TkTuiBase:
        ...

    @abstractmethod
    def __init__(self) -> None:
        ...

    @property
    @abstractmethod
    def in_focus(self) -> Widget | None:
        ...

    @in_focus.setter
    @abstractmethod
    def in_focus(self, widget: Widget) -> None:
        ...

    @abstractmethod
    def register_for_mouse_event(
        self,
        widget: Widget,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:
        ...

    @abstractmethod
    def register_for_key_event(
        self,
        widget: Widget,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:
        ...

    @abstractmethod
    def mouse_event(self):
        """Handle the mouse event by findings all the widgets that enclose the event that have
        registered for the event and calling their callback function.
        """
        ...


    @abstractmethod
    def key_event(self, char: int):
        """Handle the key inputs by findings all the widgets that enclose the cursor that have
        registered for the event and calling their callback function.
        """
        ...


    @abstractmethod
    def exit(self) -> None:
        ...

    @abstractmethod
    def mainloop(self) -> None:
        ...


class FrameBase(ABC):

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def pack(
        self,
        side: str = "top", # TODO: enum what enum should this be? TkTui.[...] or Side.[...]
        expand: bool = False,
        fill: str = "None", # TODO enum
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
        anchor: str = "nw", # TODO enum
    ) -> None:
        ...

    @abstractmethod
    def columnconfigure(
        self,
        index: int,
        weight: int,
    ) -> None:
        ...

    @abstractmethod
    def rowconfigure(
        self,
        index: int,
        weight: int,
    ) -> None:
        ...

    @abstractmethod
    def grid(
        self,
        column: int,
        row: int,
        rowspan: int,
        columnspan: int,
        sticky: str, # TODO enum
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
    ) -> None:
        ...


    @abstractmethod
    def place(
        self,
        x: int | None = None,
        y: int | None = None,
        relx: int | None = None,
        rely: int | None = None,
        width: int | None = None,
        height: int | None = None,
        relwidth: float | None = None,
        relheight: float | None = None,

    ) -> None:
        ...

class WidgetBase(ABC):

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def pack(
        self,
        side: str = "top", # TODO: enum what enum should this be? TkTui.[...] or Side.[...]
        expand: bool = False,
        fill: str = "None", # TODO enum
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
        anchor: str = "nw", # TODO enum
    ) -> None:
        ...

    @abstractmethod
    def grid(
        self,
        column: int,
        row: int,
        rowspan: int,
        columnspan: int,
        sticky: str, # TODO enum
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
    ) -> None:
        ...

    @abstractmethod
    def place(
        self,
        x: int | None = None,
        y: int | None = None,
        relx: int | None = None,
        rely: int | None = None,
        width: int | None = None,
        height: int | None = None,
        relwidth: float | None = None,
        relheight: float | None = None,

    ) -> None:
        ...
