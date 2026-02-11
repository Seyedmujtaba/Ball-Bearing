import json
import os
import re
import sys
import unicodedata
import subprocess

from PyQt5.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QParallelAnimationGroup,
    QPauseAnimation,
    QRect,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
)
from PyQt5.QtGui import QColor, QFont, QKeySequence, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QBoxLayout,
    QFrame,
    QGraphicsBlurEffect,
    QGraphicsDropShadowEffect,
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
    background-color: rgba(10, 16, 24, 145);
    border-radius: 30px;
    border: 1.5px solid rgba(255, 255, 255, 0.28);
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
        "app_title": "جستجوگر بلبرینگ و یاتاقان",
        "choose_lang": "انتخاب زبان / Choose Language",
        "choose_search": "نوع جستجو را انتخاب کنید",
        "bearing": " جستجوی بلبرینگ",
        "housing": " جستجوی یاتاقان",
        "check": "جستجو / بررسی",
        "clear": "پاکسازی فیلدها",
        "back": "بازگشت",
        "inner": "قطر داخلی (d)",
        "outer": "قطر خارجی (D)",
        "width": "عرض (B)",
        "enter_all": "⚠️ لطفاً d، D و B را وارد کنید",
        "enter_d": "⚠️ لطفاً قطر داخلی را وارد کنید",
        "not_found": "❌ نتیجه‌ای یافت نشد",
        "db_missing": "❌ فایل DataBase.json پیدا نشد",
        "select_lang": "تغییر زبان",
        "results_found": "✅ نتایج یافت شد:",
        "critical_error": "خطای بحرانی",
        "searching": "در حال جستجو...",
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

PERSIAN_DIGITS = "".join(chr(code) for code in range(0x06F0, 0x06FA))
ARABIC_INDIC_DIGITS = "".join(chr(code) for code in range(0x0660, 0x066A))
ARABIC_DECIMAL_SEP = "\u066b"
ARABIC_THOUSANDS_SEP = "\u066c"
ARABIC_COMMA = "\u060c"

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "fa"
        self.search_type = None
        self.inputs = []
        self.input_map = {}
        self.current_screen = None
        self._active_anim_group = None
        self._output_fade_anim = None
        self._pulse_group = None
        self._glass_cards = []

        self.setWindowTitle("Bearing Finder")
        self.setMinimumSize(960, 640)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        self.bg_label = QLabel(self.central)
        bg_path = resource_path("assets/background.jpg")
        if os.path.exists(bg_path):
            self.bg_pixmap = QPixmap(bg_path)
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
        for card in list(self._glass_cards):
            if card is None or not card.isVisible():
                continue
            self._update_glass_backdrop(card)

    def t(self, key):
        return TEXTS[self.lang].get(key, key)

    def clear_layout(self):
        if self._active_anim_group:
            self._active_anim_group.stop()
            self._active_anim_group = None
        if self._output_fade_anim:
            self._output_fade_anim.stop()
            self._output_fade_anim = None
        if self._pulse_group:
            self._pulse_group.stop()
            self._pulse_group = None
        for card in list(self._glass_cards):
            self._detach_glass_backdrop(card)
        self._glass_cards.clear()
        for backdrop in self.central.findChildren(QLabel, "GlassBackdrop"):
            backdrop.hide()
            backdrop.clear()
            backdrop.setParent(None)
            backdrop.deleteLater()
        self._hover_buttons = getattr(self, "_hover_buttons", set())
        self._hover_buttons.clear()
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().setParent(None)
                item.widget().deleteLater()
        self.central.update()
        self.central.repaint()

    def _apply_glass_card_effect(self, card):
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 95))
        card.setGraphicsEffect(shadow)
        if card not in self._glass_cards:
            self._glass_cards.append(card)
        card.installEventFilter(self)

    def _detach_glass_backdrop(self, card):
        backdrop = getattr(card, "_bb_backdrop_label", None)
        if backdrop is None:
            return
        backdrop.hide()
        backdrop.clear()
        backdrop.setParent(None)
        backdrop.deleteLater()
        card._bb_backdrop_label = None

    def _update_glass_backdrop(self, card):
        if not hasattr(self, "bg_pixmap"):
            return
        if card is None:
            return
        top_left = card.mapTo(self.central, QPoint(0, 0))
        card_rect = QRect(top_left, card.size())
        if card_rect.width() <= 0 or card_rect.height() <= 0:
            return

        backdrop = getattr(card, "_bb_backdrop_label", None)
        if backdrop is None:
            backdrop = QLabel(self.central)
            backdrop.setObjectName("GlassBackdrop")
            backdrop.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            blur = QGraphicsBlurEffect(backdrop)
            blur.setBlurRadius(30)
            backdrop.setGraphicsEffect(blur)
            card._bb_backdrop_label = backdrop

        scaled_bg = self.bg_pixmap.scaled(
            self.central.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )
        rect = QRect(card_rect)
        if rect.right() >= scaled_bg.width():
            rect.setRight(scaled_bg.width() - 1)
        if rect.bottom() >= scaled_bg.height():
            rect.setBottom(scaled_bg.height() - 1)
        if rect.left() < 0 or rect.top() < 0 or rect.width() <= 0 or rect.height() <= 0:
            return

        patch = scaled_bg.copy(rect)
        painter = QPainter(patch)
        painter.fillRect(patch.rect(), QColor(0, 0, 0, 34))
        painter.end()

        backdrop.setGeometry(card_rect)
        backdrop.setPixmap(patch)
        backdrop.setScaledContents(True)
        backdrop.show()
        self.bg_label.lower()
        backdrop.raise_()
        card.raise_()

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
        self._fade_in_output()

    def _fade_in_output(self):
        """انیمیشن فیداین برای لیست خروجی بعد از به‌روزرسانی نتایج."""
        if not hasattr(self, "output"):
            return
        effect = self._ensure_opacity_effect(self.output, 0.4)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(600)
        anim.setStartValue(0.4)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._output_fade_anim = anim

    def _ensure_opacity_effect(self, widget, start_opacity=0.0):
        effect = widget.graphicsEffect()
        if effect is None or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        effect.setOpacity(start_opacity)
        return effect

    def animate_widgets(self, widgets, duration=180):
        group = QParallelAnimationGroup(self)
        for w in widgets:
            effect = self._ensure_opacity_effect(w, 0.0)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            group.addAnimation(anim)
        self._active_anim_group = group
        group.start()

    def animate_widgets_staggered(self, widgets, duration=280, stagger_ms=70):
        """انیمیشن ظاهر شدن پشت سر هم با تأخیر کوتاه بین هر ویجت."""
        group = QParallelAnimationGroup(self)
        for i, w in enumerate(widgets):
            effect = self._ensure_opacity_effect(w, 0.0)
            fade = QPropertyAnimation(effect, b"opacity", self)
            fade.setDuration(duration)
            fade.setStartValue(0.0)
            fade.setEndValue(1.0)
            fade.setEasingCurve(QEasingCurve.OutCubic)
            seq = QSequentialAnimationGroup(self)
            seq.addAnimation(QPauseAnimation(i * stagger_ms))
            seq.addAnimation(fade)
            group.addAnimation(seq)
        self._active_anim_group = group
        group.start()

    def animate_card_entrance(self, card, inner_widgets=None, delay_before_inner=80):
        """ورود کارت با فید این و در صورت تمایل انیمیشن پلکانی المان‌های داخلی."""
        self.main_layout.activate()
        self._update_glass_backdrop(card)
        effect = self._ensure_opacity_effect(card, 1.0)
        effect.setOpacity(1.0)
        card.show()
        if inner_widgets:
            for w in inner_widgets:
                w.show()
        self._active_anim_group = None

    def _button_hover_anim(self, button, enter):
        """تغییر سایز فوری دکمه روی hover (بدون انیمیشن)."""
        is_hovered = getattr(button, "_bb_is_hovered", False)
        if enter == is_hovered:
            return
        button._bb_is_hovered = enter

        base_h = getattr(button, "_bb_base_height", max(button.minimumHeight(), 1))
        base_w = getattr(button, "_bb_base_width", max(button.minimumWidth(), button.sizeHint().width(), 1))
        if enter:
            button.setMinimumHeight(base_h + 14)
            button.setMinimumWidth(base_w + 36)
        else:
            button.setMinimumHeight(base_h)
            button.setMinimumWidth(base_w)

    def _button_press_anim(self, button, pressed):
        base_h = getattr(button, "_bb_base_height", max(button.minimumHeight(), 1))
        base_w = getattr(button, "_bb_base_width", max(button.minimumWidth(), button.sizeHint().width(), 1))
        if pressed:
            button.setMinimumHeight(max(base_h - 4, 48))
            button.setMinimumWidth(max(base_w - 10, 120))
        else:
            if getattr(button, "_bb_is_hovered", False):
                button.setMinimumHeight(base_h + 14)
                button.setMinimumWidth(base_w + 36)
            else:
                button.setMinimumHeight(base_h)
                button.setMinimumWidth(base_w)

    def _set_input_focus_style(self, edit, focused):
        border = "2px solid rgba(52, 152, 219, 0.95)" if focused else "2px solid rgba(255,255,255,0.18)"
        edit.setStyleSheet(f"border-radius:10px; background:white; border: {border};")

    def _install_button_hover(self, button, base_height=None):
        if base_height is None:
            base_height = button.minimumHeight()
        button._bb_base_height = base_height
        button._bb_base_width = max(button.minimumWidth(), button.sizeHint().width(), 1)
        button._bb_is_hovered = False
        button.setMinimumHeight(base_height)
        button.setMinimumWidth(button._bb_base_width)
        button.installEventFilter(self)
        button.pressed.connect(lambda b=button: self._button_press_anim(b, True))
        button.released.connect(lambda b=button: self._button_press_anim(b, False))
        self._hover_buttons = getattr(self, "_hover_buttons", set())
        self._hover_buttons.add(button)

    def _freeze_card_size(self, card, buttons=None):
        """Freeze card size so button hover/press cannot resize the page card."""
        buttons = buttons or []
        saved_sizes = []
        for b in buttons:
            saved_sizes.append((b, b.minimumWidth(), b.minimumHeight()))
            base_h = getattr(b, "_bb_base_height", b.minimumHeight())
            base_w = getattr(b, "_bb_base_width", max(b.minimumWidth(), b.sizeHint().width(), 1))
            b.setMinimumHeight(base_h + 14)
            b.setMinimumWidth(base_w + 36)

        self.main_layout.activate()
        if card.layout():
            card.layout().activate()
        card.adjustSize()
        hint = card.sizeHint()

        min_w = card.minimumWidth() if card.minimumWidth() > 0 else hint.width()
        min_h = card.minimumHeight() if card.minimumHeight() > 0 else hint.height()
        max_w = card.maximumWidth() if card.maximumWidth() < 16777215 else hint.width()
        max_h = card.maximumHeight() if card.maximumHeight() < 16777215 else hint.height()

        target_w = max(min_w, hint.width())
        target_h = max(min_h, hint.height())
        target_w = min(target_w, max_w)
        target_h = min(target_h, max_h)
        card.setFixedSize(target_w, target_h)

        for b, old_w, old_h in saved_sizes:
            b.setMinimumWidth(old_w)
            b.setMinimumHeight(old_h)

    def eventFilter(self, obj, event):
        if obj in self._glass_cards:
            if event.type() in (QEvent.Hide, QEvent.Close):
                self._detach_glass_backdrop(obj)
                return False
            if event.type() in (
                QEvent.Move,
                QEvent.Resize,
                QEvent.Show,
                QEvent.LayoutRequest,
            ):
                self._update_glass_backdrop(obj)
                return False
        if getattr(self, "_hover_buttons", None) and obj in self._hover_buttons:
            if event.type() == QEvent.Enter:
                self._button_hover_anim(obj, True)
                return False
            if event.type() == QEvent.Leave:
                self._button_hover_anim(obj, False)
                return False
        if obj in self.inputs:
            if event.type() == QEvent.FocusIn:
                self._set_input_focus_style(obj, True)
                return False
            if event.type() == QEvent.FocusOut:
                self._set_input_focus_style(obj, False)
                return False
            if event.type() == QEvent.KeyPress:
                key = event.key()
                if key in (Qt.Key_Return, Qt.Key_Enter):
                    self.handle_enter_key(obj)
                    return True
                is_rtl = self.layoutDirection() == Qt.RightToLeft
                if key == Qt.Key_Space:
                    delta = -1 if is_rtl else 1
                    self.move_focus_delta(obj, delta)
                    return True
                if key == Qt.Key_Right:
                    delta = -1 if is_rtl else 1
                    self.move_focus_delta(obj, delta)
                    return True
                if key == Qt.Key_Left:
                    delta = 1 if is_rtl else -1
                    self.move_focus_delta(obj, delta)
                    return True
        return super().eventFilter(obj, event)

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
        self._apply_glass_card_effect(card)

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
        v.addStretch(1)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

        for btn in (fa_btn, en_btn):
            self._install_button_hover(btn, 80)
        self._freeze_card_size(card, [fa_btn, en_btn])
        self.animate_card_entrance(card, [title, fa_btn, en_btn], 60)

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
        self._apply_glass_card_effect(card)

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

        v.addStretch(1)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

        for btn in menu_buttons:
            self._install_button_hover(btn, 80)
        self._freeze_card_size(card, menu_buttons)
        self.animate_card_entrance(card, [title] + menu_buttons, 80)

    def show_search_screen(self):
        self.clear_layout()
        self.current_screen = "search"
        card = QFrame()
        card.setObjectName("CardFrame")
        card.setMinimumWidth(860)
        card.setMinimumHeight(620)
        card.setMaximumWidth(1280)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._apply_glass_card_effect(card)

        v = QVBoxLayout(card)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(18)

        fields_layout = QHBoxLayout()
        fields_layout.setDirection(QBoxLayout.LeftToRight)
        fields_layout.setSpacing(16)
        self.inputs = []
        self.input_map = {}
        search_anim_widgets = []

        if self.search_type == "bearing":
            configs = [("d", self.t("inner")), ("D", self.t("outer")), ("B", self.t("width"))]
            if self.lang == "fa":
                configs = list(reversed(configs))
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
            self._set_input_focus_style(edit, False)
            edit.setMinimumWidth(180)
            edit.setPlaceholderText("مثال: 25.0 mm" if self.lang == "fa" else "e.g. 25.0 mm")
            edit.installEventFilter(self)

            box.addWidget(lbl)
            box.addWidget(edit)
            fields_layout.addLayout(box)
            self.inputs.append(edit)
            self.input_map[eng] = edit
            search_anim_widgets.append(lbl)

        v.addLayout(fields_layout)

        if self.inputs:
            self.inputs[0].setFocus()
            for inp in self.inputs:
                inp.returnPressed.connect(lambda inp=inp: self.handle_enter_key(inp))

        self.output = QListWidget()
        self.output.setMinimumHeight(250)
        output_font = QFont("B Nazanin", 12) if self.lang == "fa" else QFont("Consolas", 12)
        self.output.setFont(output_font)
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
        search_anim_widgets.append(self.output)

        btn_h = QHBoxLayout()
        search_buttons = []
        for text, style, func in [
            (self.t("check"), PRIMARY_BUTTON_STYLE, self.check_result),
            (self.t("clear"), SECONDARY_BUTTON_STYLE, self.clear_inputs),
            (self.t("back"), SECONDARY_BUTTON_STYLE, self.show_start_screen),
        ]:
            b = QPushButton(text)
            b.setMinimumHeight(70)
            b.setFont(QFont("Arial", 16, QFont.Bold))
            b.setStyleSheet(style)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(func)
            btn_h.addWidget(b)
            search_buttons.append(b)
            search_anim_widgets.append(b)
            if func == self.check_result:
                self.check_btn = b

        self.check_btn.setDefault(True)
        self.check_btn.setAutoDefault(True)

        v.addLayout(btn_h)
        v.addStretch(1)
        self.main_layout.addStretch()
        self.main_layout.addWidget(card, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

        for btn in search_buttons:
            self._install_button_hover(btn, 70)
        self._freeze_card_size(card, search_buttons)
        self.animate_card_entrance(card, search_anim_widgets, 100)

    def start_search(self, mode):
        self.search_type = mode
        self.show_search_screen()

    def on_return_pressed(self, index):
        if index < len(self.inputs) - 1:
            self.inputs[index + 1].setFocus()
        else:
            self.check_result()

    def handle_enter_key(self, current):
        if current not in self.inputs:
            self.check_result()
            return
        index = self.inputs.index(current)
        if index < len(self.inputs) - 1:
            self.inputs[index + 1].setFocus()
        else:
            self.check_result()

    def move_focus_delta(self, current, delta):
        if current not in self.inputs or len(self.inputs) < 2:
            return
        index = self.inputs.index(current)
        target_index = (index + delta) % len(self.inputs)
        self.inputs[target_index].setFocus()

    def move_focus_next(self, current):
        self.move_focus_delta(current, 1)

    def move_focus_prev(self, current):
        self.move_focus_delta(current, -1)

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

        txt = unicodedata.normalize("NFKC", txt)
        txt = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]", "", txt)

        trans = str.maketrans(
            PERSIAN_DIGITS + ARABIC_INDIC_DIGITS + ARABIC_DECIMAL_SEP + ARABIC_THOUSANDS_SEP + ARABIC_COMMA,
            "0123456789" * 2 + ".,,",
        )
        txt = txt.translate(trans)
        txt = txt.replace(",", ".").replace("/", ".").replace("\\", ".")
        txt = re.sub(r"\s+", "", txt)
        txt = re.sub(r"[^0-9.+-]", "", txt)

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
            return (
                self._get_by_keys(
                    item,
                    ["purpose_en", "description_en", "special_features_en"],
                    ["purposeen", "descriptionen", "specialfeaturesen"],
                )
                or ""
            )

        if self.lang == "fa":
            return (
                self._get_by_keys(
                    item,
                    ["purpose", "description", "special_features"],
                    ["purpose", "description", "specialfeatures"],
                )
                or ""
            )

        return ""

    def _localize_output_text(self, text):
        if self.lang != "fa":
            return str(text)

        return str(text).translate(str.maketrans("0123456789", PERSIAN_DIGITS))

    def _get_calculator_paths(self):
        cpp_dir = resource_path("Cpp")
        source_path = os.path.join(cpp_dir, "calculator.cpp")
        binary_name = "calculator.exe" if os.name == "nt" else "calculator"
        binary_path = os.path.join(cpp_dir, binary_name)
        return source_path, binary_path

    def _ensure_calculator_binary(self):
        source_path, binary_path = self._get_calculator_paths()
        if os.path.exists(binary_path):
            return binary_path
        if not os.path.exists(source_path):
            return None
        try:
            compile_cmd = ["g++", "-std=c++17", source_path, "-O2", "-o", binary_path]
            subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        return binary_path if os.path.exists(binary_path) else None

    def _query_cpp_calculator(self, db_path, user_d, user_D, user_B):
        binary_path = self._ensure_calculator_binary()
        if not binary_path:
            return None, "Calculator binary not available"

        args = [binary_path, db_path, self.search_type, str(user_d)]
        if self.search_type == "bearing":
            args.extend([str(user_D), str(user_B)])

        try:
            result = subprocess.run(args, check=False, capture_output=True, text=True)
        except OSError as exc:
            return None, str(exc)

        if result.returncode != 0:
            return None, result.stderr.strip() or result.stdout.strip() or "Calculator failed"

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None, "Invalid calculator response"

        if payload.get("error"):
            return None, payload["error"]

        return payload.get("results", []), None

    def _search_in_python(self, raw_data, user_d, user_D, user_B):
        if isinstance(raw_data, list):
            items = raw_data
        elif isinstance(raw_data, dict):
            key = "bearings" if self.search_type == "bearing" else "housings"
            items = raw_data.get(key, [])
            if not items:
                items = next((v for v in raw_data.values() if isinstance(v, list)), [])
        else:
            items = []

        def read_dimension(item, exact_keys, normalized_keys):
            return self.safe_float(self._get_by_keys(item, exact_keys, normalized_keys))

        bearing_dimensions = {
            "d": (["d"], ["inner_diameter", "innerdiameter", "inner", "id", "di"]),
            "D": (["D"], ["outer_diameter", "outerdiameter", "outer", "od"]),
            "B": (["B", "b"], ["width", "w"]),
        }
        housing_dimensions = (
            ["d", "shaft_diameter", "bearing_bore"],
            ["inner_diameter", "innerdiameter", "shaft_diameter", "shaftdiameter", "bearing_bore", "bearingbore"],
        )

        found_models = []
        for item in items:
            if not isinstance(item, dict):
                continue

            if self.search_type == "bearing":
                d_val = read_dimension(item, *bearing_dimensions["d"])
                D_val = read_dimension(item, *bearing_dimensions["D"])
                B_val = read_dimension(item, *bearing_dimensions["B"])

                if d_val is None or D_val is None or B_val is None:
                    continue

                is_match = (
                    abs(d_val - user_d) < 0.2
                    and abs(D_val - user_D) < 0.2
                    and abs(B_val - user_B) < 1.0
                )
            else:
                d_val = read_dimension(item, *housing_dimensions)
                if d_val is None:
                    continue
                is_match = abs(d_val - user_d) < 0.2

            if is_match:
                model = self._get_by_keys(item, ["model", "Model"], ["model"]) or "N/A"
                desc = self._get_localized_desc(item)
                found_models.append(
                    (self._localize_output_text(model), self._localize_output_text(desc))
                )

        return found_models

    def _start_search_pulse(self):
        """برای دکمه‌ها انیمیشن غیرفعال است."""
        return

    def _stop_search_pulse(self):
        """برای دکمه‌ها انیمیشن غیرفعال است."""
        return

    def check_result(self):
        db_path = resource_path("DataBase/DataBase.json")
        self.check_btn.setEnabled(False)
        self.check_btn.setText(self.t("searching"))
        self._start_search_pulse()
        QApplication.processEvents()

        try:
            if not os.path.exists(db_path):
                self.set_output_message(self.t("db_missing"), "#ff8a80")
                return

            with open(db_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

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

            cpp_results, cpp_error = self._query_cpp_calculator(db_path, user_d, user_D, user_B)
            if cpp_results:
                found_models = [
                    (self._localize_output_text(item.get("model", "N/A")),
                     self._localize_output_text(item.get("description", "")))
                    for item in cpp_results
                ]
            else:
                found_models = self._search_in_python(raw_data, user_d, user_D, user_B)

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
                self._fade_in_output()
            else:
                self.set_output_message(self.t("not_found"), "#ff8a80")

        except Exception as e:
            self.set_output_message(f"{self.t('critical_error')}: {e}", "#ff8a80")
        finally:
            self._stop_search_pulse()
            self.check_btn.setEnabled(True)
            self.check_btn.setText(self.t("check"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
