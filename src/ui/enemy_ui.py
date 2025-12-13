from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter

class EnemyUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_label = QLabel("敌人")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight:bold; font-size:12px; color: white;")

        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #333;
                height: 8px;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
                width: 6px;
            }
        """)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(50, 50)

        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.hp_bar)

    def update_enemy(self, enemy_name, current_hp, max_hp):
        self.name_label.setText(enemy_name)
        self.hp_bar.setValue(int(current_hp / max_hp * 100))
        self.hp_bar.setFormat(f"{current_hp}/{max_hp}")

        icons = {
            "goblin": "🧌",
            "skeleton": "💀",
            "spider": "🕷️",
            "orc": "👹"
        }
        icon = icons.get(enemy_name, "👾")
        pixmap = QPixmap(50, 50)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setFont(QFont("Arial", 25))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon)
        painter.end()
        self.image_label.setPixmap(pixmap)