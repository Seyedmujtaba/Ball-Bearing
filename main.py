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
        self.central.resizeEvent = lambda e: self.bg_label.setGeometry(
            0, 0, self.central.width(), self.central.height()
        )

        self.screen = QApplication.primaryScreen().size()
        self.show_start_screen()
        self.showMaximized()

    # ---------- پاک‌سازی کامل Layout ----------
    def clear_layout(self):
        layout = self.central.layout()
        if layout:
            self._clear_layout_recursive(layout)
            QWidget().setLayout(layout)

    def _clear_layout_recursive(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout_recursive(item.layout())

    # ---------- صفحه شروع ----------
    def show_start_screen(self):
        self.clear_layout()
        layout = QVBoxLayout(self.central)
        layout.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setFixedSize(
            int(self.screen.width() * 0.25),
            int(self.screen.height() * 0.3)
        )
        card.setStyleSheet(CARD_STYLE)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(30)

        title = QLabel("انتخاب نوع")
        title.setFont(QFont("Vazirmatn", 18))
        title.setStyleSheet("color:white")
        title.setAlignment(Qt.AlignCenter)

        bearing_btn = QPushButton("بلبرینگ")
        bearing_btn.setFont(QFont("Vazirmatn", 16))
        bearing_btn.setFixedHeight(60)
        bearing_btn.setStyleSheet(
            "background:#3498db;border-radius:20px;color:white;"
        )
        bearing_btn.clicked.connect(self.show_bearing_ui)

        yataqan_btn = QPushButton("یاتاقان")
        yataqan_btn.setFont(QFont("Vazirmatn", 16))
        yataqan_btn.setFixedHeight(60)
        yataqan_btn.setStyleSheet(
            "background:#9b59b6;border-radius:20px;color:white;"
        )
        yataqan_btn.clicked.connect(self.show_yataqan_ui)

        card_layout.addWidget(title)
        card_layout.addWidget(bearing_btn)
        card_layout.addWidget(yataqan_btn)

        layout.addWidget(card)

    # ---------- صفحات ----------
    def show_bearing_ui(self):
        self._show_bearing_or_yataqan(
            ["حلقه بیرون", "حلقه درون", "ضخامت"]
        )

    def show_yataqan_ui(self):
        self._show_bearing_or_yataqan(
            ["اندازه داخلی"], single_input=True
        )

    # ---------- UI اصلی ----------
    def _show_bearing_or_yataqan(self, inputs, single_input=False):
        self.clear_layout()

        sw, sh = self.screen.width(), self.screen.height()
        main_v = QVBoxLayout(self.central)
        main_v.setSpacing(0)

        main_h = QHBoxLayout()
        main_h.setSpacing(40)

        # همتراز کردن کارت‌ها برای یاتاقان
        if single_input:
            main_h.setAlignment(Qt.AlignCenter)
        else:
            main_h.setAlignment(Qt.AlignCenter)

        card_width = int(sw * 0.25)
        card_height = int(sh * 0.45)

        # ===== کارت خروجی =====
        left_card = QWidget()
        left_card.setFixedSize(card_width, card_height)
        left_card.setStyleSheet(CARD_STYLE)

        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter if not single_input else Qt.AlignCenter)

        output_label = QLabel("مدل‌های مطابق")
        output_label.setFont(QFont("Vazirmatn", 14))
        output_label.setStyleSheet("color:white;border:none;")
        output_label.setAlignment(Qt.AlignCenter)

        output_height = int(card_height * 0.6)
        font_out = max(12, output_height // 6)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(output_height)
        self.output.setFont(QFont("Vazirmatn", font_out))
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(0,0,0,220);
                color:white;
                border-radius:18px;
                padding:15px;
                font-size:{font_out}px;
            }}
        """)

        left_layout.addStretch()
        left_layout.addWidget(output_label)
        left_layout.addWidget(self.output)
        left_layout.addStretch()

        # ===== کارت ورودی =====
        right_card = QWidget()
        right_card.setFixedSize(card_width, card_height)
        right_card.setStyleSheet(CARD_STYLE)

        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter if not single_input else Qt.AlignCenter)

        self.inputs = []
        n = len(inputs)
        if single_input:
            box_height = output_height
        else:
            box_height = int(((card_height - 50) // n) * 0.6)  # ارتفاع کوتاه‌تر
        font_in = max(12, box_height // 3)

        for text in inputs:
            lbl = QLabel(text)
            lbl.setFont(QFont("Vazirmatn", 14))
            lbl.setStyleSheet("color:white;border:none;")
            lbl.setAlignment(Qt.AlignCenter)

            inp = QLineEdit()
            inp.setFont(QFont("Vazirmatn", font_in))
            inp.setFixedHeight(box_height)
            inp.setValidator(QIntValidator())
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background: rgba(0,0,0,220);
                    color:white;
                    border-radius:18px;
                    border:none;
                    padding:15px;
                    font-size:{font_in}px;
                }}
            """)
            inp.installEventFilter(self)

            self.inputs.append(inp)
            right_layout.addWidget(lbl)
            right_layout.addWidget(inp)

        main_h.addWidget(left_card)
        main_h.addWidget(right_card)

        # ===== Stretch بالا =====
        main_v.addStretch(1)
        main_v.addLayout(main_h)

        # ===== فاصله عمودی کارت دکمه‌ها برابر فاصله افقی =====
        main_v.addSpacing(main_h.spacing())

        # ===== کارت دکمه‌ها =====
        btn_card = QWidget()
        btn_card.setFixedSize(card_width * 2 + main_h.spacing(), 90)  # ارتفاع کارت دکمه‌ها افزایش
        btn_card.setStyleSheet(CARD_STYLE)

        btn_layout = QHBoxLayout(btn_card)
        btn_layout.setContentsMargins(20, 15, 20, 15)
        btn_layout.setSpacing(20)

        clear_btn = QPushButton("پاک کردن")
        clear_btn.setFont(QFont("Vazirmatn", 16))
        clear_btn.setFixedHeight(55)  # ارتفاع دکمه‌ها افزایش
        clear_btn.setStyleSheet("background:#f1c40f;border-radius:18px;")
        clear_btn.clicked.connect(self.clear_inputs)

        menu_btn = QPushButton("منو")
        menu_btn.setFont(QFont("Vazirmatn", 16))
        menu_btn.setFixedHeight(55)
        menu_btn.setStyleSheet("background:#3498db;border-radius:18px;")
        menu_btn.clicked.connect(self.show_start_screen)

        self.check_btn = QPushButton("بررسی")
        self.check_btn.setFont(QFont("Vazirmatn", 16))
        self.check_btn.setFixedHeight(55)
        self.check_btn.setStyleSheet("background:#2ecc71;border-radius:18px;")
        self.check_btn.clicked.connect(self.check_result)

        for b in (clear_btn, menu_btn, self.check_btn):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn_layout.addWidget(b)

        main_v.addWidget(btn_card, alignment=Qt.AlignCenter)

        # ===== Stretch پایین =====
        main_v.addStretch(1)

        self.inputs[0].setFocus()

    # ---------- Helpers ----------
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
        vals = [i.text() for i in self.inputs if i.text()]
        if not vals:
            self.output.setText("⚠️ هیچ مقداری وارد نشده")
        else:
            self.output.setText("ورودی‌های وارد شده:\n" + "\n".join(vals))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
