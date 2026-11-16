import sys
import os
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                             QGraphicsColorizeEffect, QStackedWidget, QProgressBar,
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt, QTimer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset(path):
    return os.path.join(BASE_DIR, path)


class GameDB:
    def __init__(self):
        self.conn = sqlite3.connect(asset("dream_finder.db"))
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS levels 
                         (id INTEGER PRIMARY KEY, status TEXT)""")
        self.conn.commit()

    def save_level(self, level_num):
        self.cur.execute("INSERT OR REPLACE INTO levels (id, status) VALUES (?, ?)", (level_num, "done"))
        self.conn.commit()


class InvSlot(QLabel):
    def __init__(self, name, img_path, parent=None):
        super().__init__(parent)
        self.name = name
        self.setFixedSize(90, 90)
        self.setStyleSheet("background-color: #2a2a2a; border: 1px solid #444; border-radius: 5px;")

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)

        pix = QPixmap(asset(img_path)).scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)

        self.img_lbl = QLabel()
        self.img_lbl.setPixmap(pix)
        self.img_lbl.setStyleSheet("background: transparent; border: none;")

        effect = QGraphicsColorizeEffect()
        effect.setColor(QColor(0, 0, 0))
        effect.setStrength(1.0)
        self.img_lbl.setGraphicsEffect(effect)

        lay.addWidget(self.img_lbl)

    def found(self):
        self.img_lbl.setGraphicsEffect(None)
        self.setStyleSheet("background-color: #1a1a1a; border: 2px solid #4af626; border-radius: 5px;")


class ClickItem(QLabel):
    def __init__(self, name, img_path, x, y, w, h, parent=None):
        super().__init__(parent)
        self.name = name
        self.clicked = False
        self.setGeometry(x, y, w, h)
        self.setStyleSheet("background: transparent; border: none;")
        self.setPixmap(QPixmap(asset(img_path)).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation))
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class BaseLevel(QWidget):
    def __init__(self, main_ctrl, bg_img, items, lvl_num):
        super().__init__()
        self.ctrl = main_ctrl
        self.lvl_num = lvl_num
        self.items = items
        self.found_count = 0
        self.setup_ui(bg_img)

    def setup_ui(self, bg_img):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        left = QFrame()
        left.setFixedWidth(280)
        left.setStyleSheet("background-color: #121212; border-right: 2px solid #333;")

        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(15, 20, 15, 20)

        title = QLabel("ИСКАТЬ:")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #e8d5b5;")
        left_lay.addWidget(title)
        left_lay.addSpacing(15)

        self.inv_grid = QGridLayout()
        self.inv_grid.setSpacing(10)
        left_lay.addLayout(self.inv_grid)
        left_lay.addStretch()

        self.scene = QWidget()
        self.scene.setStyleSheet("background-color: #000;")

        self.scene_bg = QLabel(self.scene)
        self.scene_bg.setGeometry(0, 0, 1000, 720)
        self.scene_bg.setPixmap(QPixmap(asset(bg_img)))
        self.scene_bg.setScaledContents(True)

        self.slots = {}
        r, c = 0, 0
        for item in self.items:
            slot = InvSlot(item["name"], item["file"], left)
            self.inv_grid.addWidget(slot, r, c)
            self.slots[item["name"]] = slot

            obj = ClickItem(item["name"], item["file"], item["x"], item["y"], item["w"], item["h"], self.scene)
            obj.mousePressEvent = lambda e, o=obj: self.on_click(o)

            c += 1
            if c > 1:
                c = 0
                r += 1

        layout.addWidget(left)
        layout.addWidget(self.scene, 1)

    def on_click(self, obj):
        if not obj.clicked:
            obj.clicked = True
            obj.hide()
            if obj.name in self.slots:
                self.slots[obj.name].found()
            self.found_count += 1

            if self.found_count == len(self.items):
                self.level_done()

    def level_done(self):
        self.ctrl.finish_level(self.lvl_num)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.ctrl.show_pause()
        else:
            super().keyPressEvent(event)


class Lvl1(BaseLevel):
    def __init__(self, ctrl):
        items = [
            {"name": "key", "file": "assets/key.png", "x": 50, "y": 400, "w": 75, "h": 75},
            {"name": "chasi", "file": "assets/chasi.png", "x": 900, "y": 420, "w": 85, "h": 85},
            {"name": "mishka", "file": "assets/mishka.png", "x": 400, "y": 420, "w": 100, "h": 100},
            {"name": "matryoshka", "file": "assets/matryoshka.png", "x": 600, "y": 400, "w": 120, "h": 120},
            {"name": "ball", "file": "assets/ball.png", "x": 100, "y": 550, "w": 250, "h": 250},
        ]
        super().__init__(ctrl, "assets/level1_bg.png", items, 1)


class Lvl2(BaseLevel):
    def __init__(self, ctrl):
        items = [
            {"name": "karandash", "file": "assets/karandash.png", "x": 300, "y": 500, "w": 80, "h": 40},
            {"name": "kniga", "file": "assets/kniga.png", "x": 450, "y": 520, "w": 60, "h": 70},
            {"name": "ruchka", "file": "assets/ruchka.png", "x": 600, "y": 500, "w": 40, "h": 40},
            {"name": "ochki", "file": "assets/ochki.png", "x": 800, "y": 460, "w": 70, "h": 40},
            {"name": "globus", "file": "assets/globus.png", "x": 150, "y": 500, "w": 80, "h": 80},
        ]
        super().__init__(ctrl, "assets/level2_bg.png", items, 2)


class Lvl3(BaseLevel):
    def __init__(self, ctrl):
        items = [
            {"name": "jeton", "file": "assets/jeton.png", "x": 750, "y": 650, "w": 50, "h": 50},
            {"name": "flask", "file": "assets/flask.png", "x": 250, "y": 580, "w": 60, "h": 70},
            {"name": "grenade", "file": "assets/grenade.png", "x": 900, "y": 450, "w": 45, "h": 45},
            {"name": "faceless", "file": "assets/faceless.png", "x": 350, "y": 390, "w": 80, "h": 120},
        ]
        super().__init__(ctrl, "assets/level_3_bg_norm.png", items, 3)

    def on_click(self, obj):
        super().on_click(obj)
        if self.found_count == 2:
            self.scene_bg.setPixmap(QPixmap(asset('assets/level_3_bg_dark.png')))


class Lvl4(BaseLevel):
    def __init__(self, ctrl):
        items = [
            {"name": "medcard", "file": "assets/medcarta.png", "x": 300, "y": 500, "w": 80, "h": 80},
            {"name": "pills", "file": "assets/tabletki.png", "x": 650, "y": 550, "w": 60, "h": 60},
            {"name": "syringe", "file": "assets/shprich.png", "x": 400, "y": 680, "w": 70, "h": 40},
        ]
        super().__init__(ctrl, "assets/level4_bg.png", items, 4)


class Menu(QWidget):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setStyleSheet("background: #000;")

        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, 1280, 720)
        self.bg.setPixmap(QPixmap(asset('assets/menu.png')))
        self.bg.setScaledContents(True)

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay.addStretch(1)

        title = QLabel("DREAM FINDER")
        title.setFont(QFont("Times New Roman", 50, QFont.Weight.Bold))
        title.setStyleSheet("color: #e8d5b5; background: transparent; letter-spacing: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)
        lay.addSpacing(30)

        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        style = "QPushButton { background: rgba(20,20,20,200); color: #ccc; border: 1px solid #555; padding: 10px 50px; font-size: 18px; min-width: 200px; } QPushButton:hover { border-color: #e8d5b5; color: white; }"

        self.b1 = QPushButton("НАЧАТЬ")
        self.b2 = QPushButton("ДОСЬЕ")
        self.b3 = QPushButton("ВЫХОД")

        for b in [self.b1, self.b2, self.b3]:
            b.setStyleSheet(style)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_layout.addWidget(b)

        lay.addLayout(btn_layout)
        lay.addStretch(1)

        self.b3.clicked.connect(self.confirm_exit)
        self.b1.clicked.connect(ctrl.show_story)
        self.b2.clicked.connect(ctrl.show_dossier)

    def confirm_exit(self):
        msg = QMessageBox()
        msg.setWindowTitle("Выход")
        msg.setText("Вы уверены, что хотите прервать сеанс и выйти?")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        msg.setStyleSheet("""
            QMessageBox { background-color: #1a1a1a; }
            QLabel { color: #d1d1d1; }
            QPushButton { background-color: #333; color: white; padding: 5px 15px; border: 1px solid #555; }
        """)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.ctrl.close()


class Story(QWidget):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setStyleSheet("background-color: #000000;")

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(20)

        self.txt = QLabel("")
        self.txt.setStyleSheet("color: #4af626; font-family: 'Courier New'; font-size: 18px; background: transparent;")
        self.txt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.txt.setWordWrap(True)
        self.txt.setFixedWidth(900)
        lay.addWidget(self.txt)

        self.bottom_stack = QStackedWidget()
        self.bottom_stack.setFixedSize(400, 45)
        self.bottom_stack.setStyleSheet("background: transparent;")

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4af626;
                border-radius: 5px;
                text-align: center;
                color: #4af626;
                background: #000;
                font-family: 'Courier New';
                font-size: 16px;
            }
            QProgressBar::chunk {
                background-color: #4af626;
            }
        """)
        self.progress.setValue(0)
        self.bottom_stack.addWidget(self.progress)

        self.btn_start = QPushButton("ЗАПУСТИТЬ СЕАНС")
        self.btn_start.setStyleSheet(
            "QPushButton { background: transparent; color: #4af626; border: 1px solid #4af626; border-radius: 5px; font-size: 16px; font-family: 'Courier New'; } "
            "QPushButton:hover { background: #4af626; color: black; }")
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.ctrl.start_game)
        self.bottom_stack.addWidget(self.btn_start)

        self.btn_next = QPushButton("ПРОДОЛЖИТЬ")
        self.btn_next.setStyleSheet(
            "QPushButton { background: transparent; color: #4af626; border: 1px solid #4af626; padding: 10px 30px; font-size: 16px; } "
            "QPushButton:hover { background: #4af626; color: black; }")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.hide()
        self.btn_next.clicked.connect(self.start_second_part)

        lay.addWidget(self.btn_next, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.bottom_stack, alignment=Qt.AlignmentFlag.AlignCenter)

        self.bottom_stack.hide()

        self.text_timer = QTimer(self)
        self.text_timer.timeout.connect(self.update_text)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)

        self.part1 = ("На дворе 2152 год. После Великой войны большая часть суши непригодна для проживания; \n"
                      "основное население сосредоточено в Центральной и Западной Европе, где спустя 7 лет после войны жизнь восстанавливается. \n"
                      "С виду всё выглядит благополучно, но отголоски войны преследуют многих.")

        self.part2 = (
            "Вы доктор Келл Моррисон работаете в \"Психоневрологическом Исследовательском Центре №6\" в городе Моренвальд, "
            "пять лет назад учёные изобрели прибор способный просматривать всю память человека начиная с детства.\n"
            "Вам предоставили опытный образец одной из последний версий этого устройства.")

        self.current_char = 0
        self.current_text = ""

    def start_sequence(self):
        self.current_char = 0
        self.current_text = self.part1
        self.txt.setText("")
        self.bottom_stack.hide()
        self.btn_next.hide()
        self.text_timer.start(25)

    def update_text(self):
        if self.current_char < len(self.current_text):
            self.current_char += 1
            self.txt.setText(self.current_text[:self.current_char])
        else:
            self.text_timer.stop()
            if self.current_text == self.part1:
                self.btn_next.show()

    def start_second_part(self):
        self.btn_next.hide()
        self.bottom_stack.show()
        self.bottom_stack.setCurrentWidget(self.progress)
        self.progress.setValue(0)
        self.current_char = 0
        self.current_text = self.part2
        self.txt.setText("")
        self.text_timer.start(25)
        self.progress_timer.start(100)

    def update_progress(self):
        val = self.progress.value() + 1
        self.progress.setValue(val)
        if val >= 100:
            self.progress_timer.stop()
            self.text_timer.stop()
            self.bottom_stack.setCurrentWidget(self.btn_start)


class Dossier(QWidget):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setStyleSheet("background-color: #121212;")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stack_container = QWidget()
        stack_container.setFixedSize(450, 600)

        clipboard_img = QLabel(stack_container)
        pixmap = QPixmap(asset("assets/planshet.png"))

        clipboard_img.setPixmap(
            pixmap.scaled(1344, 700, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        clipboard_img.setStyleSheet("background: transparent; border: none;")
        clipboard_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clipboard_img.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        clipboard_img.setGeometry(0, 0, 450, 600)

        paper = QFrame(stack_container)
        paper.setFixedSize(320, 450)

        paper.setStyleSheet("""
            QFrame {
                background-color: #f4ecd8;
                background-image: url(assets/paper_bg.jpg); 
                border: 1px solid #c0b5a0;
            }
        """)

        paper.move(65, 100)
        paper.raise_()

        paper_layout = QVBoxLayout(paper)
        paper_layout.setContentsMargins(15, 15, 15, 15)
        paper_layout.setSpacing(5)

        title = QLabel("ПСИХОНЕВРОЛОГИЧЕСКИЙ\nИССЛЕДОВАТЕЛЬСКИЙ ЦЕНТР №6\nДОСЬЕ ОБРАЗЦА")
        title.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title.setStyleSheet("color: #2a1e12; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #2a1e12; background-color: #2a1e12; max-height: 1px;")

        grid = QGridLayout()
        grid.setSpacing(4)

        text_style = "color: #2a1e12; background: transparent; font-size: 10px; font-family: 'Courier New';"
        secret_style = "color: #d1c7b0; background-color: #2a1e12; font-size: 10px; font-family: 'Courier New';"

        def add_field(row, label_text, value_text, is_secret=False):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(text_style)
            lbl.setFont(QFont("Courier New", 9, QFont.Weight.Bold))

            val = QLabel(value_text)
            val.setStyleSheet(secret_style if is_secret else text_style)
            if is_secret:
                val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            grid.addWidget(lbl, row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(val, row, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        add_field(0, "Обозначение:", "Образец-2246А")
        add_field(1, "Имя:", "[ЗАСЕКРЕЧЕНО]", True)
        add_field(2, "Фамилия:", "[ЗАСЕКРЕЧЕНО]", True)
        add_field(3, "Возраст:", "34 года")
        add_field(4, "Дата пост.:", "19.10.2152")
        add_field(5, "Статус:", "Ветеран")
        add_field(6, "Диагноз:", "Амнезия")
        add_field(7, "Служба:", "[ЗАСЕКРЕЧЕНО]", True)

        btn_back = QPushButton("ЗАКРЫТЬ")
        btn_back.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2a1e12;
                border: 1px solid #2a1e12;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #2a1e12;
                color: #f4ecd8;
            }
        """)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(ctrl.show_menu)

        paper_layout.addWidget(title)
        paper_layout.addWidget(line)
        paper_layout.addSpacing(5)
        paper_layout.addLayout(grid)
        paper_layout.addStretch()
        paper_layout.addWidget(btn_back)

        main_layout.addWidget(stack_container)


class Pause(QWidget):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        title = QLabel("ПАУЗА")
        title.setFont(QFont("Times New Roman", 48, QFont.Weight.Bold))
        title.setStyleSheet("color: #e8d5b5; letter-spacing: 10px; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addSpacing(40)

        btn_style = """
            QPushButton {
                background-color: rgba(20, 25, 30, 200);
                color: #d1d1d1;
                border: 1px solid #6b5a43;
                border-radius: 5px;
                padding: 15px;
                font-size: 18px;
                font-family: Arial;
                letter-spacing: 2px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: rgba(50, 60, 70, 240);
                border: 1px solid #e8d5b5;
                color: #ffffff;
            }
        """

        self.btn_resume = QPushButton("ПРОДОЛЖИТЬ")
        self.btn_exit = QPushButton("ВЫЙТИ В МЕНЮ")

        for btn in [self.btn_resume, self.btn_exit]:
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            main_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_resume.clicked.connect(ctrl.hide_pause)
        self.btn_exit.clicked.connect(ctrl.show_menu)


class Notes(QWidget):
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.setStyleSheet("background-color: #121212;")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.paper = QFrame()
        self.paper.setFixedSize(850, 650)
        self.paper.setStyleSheet("""
            QFrame {
                background-color: #f4ecd8;
                background-image: url(assets/paper.jpg); 
                border: 1px solid #c0b5a0;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(10)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.paper.setGraphicsEffect(shadow)

        paper_layout = QVBoxLayout(self.paper)
        paper_layout.setContentsMargins(60, 60, 60, 60)
        paper_layout.setSpacing(20)

        title = QLabel("СЕАНС. ЛИЧНЫЕ ЗАМЕТКИ.\n[ДОСТУП: ЛИЧНЫЙ]")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #555; background: transparent; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #888; background-color: #888; max-height: 1px; border: none;")

        self.txt = QLabel("Текст...")
        self.txt.setFont(QFont("Comic Sans MS", 20))
        self.txt.setStyleSheet("color: #1a237e; background: transparent; border: none;")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.b = QPushButton("ДАЛЬШЕ")
        self.b.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.b.setStyleSheet("""
            QPushButton { 
                background: transparent; 
                color: #333; 
                border: 2px dashed #333; 
                padding: 10px 30px; 
            } 
            QPushButton:hover { 
                background: #333; 
                color: white; 
            }
        """)
        self.b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b.clicked.connect(ctrl.next_level)

        paper_layout.addWidget(title)
        paper_layout.addWidget(line)
        paper_layout.addSpacing(10)
        paper_layout.addWidget(self.txt)
        paper_layout.addStretch()
        paper_layout.addWidget(self.b, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.paper)

    def load_text(self, lvl):
        try:
            with open(asset("note.txt"), "r", encoding="utf-8") as f:
                parts = f.read().split("---")
                if lvl <= len(parts):
                    self.txt.setText(parts[lvl - 1].strip())
        except Exception as e:
            self.txt.setText(f"ошибка чтения note.txt: {e}")


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dream Finder")
        self.setFixedSize(1280, 720)

        self.db = GameDB()
        self.curr_lvl = 1

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = Menu(self)
        self.dossier = Dossier(self)
        self.story = Story(self)
        self.notes = Notes(self)
        self.pause = Pause(self)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.dossier)
        self.stack.addWidget(self.story)
        self.stack.addWidget(self.notes)
        self.stack.addWidget(self.pause)

    def show_menu(self):
        self.stack.setCurrentWidget(self.menu)

    def show_dossier(self):
        self.stack.setCurrentWidget(self.dossier)

    def show_story(self):
        self.stack.setCurrentWidget(self.story)
        self.story.start_sequence()

    def start_game(self):
        self.curr_lvl = 1
        self.load_level(1)

    def load_level(self, num):
        if num == 1:
            lvl = Lvl1(self)
        elif num == 2:
            lvl = Lvl2(self)
        elif num == 3:
            lvl = Lvl3(self)
        elif num == 4:
            lvl = Lvl4(self)

        self.stack.addWidget(lvl)
        self.stack.setCurrentWidget(lvl)

    def finish_level(self, num):
        self.db.save_level(num)
        self.curr_lvl = num
        self.notes.load_text(num)
        self.stack.setCurrentWidget(self.notes)

    def next_level(self):
        if self.curr_lvl < 4:
            self.load_level(self.curr_lvl + 1)
        else:
            self.show_menu()

    def show_pause(self):
        self.stack.setCurrentWidget(self.pause)

    def hide_pause(self):
        if self.curr_lvl == 1:
            self.load_level(1)
        elif self.curr_lvl == 2:
            self.load_level(2)
        elif self.curr_lvl == 3:
            self.load_level(3)
        elif self.curr_lvl == 4:
            self.load_level(4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show_menu()
    window.show()
    sys.exit(app.exec())