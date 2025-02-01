import os
import sys
import PySide6.QtWidgets as Qw
import datetime as dt
import locale

# ロケールの設定
locale.setlocale(locale.LC_TIME, 'Japanese_Japan')  # Windows環境

# 指定した月のカレンダを文字を得る関数
def get_month_calendar(year: int, month: int) -> str:

  dt_start = dt.datetime(year, month, 1)
  dt_end = dt.datetime(year, month + 1, 1) - dt.timedelta(days=1)

  calendar = ''
  d = dt_start
  while d <= dt_end:
    calendar += d.strftime('%m月%d日(%a) \n')
    d += dt.timedelta(days=1)

  return calendar.strip()  # stripメソッドで末尾の改行を削除

# PySide6.QtWidgets.MainWindow を継承した MainWindow クラスの定義
class MainWindow(Qw.QMainWindow):

  # コンストラクタ(初期化)
  def __init__(self):

    # 親クラスのコンストラクタの呼び出し
    super().__init__()

    # ウィンドウタイトル設定
    self.setWindowTitle('MainWindow')

    # ウィンドウのサイズ(640x240)と位置(X=100,Y=50)の設定
    self.setGeometry(100, 50, 640, 240)

    # 「Save」ボタンの生成と設定
    self.btn_open = Qw.QPushButton('Save', self)
    self.btn_open.setGeometry(10, 10, 100, 25)
    self.btn_open.clicked.connect(self.btn_open_clicked)

    # ナビゲーション情報を表示するラベル
    self.init_navi_msg = \
        '[Save] ボタンを押下して保存先を選択してください。'
    self.lb_navi = Qw.QLabel(self.init_navi_msg, self)
    self.lb_navi.setGeometry(15, 35, 620, 30)

    # テキストボックス
    self.tb_calendar = Qw.QTextEdit('', self)
    self.tb_calendar.setGeometry(10, 65, 620, 160)
    self.tb_calendar.setReadOnly(True)
    self.tb_calendar.setPlainText(get_month_calendar(2024, 2))

  # 「Save」ボタンの押下処理
  def btn_open_clicked(self):
    title = 'カレンダー (テキストファイル) の保存'
    default_path = os.path.expanduser('~/Desktop/カレンダー.txt')
    filter = 'Text file (*.txt)'
    path = Qw.QFileDialog.getSaveFileName(
        self,         # 親ウィンドウ
        title,        # ダイアログタイトル
        default_path,  # デフォルトファイル名
        filter)       # 拡張子によるフィルタ
    print(f'path => "{path}"')  # 確認

    if path[0] == '':
      self.lb_navi.setText('保存をキャンセルしました。')
      return

    self.save_text(path[0], self.tb_calendar.toPlainText())
    self.lb_navi.setText(f"カレンダを '{path[0]}' に保存しました。")

  # テキストモードでファイルの書き込み
  def save_text(self, path, text):
    with open(path, mode='w', encoding='utf_8') as file:
      text = file.write(text)

# 本体
if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = MainWindow()
  main_window.show()
  sys.exit(app.exec())
