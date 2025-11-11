import curses
from tktui.base import BorderPos
from tktui.ctx import get_app

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
        border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
    ):
        self.parent_win = parent_window
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
