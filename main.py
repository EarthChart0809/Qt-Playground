import PySide6.QtWidgets as QW
import PySide6.QtGui as QG
import PySide6.QtCore as QC
from DotEditor import DotEditor

if __name__ == "__main__":
    app = QW.QApplication([])
    window = DotEditor()
    window.show()
    app.exec()
