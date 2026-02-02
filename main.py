import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

# استایل کارت اصلی
CARD_STYLE = """
QWidget#CardFrame {
    background-color: rgba(0, 0, 0, 200);
    border-radius: 30px;
    border: 2px solid rgba(255,255,255,0.15);
}
"""

TEXTS = {
    "fa": {
        "app_title": "سامانه جستجوی بلبرینگ و یاتاقان",
        "choose_lang": "انتخاب زبان / Choose Language",
        "choose_search": "نوع جستجو را انتخاب کنید",
        "bearing": "🔵 جستجوی بلبرینگ",
        "housing": "🟠 جستجوی یاتاقان",
        "check": "جستجو و بررسی",
        "clear": "پاکسازی",
        "back": "بازگشت",
        "inner": "قطر داخلی",
        "outer": "قطر خارجی",
        "width": "عرض",
        "enter_all": "⚠️ لطفاً تمام ابعاد (d, D, B) را وارد کنید",
        "enter_d": "⚠️ لطفاً قطر داخلی را وارد کنید",
        "not_found": "❌ نتیجه‌ای یافت نشد",
        "db_missing": "❌ فایل DataBase.json یافت نشد",
        "select_lang": "تغییر زبان"
    },
    "en": {
        "app_title": "Bearing & Housing Finder",
        "choose_lang": "Choose Language / انتخاب زبان",
        "choose_search": "Select Search Type",
        "bearing": "🔵 Bearing Search",
        "housing": "🟠 Housing Search",
        "check": "Search / Check",
        "clear": "Clear Fields",
        "back": "Go Back",
        "inner": "Inner Diameter",
        "outer": "Outer Diameter",
        "width": "Width",
        "enter_all": "⚠️ Please enter d, D and B",
        "enter_d": "⚠️ Please enter inner diameter",
        "not_found": "❌ No result found",
        "db_missing": "❌ DataBase.json not found",
        "select_lang": "Change Language"
    }
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "fa" 
        self.search_type = None

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        # تنظیم پس‌زمینه
        self.bg_label = QLabel(self.central)
        self.bg_pixmap = QPixmap("assets/background.jpg")
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.central.resizeEvent = self.update_bg_geometry

        self.show_language_screen()
        self.showMaximized()

    def update_bg_geometry(self, event):
        self.bg_label.setGeometry(0, 0, self.central.width(), self.central.height())

    def t(self, key):
        return TEXTS[self.lang].get(key, key)

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ---------- صفحه انتخاب زبان ----------
    def show_language_screen(self):
        self.clear_layout()
        self.setStyleSheet(CARD_STYLE)
        
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedWidth(650)
        card.setMinimumHeight(400)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(30)

        title = QLabel(TEXTS["fa"]["choose_lang"])
        title.setFont(QFont("B Nazanin", 22, QFont.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        h = QHBoxLayout()
        h.setSpacing(20)
        fa_btn = QPushButton("فارسی")
        en_btn = QPushButton("English")

        for btn in (fa_btn, en_btn):
            btn.setFont(QFont("Arial", 18, QFont.Bold))
            btn.setMinimumHeight(100)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e; color: white; 
                    border-radius: 20px; border: none;
                }
                QPushButton:hover { background-color: #2c3e50; }
            """)
            h.addWidget(btn)

        fa_btn.clicked.connect(lambda: self.set_language("fa"))
        en_btn.clicked.connect(lambda: self.set_language("en"))

        v.addLayout(h)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def set_language(self, lang):
        self.lang = lang
        self.setWindowTitle(self.t("app_title"))
        self.show_start_screen()

    # ---------- صفحه اصلی انتخاب نوع جستجو ----------
    def show_start_screen(self):
        self.clear_layout()
        
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedWidth(700)
        card.setMinimumHeight(500)

        v = QVBoxLayout(card)
        v.setContentsMargins(50, 50, 50, 50)
        v.setSpacing(25)

        title = QLabel(self.t("choose_search"))
        title.setFont(QFont("B Nazanin", 26, QFont.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        bearing_btn = QPushButton(self.t("bearing"))
        housing_btn = QPushButton(self.t("housing"))
        lang_btn = QPushButton(self.t("select_lang"))

        for btn in (bearing_btn, housing_btn, lang_btn):
            btn.setMinimumHeight(80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("B Nazanin", 18, QFont.Bold))
            
        bearing_btn.setStyleSheet("background:#3498db; color:white; border-radius:20px; border:none;")
        housing_btn.setStyleSheet("background:#e67e22; color:white; border-radius:20px; border:none;")
        lang_btn.setStyleSheet("background:#7f8c8d; color:white; border-radius:20px; border:none;")

        bearing_btn.clicked.connect(lambda: self.start_search("bearing"))
        housing_btn.clicked.connect(lambda: self.start_search("housing"))
        lang_btn.clicked.connect(self.show_language_screen)

        v.addWidget(bearing_btn)
        v.addWidget(housing_btn)
        v.addSpacing(10)
        v.addWidget(lang_btn)

        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    # ---------- صفحه جستجو ----------
    def show_search_screen(self):
        self.clear_layout()
        
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedWidth(1100)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(30)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(25)

        self.inputs = []
        
        # تنظیم تعداد فیلدها بر اساس نوع انتخاب شده
        if self.search_type == "bearing":
            field_configs = [("d", self.t("inner")), ("D", self.t("outer")), ("B", self.t("width"))]
        else:
            field_configs = [("d", self.t("inner"))]

        for eng, title in field_configs:
            box = QVBoxLayout()
            lbl = QLabel(f"{title}\n({eng})")
            lbl.setFont(QFont("B Nazanin", 14, QFont.Bold))
            lbl.setStyleSheet("color: white; border: none;")
            lbl.setAlignment(Qt.AlignCenter)

            edit = QLineEdit()
            edit.setFont(QFont("Arial", 20, QFont.Bold))
            edit.setMinimumHeight(70)
            edit.setAlignment(Qt.AlignCenter)
            edit.setStyleSheet("background: white; color: #2c3e50; border-radius: 15px;")

            box.addWidget(lbl)
            box.addWidget(edit)
            fields_layout.addLayout(box)
            self.inputs.append(edit)

        v.addLayout(fields_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Arial", 16, QFont.Bold))
        self.output.setMinimumHeight(200)
        self.output.setStyleSheet("""
            background: rgba(255,255,255,0.1); color: #f1c40f; 
            border-radius: 20px; padding: 20px; border: 1px solid #f1c40f;
        """)
        v.addWidget(self.output)

        btn_h = QHBoxLayout()
        btn_h.setSpacing(20)

        btns = [
            (self.t("check"), "#2ecc71", self.check_result),
            (self.t("clear"), "#c0392b", lambda: [i.clear() for i in self.inputs]),
            (self.t("back"), "#e67e22", self.show_start_screen)
        ]

        for text, color, func in btns:
            b = QPushButton(text)
            b.setFont(QFont("B Nazanin", 16, QFont.Bold))
            b.setMinimumHeight(75)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(f"background: {color}; color: white; border-radius: 15px; border: none;")
            b.clicked.connect(func)
            btn_h.addWidget(b)

        v.addLayout(btn_h)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def start_search(self, mode):
        self.search_type = mode
        self.show_search_screen()

    # ---------- منطق جستجو ----------
    def check_result(self):
        try:
            with open("DataBase/DataBase.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.output.clear()
            found = False

            if self.search_type == "bearing":
                values = [i.text().strip() for i in self.inputs]
                if any(not v for v in values):
                    self.output.setText(self.t("enter_all"))
                    return
                
                d, D, B = values
                for item in data.get("bearings", []):
                    if (str(item["inner_diameter"]) == d and 
                        str(item["outer_diameter"]) == D and 
                        str(item["width"]) == B):
                        self.output.append(f"✅ Model: {item['model']}")
                        found = True

            elif self.search_type == "housing":
                d = self.inputs[0].text().strip()
                if not d:
                    self.output.setText(self.t("enter_d"))
                    return

                for item in data.get("housings", []):
                    if str(item["inner_diameter"]) == d:
                        self.output.append(f"✅ Model: {item['model']}")
                        found = True

            if not found:
                self.output.setText(self.t("not_found"))

        except FileNotFoundError:
            self.output.setText(self.t("db_missing"))
        except Exception as e:
            self.output.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
