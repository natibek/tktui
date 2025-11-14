from __future__ import annotations
from typing import TYPE_CHECKING

import curses
from tktui.ctx import get_app
from tktui.base import BorderPos
from tktui.box import Box
from tktui.geometry import pack_manager, GeometryManager, Side, Fill, Anchor, PackException, GridException, PackInfo

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

        self.children: list[Widget | Frame] = []

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

        self.geometry_manager: GeometryManager | None = None
        self.__pack_info: PackInfo | None = None


    def draw(self) -> None:
        self.box.win.refresh()

    def pack(
        self,
        after: Widget | Frame | None = None,
        before: Widget | Frame | None = None,
        side: Side | str = Side.TOP,
        expand: bool = False,
        fill: Fill | str = Fill.NONE,
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
        anchor: Anchor | str = Anchor.NW,
        in_: Frame | None = None,
    ) -> None:

        if self.parent is None:
            raise PackException("Can not pack the root frame")

        if in_:
            parent = in_
        else:
            parent = self.parent

        self.__pack_info = PackInfo(
            side=side,
            expand=expand,
            fill=fill,
            ipadx=ipadx,
            ipady=ipady,
            padx=padx,
            pady=pady,
            anchor=anchor,
        )

        parent.pack_child(
            self,
            after,
            before,
        )

    def pack_child(
        self,
        target: Widget | Frame,
        after: Widget | Frame | None = None,
        before: Widget | Frame | None = None,
    ) -> None:
        assert isinstance(target, Widget)
        if self.geometry_manager == GeometryManager.GRID:
            raise PackException("Already using grid geometry manager")

        if not self.geometry_manager:
            self.geometry_manager = GeometryManager.PACK

        if after or before:
            if len(self.children) == 0:
                raise PackException()

            l = 0
            if after:
                for idx, frame_or_widget in enumerate(self.children):
                    l+=1
                    if frame_or_widget == after:
                        self.children.insert(l, target)
                        l+=1
                        break
                else:
                    raise PackException(f"Could not pack after {after}. {after} was not a found in {self}.")


            if before:
                if l >= len(self.children):
                    raise PackException(
                        f"Could not pack after {after} and before {before}. Ordering is impossible."
                    )

                for idx, frame_or_widget in enumerate(self.children[l:]):
                    if frame_or_widget == before:
                        self.children.insert(idx + l, target)
                        break
                else:
                    raise PackException(
                        f"Could not pack {"after" + str(after) + " " if after else ""}"
                        "and before {before}. Either ordering is impossible or {after} and/or {before} "
                        "are not found in {self}."
                    )

        pack_manager(self)



