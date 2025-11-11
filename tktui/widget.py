from __future__ import annotations
import curses

from typing import TYPE_CHECKING
from tktui.ctx import get_app
from tktui.base import BorderPos
from tktui.frame import Frame
from tktui.box import Box

if TYPE_CHECKING:
    from tktui.tktui import TkTui

# TODO:
# 1: Padding and Marging
# 2: Redraw on screen resize
# 3: Container widgets with tkinter style packing
# 4: Scrolling containers
# 4: Custom widgets: switch, button, label, static, textarea, list, checkbox, h/v lines

class Widget:
    """Defines what it is to occupy space on a screen."""
    def __init__(
        self,
        parent: Frame | TkTui,
        x: int,
        y: int,
        height: int | None = None,
        width: int | None = None,
        border: bool = True,
        border_title: str = "",
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
        **kwargs
    ) -> None:

        if isinstance(parent, Frame):
            self.parent = parent
        else:
            self.parent = parent._root

        self.parent_win = self.parent.box.win
        self.z_index = self.parent.z_index + 1

        assert isinstance(self.parent_win, curses.window)
        self.box = Box(
            self.parent_win,
            x=x,
            y=y,
            width=width,
            height=height,
            border=border,
            border_title=border_title,
            border_pos=border_pos
        )

        self.app = get_app()

        self.focusable = True
        self.propagates_mouse_event = True
        self.propagates_key_event = True

    def draw(self) -> None:
        self.box.win.refresh()

    def focus(self) -> None:
        if self.focusable:
            self.box.win.bkgd(" ", self.box.focus_bkgd)
            self.draw()

    def defocus(self) -> None:
        self.box.win.bkgd(" ", self.box.default_bkgd)
        self.draw()
