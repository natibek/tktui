from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
import curses

from tktui.base import TkTuiBase
from tktui.widget import Widget
from tktui.ctx import _set_app
from tktui.colors import Colors
from tktui.events import MouseEvent, KeyEvent
from tktui.frame import Frame

if TYPE_CHECKING:
    from .events import EventHandlerType
    EventCallBackAndArgs = tuple[EventHandlerType | None, tuple[Any, ...], dict[str, Any]]


class TkTui:
    __subs_for_mouse_event: dict[Widget, EventCallBackAndArgs] = {}
    __subs_for_key_event: dict[Widget, EventCallBackAndArgs] = {}

    __inst: TkTui | None = None

    def __new__(cls) -> TkTui:
        if cls.__inst is None:
            app = super().__new__(cls)
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

        self._root= Frame(self, tktui_stdscr = self.stdscr)
        self._root.draw()

        curses.curs_set(1)

        # defaults
        # self.stdscr.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.flushinp()

        # enable mouse
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

        self.cur_window = self._root
        # self.register_for_mouse_event(self._root)
        self._in_focus = None

    @property
    def in_focus(self) -> Widget | None:
        return self._in_focus

    @in_focus.setter
    def in_focus(self, widget: Widget) -> None:
        if not widget.focusable:
            return

        if self._in_focus:
            self._in_focus.defocus()

        self._in_focus = widget
        widget.focus()

    def register_for_mouse_event(
        self,
        widget: Widget,
        callback: EventHandlerType | None = None,
        args: tuple[Any, ...] = tuple(),
        kwargs: dict[str, Any] = {},
    ) -> None:

        self.__subs_for_mouse_event[widget] = (callback, args, kwargs)

    def register_for_key_event(
        self,
        widget: Widget,
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
        widgets_containing_mouse.sort(key=lambda tup: tup[0].parent.z_index, reverse=True)

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
        y, x = self._root.win.getyx()
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
        self._root.win.keypad(False)
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
                    # self._root.win.addch(chr(char))
                    self.key_event(char)

                # important for updating the screen at the end of the loop
                self.cur_window.win.refresh()


            # clears the screen but keeps the windows
            # self.cur_window.win.erase()


