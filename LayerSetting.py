import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC

class LayerListWidget(QW.QListWidget):
    layer_order_changed = QC.Signal(list)  # レイヤーの順番が変更されたときに発火するシグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QW.QListWidget.InternalMove)  # ドラッグ＆ドロップを許可
        self.setSelectionMode(QW.QListWidget.SingleSelection)  # 単一選択
        self.setAcceptDrops(True)

    def update_layer_list(self, layer_names):
        """レイヤーリストを更新する"""
        self.clear()  # 既存のリストをクリア
        for name in layer_names:
            item = QW.QListWidgetItem(name)  # レイヤー名をアイテム化
            self.addItem(item)  # リストウィジェットに追加

    def dropEvent(self, event):
        """アイテムのドロップ時にレイヤーの順番を更新"""
        super().dropEvent(event)  # 標準のドロップ処理を実行
        new_order = [self.item(i).text() for i in range(self.count())]
        self.layer_order_changed.emit(new_order)  # シグナルを発火

