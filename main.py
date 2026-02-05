import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFrame
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

# --- استایل بصری برنامه ---
CARD_STYLE = """
QWidget#CardFrame {
    background-color: rgba(0, 0, 0, 210);
    border-radius: 30px;
    border: 2px solid rgba(255, 255, 255, 0.2);
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
        "inner": "قطر داخلی (d)",
        "outer": "قطر خارجی (D)",
        "width": "عرض (B)",
        "enter_all": "⚠️ لطفاً تمام ابعاد را وارد کنید",
        "enter_d": "⚠️ لطفاً قطر داخلی را وارد کنید",
        "not_found": "❌ نتیجه‌ای یافت نشد",
        "db_missing": "❌ فایل دیتابیس (DataBase.json) پیدا نشد",
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
        "inner": "Inner Diameter (d)",
        "outer": "Outer Diameter (D)",
        "width": "Width (B)",
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
        
        # تنظیمات پنجره اصلی
        self.setWindowTitle("Bearing Finder")
        self.setMinimumSize(1200, 800)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        # مدیریت پس‌زمینه
        self.bg_label = QLabel(self.central)
        if os.path.exists("assets/background.jpg"):
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

    # --- صفحات برنامه ---
    def show_language_screen(self):
        self.clear_layout()
        self.setStyleSheet(CARD_STYLE)
        
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedSize(650, 400)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel(TEXTS["fa"]["choose_lang"])
        title.setFont(QFont("B Nazanin", 20, QFont.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        h = QHBoxLayout()
        fa_btn = QPushButton("فارسی")
        en_btn = QPushButton("English")

        for btn in (fa_btn, en_btn):
            btn.setFont(QFont("Arial", 16, QFont.Bold))
            btn.setMinimumHeight(80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background:#34495e; color:white; border-radius:15px;")
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

    def show_start_screen(self):
        self.clear_layout()
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedSize(700, 550)

        v = QVBoxLayout(card)
        v.setContentsMargins(50, 50, 50, 50)
        v.setSpacing(20)

        title = QLabel(self.t("choose_search"))
        title.setFont(QFont("B Nazanin", 24, QFont.Bold))
        title.setStyleSheet("color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        b_btn = QPushButton(self.t("bearing"))
        h_btn = QPushButton(self.t("housing"))
        l_btn = QPushButton(self.t("select_lang"))

        for btn, color in [(b_btn, "#3498db"), (h_btn, "#e67e22"), (l_btn, "#7f8c8d")]:
            btn.setMinimumHeight(80)
            btn.setFont(QFont("B Nazanin", 18, QFont.Bold))
            btn.setStyleSheet(f"background:{color}; color:white; border-radius:20px;")
            btn.setCursor(Qt.PointingHandCursor)
            v.addWidget(btn)

        b_btn.clicked.connect(lambda: self.start_search("bearing"))
        h_btn.clicked.connect(lambda: self.start_search("housing"))
        l_btn.clicked.connect(self.show_language_screen)

        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def show_search_screen(self):
        self.clear_layout()
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setFixedWidth(1100)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        
        fields_layout = QHBoxLayout()
        self.inputs = []
        
        configs = [("d", self.t("inner")), ("D", self.t("outer")), ("B", self.t("width"))] if self.search_type == "bearing" else [("d", self.t("inner"))]

        for eng, title in configs:
            box = QVBoxLayout()
            lbl = QLabel(title)
            lbl.setStyleSheet("color: white; border: none;")
            lbl.setFont(QFont("B Nazanin", 14, QFont.Bold))
            edit = QLineEdit()
            edit.setMinimumHeight(60)
            edit.setFont(QFont("Arial", 18))
            edit.setAlignment(Qt.AlignCenter)
            edit.setStyleSheet("border-radius:10px; background:white;")
            box.addWidget(lbl)
            box.addWidget(edit)
            fields_layout.addLayout(box)
            self.inputs.append(edit)

        v.addLayout(fields_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(250)
        self.output.setFont(QFont("Consolas", 14))
        self.output.setStyleSheet("background: rgba(255,255,255,0.1); color: #f1c40f; border-radius:15px; padding:15px;")
        v.addWidget(self.output)

        btn_h = QHBoxLayout()
        for text, color, func in [
            (self.t("check"), "#2ecc71", self.check_result),
            (self.t("clear"), "#c0392b", lambda: [i.clear() for i in self.inputs]),
            (self.t("back"), "#e67e22", self.show_start_screen)
        ]:
            b = QPushButton(text)
            b.setMinimumHeight(70)
            b.setFont(QFont("Arial", 16, QFont.Bold))
            b.setStyleSheet(f"background:{color}; color:white; border-radius:15px;")
            b.clicked.connect(func)
            btn_h.addWidget(b)
        
        v.addLayout(btn_h)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def start_search(self, mode):
        self.search_type = mode
        self.show_search_screen()

    # --- منطق جستجوی فوق هوشمند (حل مشکل Type و Key) ---
    def safe_float(self, value):
        try:
            if value is None: return -1.0
            # پاکسازی رشته از هر چیزی جز عدد و نقطه
            clean = "".join(c for c in str(value) if c.isdigit() or c == '.')
            return float(clean) if clean else -1.0
        except:
            return -1.0

    def check_result(self):
        db_path = "DataBase/DataBase.json"
        if not os.path.exists(db_path):
            self.output.setText(self.t("db_missing"))
            return

        try:
            with open(db_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # استخراج لیست داده‌ها
            if isinstance(raw_data, list):
                items = raw_data
            elif isinstance(raw_data, dict):
                key = "bearings" if self.search_type == "bearing" else "housings"
                items = raw_data.get(key, [])
                if not items:
                    items = next((v for v in raw_data.values() if isinstance(v, list)), [])
            else:
                items = []

            # دریافت ورودی کاربر
            user_vals = [self.safe_float(i.text()) for i in self.inputs]
            if any(v == -1.0 for v in user_vals):
                self.output.setText(self.t("enter_all") if self.search_type == "bearing" else self.t("enter_d"))
                return

            found_models = []
            for item in items:
                if not isinstance(item, dict): continue
                
                # نرمال‌سازی کلیدهای دیتابیس (تبدیل همه به حروف کوچک و حذف فضا)
                norm_item = {str(k).strip().lower(): v for k, v in item.items()}
                
                # کمکی: تلاش برای گرفتن مقدار از میان چند نام ممکن (synonyms)
                def get_any(possible_keys):
                    # possible_keys باید لیستی از اسامی به صورت lowercase باشد
                    for k in possible_keys:
                        if k in norm_item and norm_item[k] is not None:
                            return norm_item[k]
                    # fallback: چک کردن کلیدهای اوریجینال (در صورت وجود اختلاف فرمت)
                    for k0, v0 in item.items():
                        if str(k0).strip().lower() in possible_keys:
                            return v0
                    return None

                # مجموعه کلیدهای محتمل برای هر فیلد
                d_val = self.safe_float(get_any(['d','inner_diameter','inner','di','id','innerdiameter']))
                if self.search_type == "bearing":
                    D_val = self.safe_float(get_any(['d_outer','outer_diameter','outer','od','douter','outerdiameter']))
                    B_val = self.safe_float(get_any(['b','width','w']))
                    if (abs(d_val - user_vals[0]) < 0.1 and 
                        abs(D_val - user_vals[1]) < 0.1 and 
                        abs(B_val - user_vals[2]) < 0.1):
                        model = get_any(['model']) or item.get("Model") or "N/A"
                        found_models.append(str(model))

                elif self.search_type == "housing":
                    if abs(d_val - user_vals[0]) < 0.1:
                        model = get_any(['model']) or item.get("Model") or "N/A"
                        found_models.append(str(model))

            if found_models:
                res = "✅ Results Found:\n" + "\n".join([f"• {{m}}" for m in sorted(set(found_models))])
                self.output.setText(res)
            else:
                self.output.setText(self.t("not_found"))

        except Exception as e:
            self.output.setText(f"Critical Error: {{str(e)}}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())