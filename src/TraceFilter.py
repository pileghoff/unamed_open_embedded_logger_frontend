from typing import Self

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Slot
from TraceModel import TraceModel


class TraceFilter(QSortFilterProxyModel):
    def __init__(self: Self, model: TraceModel) -> None:
        super(TraceFilter, self).__init__()
        self.task_ids: set[str] = set()
        self.modules: set[str] = set()
        self.setSourceModel(model)

    def sourceModel(self: Self) -> TraceModel:  # noqa: N802
        model = super().sourceModel()
        if not isinstance(model, TraceModel):
            raise TypeError("TraceFilter does not contain TraceModel as model")
        return model

    def filterAcceptsRow(self: Self, source_row: int,  # noqa: N802
                         source_parent: QModelIndex | QPersistentModelIndex) -> bool:
        if source_row >= len(self.sourceModel().logs):
            return False
        log = self.sourceModel().logs[source_row]
        return log.task_id in self.task_ids and log.module in self.modules

    @Slot(list)
    def update_modules(self: Self, modules: list[str]) -> None:
        self.beginResetModel()
        self.modules = set(modules)
        self.endResetModel()

    @Slot(list)
    def update_tasks(self: Self, tasks: list[str]) -> None:
        self.beginResetModel()
        self.task_ids = set(tasks)
        self.endResetModel()
