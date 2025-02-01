import os
import sys
import PySide6.QtWidgets as Qw

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

    # 「Open」ボタンの生成と設定
    self.btn_open = Qw.QPushButton('Open', self)
    self.btn_open.setGeometry(10, 10, 100, 25)
    self.btn_open.clicked.connect(self.btn_open_clicked)

    # ナビゲーション情報を表示するラベル
    self.init_navi_msg = \
        '[Open] ボタンを押下して ファイル ( *.txt または *.csv ) を選択してください。'
    self.lb_navi = Qw.QLabel(self.init_navi_msg, self)
    self.lb_navi.setGeometry(15, 35, 620, 30)

    # テキストボックス
    self.tb_viwer = Qw.QTextEdit('', self)
    self.tb_viwer.setGeometry(10, 65, 620, 160)
    self.tb_viwer.setPlaceholderText('(読み込んだファイルの内容が表示されます)')
    self.tb_viwer.setReadOnly(True)

  # 「Open」ボタンの押下処理
  def btn_open_clicked(self):
    title = 'テキストファイル または CSVファイル を開く'
    init_path = os.path.expanduser('~/Desktop')
    filter = 'Text file (*.txt);;CSV file (*.csv)'
    path = Qw.QFileDialog.getOpenFileName(
        self,      # 親ウィンドウ
        title,     # ダイアログタイトル
        init_path,  # 初期位置（フォルダパス）
        filter)    # 拡張子によるフィルタ
    print(f'path => "{path}"')  # 確認

    if path[0] == '':
      print('ファイル選択がキャンセルされました。')
      self.lb_navi.setText(self.init_navi_msg)
      return

    ret = self.read_text(path[0])
    self.tb_viwer.setPlainText(ret)
    self.lb_navi.setText(f"ファイル '{path[0]}' を読み込みました。")

    if len(ret) == 0:
      self.tb_viwer.setPlaceholderText('(空ファイルです)')

  # テキストモードでファイルの読込み
  def read_text(self, path):
    # 念のためファイルの存在をチェック
    assert os.path.isfile(path) == True
    with open(path, encoding='utf_8') as file:
      text = file.read()
    return text

# 本体
if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = MainWindow()
  main_window.show()
  sys.exit(app.exec())
