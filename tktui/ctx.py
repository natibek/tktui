from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .tktui import TkTui

# Global context for the running app
app: "TkTui | None" = None

def get_app() -> "TkTui":
    if _app is None:
        raise RuntimeError("TkTui has not been created yet.")
    return _app

def _set_app(app: "TkTui") -> None:
    global _app
    _app = app
