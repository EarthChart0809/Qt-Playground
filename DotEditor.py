import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC
from PixelCanvas import PixelCanvas
from LayerSetting import LayerListWidget

class DotEditor(QW.QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = PixelCanvas()
        self.brush_mode = None  # ブラシモード（normal, checker, symmetry）

        # 色のパレットを保持するリスト
        self.color_palette = [
            QG.QColor(0, 0, 0),  # 黒
            QG.QColor(255, 0, 0),  # 赤
            QG.QColor(0, 0, 255),  # 青
            QG.QColor(0, 255, 0),  # 緑
            QG.QColor(255, 255, 0),  # 黄
            QG.QColor(255, 165, 0)  # オレンジ
        ]

        self.layers = {  # self.layers を先に定義
            "background": {},
            "foreground": {}
        }

        self.layer_visibility = {name: True for name in self.layers}
        self.layer_lock = {name: False for name in self.layers}

        # ===== 左側（ツール） =====
        tool_layout = QW.QVBoxLayout()

        # パレットボタン
        self.palette_buttons = []
        for color in self.color_palette:
            btn = QW.QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black;")
            btn.clicked.connect(
                lambda checked, c=color: self.canvas.set_color(c))
            self.palette_buttons.append(btn)
            tool_layout.addWidget(btn)

        # 画像読み込みボタン
        self.load_image_button = QW.QPushButton("画像を読み込む")
        self.load_image_button.clicked.connect(self.load_image)
        tool_layout.addWidget(self.load_image_button)

        # ショートカットキーの設定
        undo_shortcut = QG.QShortcut(QG.QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.canvas.undo)

        redo_shortcut = QG.QShortcut(QG.QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.canvas.redo)

        # 色を追加するボタン
        self.add_color_button = QW.QPushButton("色を追加")
        self.add_color_button.clicked.connect(self.add_color)
        tool_layout.addWidget(self.add_color_button)

        # 消しゴムボタン
        self.eraser_button = QW.QPushButton("消しゴム")
        self.eraser_button.clicked.connect(self.erase_color)
        tool_layout.addWidget(self.eraser_button)

        # クリアボタン
        self.clear_button = QW.QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_canvas)
        tool_layout.addWidget(self.clear_button)

        # 画像保存ボタン
        self.save_button = QW.QPushButton("画像を保存")
        self.save_button.clicked.connect(self.canvas.save_canvas)
        tool_layout.addWidget(self.save_button)

        # ツール部分を上部に寄せる
        tool_layout.addStretch()

        # キャンバスサイズ変更 UI
        self.size_input = QW.QSpinBox()
        self.size_input.setRange(8, 64)  # 最小 8x8、最大 64x64
        self.size_input.setValue(self.canvas.grid_size)

        self.resize_button = QW.QPushButton("キャンバスサイズ変更")
        self.resize_button.clicked.connect(self.change_canvas_size)

        #グリッドON / OFFボタン
        self.grid_button = QW.QCheckBox("グリッド ON/OFF")
        self.grid_button.clicked.connect(self.canvas.toggle_grid)

        self.checker_brush_button = QW.QPushButton("市松模様")
        self.checker_brush_button.clicked.connect(lambda: self.set_brush_mode("checker"))

        self.symmetry_brush_button = QW.QPushButton("シンメトリー")
        self.symmetry_brush_button.clicked.connect(lambda: self.set_brush_mode("symmetry"))

        # ツールのレイアウトに追加
        tool_layout.addWidget(QW.QLabel("キャンバスサイズ:"))
        tool_layout.addWidget(self.size_input)
        tool_layout.addWidget(self.resize_button)
        tool_layout.addWidget(self.grid_button)
        tool_layout.addWidget(self.checker_brush_button)
        tool_layout.addWidget(self.symmetry_brush_button)


        # ===== 右側（レイヤー操作） =====
        layer_layout = QW.QVBoxLayout()

        # レイヤーリストウィジェット
        self.layer_list_widget = LayerListWidget(self)
        self.layer_list_widget.setFixedWidth(150)  # 横幅を狭める
        self.layer_list_widget.layer_order_changed.connect(self.reorder_layers)  # シグナルを接続
        layer_layout.addWidget(self.layer_list_widget)

        # 新しいレイヤー
        self.add_layer_button = QW.QPushButton("レイヤー追加")
        self.add_layer_button.setFixedWidth(100)  # 横幅を狭める
        self.add_layer_button.clicked.connect(self.add_layer)
        layer_layout.addWidget(self.add_layer_button)

        # レイヤー削除
        self.delete_layer_button = QW.QPushButton("レイヤー削除")
        self.delete_layer_button.setFixedWidth(100)  # 横幅を狭める
        self.delete_layer_button.clicked.connect(self.delete_layer)
        layer_layout.addWidget(self.delete_layer_button)

        # 透明度設定
        self.set_opacity_button = QW.QPushButton("透明度設定")
        self.set_opacity_button.setFixedWidth(100)  # 横幅を狭める
        self.set_opacity_button.clicked.connect(self.set_opacity)
        layer_layout.addWidget(self.set_opacity_button)

        # レイヤー部分を上部に寄せる
        layer_layout.addStretch()

        # ===== 全体レイアウト（横並び） =====
        main_layout = QW.QHBoxLayout()
        main_layout.addLayout(tool_layout)  # 左側（ツール）
        main_layout.addWidget(self.canvas)  # 中央（キャンバス）
        main_layout.addLayout(layer_layout)  # 右側（レイヤー）

        self.setLayout(main_layout)

        # 初期レイヤーリストを更新
        self.layer_list_widget.update_layer_list(self.layers.keys())

        # ウィンドウ全体の背景色
        self.setStyleSheet("background-color: #F0F0F0;")  # 淡いグレー

        # キャンバスを白に
        self.canvas.setStyleSheet(
            "background-color: white; border: 1px solid gray;")

        # レイヤーリストの背景色を変更
        self.layer_list_widget.setStyleSheet(
            "background-color: #E0E0E0; border-radius: 5px;")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("DotEditor")


    def load_image(self):
        """ 画像を読み込み、PixelCanvas に渡す """
        file_name, _ = QW.QFileDialog.getOpenFileName(
            self, "画像を選択", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.canvas.load_and_crop_image(file_name)

    def add_color(self):
        """新しい色を追加する"""
        color = QW.QColorDialog.getColor()
        if color.isValid() and len(self.color_palette) < 10:  # 最大10色まで保持
            self.color_palette.append(color)
            btn = QW.QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black;")
            btn.clicked.connect(
                lambda checked, c=color: self.canvas.set_color(c))
            self.palette_buttons.append(btn)
            self.layout().insertWidget(1, btn)  # パレットのレイアウトに追加

    def add_layer(self):
      """新しいレイヤーを追加"""
      layer_name, ok = QW.QInputDialog.getText(self, "レイヤー名", "レイヤー名を入力:")
      if ok and layer_name:
        self.canvas.add_layer(layer_name)
        self.layer_list_widget.add_layer_item(layer_name)  # レイヤーアイテムを追加

    def delete_layer(self):
      """選択したレイヤーを削除"""
      layer_name, ok = QW.QInputDialog.getText(
        self, "削除するレイヤー名", "削除したいレイヤー名を入力:")
      if ok and layer_name:
        self.canvas.delete_layer(layer_name)

    def erase_color(self):
        """消しゴムを選択する"""
        self.canvas.set_color(None)

    def clear_canvas(self):
        """キャンバスをクリアする"""
        for layer in self.canvas.layers.values():
            layer.clear()
        self.canvas.update()

    def toggle_layer(self):
        """背景と前景の切り替え"""
        new_layer = "background" if self.canvas.current_layer == "foreground" else "foreground"
        self.canvas.set_layer(new_layer)
        self.layer_switch_button.setText(f"レイヤー: {new_layer}")

    def move_layer_to_front(self):
      """レイヤーを前面に移動"""
      layer_name, ok = QW.QInputDialog.getText(self, "前面に移動", "移動するレイヤー名を入力:")
      if ok and layer_name:
        self.canvas.move_layer_to_front(layer_name)

    def move_layer_to_back(self):
      """レイヤーを背面に移動"""
      layer_name, ok = QW.QInputDialog.getText(self, "背面に移動", "移動するレイヤー名を入力:")
      if ok and layer_name:
        self.canvas.move_layer_to_back(layer_name)

    def set_opacity(self):
      """レイヤーの透明度を設定"""
      layer_name, ok = QW.QInputDialog.getText(self, "透明度設定", "設定するレイヤー名を入力:")
      if ok and layer_name in self.canvas.layers:
        opacity, ok = QW.QInputDialog.getDouble(
            self, "透明度", "透明度 (0.0-1.0):", 1.0, 0.0, 1.0, 1)
        if ok:
            self.canvas.set_layer_opacity(layer_name, opacity)

    def change_canvas_size(self):
        """キャンバスのサイズを変更する"""
        new_size = self.size_input.value()
        self.canvas.resize_canvas(new_size)

    def set_brush_mode(self, mode):
      self.brush_mode = mode
      print(f"Brush mode set to: {self.brush_mode}")  # デバッグ用

    def update_layer_order(self, new_order):
      """ ドラッグ＆ドロップ後にレイヤーの順序を更新 """
      new_layers = {name: self.layers[name]
                  for name in new_order if name in self.layers}
      self.layers = new_layers  # 更新
      self.update()  # 再描画

    def reorder_layers(self, new_order):
      """レイヤーの順番を self.layers に反映"""
      self.layers = {name: self.layers[name]for name in new_order if name in self.layers}
      self.update()  # 再描画

    def update_layer_list(self):
      """レイヤーリストを更新"""
      self.layer_list_widget.update_layer_list(self.canvas.layers.keys())  

    def toggle_layer_visibility(self, layer_name):
      """レイヤーの表示/非表示を切り替える"""
      if layer_name not in self.layer_visibility:
        self.layer_visibility[layer_name] = True  # デフォルトで表示

      self.layer_visibility[layer_name] = not self.layer_visibility[layer_name]
      self.update_canvas()
      return self.layer_visibility[layer_name]

    def toggle_layer_lock(self, layer_name):
      """レイヤーのロック/解除を切り替え"""
      if layer_name not in self.layer_lock:
        self.layer_lock[layer_name] = False  # デフォルトを設定

      self.layer_lock[layer_name] = not self.layer_lock[layer_name]  # ロックをトグル
      return self.layer_lock[layer_name]  # 現在のロック状態を返す

    def update_canvas(self):
        self.canvas.update()
