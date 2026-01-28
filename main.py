import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("بلبرینگ")

        # ===== Central Widget =====
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        # بک‌گراند فقط برای central
        central.setStyleSheet("""
        #central {
            background-image: url(assets/background.jpg);
            background-repeat: no-repeat;
            background-position: center;
        }
        """)

        screen = QApplication.primaryScreen().size()
        sw, sh = screen.width(), screen.height()

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(40)
        main_layout.setAlignment(Qt.AlignCenter)

        font_label = QFont("Vazirmatn", 14)
        font_input = QFont("Vazirmatn", 16)

        # ================= Right Card (Inputs) =================
        right_card = QWidget()
        right_card.setFixedSize(int(sw * 0.25), int(sh * 0.55))
        right_card.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 180);
            border-radius: 25px;
        }
        """)

        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(22)

        self.inputs = []
        labels = ["حلقه بیرون", "حلقه درون", "ضخامت"]

        for text in labels:
            lbl = QLabel(text)
            lbl.setFont(font_label)
            lbl.setStyleSheet("color: white;")

            inp = QLineEdit()
            inp.setFont(font_input)
            inp.setFixedHeight(55)
            inp.setValidator(QIntValidator())
            inp.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 220);
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            """)

            inp.installEventFilter(self)
            self.inputs.append(inp)

            right_layout.addWidget(lbl)
            right_layout.addWidget(inp)

        clear_btn = QPushButton("پاک کردن")
        clear_btn.setFixedHeight(55)
        clear_btn.setFont(font_input)
        clear_btn.setStyleSheet("""
        QPushButton {
            background-color: #f1c40f;
            border-radius: 18px;
        }
        QPushButton:hover {
            background-color: #f39c12;
        }
        """)
        clear_btn.clicked.connect(self.clear_inputs)

        right_layout.addStretch()
        right_layout.addWidget(clear_btn)

        # ================= Left Card (Output) =================
        left_card = QWidget()
        left_card.setFixedSize(int(sw * 0.25), int(sh * 0.55))
        left_card.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 180);
            border-radius: 25px;
        }
        """)

        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(22)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(font_input)
        self.output.setStyleSheet("""
        QTextEdit {
            background-color: rgba(0, 0, 0, 220);
            color: white;
            border-radius: 18px;
            padding: 15px;
        }
        """)

        self.check_btn = QPushButton("بررسی")
        self.check_btn.setFixedHeight(60)
        self.check_btn.setFont(font_input)
        self.check_btn.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71;
            border-radius: 20px;
        }
        QPushButton:hover {
            background-color: #27ae60;
        }
        """)
        self.check_btn.clicked.connect(self.check_result)

        left_layout.addWidget(self.output)
        left_layout.addWidget(self.check_btn)

        # ================= Add Cards =================
        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card)

        self.inputs[0].setFocus()

    # ===== Keyboard handling =====
    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress and obj in self.inputs:
            if event.key() == Qt.Key_Space:
                i = self.inputs.index(obj)
                if i < len(self.inputs) - 1:
                    self.inputs[i + 1].setFocus()
                return True
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.check_btn.click()
                return True
        return super().eventFilter(obj, event)

    # ===== Logic =====
    def clear_inputs(self):
        for i in self.inputs:
            i.clear()
        self.output.clear()
        self.inputs[0].setFocus()

    def check_result(self):
        values = [i.text() for i in self.inputs]
        if "" in values:
            self.output.setText("⚠️ همه مقادیر را وارد کنید")
        else:
            self.output.setText(f"ورودی‌ها:\n{values}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())
