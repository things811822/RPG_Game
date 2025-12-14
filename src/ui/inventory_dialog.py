from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class InventoryDialog(QDialog):
    def __init__(self, items, player, in_battle=False, game=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("背包" if not in_battle else "战斗道具")
        self.setFixedSize(400, 300)
        self.selected_item = None
        self.items = items
        self.player = player
        self.in_battle = in_battle
        self.game = game
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("背包" if not in_battle else "战斗道具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 道具网格
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        
        # 添加道具
        for i, item in enumerate(items):
            group = QGroupBox()
            group.setStyleSheet("QGroupBox { border: 1px solid #555; border-radius: 5px; margin: 5px; }")
            group_layout = QVBoxLayout(group)
            
            # 道具名称
            name_label = QLabel(f"<b>{item.name}</b>")
            name_label.setFont(QFont("Arial", 10))
            group_layout.addWidget(name_label)
            
            # 道具描述
            desc_label = QLabel(item.desc)
            desc_label.setFont(QFont("Arial", 9))
            desc_label.setWordWrap(True)
            group_layout.addWidget(desc_label)
            
            # 使用按钮
            use_btn = QPushButton("使用")
            use_btn.setFixedHeight(25)
            use_btn.clicked.connect(lambda _, it=item: self.use_item(it))
            group_layout.addWidget(use_btn)
            
            # 添加到网格
            row = i // 2
            col = i % 2
            self.grid_layout.addWidget(group, row, col)
        
        # 添加网格布局到主布局
        layout.addLayout(self.grid_layout)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(30)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def use_item(self, item):
        """直接使用道具"""
        self.selected_item = item
        self.accept()