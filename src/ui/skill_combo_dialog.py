from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class SkillComboDialog(QDialog):
    def __init__(self, skills, player, game=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("技能组合调配")
        self.setFixedSize(500, 400)
        self.skills = skills
        self.player = player
        self.game = game
        self.selected_combo = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("技能组合调配")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 说明
        desc_label = QLabel("选择2-3个技能创建组合，顺序很重要！")
        desc_label.setStyleSheet("color: #aaa;")
        layout.addWidget(desc_label)
        
        # 技能列表
        self.skill_list = QListWidget()
        self.skill_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for skill in skills:
            item = QListWidgetItem(f"{skill.name} (MP: {skill.mp_cost})")
            item.setData(Qt.ItemDataRole.UserRole, skill)
            self.skill_list.addItem(item)
        layout.addWidget(self.skill_list)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存组合")
        self.save_btn.clicked.connect(self.save_combo)
        btn_layout.addWidget(self.save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def save_combo(self):
        """保存技能组合"""
        selected_items = self.skill_list.selectedItems()
        
        if len(selected_items) < 2:
            QMessageBox.warning(self, "错误", "至少需要选择2个技能！")
            return
        
        if len(selected_items) > 3:
            QMessageBox.warning(self, "错误", "最多只能选择3个技能！")
            return
        
        # 检查MP是否足够
        total_mp = sum(item.data(Qt.ItemDataRole.UserRole).mp_cost for item in selected_items)
        if self.player.mp < total_mp and not getattr(self.player, 'god_mode', False):
            QMessageBox.warning(self, "魔法值不足", f"需要 {total_mp} MP，但你只有 {self.player.mp} MP！")
            return
        
        # 保存选中的技能
        self.selected_combo = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        self.accept()