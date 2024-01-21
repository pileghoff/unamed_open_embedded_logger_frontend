from typing import Self

from loguru import logger
from PySide6.QtCore import QMargins, QMimeData, QObject, QRect, Qt, Slot
from PySide6.QtGui import (
    QColor,
    QDrag,
    QDragEnterEvent,
    QDropEvent,
    QMouseEvent,
    QPainter,
)
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QRubberBand,
    QSplitter,
    QTabBar,
    QTabWidget,
    QWidget,
)
from utils import has_focus


class TabWidget(QTabWidget):
    def __init__(self: Self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTabBar(TabContainerBar(self))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.remove_tab)
        self.currentChanged.connect(self.active_tab_changed)

    def remove_tab(self: Self, index: int) -> None:
        super().removeTab(index)
        if self.count() == 0:
            self.close()

    def dragEnterEvent(self: Self, event: QDragEnterEvent) -> None:  # noqa: N802
        event.acceptProposedAction()

    def dragMoveEvent(self: Self, event: QMouseEvent) -> None:  # noqa: N802
        event.acceptProposedAction()

    def dropEvent(self: Self, event: QDropEvent) -> None:  # noqa: N802
        event.acceptProposedAction()

    def active_tab_changed(self: Self, new_active: int) -> None:
        def hide_child_sidebar(widget: QWidget) -> None:
            for child in widget.children():
                if hasattr(child, "hide_sidebar") and callable(child.hide_sidebar):
                    child.hide_sidebar()

        for i, child in enumerate(self.children()):
            if new_active != i:
                hide_child_sidebar(child)


class TabContainer(QSplitter):
    def __init__(self: Self, parent: QObject | None = None) -> None:  # noqa: F821
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.highlight_area: QRubberBand | None = None
        self.handle_margin = QMargins(50, 0, 50, 0)
        self.addWidget(TabWidget())

    def set_all_tabs_same_width(self: Self) -> None:
        """
        Make all the the tabs same width
        """
        new_size = [self.widget(i).sizeHint().width() for i in range(self.count())]
        self.setSizes(new_size)

    def translate_rect(self: Self, area: QRect) -> None:
        """
        Translate a rect from the global coords to coords relative to this widget
        """
        area.moveTo(area.x() + self.x(), area.y() + self.y())

    def dragEnterEvent(self: Self, event: QDragEnterEvent) -> None:  # noqa: N802
        event.acceptProposedAction()

    def dragMoveEvent(self: Self, event: QMouseEvent) -> None:  # noqa: N802
        event.acceptProposedAction()

        pos = event.pos()
        if self.highlight_area is None:
            self.highlight_area = QRubberBand(QRubberBand.Shape.Rectangle, self.parent())

        for i in range(self.count()):
            handle = self.handle(i)
            rect = handle.geometry() + self.handle_margin
            self.translate_rect(rect)
            if rect.contains(pos):
                self.highlight_area.setGeometry(rect)
                self.highlight_area.show()
                return

        rect = self.geometry()
        left_edge = QRect(rect.left(), rect.top(), 120, rect.height())
        right_edge = QRect(rect.right() - 120, rect.top(), 120, rect.height())
        if left_edge.contains(pos):
            self.highlight_area.setGeometry(left_edge)
            self.highlight_area.show()
            return

        if right_edge.contains(pos):
            self.highlight_area.setGeometry(right_edge)
            self.highlight_area.show()
            return

        for i in range(self.count()):
            widget = self.widget(i)
            rect = widget.geometry()
            self.translate_rect(rect)
            if rect.contains(pos):
                self.highlight_area.setGeometry(rect)
                self.highlight_area.show()
                return

    def dropEvent(self: Self, event: QDropEvent) -> None:  # noqa: N802
        pos = event.position().toPoint()
        drop_complete = False

        source_tab_widget = event.source().parent()
        source_tab_index = int(event.mimeData().text())
        source_tab = source_tab_widget.widget(source_tab_index)
        source_tab_title = source_tab_widget.tabText(source_tab_index)

        self.highlight_area.close()
        self.highlight_area = None

        if not isinstance(source_tab, QWidget):
            return

        if not isinstance(source_tab_widget, QTabWidget):
            return

        for i in range(self.count()):
            self.handle(i).highlight = False
            self.handle(i).update()

        # Check if drop was on the edge
        rect = self.geometry()
        left_edge = QRect(rect.left(), rect.top(), 120, rect.height())
        right_edge = QRect(rect.right() - 120, rect.top(), 120, rect.height())
        if left_edge.contains(pos) and not drop_complete:
            new_tab = TabWidget()
            self.insertWidget(0, new_tab)
            new_tab.addTab(source_tab, source_tab_title)
            drop_complete = True

        if right_edge.contains(pos) and not drop_complete:
            new_tab = TabWidget()
            self.addWidget(new_tab)
            new_tab.addTab(source_tab, source_tab_title)
            drop_complete = True

        # Check if drop was on handle, and create a new split
        for i in range(self.count()):
            handle = self.handle(i)
            rect = handle.geometry() + self.handle_margin
            self.translate_rect(rect)
            if rect.contains(pos) and not drop_complete:
                logger.info(f"Drop on handle {i}")
                new_tab = TabWidget()
                self.insertWidget(i, new_tab)
                new_tab.addTab(source_tab, source_tab_title)
                drop_complete = True

        # We go from left to right
        # Check if drop was on Tab Widget
        for i in range(self.count()):
            widget = self.widget(i)
            rect = widget.geometry()
            self.translate_rect(rect)
            if rect.contains(pos) and not drop_complete:
                logger.info(f"Drop on widget {i}")
                index = widget.addTab(source_tab, source_tab_title)
                widget.setCurrentIndex(index)
                drop_complete = True

        if source_tab_widget.count() == 0:
            source_tab_widget.close()
        self.set_all_tabs_same_width()

    def addTab(self: Self, widget: QWidget, text: str) -> None:  # noqa: N802
        for c in self.children():
            if isinstance(c, TabWidget):
                if has_focus(c):
                    index = c.addTab(widget, text)
                    c.tabBar().rename_tab(index)
                    c.setCurrentIndex(index)
                    return


class TabContainerBar(QTabBar):
    def __init__(self: Self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.tabBarDoubleClicked.connect(self.rename_tab)
        self.tab_text_editing_index = None
        self.tab_text_editor = QLineEdit("")
        self.tab_text_editor.editingFinished.connect(self.rename_tab_done)

    @Slot(int)
    def rename_tab(self: Self, index: int) -> None:
        if self.tab_text_editing_index is not None:
            self.rename_tab_done()
        self.tab_text_editing_index = index
        self.tab_text_editor.setText(self.tabText(index))
        self.tab_text_editor.setFocus()
        self.setTabButton(index, QTabBar.ButtonPosition.LeftSide, self.tab_text_editor)
        self.setTabText(index, "")

    @Slot()
    def rename_tab_done(self: Self) -> None:
        assert self.tab_text_editing_index is not None
        self.setTabText(self.tab_text_editing_index, self.tab_text_editor.text())
        self.setTabButton(self.tab_text_editing_index, QTabBar.ButtonPosition.LeftSide, None)
        self.tab_text_editing_index = None
        self.parent().setFocus()

    def mousePressEvent(self: Self, event: QMouseEvent) -> None:  # noqa: N802
        self.__drag_start = event.pos()
        self.__tab_grabbed = self.tabAt(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self: Self, event: QMouseEvent) -> None:  # noqa: N802
        if not event.buttons() & Qt.MouseButton.LeftButton:
            return
        if (
            event.position() - self.__drag_start
        ).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.__tab_grabbed))
        drag.setMimeData(mime_data)

        pixmap = self.parent().currentWidget().grab()
        painter = QPainter()
        painter.begin(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(200, 0, 200, 200))
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        drag.exec(Qt.MoveAction)
