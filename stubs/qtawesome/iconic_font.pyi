"""
This type stub file was generated by pyright.
"""

import os

from qtpy.QtCore import QObject
from qtpy.QtGui import QIconEngine

r"""

Iconic Font
===========

A lightweight module handling iconic fonts.

It is designed to provide a simple way for creating QIcons from glyphs.

From a user's viewpoint, the main entry point is the ``IconicFont`` class which
contains methods for loading new iconic fonts with their character map and
methods returning instances of ``QIcon``.

"""
SYSTEM_FONTS = ...
if os.name == 'nt':
    ...
def text_color(): # -> QColor:
    ...

def text_color_disabled(): # -> QColor:
    ...

_default_options = ...
def set_global_defaults(**kwargs): # -> None:
    """Set global defaults for the options passed to the icon painter."""
    ...

class CharIconPainter:
    """Char icon painter."""
    def paint(self, iconic, painter, rect, mode, state, options): # -> None:
        """Main paint method."""
        ...



class FontError(Exception):
    """Exception for font errors."""


class CharIconEngine(QIconEngine):
    """Specialization of QIconEngine used to draw font-based icons."""
    def __init__(self, iconic, painter, options) -> None:
        ...

    def paint(self, painter, rect, mode, state): # -> None:
        ...

    def pixmap(self, size, mode, state): # -> QPixmap:
        ...



class IconicFont(QObject):
    """Main class for managing iconic fonts."""
    def __init__(self, *args) -> None:
        """IconicFont Constructor.

        Parameters
        ----------
        ``*args``: tuples
            Each positional argument is a tuple of 3 or 4 values:
            - The prefix string to be used when accessing a given font set,
            - The ttf font filename,
            - The json charmap filename,
            - Optionally, the directory containing these files. When not
              provided, the files will be looked for in the QtAwesome ``fonts``
              directory.
        """
        ...

    def load_font(self, prefix, ttf_filename, charmap_filename, directory=...): # -> None:
        """Loads a font file and the associated charmap.

        If ``directory`` is None, the files will be looked for in
        the qtawesome ``fonts`` directory.

        Parameters
        ----------
        prefix: str
            Prefix string to be used when accessing a given font set
        ttf_filename: str
            Ttf font filename
        charmap_filename: str
            Charmap filename
        directory: str or None, optional
            Directory path for font and charmap files
        """
        ...

    def icon(self, *names, **kwargs): # -> QIcon:
        """Return a QIcon object corresponding to the provided icon name."""
        ...

    def font(self, prefix, size): # -> QFont:
        """Return a QFont corresponding to the given prefix and size."""
        ...

    def rawfont(self, prefix, size, hintingPreference=...):
        """Return a QRawFont corresponding to the given prefix and size."""
        ...

    def set_custom_icon(self, name, painter): # -> None:
        """Associate a user-provided CharIconPainter to an icon name.

        The custom icon can later be addressed by calling
        icon('custom.NAME') where NAME is the provided name for that icon.

        Parameters
        ----------
        name: str
            name of the custom icon
        painter: CharIconPainter
            The icon painter, implementing
            ``paint(self, iconic, painter, rect, mode, state, options)``
        """
        ...



