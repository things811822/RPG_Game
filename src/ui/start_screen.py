from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class StartScreen(QWidget):
    """游戏开始界面"""
    # 正确定义信号
    start_game_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置开始界面UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 游戏标题
        title_label = QLabel("⚔️ PyQt6 RPG 冒险 ⚔️")
        title_label.setFont(QFont("Microsoft YaHei", 48, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffd700;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 游戏说明
        desc_frame = QFrame()
        desc_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px; border: 2px solid #444;")
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        desc_layout.setSpacing(10)
        
        desc_label = QLabel("探索迷宫，击败怪物，获取经验升级！\n"
                           "每10关将面对强大的Boss！\n"
                           "收集道具，学习技能，成为最强冒险者！")
        desc_label.setFont(QFont("Microsoft YaHei", 16))
        desc_label.setStyleSheet("color: #ccc; line-height: 1.5;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        
        main_layout.addWidget(desc_frame)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 开始游戏按钮
        start_btn = QPushButton("🎮 开始游戏")
        start_btn.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #4a6fa5, stop:1 #3a5a80);
                color: white;
                border: 2px solid #5a7fb5;
                border-radius: 15px;
                padding: 15px 30px;
                min-width: 200px;
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
        start_btn.clicked.connect(self.start_game)
        btn_layout.addWidget(start_btn)
        
        # 退出游戏按钮
        quit_btn = QPushButton("❌ 退出游戏")
        quit_btn.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        quit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #a03030, stop:1 #802020);
                color: white;
                border: 2px solid #c04040;
                border-radius: 15px;
                padding: 15px 30px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #c04040, stop:1 #a03030);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #802020, stop:1 #601010);
            }
        """)
        quit_btn.clicked.connect(self.quit_game)
        btn_layout.addWidget(quit_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 游戏信息
        info_label = QLabel("使用 WASD 移动，IJKL 控制视角\n"
                           "E 拾取物品，I 打开背包\n"
                           "Esc 退出游戏")
        info_label.setFont(QFont("Microsoft YaHei", 12))
        info_label.setStyleSheet("color: #aaa;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        # 设置背景
        self.setStyleSheet("background-color: #1a1a1a;")
    
    def start_game(self):
        """发射开始游戏信号"""
        self.start_game_signal.emit()
    
    def quit_game(self):
        """退出游戏"""
        import sys
        sys.exit()