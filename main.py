import PySide6.QtWidgets as QW
from DotEditor import DotEditor

if __name__ == "__main__":
    app = QW.QApplication([])
    window = DotEditor()
    window.show()
    app.exec()
