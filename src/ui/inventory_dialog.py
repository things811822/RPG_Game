from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class InventoryDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择道具")
        self.setFixedSize(300, 400)
        self.selected_item = None
        self.items = items
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("使用道具")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 道具列表
        self.item_list = QListWidget()
        for item in items:
            self.item_list.addItem(f"{item.name} - {item.desc}")
        self.item_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.item_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.use_btn = QPushButton("使用")
        self.use_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.use_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def accept(self):
        """确认选择"""
        current_row = self.item_list.currentRow()
        if current_row >= 0 and current_row < len(self.items):
            self.selected_item = self.items[current_row]
        super().accept()