import sys
import PySide6.QtCore as Qc
import PySide6.QtWidgets as Qw

# クラスの定義
class Grade():
  def __init__(self, label: str, msg: str):
    self.label = label
    self.msg = msg

grades = [Grade('秀', '90点以上'),
          Grade('優', '80点以上90点未満'),
          Grade('良', '65点以上80点未満'),
          Grade('可', '60点以上65点未満'),
          Grade('不可', '60点未満 (不合格)')]

class MainWindow(Qw.QMainWindow):

  def __init__(self):

    super().__init__()
    self.setWindowTitle('MainWindow')
    self.setGeometry(100, 50, 640, 100)

    # メインレイアウトの設定
    central_widget = Qw.QWidget(self)
    self.setCentralWidget(central_widget)
    main_layout = Qw.QVBoxLayout(central_widget)  # 要素を垂直配置
    main_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignTop)  # 上寄せ
    main_layout.setContentsMargins(15, 10, 10, 10)

    # ラジオボタンを格納する画面表示上のコンテナ
    rb_layout = Qw.QHBoxLayout()  # 要素を水平配置
    rb_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignLeft)  # 左寄せ
    main_layout.addLayout(rb_layout)

    # ラジオボタンを格納する論理的なグループ (論理的なコンテナ)
    self.rb_group = Qw.QButtonGroup(self)

    # ラジオボタンの生成と設定
    for i, grade in enumerate(grades, 1):
      rb = Qw.QRadioButton(self)
      rb.setText(grade.label)
      rb.setFixedSize(50, 25)
      rb_layout.addWidget(rb)
      self.rb_group.addButton(rb, i)

    # ラベル
    self.lb_navi = Qw.QLabel('', self)
    main_layout.addWidget(self.lb_navi)

    # イベント処理
    self.rb_group.buttonClicked.connect(self.rb_state_changed)

    # 初期値設定
    self.rb_group.button(3).setChecked(True)
    self.rb_state_changed()

  def rb_state_changed(self):
    rb_id = self.rb_group.checkedId() - 1
    if 0 <= rb_id < len(grades):
      self.lb_navi.setText(f'評点 : {grades[rb_id].msg}')
    else:
      self.lb_navi.setText('想定外の処理がされました。')

# 本体
if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = MainWindow()
  main_window.show()
  sys.exit(app.exec())
