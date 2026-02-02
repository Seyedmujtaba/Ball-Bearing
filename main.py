import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt


CARD_STYLE = """
QWidget {
    background-color: rgba(0, 0, 0, 180);
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.2);
}
"""

TEXTS = {
    "fa": {
        "app_title": "بلبرینگ / یاتاقان",
        "choose_lang": "انتخاب زبان",
        "choose_search": "انتخاب نوع جستجو",
        "bearing": "🔵 بلبرینگ",
        "housing": "🟠 یاتاقان",
        "check": "بررسی",
        "inner": "قطر داخلی",
        "outer": "قطر خارجی",
        "width": "عرض",
        "enter_all": "⚠️ لطفاً d و D و B را وارد کنید",
        "enter_d": "⚠️ لطفاً قطر داخلی را وارد کنید",
        "not_found": "❌ موردی یافت نشد",
        "db_missing": "❌ فایل DataBase.json پیدا نشد"
    },
    "en": {
        "app_title": "Bearing / Housing",
        "choose_lang": "Choose Language",
        "choose_search": "Select Search Type",
        "bearing": "🔵 Bearing",
        "housing": "🟠 Housing",
        "check": "Check",
        "inner": "Inner Diameter",
        "outer": "Outer Diameter",
        "width": "Width",
        "enter_all": "⚠️ Please enter d, D and B",
        "enter_d": "⚠️ Please enter inner diameter",
        "not_found": "❌ No result found",
        "db_missing": "❌ DataBase.json not found"
    }
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.search_type = None

        self.central = QWidget()
        self.setCentralWidget(self.central)

        # Background
        self.bg_label = QLabel(self.central)
        self.bg_pixmap = QPixmap("assets/background.jpg")
        self.bg_label.setPixmap(self.bg_pixmap)
        self.bg_label.setScaledContents(True)
        self.central.resizeEvent = lambda e: self.bg_label.setGeometry(
            0, 0, self.central.width(), self.central.height()
        )

        self.show_language_screen()
        self.showMaximized()

    def t(self, key):
        return TEXTS[self.lang].get(key, key)

    def clear_layout(self):
        layout = self.central.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    # ---------- Language Screen ----------
    def show_language_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.addStretch(1)

        card = QWidget()
        card.setStyleSheet(CARD_STYLE)
        card.setFixedSize(420, 260)

        v = QVBoxLayout(card)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(25)

        title = QLabel("Choose Language / انتخاب زبان")
        title.setFont(QFont("B Nazanin", 20, QFont.Bold))
        title.setStyleSheet("color:white;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        h = QHBoxLayout()
        fa_btn = QPushButton("فا")
        en_btn = QPushButton("En")

        for btn in (fa_btn, en_btn):
            btn.setFont(QFont("Arial", 18, QFont.Bold))
            btn.setFixedSize(120, 80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "background:#34495e; color:white; border-radius:15px;"
            )
            h.addWidget(btn)

        fa_btn.clicked.connect(lambda: self.set_language("fa"))
        en_btn.clicked.connect(lambda: self.set_language("en"))

        v.addLayout(h)
        main_v.addWidget(card, alignment=Qt.AlignCenter)
        main_v.addStretch(1)

    def set_language(self, lang):
        self.lang = lang
        self.setWindowTitle(self.t("app_title"))
        self.show_start_screen()

    # ---------- Start Screen ----------
    def show_start_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.addStretch(1)

        card = QWidget()
        card.setStyleSheet(CARD_STYLE)
        card.setFixedSize(520, 320)

        v = QVBoxLayout(card)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(25)

        title = QLabel(self.t("choose_search"))
        title.setFont(QFont("B Nazanin", 24, QFont.Bold))
        title.setStyleSheet("color:white;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        bearing_btn = QPushButton(self.t("bearing"))
        housing_btn = QPushButton(self.t("housing"))

        for btn in (bearing_btn, housing_btn):
            btn.setFont(QFont("B Nazanin", 16))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "background:#3498db; color:white; border-radius:15px; padding:15px;"
            )
            v.addWidget(btn)

        bearing_btn.clicked.connect(lambda: self.start_search("bearing"))
        housing_btn.clicked.connect(lambda: self.start_search("housing"))

        main_v.addWidget(card, alignment=Qt.AlignCenter)
        main_v.addStretch(1)

    def start_search(self, mode):
        self.search_type = mode
        self.show_search_screen()

    # ---------- Search Screen ----------
    def show_search_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.setContentsMargins(40, 40, 40, 40)

        card = QWidget()
        card.setStyleSheet(CARD_STYLE)
        card.setFixedWidth(850)

        v = QVBoxLayout(card)
        v.setContentsMargins(35, 35, 35, 35)
        v.setSpacing(25)

        fields = [
            ("d", self.t("inner")),
            ("D", self.t("outer")),
            ("B", self.t("width"))
        ]

        self.inputs = []
        h = QHBoxLayout()

        for eng, title in fields:
            box = QVBoxLayout()
            lbl = QLabel(f"{title} ({eng})")
            lbl.setFont(QFont("B Nazanin", 11))
            lbl.setStyleSheet("color:white;")
            lbl.setAlignment(Qt.AlignCenter)

            edit = QLineEdit()
            edit.setFont(QFont("Arial", 16))
            edit.setFixedSize(170, 55)
            edit.setAlignment(Qt.AlignCenter)
            edit.setStyleSheet(
                "background:white; color:#2c3e50; border-radius:12px;"
            )

            if self.search_type == "housing" and eng != "d":
                edit.setDisabled(True)

            box.addWidget(lbl)
            box.addWidget(edit)
            h.addLayout(box)
            self.inputs.append(edit)

        v.addLayout(h)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Arial", 14))
        self.output.setFixedHeight(150)
        self.output.setStyleSheet(
            "background:rgba(255,255,255,0.1); color:#f1c40f; "
            "border-radius:15px; padding:10px;"
        )
        v.addWidget(self.output)

        btn = QPushButton(self.t("check"))
        btn.setFont(QFont("B Nazanin", 14, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "background:#2ecc71; color:white; border-radius:15px; padding:12px;"
        )
        btn.clicked.connect(self.check_result)
        v.addWidget(btn)

        main_v.addWidget(card, alignment=Qt.AlignCenter)

    # ---------- Logic ----------
    def check_result(self):
        try:
            with open("DataBase/DataBase.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.output.clear()
            found = False

            if self.search_type == "bearing":
                d, D, B = [i.text().strip() for i in self.inputs]
                if not all([d, D, B]):
                    self.output.setText(self.t("enter_all"))
                    return

                for item in data["bearings"]:
                    if (
                        str(item["inner_diameter"]) == d and
                        str(item["outer_diameter"]) == D and
                        str(item["width"]) == B
                    ):
                        self.output.append(item["model"])
                        found = True

            elif self.search_type == "housing":
                d = self.inputs[0].text().strip()
                if not d:
                    self.output.setText(self.t("enter_d"))
                    return

                for item in data["housings"]:
                    if str(item["inner_diameter"]) == d:
                        self.output.append(item["model"])
                        found = True

            if not found:
                self.output.setText(self.t("not_found"))

        except FileNotFoundError:
            self.output.setText(self.t("db_missing"))
        except Exception as e:
            self.output.setText(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
