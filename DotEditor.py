import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC
from PixelCanvas import PixelCanvas

class DotEditor(QW.QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = PixelCanvas()

        # 色のパレットを保持するリスト
        self.color_palette = [
            QG.QColor(0, 0, 0),  # 黒
            QG.QColor(255, 0, 0),  # 赤
            QG.QColor(0, 0, 255),  # 青
            QG.QColor(0, 255, 0),  # 緑
            QG.QColor(255, 255, 0),  # 黄
            QG.QColor(255, 165, 0)  # オレンジ
        ]

        # パレットボタン
        self.palette_buttons = []
        palette_layout = QW.QHBoxLayout()
        for color in self.color_palette:
            btn = QW.QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black;")
            btn.clicked.connect(
                lambda checked, c=color: self.canvas.set_color(c))
            self.palette_buttons.append(btn)
            palette_layout.addWidget(btn)

        # ショートカットキーの設定
        undo_shortcut = QG.QShortcut(QG.QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.canvas.undo)

        redo_shortcut = QG.QShortcut(QG.QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.canvas.redo)

        # 色を追加するボタン
        self.add_color_button = QW.QPushButton("色を追加")
        self.add_color_button.clicked.connect(self.add_color)

        # 消しゴムボタン
        self.eraser_button = QW.QPushButton("消しゴム")
        self.eraser_button.clicked.connect(self.erase_color)

        # グリッドON/OFFボタン
        self.grid_button = QW.QCheckBox("グリッド ON/OFF")
        self.grid_button.clicked.connect(self.canvas.toggle_grid)

        # クリアボタン
        self.clear_button = QW.QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_canvas)

        # 保存ボタン
        self.save_button = QW.QPushButton("画像を保存")
        self.save_button.clicked.connect(self.canvas.save_canvas)

        self.layer_switch_button = QW.QPushButton("背景/前景切替")
        self.layer_switch_button.clicked.connect(self.toggle_layer)

        # レイアウト構築
        layout = QW.QVBoxLayout()
        layout.addWidget(self.grid_button)
        layout.addWidget(self.canvas)
        layout.addLayout(palette_layout)
        layout.addWidget(self.add_color_button)
        layout.addWidget(self.eraser_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.layer_switch_button)
        self.setLayout(layout)

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

    def erase_color(self):
        """消しゴムを選択する"""
        self.canvas.set_color(None)

    def clear_canvas(self):
        """キャンバスをクリアする"""
        self.canvas.pixels.clear()
        self.canvas.update()

    def toggle_layer(self):
        """背景と前景の切り替え"""
        new_layer = "background" if self.canvas.current_layer == "foreground" else "foreground"
        self.canvas.set_layer(new_layer)
        self.layer_switch_button.setText(f"レイヤー: {new_layer}")
