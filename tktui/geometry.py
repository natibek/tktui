from typing import TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

if TYPE_CHECKING:
    from tktui.frame import Frame
    from tktui.widget import Widget

class GeometryManager(Enum, str):
    """Enum for the geometry manager being used by a Frame."""
    PACK = "pack"
    GRID = "grid"
    POSITION = "position"

class Anchor(Enum, str):
    """Enum for the Anchor attribute."""
    N = "n"
    S = "s"
    W = "w"
    E = "e"
    NW = "nw"
    NE = "ne"
    SW = "sw"
    SE = "se"
    CENTER = "center"

class Fill(Enum, str):
    """Enum for the Fill attribute."""
    X = "x"
    Y = "y"
    BOTH = "both"
    NONE = "none"

class Side(Enum, str):
    """Enum for the Side attribute."""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

class PackException(Exception):
    pass

@dataclass
class PackInfo:
    side: Side | str = Side.TOP
    expand: bool = False
    fill: Fill | str = Fill.NONE
    ipadx: int = 0
    ipady: int = 0
    padx: int = 0
    pady: int = 0
    anchor: Anchor | str = Anchor.NW


def pack_manager(parent: Frame) -> None:
    """Packs frames and widgets in a parent frame."""
    ...



class Sticky(Enum, str):
    """Enum for the Sticky attribute."""
    N = "n"
    S = "s"
    W = "w"
    E = "e"
    NW = "nw"
    NE = "ne"
    SW = "sw"
    SE = "se"
    NS = "ns"
    EW = "ew"

class GridException(Exception):
    pass

def grid_manager(
        parent: Frame,
        column: int,
        row: int,
        rowspan: int,
        columnspan: int,
        sticky: str,
        ipadx: int = 0,
        ipady: int = 0,
        padx: int = 0,
        pady: int = 0,
    ) -> None:
        ...
