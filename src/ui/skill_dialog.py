from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QWidget, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class SkillCard(QFrame):
    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.setStyleSheet("border: 1px solid #555; border-radius: 8px; background: #333;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 技能名称
        name_label = QLabel(f"<b>{skill.name}</b>")
        name_label.setStyleSheet("color: #ffd700; font-size: 14px;")
        layout.addWidget(name_label)
        
        # MP消耗
        mp_label = QLabel(f"MP消耗: {skill.mp_cost}")
        mp_label.setStyleSheet("color: #55aaff; font-size: 12px;")
        layout.addWidget(mp_label)
        
        # 描述
        desc_label = QLabel(skill.description)
        desc_label.setStyleSheet("color: #aaa; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 使用按钮
        self.use_btn = QPushButton("使用")
        self.use_btn.setStyleSheet("background-color: #4a6fa5; color: white;")
        layout.addWidget(self.use_btn)

class SkillDialog(QDialog):
    def __init__(self, skills, player, parent=None):
        super().__init__(parent)
        self.setWindowTitle("技能")
        self.setFixedSize(500, 400)
        self.selected_skill = None
        self.skills = skills
        self.player = player
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("可用技能")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        
        # 添加技能卡片
        for skill in skills:
            card = SkillCard(skill)
            card.use_btn.clicked.connect(lambda _, s=skill: self.select_skill(s))
            container_layout.addWidget(card)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("padding: 8px;")
        close_btn.clicked.connect(self.reject)
        main_layout.addWidget(close_btn)

    def select_skill(self, skill):
        if skill.can_use(self.player):
            self.selected_skill = skill
            self.accept()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "技能不可用", "魔法值不足！")