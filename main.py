import sys
import json  # اضافه شده برای کار با دیتابیس
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
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout_recursive(child.layout())

    # ---------- صفحه شروع ----------
    def show_start_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.addStretch(1)

        start_card = QWidget()
        start_card.setStyleSheet(CARD_STYLE)
        start_card.setFixedSize(500, 300)
        
        card_v = QVBoxLayout(start_card)
        card_v.setContentsMargins(30, 30, 30, 30)

        title = QLabel("سیستم جستجوی بلبرینگ")
        title.setFont(QFont("B Nazanin", 26, QFont.Bold))
        title.setStyleSheet("color: white; border: none; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        card_v.addWidget(title)

        card_v.addStretch(1)

        start_btn = QPushButton("ورود به بخش جستجو")
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setFont(QFont("B Nazanin", 16))
        start_btn.setStyleSheet("background: #3498db; color: white; border-radius: 15px; padding: 15px;")
        start_btn.clicked.connect(self.show_search_screen)
        card_v.addWidget(start_btn)

        main_v.addWidget(start_card, alignment=Qt.AlignCenter)
        main_v.addStretch(1)

    # ---------- صفحه جستجو ----------
    def show_search_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.setContentsMargins(40, 40, 40, 40)

        # ===== هدر =====
        header_h = QHBoxLayout()
        back_btn = QPushButton("⬅ بازگشت")
        back_btn.setFixedSize(120, 45)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("background: #e74c3c; color: white; border-radius: 12px;")
        back_btn.clicked.connect(self.show_start_screen)
        header_h.addWidget(back_btn)
        header_h.addStretch()
        main_v.addLayout(header_h)

        main_v.addStretch(1)

        # ===== کارت ورودی‌ها =====
        input_card = QWidget()
        input_card.setStyleSheet(CARD_STYLE)
        input_card.setFixedWidth(min(800, self.screen.width() - 100))
        
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(35, 35, 35, 35)
        input_layout.setSpacing(25)

        fields_h = QHBoxLayout()
        self.inputs = []
        labels = [("d (Internal)", "قطر داخلی"), ("D (Outer)", "قطر خارجی"), ("B (Width)", "عرض")]
        
        for eng, per in labels:
            box = QVBoxLayout()
            l = QLabel(f"{per}\n({eng})")
            l.setFont(QFont("B Nazanin", 11))
            l.setStyleSheet("color: #ecf0f1; border: none; background: transparent;")
            l.setAlignment(Qt.AlignCenter)
            
            edit = QLineEdit()
            edit.setPlaceholderText("00.0")
            edit.setAlignment(Qt.AlignCenter)
            edit.setFont(QFont("Arial", 18, QFont.Bold))
            edit.setFixedSize(160, 60)
            edit.setStyleSheet("background: white; color: #2c3e50; border-radius: 15px; border: 2px solid #3498db;")
            edit.installEventFilter(self)
            
            box.addWidget(l)
            box.addWidget(edit)
            fields_h.addLayout(box)
            self.inputs.append(edit)

        input_layout.addLayout(fields_h)

        # ===== خروجی =====
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("مدل بلبرینگ در اینجا نمایش داده می‌شود...")
        self.output.setFont(QFont("Arial", 16))
        self.output.setAlignment(Qt.AlignCenter)
        self.output.setFixedHeight(120)
        self.output.setStyleSheet("background: rgba(255,255,255,0.1); color: #f1c40f; border-radius: 15px; border: 1px dashed #f1c40f; padding: 10px;")
        input_layout.addWidget(self.output)

        # ===== دکمه‌ها =====
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("پاک کردن")
        clear_btn.clicked.connect(self.clear_inputs)
        clear_btn.setStyleSheet("background:#95a5a6; border-radius:18px; padding:12px; color:white;")
        
        menu_btn = QPushButton("راهنما")
        menu_btn.setStyleSheet("background:#34495e; border-radius:18px; padding:12px; color:white;")

        self.check_btn = QPushButton("بررسی (Check)")
        self.check_btn.setFont(QFont("B Nazanin", 14, QFont.Bold))
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.setStyleSheet("background:#2ecc71; border-radius:18px; padding:12px; color:white;")
        self.check_btn.clicked.connect(self.check_result)

        for b in (clear_btn, menu_btn, self.check_btn):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn_layout.addWidget(b)

        input_layout.addLayout(btn_layout)
        main_v.addWidget(input_card, alignment=Qt.AlignCenter)
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

    # تابع تغییر یافته برای جستجو در ۶۳۰ ردیف دیتابیس
    def check_result(self):
        d_val = self.inputs[0].text().strip()
        D_val = self.inputs[1].text().strip()
        B_val = self.inputs[2].text().strip()

        if not all([d_val, D_val, B_val]):
            self.output.setText("⚠️ لطفاً d و D و B را وارد کنید")
            return

        try:
            with open('DataBase.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = []
            for item in data['bearings']:
                # مقایسه به صورت رشته برای جلوگیری از تضاد عدد و متن
                if (str(item['inner_diameter']) == d_val and 
                    str(item['outer_diameter']) == D_val and 
                    str(item['width']) == B_val):
                    results.append(item['model'])

            if results:
                self.output.setText(f"✅ مدل‌های یافت شده:\n" + " | ".join(results))
            else:
                self.output.setText(f"❌ موردی با ابعاد {d_val}x{D_val}x{B_val} یافت نشد")
        
        except FileNotFoundError:
            self.output.setText("❌ خطا: فایل DataBase.json پیدا نشد")
        except Exception as e:
            self.output.setText(f"خطای سیستم: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
