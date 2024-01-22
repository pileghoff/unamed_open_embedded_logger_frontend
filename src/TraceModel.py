from queue import Empty, Queue
from random import choice, randint
from typing import Self, Type

from essential_generators import DocumentGenerator
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)

gen = DocumentGenerator()

modules = [gen.word() for i in range(5)]

current_time = 0

class TraceMessage:
    def __init__(self: Self, task_id: str, module: str, timestamp: int, message: str) -> None:
        self.task_id: str = task_id
        self.module: str = module
        self.timestamp: int = timestamp
        self.message: str = message.replace("\n", "")

    @classmethod
    def generate(cls: Type[Self]) -> Self:
        global current_time
        current_time += 1
        return TraceMessage(
            str(randint(2, 5)),
            choice(modules),
            current_time,
            gen.sentence(),
        )

    def __str__(self: Self) -> str:
        return f"[{self.timestamp}] {self.message}"

    def __lt__(self, other):
        return self.timestamp < other.timestamp

class TraceWorker(QThread):
    more_data: Signal = Signal(list)

    def __init__(self: Self, parent: QObject) -> None:
        super(TraceWorker, self).__init__()

    def run(self: Self) -> None:
        """Long-running task." that calls a separate class for computation"""
        while True:
            QThread.msleep(randint(2, 20))
            self.more_data.emit([TraceMessage.generate()])


class TraceModel(QAbstractListModel):
    global_time_updated = Signal(int)

    def __init__(self: Self) -> None:
        print("New trace model")
        super(TraceModel, self).__init__()
        self.logs: list[TraceMessage] = []
        for i in range(50000):
            self.logs.append(TraceMessage.generate())
        self.in_buffer: Queue = Queue()
        self.thread = TraceWorker(self)
        self.thread.more_data.connect(self.more_data)
        self.thread.start()
        self.modules = modules

        self.new_data_timer = QTimer(self)
        self.new_data_timer.timeout.connect(self.update_data)
        self.new_data_timer.start(50)

        self.global_time = 0


    def timestamp_at_index(self: Self, index: QModelIndex) -> int:
        return self.logs[index.row()].timestamp

    def data(self: Self, index: QModelIndex | QPersistentModelIndex, role: int = -1) -> TraceMessage | str | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            log = self.logs[index.row()]
            return str(log)

        if role == Qt.ItemDataRole.UserRole:
            return self.logs[index.row()]

        return None

    @Slot(list)
    def more_data(self: Self, data: list[TraceMessage]) -> None:
        for d in data:
            self.in_buffer.put(d)

    @Slot()
    def update_data(self: Self) -> None:
        new_data = []
        while True:
            try:
                new_data.append(self.in_buffer.get_nowait())
            except Empty:
                break
        new_rows = len(new_data)

        self.beginInsertRows(QModelIndex(), len(self.logs), len(self.logs) + new_rows)
        self.logs.extend(new_data)
        self.endInsertRows()

    def rowCount(  # noqa: N802
        self: Self, parent: QModelIndex | QPersistentModelIndex | None = None
    ) -> int:
        if parent is None:
            parent = QModelIndex()
        return len(self.logs)

    def parent(self: Self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def columnCount(  # noqa: N802
        self: Self, parent: QModelIndex | QPersistentModelIndex | None = None
    ) -> int:
        return 1

    def index(self: Self, row: int, column: int, parent: QModelIndex | None = None) -> QModelIndex:
        return self.createIndex(row, column, self.logs[row])

    def clear(self: Self) -> None:
        self.beginRemoveRows(QModelIndex(), 0, len(self.logs))
        self.logs = []
        self.endRemoveRows()

    def pause_stream(self: Self) -> None:
        pass

    def start_stream(self: Self) -> None:
        pass

    def set_active(self: Self, index: QModelIndex) -> None:
        self.global_time = self.logs[index.row()].timestamp
        self.global_time_updated.emit(self.global_time)
