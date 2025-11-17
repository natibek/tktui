import curses
from tktui.ctx import get_app
from enum import StrEnum

class BorderPos(StrEnum):
    """Enum for the Anchor attribute."""
    N = "n"
    S = "s"
    NW = "nw"
    NE = "ne"
    SW = "sw"
    SE = "se"

class BorderPosError(Exception):
    ...

class Box:
    def __init__(
        self,
        parent_window: curses.window,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
        border: bool = False,
        border_title: str = "",
        border_pos: BorderPos | str = BorderPos.NW,
        # padding: tuple[int, int] = (0, 0),
    ):
        self.parent_win = parent_window

        self.content_width = 10
        self.content_height = 10
        self.height = height or self.parent_win.getmaxyx()[0]
        self.width = width or self.parent_win.getmaxyx()[1]

        self.x = x
        self.y = y

        self.app = get_app()
        self.win = self.parent_win.derwin(self.height, self.width, y, x)

        self.focus_bkgd = self.app.colors["WHITE_BLUE"]
        self.default_bkgd = self.app.colors["WHITE_GREEN"]

        self.win.bkgd(" ", self.default_bkgd)

        # for mouse presses
        self.win.keypad(True)
        self.win.nodelay(True)

        # list of the child Frames and Widgets
        self.border = border
        self.update_border_title(border_title, border_pos=border_pos)

    def remove_border(self) -> None:
        """Remove the border around the box"""
        self.win.border(1,1,1,1,1,1,1,1)
        # self.win.box()

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
        else:
            self._border = False
            self.remove_border()


    def update_border_title(self, title: str, border_pos: BorderPos | str | None = None) -> None:
        """Write the border title."""
        if not title:
            return

        X_OFFSET = 3

        if border_pos:
            if not border_pos in set(BorderPos):
                raise BorderPosError(f"Value for border position {self.border_pos} is not valid.")

            self.border_pos = border_pos

        self.border_title = title

        if self.border_pos.startswith("n"):
            y = 0
        else:
            y = self.height - 1

        match self.border_pos[-1]:
            case "w":
                x = X_OFFSET
            case "e":
                x = max(0, self.width - X_OFFSET - len(title))
            case _:
                assert self.border_pos in ("n", "s")
                x = max(0, (self.width // 2)  - (len(title) // 2))

        if len(title) >= self.width - x:
            title = title[:self.width - x]
        self.win.addstr(y, x, title)

    def update(self, x: float, y: float, width: float, height: float, available_width: float, available_height: float) -> None:
        ...
