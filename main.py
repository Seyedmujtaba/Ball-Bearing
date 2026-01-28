import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy
)
from PyQt5.QtGui import QFont, QIntValidator, QPixmap
from PyQt5.QtCore import Qt

CARD_STYLE = """
QWidget {
    background-color: rgba(0, 0, 0, 180);
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.2);
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بلبرینگ / یاتاقان")

        self.central = QWidget()
        self.setCentralWidget(self.central)

        # پس‌زمینه
        self.bg_label = QLabel(self.central)
        self.bg_pixmap = QPixmap("assets/background.jpg")
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.central.resizeEvent = lambda event: self.bg_label.setGeometry(0, 0, self.central.width(), self.central.height())

        self.screen = QApplication.primaryScreen().size()
        self.show_start_screen()
        self.showMaximized()

    # ---------- صفحه شروع ----------
    def show_start_screen(self):
        self.clear_layout()
        layout = QVBoxLayout(self.central)
        layout.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setFixedSize(int(self.screen.width()*0.25), int(self.screen.height()*0.3))
        card.setStyleSheet(CARD_STYLE)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40,40,40,40)
        card_layout.setSpacing(30)

        title = QLabel("انتخاب نوع")
        title.setFont(QFont("Vazirmatn",18))
        title.setStyleSheet("color:white")
        title.setAlignment(Qt.AlignCenter)

        bearing_btn = QPushButton("بلبرینگ")
        bearing_btn.setFont(QFont("Vazirmatn",16))
        bearing_btn.setFixedHeight(60)
        bearing_btn.setStyleSheet("background-color:#3498db;border-radius:20px;color:white;")
        bearing_btn.clicked.connect(self.show_bearing_ui)

        yataqan_btn = QPushButton("یاتاقان")
        yataqan_btn.setFont(QFont("Vazirmatn",16))
        yataqan_btn.setFixedHeight(60)
        yataqan_btn.setStyleSheet("background-color:#9b59b6;border-radius:20px;color:white;")
        yataqan_btn.clicked.connect(self.show_yataqan_ui)

        card_layout.addWidget(title)
        card_layout.addWidget(bearing_btn)
        card_layout.addWidget(yataqan_btn)
        layout.addWidget(card)

    # ---------- صفحات بلبرینگ و یاتاقان ----------
    def show_bearing_ui(self):
        self._show_bearing_or_yataqan(inputs=["حلقه بیرون","حلقه درون","ضخامت"])

    def show_yataqan_ui(self):
        self._show_bearing_or_yataqan(inputs=["اندازه داخلی"], single_input=True)

    # ---------- ساختار کارت‌ها ----------
    def _show_bearing_or_yataqan(self, inputs, single_input=False):
        self.clear_layout()
        sw, sh = self.screen.width(), self.screen.height()

        main_v_layout = QVBoxLayout(self.central)
        main_v_layout.setSpacing(0)
        main_v_layout.setAlignment(Qt.AlignCenter)

        # ---------- کارت‌های ورودی و خروجی ----------
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(40)  # فاصله بین ورودی و خروجی
        main_h_layout.setAlignment(Qt.AlignCenter)

        card_width = int(sw*0.25)
        card_height = int(sh*0.45)

        # کارت خروجی
        left_card = QWidget()
        left_card.setFixedSize(card_width, card_height)
        left_card.setStyleSheet(CARD_STYLE)

        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(30,30,30,30)
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignCenter)

        output_label = QLabel("مدل‌های مطابق")
        output_label.setFont(QFont("Vazirmatn",14))
        output_label.setStyleSheet("color:white; background: transparent; border: none;")
        output_label.setAlignment(Qt.AlignCenter)

        output_height = int(card_height * 0.6)
        font_size_out = max(12, output_height // 6)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(output_height)
        self.output.setFont(QFont("Vazirmatn", font_size_out))
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(0,0,0,220);
                color:white;
                border-radius:18px;
                padding:15px;
                font-size:{font_size_out}px;
            }}
        """)

        left_layout.addStretch(1)
        left_layout.addWidget(output_label)
        left_layout.addWidget(self.output)
        left_layout.addStretch(1)

        # کارت ورودی
        right_card = QWidget()
        right_card.setFixedSize(card_width, card_height)
        right_card.setStyleSheet(CARD_STYLE)

        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(30,30,30,30)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.inputs = []
        n_inputs = len(inputs)
        if single_input:
            box_height = output_height
        else:
            available_height = int(card_height - 50)
            box_height = int((available_height // n_inputs) * 0.9)
        font_size = max(12, box_height // 3)

        total_input_height = n_inputs * (box_height + 25)
        total_output_height = output_height + output_label.sizeHint().height()
        top_spacing = max((total_output_height - total_input_height)//2, 0)
        right_layout.addSpacing(top_spacing)

        for text in inputs:
            lbl = QLabel(text)
            lbl.setFont(QFont("Vazirmatn",14))
            lbl.setStyleSheet("color:white; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignCenter)
            inp = QLineEdit()
            inp.setFont(QFont("Vazirmatn", font_size))
            inp.setFixedHeight(box_height)
            inp.setValidator(QIntValidator())
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background-color: rgba(0,0,0,220);
                    color:white;
                    border-radius:18px;
                    border:none;
                    padding:15px;
                    font-size:{font_size}px;
                }}
            """)
            inp.installEventFilter(self)
            self.inputs.append(inp)
            right_layout.addWidget(lbl)
            right_layout.addWidget(inp)

        main_h_layout.addWidget(left_card)
        main_h_layout.addWidget(right_card)
        main_v_layout.addLayout(main_h_layout)

        # ---------- فاصله کارت دکمه‌ها هم‌اندازه با فاصله بین کارت‌ها ----------
        card_spacing = main_h_layout.spacing()
        main_v_layout.addSpacing(card_spacing)

        # کارت دکمه‌ها (عرض برابر با مجموع دو کارت + فاصله)
        total_width = card_width * 2 + main_h_layout.spacing()
        button_card = QWidget()
        button_card.setFixedSize(total_width, 80)
        button_card.setStyleSheet(CARD_STYLE)

        button_layout = QHBoxLayout(button_card)
        button_layout.setContentsMargins(20,15,20,15)
        button_layout.setSpacing(20)

        clear_btn = QPushButton("پاک کردن")
        clear_btn.setFont(QFont("Vazirmatn",16))
        clear_btn.setStyleSheet("background-color:#f1c40f;border-radius:18px;")
        clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        clear_btn.clicked.connect(self.clear_inputs)

        menu_btn = QPushButton("منو")
        menu_btn.setFont(QFont("Vazirmatn",16))
        menu_btn.setStyleSheet("background-color:#3498db;border-radius:18px;")
        menu_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        menu_btn.clicked.connect(self.show_start_screen)

        self.check_btn = QPushButton("بررسی")
        self.check_btn.setFont(QFont("Vazirmatn",16))
        self.check_btn.setStyleSheet("background-color:#2ecc71;border-radius:18px;")
        self.check_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.check_btn.clicked.connect(self.check_result)

        button_layout.addWidget(clear_btn)
        button_layout.addWidget(menu_btn)
        button_layout.addWidget(self.check_btn)

        # کارت دکمه‌ها دقیقا وسط دو کارت بالا
        main_v_layout.addWidget(button_card, alignment=Qt.AlignCenter)

        self.inputs[0].setFocus()

    # ---------- Helpers ----------
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
                if i < len(self.inputs)-1:
                    self.inputs[i+1].setFocus()
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
        filled = [v for v in values if v]
        if not filled:
            self.output.setText("⚠️ هیچ مقداری وارد نشده")
        else:
            self.output.setText("ورودی‌های وارد شده:\n" + "\n".join(filled))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
