from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class DeathScreen(QWidget):
    """死亡界面"""
    # 正确定义信号
    restart_game_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置死亡界面UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 大字"菜"
        self.death_label = QLabel("菜")
        self.death_label.setFont(QFont("Microsoft YaHei", 120, QFont.Weight.Bold))
        self.death_label.setStyleSheet("color: #ff5555;")
        self.death_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.death_label)
        
        # 重新开始按钮
        restart_btn = QPushButton("↺ 重新开始")
        restart_btn.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        restart_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4a6fa5, stop:1 #3a5a80);
                color: white;
                border: 2px solid #5a7fb5;
                border-radius: 15px;
                padding: 15px 30px;
                min-width: 250px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #5a7fb5, stop:1 #4a6fa5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #3a5a80, stop:1 #2a4a70);
            }
        """)
        restart_btn.clicked.connect(self.restart_game)
        main_layout.addWidget(restart_btn)
        
        # 设置背景
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.85);")
    
    def restart_game(self):
        """发射重新开始游戏信号"""
        self.restart_game_signal.emit()