from PySide6.QtCore import QRect, QTimer, Slot
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
)


class timelineWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(QHBoxLayout())
        self.scene = QGraphicsScene(QRect(0, 0, 500, 500))
        self.view = QGraphicsView(self.scene, self)
        self.view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.view.show()

        update_timer = QTimer(self)
        update_timer.timeout.connect(self.update)
        update_timer.start(100)

    @Slot()
    def update(self):
        height = self.view.geometry().height()
        width = 500
        self.scene.setSceneRect(QRect(0, 0, width, height))
        self.view.update()
