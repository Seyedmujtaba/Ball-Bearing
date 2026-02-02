import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("بلبرینگ / یاتاقان")
        self.search_type = None

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

        self.show_start_screen()
        self.showMaximized()

    # ---------- پاک‌سازی Layout ----------
    def clear_layout(self):
        layout = self.central.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    # ---------- صفحه انتخاب ----------
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

        title = QLabel("انتخاب نوع جستجو")
        title.setFont(QFont("B Nazanin", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        bearing_btn = QPushButton("🔵 بلبرینگ")
        housing_btn = QPushButton("🟠 یاتاقان")

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

    # ---------- صفحه جستجو ----------
    def show_search_screen(self):
        self.clear_layout()
        main_v = QVBoxLayout(self.central)
        main_v.setContentsMargins(40, 40, 40, 40)

        input_card = QWidget()
        input_card.setStyleSheet(CARD_STYLE)
        input_card.setFixedWidth(850)

        v = QVBoxLayout(input_card)
        v.setContentsMargins(35, 35, 35, 35)
        v.setSpacing(25)

        fields = [
            ("d", "قطر داخلی"),
            ("D", "قطر خارجی"),
            ("B", "عرض")
        ]

        self.inputs = []
        h = QHBoxLayout()

        for eng, per in fields:
            box = QVBoxLayout()
            lbl = QLabel(f"{per} ({eng})")
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

        btn = QPushButton("بررسی")
        btn.setFont(QFont("B Nazanin", 14, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "background:#2ecc71; color:white; border-radius:15px; padding:12px;"
        )
        btn.clicked.connect(self.check_result)
        v.addWidget(btn)

        main_v.addWidget(input_card, alignment=Qt.AlignCenter)

    # ---------- منطق جستجو ----------
    def check_result(self):
        try:
            with open("DataBase/DataBase.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            self.output.clear()
            found = False

            # ===== بلبرینگ =====
            if self.search_type == "bearing":
                d = self.inputs[0].text().strip()
                D = self.inputs[1].text().strip()
                B = self.inputs[2].text().strip()

                if not all([d, D, B]):
                    self.output.setText("⚠️ لطفاً d و D و B را وارد کنید")
                    return

                for item in data["bearings"]:
                    if (
                        str(item["inner_diameter"]) == d and
                        str(item["outer_diameter"]) == D and
                        str(item["width"]) == B
                    ):
                        self.output.append(item["model"])
                        found = True

            # ===== یاتاقان =====
            elif self.search_type == "housing":
                d = self.inputs[0].text().strip()

                if not d:
                    self.output.setText("⚠️ لطفاً قطر داخلی را وارد کنید")
                    return

                for item in data["housings"]:
                    if str(item["inner_diameter"]) == d:
                        self.output.append(item["model"])
                        found = True

            if not found:
                self.output.setText("❌ موردی یافت نشد")

        except FileNotFoundError:
            self.output.setText("❌ فایل DataBase.json پیدا نشد")
        except Exception as e:
            self.output.setText(f"خطای سیستم: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
