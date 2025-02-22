import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC
from CropSelection import CropSelectionView
import cv2
import numpy as np

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
        self.layer_visibility = {"background": True, "foreground": True}# レイヤーの表示状態
        self.brush_mode = "normal"  # ブラシモード（normal, checker, symmetry）
        self.layer_lock = {"background": False,"foreground": False}  # レイヤーのロック状態
        self.setFixedSize(grid_size * pixel_size, grid_size * pixel_size)

    def set_brush_mode(self, mode):
      self.brush_mode = mode
      print(f"Brush mode set to: {self.brush_mode}")  # デバッグ用

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

          if color is None:
            painter.setPen(QC.Qt.NoPen)  # ペンなし
            color = QC.Qt.white  # デフォルト色を白にする
          else:
            painter.setPen(QG.QPen(color))  # 適切なペンを設定

          painter.fillRect(*rect, color)  # 塗りつぶし

        # すべてのレイヤーを描画
        for layer_name, layer_data in self.layers.items():
          if self.layer_visibility.get(layer_name, True):  # 表示されているレイヤーのみ描画
            for (x, y), color in layer_data.items():
                if color is None:
                    painter.setPen(QC.Qt.NoPen)
                    color = QC.Qt.white
                else:
                    painter.setPen(QG.QPen(color))

                painter.fillRect(x, y, self.pixel_size, self.pixel_size, color)

        # グリッド描画（ON の場合のみ）
        if self.show_grid:
          painter.setPen(QC.Qt.gray)
          for x in range(0, self.width(), self.pixel_size):
            for y in range(0, self.height(), self.pixel_size):
                rect = (x, y, self.pixel_size, self.pixel_size)
                painter.drawRect(*rect)

        # デバッグ: レイヤーごとにポイント描画
        for layer_name, layer_data in self.layers.items():
          for pos, color in layer_data.items():
            if color is None:
                color = QC.Qt.black  # `None` の場合、デフォルトで黒を設定
            painter.setPen(QG.QPen(color))
            painter.drawPoint(*pos)

        # 中心線（show_grid とは別フラグにした方が柔軟かも）
        if self.show_grid:
          painter.setPen(QG.QColor(255, 127, 127, 255))
          center_x = self.width() // 2
          center_y = self.height() // 2
          painter.drawLine(center_x, 0, center_x, self.height())
          painter.drawLine(0, center_y, self.width(), center_y)
          painter.drawLine(center_x - 1, 0, center_x - 1, self.height())
          painter.drawLine(0, center_y - 1, self.width(), center_y - 1)

        painter.end()  # QPainter を明示的に終了

    def clear_canvas(self):
        """キャンバスをクリア"""
        self.pixels.clear()
        self.layers = {"background": {}, "foreground": {}}
        self.update

    def toggle_grid(self):
        """グリッドの ON/OFF を切り替える"""
        self.show_grid = not self.show_grid
        self.update()

    def mousePressEvent(self, event: QG.QMouseEvent):
        x = (event.pos().x() // self.pixel_size) * self.pixel_size
        y = (event.pos().y() // self.pixel_size) * self.pixel_size

        if event.button() == QC.Qt.LeftButton:
          self.save_state()  # 変更前の状態を保存

          if self.brush_mode == "checker":  # 市松模様モード
            self.draw_checker_pattern(x, y)
          elif self.brush_mode == "symmetry":  # 左右対称モード
            self.draw_symmetric(x, y)
          else:
            if self.current_color is not None:
                self.layers[self.current_layer][(x, y)] = self.current_color
            elif (x, y) in self.layers[self.current_layer]:  # 消しゴム
                self.erase_pixel(x, y)

        elif event.button() == QC.Qt.RightButton:
            if (x, y) in self.layers[self.current_layer]:
                self.set_color(self.layers[self.current_layer][(x, y)])

        self.update()

    def set_color(self, color):
        """スポイトで取得した色を設定"""
        self.current_color = color
        print(f"現在の色: {color}")  # デバッグ用

    def save_state(self):
        """現在のピクセルの状態を履歴に保存"""
        self.history.append(self.layers[self.current_layer].copy())
        self.future.clear()  # 新しい操作をしたらリドゥ履歴をクリア

    def undo(self):
        """アンドゥ（元に戻す）"""
        if self.history:
            self.future.append(
                self.layers[self.current_layer].copy())  # 現在の状態をリドゥ用に保存
            self.layers[self.current_layer] = self.history.pop()  # 直前の状態を復元
            self.update()

    def redo(self):
        """リドゥ（やり直す）"""
        if self.future:
            self.history.append(self.layers[self.current_layer].copy())  # 現在の状態をアンドゥ用に保存
            self.layers[self.current_layer] = self.future.pop()  # 直後の状態を復元
            self.update()

    def set_layer(self, layer):
      """描画するレイヤーを変更"""
      if layer in self.layers:
        self.current_layer = layer

    def add_layer(self, layer_name):
      """新しいレイヤーを追加"""
      if layer_name not in self.layers:
        self.layers[layer_name] = {}
        self.layer_visibility[layer_name] = True  # デフォルトで表示
        self.layer_lock[layer_name] = False  # デフォルトで編集可能

      # DotEditor に更新を伝える
      self.parent().update_layer_list()
      self.layer_list_widget.add_layer_item(layer_name)  # リストに追加

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

    def draw_checker_pattern(self, x, y):
        """市松模様を描画"""
        base_x = (x // self.pixel_size) * self.pixel_size
        base_y = (y // self.pixel_size) * self.pixel_size

        for i in range(2):
          for j in range(2):
            grid_x = base_x + i * self.pixel_size
            grid_y = base_y + j * self.pixel_size
            if ((grid_x // self.pixel_size) + (grid_y // self.pixel_size)) % 2 == 0:
                self.layers[self.current_layer][(
                    grid_x, grid_y)] = self.current_color

        self.update()

    def draw_symmetric(self, x, y):
        """左右対称にドットを描画（補正版）"""
        canvas_width = self.width() // self.pixel_size  # ピクセル単位でキャンバスの幅を取得
        canvas_height = self.height() // self.pixel_size  # ピクセル単位でキャンバスの高さを取得

        mirrored_x = (canvas_width - 1 - (x // self.pixel_size)) * self.pixel_size
        mirrored_y = (canvas_height - 1 - (y // self.pixel_size)) * self.pixel_size

        print(f"クリック座標: {x}, {y}")
        print(f"左右対称の座標: {mirrored_x}, {y} と {x}, {mirrored_y}")
        print(f"対角対称の座標: {mirrored_x}, {mirrored_y}")
        print(
            f"描画対象座標: ({x}, {y}), ミラー座標: ({mirrored_x}, {y}), ({x}, {mirrored_y}), ({mirrored_x}, {mirrored_y})")
        self.layers[self.current_layer][(x, y)] = self.current_color
        self.layers[self.current_layer][(mirrored_x, y)] = self.current_color
        self.layers[self.current_layer][(x, mirrored_y)] = self.current_color
        self.layers[self.current_layer][(mirrored_x, mirrored_y)] = self.current_color
        
        print("Calling self.update()")  # 確認用
        self.update()
        

    def get_crop_rect(self, pixmap):
      dialog = QW.QDialog(self)
      dialog.setWindowTitle("切り取り範囲を選択")
      layout = QW.QVBoxLayout(dialog)

      scene = QW.QGraphicsScene()
      pixmap_item = QW.QGraphicsPixmapItem(pixmap)
      scene.addItem(pixmap_item)

      view = CropSelectionView(scene)  # カスタムビューを使用
      layout.addWidget(view)

      select_button = QW.QPushButton("選択完了")
      layout.addWidget(select_button)

      def on_select():
        if view.selection_rect:
            rect = view.selection_rect.rect().toRect()
            dialog.accept()
            return rect
        return None

      select_button.clicked.connect(on_select)
      if dialog.exec() == QW.QDialog.Accepted:
        return on_select()
      return None

    def load_and_crop_image(self, file_path):
      """ 画像を読み込み、切り取り、キャンバスに適用 """
      original_pixmap = QG.QPixmap(file_path)
      if original_pixmap.isNull():
        return  # 画像が無効なら何もしない

      # トリミングウィンドウを開く
      rect = self.get_crop_rect(original_pixmap)
      if rect is None:
        return  # 選択なし

      cropped_pixmap = original_pixmap.copy(rect)

      # キャンバスのピクセルグリッドサイズに合わせてリサイズ
      scaled_pixmap = cropped_pixmap.scaled(
                      self.width() * self.pixel_size,
                      self.height() * self.pixel_size,
          QC.Qt.IgnoreAspectRatio,
          QC.Qt.SmoothTransformation)

      # QPixmap → QImage に変換してドット絵化
      self.apply_to_canvas(scaled_pixmap.toImage(), num_colors=64) #256まで調整可能

    def apply_to_canvas(self, image, num_colors=16):
      """ ピクセルデータをキャンバスに適用（リサイズ＆減色処理） """

      # 画像をキャンバスのピクセルグリッドサイズにリサイズ
      image = image.scaled(self.width(), self.height(),
                        QC.Qt.IgnoreAspectRatio, QC.Qt.SmoothTransformation)

      width, height = image.width(), image.height()
      ptr = image.bits()
      data = np.frombuffer(ptr, dtype=np.uint8).copy().reshape(
        (height, width, 4))  # RGBA

      # アルファチャンネルを無視して RGB のみにする
      data = data[:, :, :3]  # (height, width, 3) の形にする

      # RGB → Lab 色空間に変換
      lab_image = cv2.cvtColor(data, cv2.COLOR_RGB2Lab)

      # K-means クラスタリング
      Z = np.float32(lab_image.reshape((-1, 3)))  # 1次元化
      _, labels, centers = cv2.kmeans(Z, num_colors, None,
                                    (cv2.TERM_CRITERIA_EPS +
                                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
                                    10, cv2.KMEANS_RANDOM_CENTERS)

      # 量子化した結果を元の形に戻す
      centers = np.uint8(centers)
      quantized_lab = centers[labels.flatten()].reshape(data.shape)

      # Lab → RGB に戻す
      quantized = cv2.cvtColor(quantized_lab, cv2.COLOR_Lab2RGB)

      # ピクセルグリッドに合わせてキャンバスデータに適用
      pixel_size = self.pixel_size
      for y in range(height):
        for x in range(width):
            grid_x = (x // pixel_size) * pixel_size
            grid_y = (y // pixel_size) * pixel_size
            color = tuple(map(int, quantized[y, x]))  # RGB値を整数タプル化

            # PySide6 QColor へ変換
            qcolor = QG.QColor(*color)
            self.layers[self.current_layer][(
                grid_x, grid_y)] = qcolor  # ピクセル情報を適用

      self.update()  # キャンバスを更新

    def erase_pixel(self, x, y):
      """消しゴムで消す処理（シンメトリー・市松模様対応）"""
      to_erase = [(x, y)]  # 通常の座標を追加

      if self.brush_mode == "checker":
        # 市松模様で生成された座標を削除
        for i in range(2):
            for j in range(2):
                grid_x = x + i * self.pixel_size
                grid_y = y + j * self.pixel_size
                if (i + j) % 2 == 0:
                    to_erase.append((grid_x, grid_y))

      elif self.brush_mode == "symmetry":
        # 左右対称で生成された座標を削除
        width = self.width()
        height = self.height()
        mirrored_x = width - x - self.pixel_size
        mirrored_y = height - y - self.pixel_size

        to_erase.extend([(mirrored_x, y), (x, mirrored_y), (mirrored_x, mirrored_y)])

      # 削除処理
      for pos in to_erase:
        if pos in self.layers[self.current_layer]:
          self.layers[self.current_layer][pos] = QC.Qt.white  # 背景色にする

      self.update()
