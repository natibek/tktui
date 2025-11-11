from tktui.base import FrameBase, TkTuiBase

def pack_manager(
        parent: FrameBase | TkTuiBase,
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


def grid_manager(
        parent: FrameBase | TkTuiBase,
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
