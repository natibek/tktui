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
        pack_info = el.__pack_info
        if pack_info.side in ("left", "right"):
            right_left.append(el)
            # keep track of the number of expandable elements in the frame.
            # The width each can occupy is equal split of the width left from non expanding
            # elements.
            if pack_info.expand:
                expand_cnt_rl += 1
                # no need to account for the internal padding since it will be part of the width
                non_expand_width_rl += pack_info.padx*2
            else: non_expand_width_rl += el.box.content_width + pack_info.ipadx*2 + pack_info.padx*2
        elif pack_info.side in ("top", "bottom"):
            top_bottom.append(el)
            # Same as above, except for height.
            if pack_info.expand:
                expand_cnt_tb += 1
                non_expand_height_tb += pack_info.pady*2
            else: non_expand_height_tb += el.box.content_height + pack_info.ipady*2 + pack_info.pady*2
        else:
            raise

    if expand_cnt_rl == 0: expand_width_rl  = 0
    else: expand_width_rl = max(0, (parent.box.width - non_expand_width_rl) / expand_cnt_rl)

    if expand_cnt_tb == 0: expand_height_tb = 0
    else: expand_height_tb = max(0, (parent.box.height - non_expand_height_tb) / expand_cnt_tb)

    # keep track of the last value for each direction
    left , right, top, bottom = 0, parent.box.width, 0, parent.box.height

    for el in parent.children:
        pack_info = el.__pack_info
        fill = Fill.NONE if not pack_info.expand else pack_info.fill
        # whether the element should fill the available height
        fill_vert = fill in ("both", "y")
        # whether the element should fill the available width
        fill_horz = fill in ("both", "x")
        # TODO: add checks for resulting side
        content_width = el.box.width + pack_info.ipadx*2
        content_height = el.box.height + pack_info.ipady*2

        if pack_info.side in ("left", "right"):
            available_height = bottom - top
            height = max(available_height, content_height) if fill_vert else content_height
            width = max(expand_width_rl, content_width) if fill_horz else content_width
            # available width is either what it can expand to if expandable or it's own width
            # with internal padding
            available_width = width

            # default y and x
            y = top + pack_info.pady
            x = left + pack_info.padx if pack_info.side == "left" else right - width - pack_info.padx
            # the x, y position depends on whether we are filling the available height or not and
            # the anchor
            if pack_info.expand and fill != Fill.BOTH:
                # need to consider the anchor for the x and y position

                if fill == Fill.NONE or fill == Fill.X:
                    # for the y
                    if pack_info.anchor[0] == "n":
                        y = top + pack_info.pady
                    elif pack_info.anchor[0] == "s":
                        y = top + available_height - height + pack_info.pady
                    else:
                        y = top + (available_height // 2)  - (height // 2)

                if fill == Fill.NONE or fill == Fill.Y:
                    if pack_info.anchor[0] == "w":
                        x = left if pack_info.side == "left" else right - available_width + width
                    elif pack_info.anchor[0] == "e":
                        x = left + available_width - width if pack_info.side == "left" else right - width
                    else:
                        if pack_info.side == "left":
                            x = left + (available_width // 2)  - (width // 2)
                        else:
                            x = right - (available_width // 2)  + (width // 2)

            if pack_info.side == "right": right -= width
            elif pack_info.side == "left": left += width

        else:
            assert pack_info.side in ("top", "bottom")

            available_width = left - right
            width = available_width if fill_horz else el.box.width
            available_height = height = expand_height_tb if fill_vert else el.box.height

            if pack_info.side == "top": top += height
            elif pack_info.side == "bottom": bottom -= height

        el.box.update(x, y, width, height, available_width, available_height)


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
