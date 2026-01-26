import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("بلبرینگ")  # عنوان پنجره

        # اندازه صفحه در init فقط برای محاسبه کارت‌ها
        screen = QApplication.primaryScreen().size()
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        # ===== Background =====
        self.setStyleSheet("""
        QWidget {
            background-image: url(assets/background.jpg);
            background-repeat: no-repeat;
            background-position: center;
        }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(40)  # فاصله کارت‌ها کم

        # ================= Right Card (Inputs) =================
        right_card = QWidget()
        right_card_width = int(self.screen_width * 0.25)
        right_card_height = int(self.screen_height * 0.55)
        right_card.setFixedSize(right_card_width, right_card_height)
        right_card.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 170);
            border-radius: 25px;
        }
        """)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(20)

        font_label = QFont("Vazirmatn", 14)
        font_input = QFont("Vazirmatn", 16)

        self.inputs = []
        labels = ["حلقه بیرون", "حلقه دورن", "ضخامت"]

        for i, text in enumerate(labels):
            lbl = QLabel(text)
            lbl.setFont(font_label)
            lbl.setStyleSheet("color: white;")

            inp = QLineEdit()
            inp.setFont(font_input)
            inp.setFixedHeight(55)
            inp.setValidator(QIntValidator())
            inp.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 210);
                color: white;
                border-radius: 15px;
                padding: 10px;
            }
            """)

            inp.installEventFilter(self)  # Space → بعدی
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
        right_card.setLayout(right_layout)

        # ================= Left Card (Output) =================
        left_card = QWidget()
        left_card_width = int(self.screen_width * 0.25)
        left_card_height = int(self.screen_height * 0.55)
        left_card.setFixedSize(left_card_width, left_card_height)
        left_card.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 170);
            border-radius: 25px;
        }
        """)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(20)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(font_input)
        self.output.setStyleSheet("""
        QTextEdit {
            background-color: rgba(0, 0, 0, 210);
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
        left_card.setLayout(left_layout)

        # ================= Add Cards to Layout =================
        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card)
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)

        # فوکوس اولیه روی اولین باکس
        self.inputs[0].setFocus()

    # ===== Space handling =====
    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress and obj in self.inputs:
            if event.key() == Qt.Key_Space:
                index = self.inputs.index(obj)
                if index < len(self.inputs) - 1:
                    self.inputs[index + 1].setFocus()
                return True
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
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
    window.show()             # پنجره ساخته می‌شود
    window.showMaximized()     # بعد از show → ماکزیمایز واقعی
    sys.exit(app.exec_())

