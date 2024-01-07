
from typing import Iterator
from PySide6.QtWidgets import QWidget

def has_focus(w: QWidget) -> bool:
    if w.hasFocus():
        return True
    return any([c.hasFocus() for c in all_children(w)])

def all_children(w: QWidget) -> Iterator[QWidget]:
    for c in w.children():
        if isinstance(c, QWidget):
            yield c
        if hasattr(c, "children") and callable(c.children):
            yield from all_children(c)