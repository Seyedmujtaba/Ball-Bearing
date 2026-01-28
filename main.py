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
        self.central = QWidget()
        self.central.setObjectName("central")
        self.setCentralWidget(self.central)

        self.central.setStyleSheet("""
        #central {
            background-image: url(assets/background.jpg);
            background-repeat: no-repeat;
            background-position: center;
        }
        """)

        self.screen = QApplication.primaryScreen().size()
        self.font_label = QFont("Vazirmatn", 14)
        self.font_input = QFont("Vazirmatn", 16)

        self.show_start_screen()

    # ================= Start Screen =================
    def show_start_screen(self):
        self.clear_layout()

        layout = QVBoxLayout(self.central)
        layout.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setFixedSize(
            int(self.screen.width() * 0.25),
            int(self.screen.height() * 0.3)
        )
        card.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 180);
            border-radius: 30px;
        }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(30)

        title = QLabel("انتخاب نوع")
        title.setFont(QFont("Vazirmatn", 18))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)

        bearing_btn = QPushButton("بلبرینگ")
        bearing_btn.setFont(self.font_input)
        bearing_btn.setFixedHeight(60)
        bearing_btn.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            border-radius: 20px;
            color: white;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """)
        bearing_btn.clicked.connect(self.show_bearing_ui)

        bearing2_btn = QPushButton("یاتاقان")
        bearing2_btn.setFont(self.font_input)
        bearing2_btn.setFixedHeight(60)
        bearing2_btn.setStyleSheet("""
        QPushButton {
            background-color: #9b59b6;
            border-radius: 20px;
            color: white;
        }
        QPushButton:hover {
            background-color: #8e44ad;
        }
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(bearing_btn)
        card_layout.addWidget(bearing2_btn)

        layout.addWidget(card)

    # ================= Bearing UI =================
    def show_bearing_ui(self):
        self.clear_layout()

        sw, sh = self.screen.width(), self.screen.height()

        main_layout = QHBoxLayout(self.central)
        main_layout.setSpacing(40)
        main_layout.setAlignment(Qt.AlignCenter)

        # -------- Right Card (Inputs)
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
        for text in ["حلقه بیرون", "حلقه درون", "ضخامت"]:
            lbl = QLabel(text)
            lbl.setFont(self.font_label)
            lbl.setStyleSheet("color: white;")

            inp = QLineEdit()
            inp.setFont(self.font_input)
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
        clear_btn.setFont(self.font_input)
        clear_btn.setStyleSheet("""
        QPushButton {
            background-color: #f1c40f;
            border-radius: 18px;
        }
        """)
        clear_btn.clicked.connect(self.clear_inputs)

        right_layout.addStretch()
        right_layout.addWidget(clear_btn)

        # -------- Left Card (Output)
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
        left_layout.setSpacing(18)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(int(sh * 0.28))  # کوچیک‌تر شد
        self.output.setFont(self.font_input)
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
        self.check_btn.setFont(self.font_input)
        self.check_btn.setStyleSheet("""
        QPushButton {
            background-color: #2ecc71;
            border-radius: 20px;
        }
        """)
        self.check_btn.clicked.connect(self.check_result)

        left_layout.addWidget(self.output)
        left_layout.addWidget(self.check_btn)

        main_layout.addWidget(left_card)
        main_layout.addWidget(right_card)

        self.inputs[0].setFocus()

    # ================= Helpers =================
    def clear_layout(self):
        layout = self.central.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(layout)

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
