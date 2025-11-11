from __future__ import annotations
from typing import TYPE_CHECKING

import curses
from tktui.ctx import get_app
from tktui.base import BorderPos, FrameBase

if TYPE_CHECKING:
    from tktui.tktui import TkTui
    from tktui.widget import Widget

class Frame: #(FrameBase):
    """Defines what it is to occupy space on a screen."""
    def __init__(
        self,
        parent: Frame | TkTui,
        #border: bool = True,
        #border_title: str = "",
        #border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
        **kwargs
    ) -> None:


        if isinstance(parent, Frame):
            self.parent = parent
            self.parent_win = parent.win
            self.z_index = parent.z_index + 1
        else:
            self.z_index = 1
            if hasattr(parent, "_root"):
                # the _root frame for the app has been created yet
                self.parent = parent._root
                self.parent_win = parent._root.win
            else:
                assert "tktui_stdscr" in kwargs
                win = kwargs["tktui_stdscr"]
                assert isinstance(win, curses.window)
                self.parent_win = win
                self.parent = None


        assert isinstance(self.parent_win, curses.window)
        self.height = self.parent_win.getmaxyx()[0]
        self.width = self.parent_win.getmaxyx()[1]

        self.app = get_app()
        self.win = self.parent_win.derwin(self.height, self.width, 0, 0)
        self.focus_bkgd = self.app.colors["WHITE_BLUE"]
        self.default_bkgd = self.app.colors["WHITE_GREEN"]

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        # list of the child Frames and Widgets
        self.children: list[Widget] = []

    def remove_border(self) -> None:
        """Remove the border around the box"""
        self.win.border(1,1,1,1,1,1,1,1)

    def add_border(self) -> None:
        """Add the border around the box"""
        self.win.border(0,0,0,0,0,0,0,0)


    @property
    def border(self) -> bool:
        return self._border

    @border.setter
    def border(self, border: bool) -> None:
        if border:
            self._border = True
            self.add_border()
            # self.win.box()
        else:
            self._border = False
            self.remove_border()


    def update_border_title(self, title: str, border_pos: BorderPos | None = None) -> None:
        """Write the border title."""
        # TODO: Include position arguments
        X_OFFSET = 3
        self.border_title = title

        if border_pos:
            self.border_pos = border_pos

        if not title:
            return

        if self.border_pos.value % 2 == 0:
            y = 0
        else:
            y = self.height - 1

        match self.border_pos:
            case BorderPos.TOP_LEFT | BorderPos.BOTTOM_LEFT:
                x = X_OFFSET
            case BorderPos.TOP_RIGHT | BorderPos.BOTTOM_RIGHT:
                x = max(0, self.width - X_OFFSET - len(title))
            case BorderPos.TOP_CENTER | BorderPos.BOTTOM_CENTER:
                x = max(0, (self.width // 2)  - (len(title) // 2))

        if len(title) >= self.width - x:
            title = title[:self.width - x]
        self.win.addstr(y, x, title)

    def draw(self) -> None:
        self.win.refresh()
