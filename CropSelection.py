import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC

class CropSelectionView(QW.QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self.start_pos = None
        self.selection_rect = None

    def mousePressEvent(self, event):
        if event.button() == QC.Qt.LeftButton:
            self.start_pos = self.mapToScene(event.pos())  # マウス開始位置
            if self.selection_rect:
                self.scene.removeItem(self.selection_rect)  # 以前の選択を削除
            self.selection_rect = QW.QGraphicsRectItem()
            self.selection_rect.setPen(
                QG.QPen(QC.Qt.red, 2, QC.Qt.DashLine))  # 破線の枠
            self.scene.addItem(self.selection_rect)

    def mouseMoveEvent(self, event):
        if self.start_pos and self.selection_rect:
            end_pos = self.mapToScene(event.pos())  # マウス終了位置
            rect = QC.QRectF(self.start_pos, end_pos).normalized()  # 位置補正
            self.selection_rect.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == QC.Qt.LeftButton and self.selection_rect:
            print("選択範囲:", self.selection_rect.rect())  # デバッグ用に範囲を表示
