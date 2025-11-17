from __future__ import annotations
from typing import TYPE_CHECKING
from enum import StrEnum
from dataclasses import dataclass

if TYPE_CHECKING:
    from tktui.frame import Frame

class GeometryManager(StrEnum):
    """Enum for the geometry manager being used by a Frame."""
    PACK = "pack"
    GRID = "grid"
    POSITION = "position"

class Anchor(StrEnum):
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

class Fill(StrEnum):
    """Enum for the Fill attribute."""
    X = "x"
    Y = "y"
    BOTH = "both"
    NONE = "none"

class Side(StrEnum):
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
    right_left, top_bottom = [], []
    expand_cnt_rl, expand_cnt_tb = 0, 0
    non_expand_width_rl, non_expand_height_tb = 0, 0


    for el in parent.children:
        if el.__pack_info.side in ("right", "left"):
            right_left.append(el)
            # keep track of the number of expandable elements in the frame.
            # The width each can occupy is equal split of the width left from non expanding
            # elements.
            if el.__pack_info.expand: expand_cnt_rl += 1
            else: non_expand_width_rl += el.box.width
        elif el.__pack_info.side in ("top", "bottom"):
            top_bottom.append(el)
            # Same as above, except for height.
            if el.__pack_info.expand: expand_cnt_tb += 1
            else: non_expand_height_tb += el.box.height
        else:
            raise

    if expand_cnt_rl == 0: expand_width_rl  = 0
    else: expand_width_rl = max(0, (parent.box.width - non_expand_width_rl) / expand_cnt_rl)

    if expand_cnt_tb == 0: expand_height_tb = 0
    else: expand_height_tb = max(0, (parent.box.height - non_expand_height_tb) / expand_cnt_tb)

    # keep track of the last value for each direction
    right, left, top, bottom = 0, parent.box.width, 0, parent.box.height

    for el in parent.children:
        pack_info = el.__pack_info
        fill = Fill.NONE if not pack_info.expand else pack_info.fill
        # whether the element should fill the available height
        fill_vert = fill in ("both", "y")
        # whether the element should fill the available width
        fill_horz = fill in ("both", "x")

        # TODO: add checks for resulting side
        if pack_info.side in ("right", "left"):
            available_height = bottom - top
            height = available_height if fill_vert else el.box.height
            width = expand_width_rl if fill_horz else el.box.width

            # the x, y position depends on whether we are filling the available height or not and
            # the anchor
            y = top if pack_info.fill else _pack_get_xy(available_height, el.box.height, pack_info.anchor)

            if fill == Fill.NONE and pack_info.expand:
                # need to consider the anchor for the x and y position
                ...


            if pack_info.side == "right":
                left -= width
            elif pack_info.side == "left":
                right += width

        elif pack_info.side in ("top", "bottom"):

            available_width = left - right
            height = expand_height_tb if fill_vert else el.box.height
            width = available_width if fill_hozz else el.box.width

            x = _pack_get_xy(available_width, el.box.width, pack_info.anchor)

            if pack_info.side == "top":
                top += y
            elif pack_info.side == "bottom":
                bottom -= height

        else:
            raise

def _pack_get_xy(available_width: float, available_height: float, element_width: float, element_height, anchor: Anchor | str) -> float:


class Sticky(StrEnum):
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
