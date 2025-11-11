from __future__ import annotations
from typing import TYPE_CHECKING

import curses
from tktui.ctx import get_app
from tktui.base import BorderPos
from tktui.box import Box

if TYPE_CHECKING:
    from tktui.tktui import TkTui
    from tktui.widget import Widget

class Frame:
    """Defines what it is to occupy space on a screen."""
    def __init__(
        self,
        parent: Frame | TkTui,
        border: bool = False,
        border_title: str = "",
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
        **kwargs
    ) -> None:

        self.children: list[Widget] = []

        if isinstance(parent, Frame):
            self.parent = parent
            self.parent_win = parent.box.win
            self.z_index = parent.z_index + 1
        else:
            self.z_index = 1
            if hasattr(parent, "_root"):
                # the _root frame for the app has been created yet
                self.parent = parent._root
                self.parent_win = parent._root.box.win
            else:
                assert "tktui_stdscr" in kwargs
                win = kwargs["tktui_stdscr"]
                assert isinstance(win, curses.window)
                self.parent_win = win
                self.parent = None

        assert isinstance(self.parent_win, curses.window)
        self.app = get_app()
        self.box = Box(
            self.parent_win,
            border=border,
            border_title=border_title,
            border_pos=border_pos
        )


    def draw(self) -> None:
        self.box.win.refresh()
