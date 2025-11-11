from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
import curses

from tktui.base import TkTuiBase, WidgetBase, FrameBase, BorderPos
from tktui.widget import Widget
from tktui.ctx import _set_app, get_app
from tktui.colors import Colors
from tktui.events import MouseEvent, KeyEvent

if TYPE_CHECKING:
    from .events import EventHandlerType
    EventCallBackAndArgs = tuple[EventHandlerType | None, tuple[Any, ...], dict[str, Any]]

class Frame(FrameBase):
    """Defines what it is to occupy space on a screen."""
    __num_roots: int = 0
    def __init__(
        self,
        parent: Frame | TkTui | None,
        #border: bool = True,
        #border_title: str = "",
        #border_pos: BorderPos = BorderPos.TOP_LEFT,
        # padding: tuple[int, int] = (0, 0),
        **kwargs
    ) -> None:

        self.parent = parent

        if not parent: # we are creating the root box
            if self.__num_roots != 0:
                raise ValueError("Can not create more than one root Frame. Pass the parent as an argument.")

            self.__num_roots += 1
            # Expect that curses.initscr() has been called and the resulting screen is passed as
            # a keyword argument.
            assert "stdscr" in kwargs and isinstance(kwargs["stdscr"], curses.window)
            self.parent_win: curses.window = kwargs["stdscr"]
            self.parent_win.clear()
            self.z_index = 0
        elif isinstance(parent, TkTui):
            self.parent_win = parent.root.win
            self.z_index = 1
        else:
            self.parent_win = parent.win
            self.z_index = parent.z_index + 1

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
        self.children = []

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

class TkTui(TkTuiBase):
    __subs_for_mouse_event: dict[WidgetBase, EventCallBackAndArgs] = {}
    __subs_for_key_event: dict[WidgetBase, EventCallBackAndArgs] = {}

    __inst: TkTui | None = None

    def __new__(cls) -> TkTui:
        if cls.__inst is None:
            app = cast(TkTui, super().__new__(cls))
            cls.__inst = app
            # update the global context with a new TkTui
            _set_app(app)
        else:
            app = cls.__inst


        return app

    def __init__(self) -> None:
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        self.colors = Colors()
        self.colors._generate_defaults()

        self.root= Frame(None, 0, 0, stdscr = self.stdscr)
        self.root.draw()

        curses.curs_set(1)

        # defaults
        # self.stdscr.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.flushinp()

        # enable mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        self.cur_window = self.root
        self.register_for_mouse_event(self.root)
        self._in_focus = None

    @property
    def in_focus(self) -> WidgetBase | None:
        return self._in_focus

    @in_focus.setter
    def in_focus(self, widget: WidgetBase) -> None:
        if not widget.focusable:
            return

        if self._in_focus:
            self._in_focus.defocus()

        self._in_focus = widget
        widget.focus()

    def register_for_mouse_event(
        self,
        widget: WidgetBase,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:

        self.__subs_for_mouse_event[widget] = (callback, args, kwargs)

    def register_for_key_event(
        self,
        widget: WidgetBase,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:
        self.__subs_for_key_event[widget] = (callback, args, kwargs)

    def mouse_event(self):
        """Handle the mouse event by findings all the widgets that enclose the event that have
        registered for the event and calling their callback function.
        """
        (_, x, y, _, bstate) = curses.getmouse()
        self.cur_window.win.move(y, x)
        event = MouseEvent(x, y, bstate)

        widgets_containing_mouse: list[tuple[Widget, EventCallBackAndArgs]] = []
        if bstate & curses.BUTTON1_CLICKED:
            for widget, callback_and_args in self.__subs_for_mouse_event.items():
                # find all the widgets that enclose the location of the mouse event
                if widget.win.enclose(y, x):
                    widgets_containing_mouse.append((widget, callback_and_args))


        if not widgets_containing_mouse:
            return

        # sort the widgets by their depth in reverse order
        # TODO: handle overlapping widgets
        widgets_containing_mouse.sort(key=lambda tup: tup[0].z_index, reverse=True)

        focused = False
        for widget, callback_and_args in widgets_containing_mouse:
            if not focused and widget.focusable:
                self.in_focus = widget
                focused = True

            if not event.stop_propagation:
                event.widget = widget
                callback, args, kwargs = callback_and_args

                if callback is None:
                    continue

                callback(event, *args, **kwargs)
                if not widget.propagates_mouse_event:
                    event.stop()


    def key_event(self, char: int):
        """Handle the key inputs by findings all the widgets that enclose the cursor that have
        registered for the event and calling their callback function.
        """
        y, x = self.root.win.getyx()
        event = KeyEvent(x, y, char)

        widgets_containing_cursor: list[tuple[Widget, EventCallBackAndArgs]] = []

        for widget, callback_and_args in self.__subs_for_key_event.items():
            if widget.win.enclose(y, x):
                widgets_containing_cursor.append((widget, callback_and_args))

        if not widgets_containing_cursor:
            return

        widgets_containing_cursor.sort(key=lambda tup: tup[0].z_index, reverse=True)
        for widget, callback_and_args in widgets_containing_cursor:
            if not event.stop_propagation:
                event.widget = widget
                callback, args, kwargs = callback_and_args
                if callback is None:
                    continue
                callback(event, *args, **kwargs)
                if not widget.propagates_key_event:
                    event.stop()


    def exit(self) -> None:
        curses.nocbreak()
        self.root.win.keypad(False)
        curses.echo()
        curses.endwin()
        curses.flushinp()

        self._running= False

    def mainloop(self) -> None:
        self._running = True
        while self._running:
            char = self.cur_window.win.getch()
            if char == -1:
                continue

            if "q" == chr(char):
                self.exit()
                # break
            else:
                if char == curses.KEY_MOUSE:
                    self.mouse_event()
                else:
                    # self.root.win.addch(chr(char))
                    self.key_event(char)

                # important for updating the screen at the end of the loop
                self.cur_window.win.refresh()


            # clears the screen but keeps the windows
            # self.cur_window.win.erase()


