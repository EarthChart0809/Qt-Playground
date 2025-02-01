import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC

class PixelCanvas(QW.QWidget):
    def __init__(self, grid_size=16, pixel_size=20):
        super().__init__()
        self.grid_size = grid_size
        self.pixel_size = pixel_size
        self.pixels = {}  # ピクセルの色を保存
        self.current_color = QG.QColor(0, 0, 0)  # 初期色（黒）
        self.show_grid = True  # グリッド線の表示/非表示

        self.history = []
        self.future = []

        self.layers = {
            "background": {},  # 背景レイヤー
            "foreground": {}   # 前景レイヤー
        }

        self.current_layer = "foreground"  # 初期レイヤーは前景
        self.layer_visibility = {"background": True, "foreground": True}

        self.setFixedSize(grid_size * pixel_size, grid_size * pixel_size)

    def update_canvas_size(self):
        """キャンバスのサイズを更新"""
        self.setFixedSize(self.grid_size * self.pixel_size, self.grid_size * self.pixel_size)
        self.update()

    def resize_canvas(self, new_size):
        """キャンバスサイズを変更"""
        self.grid_size = new_size
        self.pixels.clear()  # サイズ変更時にリセット
        self.update_canvas_size()

    def save_canvas(self):
        """キャンバスの内容を画像として保存（グリッドなし）"""
        file_path, _ = QW.QFileDialog.getSaveFileName(
            self, "画像を保存", "", "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;All Files (*)"
        )

        if file_path:
            # 一時的にグリッドを非表示
            original_show_grid = self.show_grid
            self.show_grid = False
            self.repaint()  # 再描画

            image = QG.QImage(self.width(), self.height(),
                              QG.QImage.Format_ARGB32)
            image.fill(QC.Qt.white)

            painter = QG.QPainter(image)
            self.render(painter, QC.QPoint(0, 0))
            painter.end()

            # グリッド表示を元に戻す
            self.show_grid = original_show_grid
            self.repaint()  # 再描画

            image.save(file_path)

    def paintEvent(self, event):
        painter = QG.QPainter(self)

        # ピクセルを描画
        for (x, y), color in self.pixels.items():
            rect = (x, y, self.pixel_size, self.pixel_size)
            painter.fillRect(*rect, color)

        for layer in ["background", "foreground"]:
          if self.layer_visibility.get(layer, True):  # 表示されているレイヤーのみ描画
            for (x, y), color in self.layers[layer].items():
                painter.fillRect(x, y, self.pixel_size, self.pixel_size, color)

        # グリッド描画（ON の場合のみ）
        if self.show_grid:
            painter.setPen(QC.Qt.gray)
            for x in range(0, self.width(), self.pixel_size):
                for y in range(0, self.height(), self.pixel_size):
                    rect = (x, y, self.pixel_size, self.pixel_size)
                    painter.drawRect(*rect)

        # 中心線
        if self.show_grid:
            painter.setPen(QG.QColor(255, 127, 127, 255))
            center_x = self.width() // 2
            center_y = self.height() // 2
            painter.drawLine(center_x, 0, center_x, self.height())
            painter.drawLine(0, center_y, self.width(), center_y)
            painter.drawLine(center_x - 1, 0, center_x - 1, self.height())
            painter.drawLine(0, center_y - 1, self.width(), center_y - 1)

    def toggle_grid(self):
        """グリッドの ON/OFF を切り替える"""
        self.show_grid = not self.show_grid
        self.update()

    def mousePressEvent(self, event: QG.QMouseEvent):
        x = (event.pos().x() // self.pixel_size) * self.pixel_size
        y = (event.pos().y() // self.pixel_size) * self.pixel_size

        if event.button() == QC.Qt.LeftButton:
            self.save_state()  # 変更前の状態を保存
            if self.current_color is not None:
                self.layers[self.current_layer][(x, y)] = self.current_color
            else:
                if (x, y) in self.layers[self.current_layer]:
                    del self.layers[self.current_layer][(x, y)]  # 消しゴム機能

        elif event.button() == QC.Qt.RightButton:
            if (x, y) in self.layers[self.current_layer]:
                self.set_color(self.layers[self.current_layer][(x, y)])

        self.update()

    def set_color(self, color):
        """スポイトで取得した色を設定"""
        self.current_color = color

    def save_state(self):
        """現在のピクセルの状態を履歴に保存"""
        self.history.append(self.pixels.copy())
        self.future.clear()  # 新しい操作をしたらリドゥ履歴をクリア

    def undo(self):
        """アンドゥ（元に戻す）"""
        if self.history:
            self.future.append(self.pixels.copy())  # 現在の状態をリドゥ用に保存
            self.pixels = self.history.pop()  # 直前の状態を復元
            self.update()

    def redo(self):
        """リドゥ（やり直す）"""
        if self.future:
            self.history.append(self.pixels.copy())  # 現在の状態をアンドゥ用に保存
            self.pixels = self.future.pop()  # 直後の状態を復元
            self.update()

    def set_layer(self, layer):
      """描画するレイヤーを変更"""
      if layer in self.layers:
        self.current_layer = layer

    def add_layer(self, layer_name):
      """新しいレイヤーを追加"""
      if layer_name not in self.layers:
        self.layers[layer_name] = {}

    def delete_layer(self, layer_name):
      """レイヤーを削除"""
      if layer_name in self.layers and len(self.layers) > 1:
        del self.layers[layer_name]

    def move_layer_to_front(self, layer_name):
      """指定したレイヤーを前面に移動"""
      if layer_name in self.layers:
        layer = self.layers.pop(layer_name)
        self.layers = {layer_name: layer, **self.layers}

    def move_layer_to_back(self, layer_name):
      """指定したレイヤーを背面に移動"""
      if layer_name in self.layers:
        layer = self.layers.pop(layer_name)
        self.layers[layer_name] = layer

    def set_layer_opacity(self, layer_name, opacity):
      """指定したレイヤーの透明度を設定"""
      if layer_name in self.layers:
        for key, color in self.layers[layer_name].items():
            new_color = color.withAlphaF(opacity)
            self.layers[layer_name][key] = new_color

    def toggle_layer_visibility(self, layer_name):
      """レイヤーの表示/非表示を切り替え"""
      if layer_name in self.layer_visibility:
        self.layer_visibility[layer_name] = not self.layer_visibility[layer_name]
        self.update()  # 再描画して反映

    def rename_layer(self, old_name, new_name):
      """レイヤー名を変更"""
      if old_name in self.layers and new_name not in self.layers:
        self.layers[new_name] = self.layers.pop(old_name)
