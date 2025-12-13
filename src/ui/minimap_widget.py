from PyQt6.QtWidgets import QScrollArea, QWidget, QTableWidget, QVBoxLayout, QFrame, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QResizeEvent, QLinearGradient, QBrush, QPen

class MinimapWidget(QScrollArea):
    def __init__(self, game_map):
        super().__init__()
        self.game_map = game_map
        self.setWidgetResizable(True)
        
        # 创建内容小部件
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        # 设置内容小部件的布局
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setStyleSheet("background:#222; gridline-color: #444;")
        
        self.content_layout.addWidget(self.table)

    def resizeEvent(self, event: QResizeEvent):
        """窗口大小变化时自动调整"""
        super().resizeEvent(event)
        self.render()

    def render(self):
        size = self.game_map.size
        self.table.setRowCount(size)
        self.table.setColumnCount(size)
        
        # 计算最佳单元格大小
        area_width = self.table.width()
        area_height = self.table.height()
        cell_size = min(area_width // size, area_height // size, 25)
        
        # 设置行高和列宽
        for i in range(size):
            self.table.setRowHeight(i, cell_size)
            self.table.setColumnWidth(i, cell_size)
        
        # 清空表格
        self.table.clearContents()
        
        # 填充地图格子
        for y in range(size):
            for x in range(size):
                item = self.table.item(y, x)
                if item is None:
                    item = QTableWidgetItem()
                
                if self.game_map.is_wall(x, y):
                    item.setBackground(QColor("#555555"))
                else:
                    item.setBackground(QColor("#333333"))
                self.table.setItem(y, x, item)

        # 标记玩家位置
        px, py = int(self.game_map.player_x), int(self.game_map.player_y)
        if 0 <= px < size and 0 <= py < size:
            player_item = self.table.item(py, px)
            if player_item:
                player_item.setBackground(QColor("#ff5555"))

        # 标记敌人
        for e in self.game_map.enemies:
            if e.active and 0 <= e.x < size and 0 <= e.y < size:
                ei = self.table.item(e.y, e.x)
                if ei:
                    ei.setBackground(QColor("#ff9999"))

        # 标记道具
        for i in self.game_map.items:
            if i.active and 0 <= i.x < size and 0 <= i.y < size:
                ii = self.table.item(i.y, i.x)
                if ii:
                    ii.setBackground(QColor("#55ff55"))
        
        # 标记出口
        exit_x, exit_y = self.game_map.exit_point
        if 0 <= exit_x < size and 0 <= exit_y < size:
            exit_item = self.table.item(exit_y, exit_x)
            if exit_item:
                exit_item.setBackground(QColor("#ffcc00"))