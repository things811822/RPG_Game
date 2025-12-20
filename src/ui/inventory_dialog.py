from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class InventoryDialog(QDialog):
    item_selected = pyqtSignal(object)  # 添加信号
    item_used = pyqtSignal(object)      # 添加信号

    def __init__(self, inventory, player, in_battle=False, game=None, parent=None):
        super().__init__(parent)
        self.inventory = inventory
        self.player = player
        self.in_battle = in_battle
        self.game = game
        self.selected_item = None
        self.setWindowTitle("背包")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("🎒 背包")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffd700;")
        layout.addWidget(title_label)
        
        # 背包描述
        desc_label = QLabel(f"玩家等级: {self.player.level} | 金币: {self.player.gold}")
        desc_label.setStyleSheet("color: #aaa;")
        layout.addWidget(desc_label)
        
        # 道具列表
        self.item_list = QListWidget()
        self.item_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3a4a6a;
                color: white;
            }
        """)
        self.item_list.itemDoubleClicked.connect(self.handle_item_double_click)  # 双击使用
        self.update_item_list()
        layout.addWidget(self.item_list)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 使用按钮（战斗中可用）
        if in_battle:
            self.use_btn = QPushButton("使用 (E)")
            self.use_btn.setShortcut("E")  # 设置快捷键
            self.use_btn.clicked.connect(self.use_selected_item)
            self.use_btn.setEnabled(False)  # 默认禁用，直到选择道具
            btn_layout.addWidget(self.use_btn)
        
        # 装备按钮（非战斗中可用）
        if not in_battle:
            self.equip_btn = QPushButton("装备 (E)")
            self.equip_btn.setShortcut("E")  # 设置快捷键
            self.equip_btn.clicked.connect(self.equip_selected_item)
            self.equip_btn.setEnabled(False)  # 默认禁用，直到选择道具
            btn_layout.addWidget(self.equip_btn)
        
        # 关闭按钮
        close_btn = QPushButton("关闭 (ESC)")
        close_btn.setShortcut("ESC")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 连接选择变化事件
        self.item_list.itemSelectionChanged.connect(self.handle_selection_changed)
    
    def update_item_list(self):
        """更新道具列表"""
        self.item_list.clear()
        
        if not self.inventory:
            empty_item = QListWidgetItem("背包为空")
            empty_item.setForeground(QColor("#aaa"))
            self.item_list.addItem(empty_item)
            return
        
        for item in self.inventory:
            # 根据是否为Boss奖励设置不同颜色
            if hasattr(item, 'boss_reward') and item.boss_reward:
                item_text = f"🌟 {item.name} - {item.description}"
                item_color = QColor(255, 215, 0)  # 金色
            else:
                item_text = f"• {item.name} - {item.description}"
                item_color = QColor(200, 200, 200)  # 浅灰色
            
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            list_item.setForeground(item_color)
            self.item_list.addItem(list_item)
    
    def handle_selection_changed(self):
        """处理道具选择变化"""
        selected_items = self.item_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        if self.in_battle and hasattr(self, 'use_btn'):
            self.use_btn.setEnabled(has_selection)
        elif not self.in_battle and hasattr(self, 'equip_btn'):
            self.equip_btn.setEnabled(has_selection)
    
    def handle_item_double_click(self, item):
        """处理道具双击事件"""
        self.selected_item = item.data(Qt.ItemDataRole.UserRole)
        if self.in_battle:
            self.use_selected_item()
        else:
            self.equip_selected_item()
    
    def use_selected_item(self):
        """使用选中的道具"""
        selected_items = self.item_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个道具")
            return
        
        self.selected_item = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # 检查道具是否可用
        if hasattr(self.selected_item, 'consumable_on_death') and self.selected_item.consumable_on_death:
            # 复活石等特殊道具
            if self.player.hp <= 0:
                self.item_used.emit(self.selected_item)
                self.accept()
                return
        
        # 发射信号
        self.item_used.emit(self.selected_item)
        
        # 从背包中移除道具
        if self.selected_item in self.inventory:
            self.inventory.remove(self.selected_item)
        
        self.update_item_list()
        self.accept()
    
    def equip_selected_item(self):
        """装备选中的道具"""
        selected_items = self.item_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个道具")
            return
        
        self.selected_item = selected_items[0].data(Qt.ItemDataRole.UserRole)
        # 这里可以添加装备逻辑
        self.item_selected.emit(self.selected_item)
        self.accept()