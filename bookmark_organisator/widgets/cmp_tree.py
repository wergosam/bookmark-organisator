# bookmark_organisator/widgets/cmp_tree.py
"""CmpTree – Baum-Widget mit Drag & Drop."""

from PyQt6.QtWidgets import QTreeWidget, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDrag


class CmpTree(QTreeWidget):
    """QTreeWidget, dessen Lesezeichen und Ordner per Maus verschoben werden
    können – innerhalb einer Seite (oben ↔ unten) und zwischen den beiden
    Seiten (links ↔ rechts)."""

    MIME = "application/x-qabstractitemmodeldatalist"

    def __init__(self, on_drop, parent=None):
        super().__init__(parent)
        self._on_drop = on_drop
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropOverwriteMode(False)

    def startDrag(self, supportedActions):
        indexes = self.selectedIndexes()
        if not indexes:
            return
        mime = self.model().mimeData(indexes)
        if mime is None:
            return
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)

    def dropEvent(self, event):
        source = event.source()
        if not isinstance(source, CmpTree):
            event.ignore()
            return
        target_item = self.itemAt(event.position().toPoint())
        indicator = self.dropIndicatorPosition()
        moved = self._on_drop(source, self, source.selectedItems(),
                              target_item, indicator)
        if moved:
            event.acceptProposedAction()
        else:
            event.ignore()