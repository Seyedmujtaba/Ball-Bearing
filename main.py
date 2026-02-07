import json
import os
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

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
        "not_found": "❌ نتیجهای یافت نشد",
        "db_missing": "❌ فایل دیتابیس (DataBase.json) پیدا نشد",
        "select_lang": "تغییر زبان",
        "results_found": "✅ نتیجه یافت شد:",
        "critical_error": "خطای بحرانی",
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
        "select_lang": "Change Language",
        "results_found": "✅ Results Found:",
        "critical_error": "Critical Error",
    },
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "fa"
        self.search_type = None
        self.inputs = []

        self.setWindowTitle("Bearing Finder")
        self.setMinimumSize(1200, 800)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        self.bg_label = QLabel(self.central)
        if os.path.exists("assets/background.jpg"):
            self.bg_pixmap = QPixmap("assets/background.jpg")
            self.bg_label.setPixmap(self.bg_pixmap)
            self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        self.show_language_screen()
        self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_label.setGeometry(self.central.rect())

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

        if self.search_type == "bearing":
            configs = [("d", self.t("inner")), ("D", self.t("outer")), ("B", self.t("width"))]
        else:
            configs = [("d", self.t("inner"))]

        for _eng, title in configs:
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

        if self.inputs:
            self.inputs[0].setFocus()
            for i, inp in enumerate(self.inputs):
                inp.returnPressed.connect(lambda i=i: self.on_return_pressed(i))

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(250)
        self.output.setFont(QFont("Consolas", 14))
        self.output.setStyleSheet(
            "background: rgba(255,255,255,0.1); color: #f1c40f; border-radius:15px; padding:15px;"
        )
        v.addWidget(self.output)

        btn_h = QHBoxLayout()
        for text, color, func in [
            (self.t("check"), "#2ecc71", self.check_result),
            (self.t("clear"), "#c0392b", self.clear_inputs),
            (self.t("back"), "#e67e22", self.show_start_screen),
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

    def on_return_pressed(self, index):
        if index < len(self.inputs) - 1:
            self.inputs[index + 1].setFocus()
        else:
            self.check_result()

    def clear_inputs(self):
        for field in self.inputs:
            field.clear()
        self.output.clear()
        if self.inputs:
            self.inputs[0].setFocus()

    def safe_float(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        txt = str(value).strip()
        if not txt:
            return None

        # پشتیبانی از ارقام فارسی/عربی و جداکننده های رایج
        trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬", "01234567890123456789.,")
        txt = txt.translate(trans).replace(",", ".")

        match = re.search(r"[-+]?\d*\.?\d+", txt)
        if not match:
            return None

        try:
            return float(match.group(0))
        except ValueError:
            return None

    def _norm_key(self, key):
        return re.sub(r"[^a-z0-9]", "", str(key).strip().lower())

    def _get_by_keys(self, item, exact_keys, normalized_keys):
        # exact case-sensitive match اولویت دارد تا d و D قاطی نشوند
        for key in exact_keys:
            if key in item and item[key] is not None:
                return item[key]

        exact_map = {str(k).strip().lower(): v for k, v in item.items() if v is not None}
        for key in exact_keys:
            hit = exact_map.get(str(key).strip().lower())
            if hit is not None:
                return hit

        normalized_candidates = {self._norm_key(k) for k in normalized_keys}
        for k, v in item.items():
            if v is None:
                continue
            if self._norm_key(k) in normalized_candidates:
                return v

        return None

    def _get_localized_desc(self, item):
        if self.lang == "en":
            primary = self._get_by_keys(
                item,
                ["purpose_en", "description_en", "special_features_en"],
                ["purposeen", "descriptionen", "specialfeaturesen"],
            )
            if primary:
                return primary

        if self.lang == "fa":
            primary = self._get_by_keys(
                item,
                ["purpose", "description", "special_features"],
                ["purpose", "description", "specialfeatures"],
            )
            if primary:
                return primary

        fallback = self._get_by_keys(
            item,
            [
                "purpose",
                "purpose_en",
                "description",
                "description_en",
                "special_features",
                "special_features_en",
            ],
            [
                "purpose",
                "purposeen",
                "description",
                "descriptionen",
                "specialfeatures",
                "specialfeaturesen",
            ],
        )
        return fallback or ""

    def check_result(self):
        db_path = "DataBase/DataBase.json"
        if not os.path.exists(db_path):
            self.output.setText(self.t("db_missing"))
            return

        try:
            with open(db_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if isinstance(raw_data, list):
                items = raw_data
            elif isinstance(raw_data, dict):
                key = "bearings" if self.search_type == "bearing" else "housings"
                items = raw_data.get(key, [])
                if not items:
                    items = next((v for v in raw_data.values() if isinstance(v, list)), [])
            else:
                items = []

            user_vals = [self.safe_float(i.text()) for i in self.inputs]
            if any(v is None for v in user_vals):
                self.output.setText(self.t("enter_all") if self.search_type == "bearing" else self.t("enter_d"))
                return

            found_models = []
            for item in items:
                if not isinstance(item, dict):
                    continue

                d_val = self.safe_float(
                    self._get_by_keys(
                        item,
                        exact_keys=["d"],
                        normalized_keys=["inner_diameter", "inner", "di", "id", "innerdiameter"],
                    )
                )

                if self.search_type == "bearing":
                    D_val = self.safe_float(
                        self._get_by_keys(
                            item,
                            exact_keys=["D"],
                            normalized_keys=["outer_diameter", "outer", "od", "douter", "outerdiameter", "de"],
                        )
                    )
                    B_val = self.safe_float(
                        self._get_by_keys(
                            item,
                            exact_keys=["B", "b"],
                            normalized_keys=["width", "w"],
                        )
                    )

                    if d_val is None or D_val is None or B_val is None:
                        continue

                    if (
                        abs(d_val - user_vals[0]) < 0.1
                        and abs(D_val - user_vals[1]) < 0.1
                        and abs(B_val - user_vals[2]) < 0.1
                    ):
                        model = self._get_by_keys(item, ["model", "Model"], ["model"]) or "N/A"
                        desc = self._get_localized_desc(item)
                        found_models.append((str(model), str(desc)))

                elif self.search_type == "housing":
                    if d_val is None:
                        continue

                    if abs(d_val - user_vals[0]) < 0.1:
                        model = self._get_by_keys(item, ["model", "Model"], ["model"]) or "N/A"
                        desc = self._get_localized_desc(item)
                        found_models.append((str(model), str(desc)))

            if found_models:
                unique = sorted(set(found_models), key=lambda x: x[0])
                lines = [f"• {m} — {desc}" if desc else f"• {m}" for m, desc in unique]
                self.output.setText(f"{self.t('results_found')}\n" + "\n".join(lines))
            else:
                self.output.setText(self.t("not_found"))

        except Exception as e:
            self.output.setText(f"{self.t('critical_error')}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
