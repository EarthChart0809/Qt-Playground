import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC


class LayerListWidget(QW.QListWidget):
    layer_order_changed = QC.Signal(list)  # レイヤーの順番が変更されたときに発火するシグナル
    layer_renamed = QC.Signal(str, str)  # (old_name, new_name)
    layer_deleted = QC.Signal(str)
    layer_duplicated = QC.Signal(str)
    layer_visibility_changed = QC.Signal(str, bool)
    layer_lock_changed = QC.Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QW.QListWidget.InternalMove)  # ドラッグ＆ドロップを許可
        self.setSelectionMode(QW.QListWidget.SingleSelection)  # 単一選択
        self.setContextMenuPolicy(QC.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setDragDropMode(QW.QAbstractItemView.InternalMove)
        self.setAcceptDrops(True)

    def update_layer_list(self, layer_names):
        """レイヤーリストを更新する"""
        self.clear()  # 既存のリストをクリア
        for name in layer_names:
            self.add_layer_item(name)  # レイヤーアイテムを追加

    def dropEvent(self, event):
        """アイテムのドロップ時にレイヤーの順番を更新"""
        super().dropEvent(event)  # 標準のドロップ処理を実行
        new_order = [self.item(i).text() for i in range(self.count())]
        self.layer_order_changed.emit(new_order)  # シグナルを発火

    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return

        layer_name = item.text()
        menu = QW.QMenu(self)

        rename_action = menu.addAction("名前変更")
        delete_action = menu.addAction("削除")
        duplicate_action = menu.addAction("複製")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == rename_action:
            self.rename_layer(layer_name)
        elif action == delete_action:
            self.layer_deleted.emit(layer_name)
        elif action == duplicate_action:
            self.layer_duplicated.emit(layer_name)

    def rename_layer(self, old_name):
        new_name, ok = QW.QInputDialog.getText(
            self, "レイヤー名変更", "新しいレイヤー名:", text=old_name)
        if ok and new_name and new_name != old_name:
            self.layer_renamed.emit(old_name, new_name)

    def add_layer_item(self, layer_name):
        item = QW.QListWidgetItem(layer_name, self)

        # 👁️ 表示ボタン（デフォルト: 表示）
        visibility_button = QW.QPushButton("👁️")
        visibility_button.setFixedSize(24, 24)
        visibility_button.clicked.connect(lambda: self.toggle_visibility(layer_name, visibility_button))

        # 🔒 ロックボタン（デフォルト: 編集可能）
        lock_button = QW.QPushButton("🔓")
        lock_button.setFixedSize(24, 24)
        lock_button.clicked.connect(lambda: self.toggle_lock(layer_name, lock_button))

        # レイヤー名ラベル
        name_label = QW.QLabel(layer_name)

        # レイアウト設定
        widget = QW.QWidget()
        layout = QW.QHBoxLayout(widget)
        layout.addWidget(visibility_button)
        layout.addWidget(lock_button)
        layout.addWidget(name_label)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        self.setItemWidget(item, widget)

    def toggle_visibility(self, layer_name, button):
        is_visible = self.parent().toggle_layer_visibility(layer_name)  # 表示/非表示を切り替え
        button.setText("👁️" if is_visible else "🚫")  # 👁️ → 🚫 に変更

    def toggle_lock(self, layer_name, button):
        is_locked = self.parent().toggle_layer_lock(layer_name)  # ロック/解除を切り替え
        button.setText("🔒" if is_locked else "🔓")  # 🔓 → 🔒 に変更