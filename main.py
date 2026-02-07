import json
import os
import re
import sys
import unicodedata

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, Qt
from PyQt5.QtGui import QColor, QFont, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QBoxLayout,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QShortcut,
    QSizePolicy,
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

PRIMARY_BUTTON_STYLE = """
QPushButton {
    background: #27ae60;
    color: white;
    border-radius: 15px;
    padding: 10px 16px;
    font-weight: bold;
}
QPushButton:hover { background: #2ecc71; }
QPushButton:disabled { background: #7f8c8d; color: #ecf0f1; }
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.45);
    border-radius: 15px;
    padding: 10px 16px;
    font-weight: bold;
}
QPushButton:hover { background: rgba(255, 255, 255, 0.16); }
"""

TEXTS = {
    "fa": {
        "app_title": "سامانه جستجوی بلبرینگ و یاتاقان",
        "choose_lang": "انتخاب زبان / Choose Language",
        "choose_search": "نوع جستجو را انتخاب کنید",
        "bearing": " جستجوی بلبرینگ",
        "housing": " جستجوی یاتاقان",
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
        "select_lang": "تغییر زبان",
        "results_found": "✅ نتیجه یافت شد:",
        "critical_error": "خطای بحرانی",
        "searching": "در حال بررسی...",
    },
    "en": {
        "app_title": "Bearing & Housing Finder",
        "choose_lang": "Choose Language / انتخاب زبان",
        "choose_search": "Select Search Type",
        "bearing": " Bearing Search",
        "housing": " Housing Search",
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
        "searching": "Searching...",
    },
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "fa"
        self.search_type = None
        self.inputs = []
        self.input_map = {}
        self.current_screen = None

        self.setWindowTitle("Bearing Finder")
        self.setMinimumSize(960, 640)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        self.bg_label = QLabel(self.central)
        if os.path.exists("assets/background.jpg"):
            self.bg_pixmap = QPixmap("assets/background.jpg")
            self.bg_label.setPixmap(self.bg_pixmap)
            self.bg_label.setScaledContents(True)
        self.bg_label.lower()
        self.init_shortcuts()
        self.apply_language_ui()

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

    def init_shortcuts(self):
        self.shortcut_back = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_back.activated.connect(self.handle_back_shortcut)

        self.shortcut_lang = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_lang.activated.connect(self.show_language_screen)

    def apply_language_ui(self):
        if self.lang == "fa":
            self.setLayoutDirection(Qt.RightToLeft)
            self.setFont(QFont("B Nazanin", 12))
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            self.setFont(QFont("Segoe UI", 10))

        self.setWindowTitle(self.t("app_title"))

    def set_output_message(self, text, color="#f1c40f"):
        self.output.clear()
        item = QListWidgetItem(text)
        item.setForeground(QColor(color))
        self.output.addItem(item)

    def animate_widgets(self, widgets, duration=180):
        # نگهداری رفرنس انیمیشن‌ها برای جلوگیری از garbage collection
        self._active_anim_group = QSequentialAnimationGroup(self)
        for w in widgets:
            effect = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(effect)
            effect.setOpacity(0.0)

            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            self._active_anim_group.addAnimation(anim)

        self._active_anim_group.start()

    def handle_back_shortcut(self):
        if self.current_screen == "search":
            self.show_start_screen()
        elif self.current_screen == "start":
            self.show_language_screen()

    # --- صفحات برنامه ---
    def show_language_screen(self):
        self.clear_layout()
        self.current_screen = "language"
        self.setStyleSheet(CARD_STYLE)

        card = QFrame()
        card.setObjectName("CardFrame")
        card.setMinimumSize(520, 320)
        card.setMaximumWidth(700)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

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
            btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
            h.addWidget(btn)

        fa_btn.clicked.connect(lambda: self.set_language("fa"))
        en_btn.clicked.connect(lambda: self.set_language("en"))

        v.addLayout(h)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    def set_language(self, lang):
        self.lang = lang
        self.apply_language_ui()
        self.show_start_screen()

    def show_start_screen(self):
        self.clear_layout()
        self.current_screen = "start"
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setMinimumSize(600, 460)
        card.setMaximumWidth(780)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

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

        menu_buttons = []
        for btn, style in [
            (b_btn, SECONDARY_BUTTON_STYLE),
            (h_btn, SECONDARY_BUTTON_STYLE),
            (l_btn, SECONDARY_BUTTON_STYLE),
        ]:
            btn.setMinimumHeight(80)
            btn.setFont(QFont("B Nazanin", 18, QFont.Bold))
            btn.setStyleSheet(style)
            btn.setCursor(Qt.PointingHandCursor)
            v.addWidget(btn)
            menu_buttons.append(btn)

        b_btn.clicked.connect(lambda: self.start_search("bearing"))
        h_btn.clicked.connect(lambda: self.start_search("housing"))
        l_btn.clicked.connect(self.show_language_screen)

        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()
        self.animate_widgets([title] + menu_buttons)

    def show_search_screen(self):
        self.clear_layout()
        self.current_screen = "search"
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setMinimumWidth(1080)
        card.setMinimumHeight(760)
        card.setMaximumWidth(1500)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(18)

        fields_layout = QHBoxLayout()
        fields_layout.setDirection(QBoxLayout.LeftToRight)
        self.inputs = []
        self.input_map = {}

        if self.search_type == "bearing":
            configs = [("d", self.t("inner")), ("D", self.t("outer")), ("B", self.t("width"))]
        else:
            configs = [("d", self.t("inner"))]

        for eng, title in configs:
            box = QVBoxLayout()
            lbl = QLabel(title)
            lbl.setStyleSheet("color: white; border: none;")
            lbl.setFont(QFont("B Nazanin", 14, QFont.Bold))

            edit = QLineEdit()
            edit.setMinimumHeight(60)
            edit.setFont(QFont("Arial", 18))
            edit.setAlignment(Qt.AlignCenter)
            edit.setLayoutDirection(Qt.LeftToRight)
            edit.setStyleSheet("border-radius:10px; background:white;")
            edit.setMinimumWidth(220)
            edit.setPlaceholderText("مثال: 25.0 mm" if self.lang == "fa" else "e.g. 25.0 mm")

            box.addWidget(lbl)
            box.addWidget(edit)
            fields_layout.addLayout(box)
            self.inputs.append(edit)
            self.input_map[eng] = edit

        v.addLayout(fields_layout)

        if self.inputs:
            self.inputs[0].setFocus()
            for i, inp in enumerate(self.inputs):
                inp.returnPressed.connect(lambda i=i: self.on_return_pressed(i))

        self.output = QListWidget()
        self.output.setMinimumHeight(250)
        self.output.setFont(QFont("Consolas", 12))
        self.output.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.output.setAlternatingRowColors(False)
        self.output.setStyleSheet(
            """
            QListWidget {
                background: rgba(255,255,255,0.1);
                color: #f1c40f;
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.2);
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 8px;
                background: transparent;
            }
            QListWidget::item:selected {
                background: rgba(241, 196, 15, 0.28);
                color: #ffffff;
            }
            """
        )
        v.addWidget(self.output)

        btn_h = QHBoxLayout()
        for text, style, func in [
            (self.t("check"), PRIMARY_BUTTON_STYLE, self.check_result),
            (self.t("clear"), SECONDARY_BUTTON_STYLE, self.clear_inputs),
            (self.t("back"), SECONDARY_BUTTON_STYLE, self.show_start_screen),
        ]:
            b = QPushButton(text)
            b.setMinimumHeight(70)
            b.setFont(QFont("Arial", 16, QFont.Bold))
            b.setStyleSheet(style)
            b.clicked.connect(func)
            btn_h.addWidget(b)
            if func == self.check_result:
                self.check_btn = b

        self.check_btn.setDefault(True)
        self.check_btn.setAutoDefault(True)

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
        if hasattr(self, "output"):
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

        # نرمال‌سازی برای حذف علائم کنترلی RTL/LTR و اختلاف‌های یونیکدی
        txt = unicodedata.normalize("NFKC", txt)
        txt = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]", "", txt)

        # ارقام فارسی/عربی + جداکننده‌های اعشاری رایج
        trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬،", "01234567890123456789.,,")
        txt = txt.translate(trans)
        txt = txt.replace(",", ".").replace("/", ".").replace("\\", ".")
        txt = re.sub(r"\s+", "", txt)
        txt = re.sub(r"[^0-9.+-]", "", txt)

        # اگر چند نقطه وجود داشت، فقط اولین نقطه نگه داشته شود
        if txt.count(".") > 1:
            first = txt.find(".")
            txt = txt[: first + 1] + txt[first + 1 :].replace(".", "")

        match = re.search(r"[-+]?(?:\d+\.\d+|\d+|\.\d+)", txt)
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
        self.check_btn.setEnabled(False)
        self.check_btn.setText(self.t("searching"))
        QApplication.processEvents()

        try:
            if not os.path.exists(db_path):
                self.set_output_message(self.t("db_missing"), "#ff8a80")
                return

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

            if self.search_type == "bearing":
                user_d = self.safe_float(self.input_map.get("d").text()) if self.input_map.get("d") else None
                user_D = self.safe_float(self.input_map.get("D").text()) if self.input_map.get("D") else None
                user_B = self.safe_float(self.input_map.get("B").text()) if self.input_map.get("B") else None
                missing_input = any(v is None for v in (user_d, user_D, user_B))
            else:
                user_d = self.safe_float(self.input_map.get("d").text()) if self.input_map.get("d") else None
                user_D = None
                user_B = None
                missing_input = user_d is None

            if missing_input:
                msg = self.t("enter_all") if self.search_type == "bearing" else self.t("enter_d")
                self.set_output_message(msg, "#ffd180")
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
                        abs(d_val - user_d) < 0.1
                        and abs(D_val - user_D) < 0.1
                        and abs(B_val - user_B) < 0.1
                    ):
                        model = self._get_by_keys(item, ["model", "Model"], ["model"]) or "N/A"
                        desc = self._get_localized_desc(item)
                        found_models.append((str(model), str(desc)))

                elif self.search_type == "housing":
                    if d_val is None:
                        continue

                    if abs(d_val - user_d) < 0.1:
                        model = self._get_by_keys(item, ["model", "Model"], ["model"]) or "N/A"
                        desc = self._get_localized_desc(item)
                        found_models.append((str(model), str(desc)))

            self.output.clear()
            if found_models:
                unique = sorted(set(found_models), key=lambda x: x[0])
                header = QListWidgetItem(self.t("results_found"))
                header.setForeground(QColor("#2ecc71"))
                self.output.addItem(header)
                for idx, (model, desc) in enumerate(unique):
                    text = f"• {model} — {desc}" if desc else f"• {model}"
                    item = QListWidgetItem(text)
                    item.setForeground(QColor("#f1c40f"))
                    self.output.addItem(item)
                    if idx < len(unique) - 1:
                        sep = QListWidgetItem("-" * 52)
                        sep.setForeground(QColor("#95a5a6"))
                        sep.setFlags(Qt.NoItemFlags)
                        self.output.addItem(sep)
            else:
                self.set_output_message(self.t("not_found"), "#ff8a80")

        except Exception as e:
            self.set_output_message(f"{self.t('critical_error')}: {e}", "#ff8a80")
        finally:
            self.check_btn.setEnabled(True)
            self.check_btn.setText(self.t("check"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
