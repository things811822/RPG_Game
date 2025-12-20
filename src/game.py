import sys
import random
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QGridLayout, QSizePolicy,
    QFrame, QSpacerItem, QScrollArea, QDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QTime, QPoint
from PyQt6.QtGui import QKeyEvent, QFont, QColor, QLinearGradient, QPalette, QBrush, QPainter
from src.ui.skill_dialog import SkillDialog
from src.ui.skill_combo_dialog import SkillComboDialog
from .player import Player
from .map import GameMap
from .battle import Enemy
from .ui.first_person_view import FirstPersonView
from .ui.minimap_widget import MinimapWidget
from .ui.enemy_ui import EnemyUI
from .ui.inventory_dialog import InventoryDialog
from .systems.skills import create_skills, check_skill_combo
from .systems.items import create_items
from .systems.monsters import create_monster

DEV_MODE_ENABLED = True  # 将此设置为 True 以启用开发者模式

class RPGGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 RPG 冒险 - 完整系统")
        self.resize(1600, 900)
        # 设置深色主题
        self.set_dark_theme()
        # 主要游戏对象
        self.player = Player()
        self.current_level = 1
        self.in_battle = False
        self.current_enemy = None
        self.current_enemy_spot = None  # 存储当前战斗敌人的位置
        self.god_mode = False  # 无敌模式
        # 控制相关
        self.keys_pressed = {'w': False, 'a': False, 's': False, 'd': False}
        self.move_speed = 0.1
        self.last_move_time = 0
        self.move_cooldown = 100
        self.player_dir = 0  # 默认视角J（北/上）- 0度
        # 传送模式
        self.teleport_mode = False
        # 生成初始地图
        self.game_map = GameMap(level=self.current_level)
        # 设置中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # ===== 主游戏区域 =====
        game_area = QWidget()
        game_layout = QVBoxLayout(game_area)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(5)
        
        # 第一人称视图区域
        self.fp_view = FirstPersonView(self.game_map, self)
        game_layout.addWidget(self.fp_view, 5)
        
        # ===== 右侧UI区域 =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        # ===== 右侧UI主框架 =====
        main_ui_frame = QFrame()
        main_ui_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        main_ui_layout = QVBoxLayout(main_ui_frame)
        main_ui_layout.setContentsMargins(8, 8, 8, 8)
        main_ui_layout.setSpacing(8)
        
        # ===== 状态信息区域 =====
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 8, 8, 8)
        status_layout.setSpacing(5)
        self.level_label = QLabel(f"关卡：{self.current_level}")
        self.level_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700; font-family: 'Microsoft YaHei';")
        self.hp_label = QLabel("❤️ HP: 100/100")
        self.hp_label.setStyleSheet("font-size: 13px; color: #ff5555; font-family: 'Microsoft YaHei';")
        self.mp_label = QLabel("💙 MP: 50/50")
        self.mp_label.setStyleSheet("font-size: 13px; color: #55aaff; font-family: 'Microsoft YaHei';")
        status_layout.addWidget(self.level_label)
        status_layout.addWidget(self.hp_label)
        status_layout.addWidget(self.mp_label)
        
        # ===== 操作按钮区域 =====
        action_frame = QFrame()
        action_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(8, 8, 8, 8)
        action_layout.setSpacing(5)
        
        # 基础按钮
        self.inventory_btn = QPushButton("🎒 背包")
        self.inventory_btn.setStyleSheet("padding: 8px; font-family: 'Microsoft YaHei'; color: white;")
        self.pickup_btn = QPushButton("✅ 拾取 (E)")
        self.pickup_btn.setEnabled(False)
        self.pickup_btn.setStyleSheet("padding: 8px; font-family: 'Microsoft YaHei'; color: white;")
        self.skill_btn = QPushButton("✨ 技能")
        self.skill_btn.setStyleSheet("padding: 8px; font-family: 'Microsoft YaHei'; color: white;")
        
        # 添加到交互区域
        action_layout.addWidget(self.inventory_btn)
        action_layout.addWidget(self.pickup_btn)
        action_layout.addWidget(self.skill_btn)
        
        # ===== 提示区域 =====
        hint_frame = QFrame()
        hint_frame.setStyleSheet("background-color: #262626; border-radius: 8px; border: 1px solid #444;")
        hint_layout = QVBoxLayout(hint_frame)
        hint_layout.setContentsMargins(8, 8, 8, 8)
        self.move_hint = QLabel("移动：WASD | 视角：IJKL")
        self.move_hint.setStyleSheet("font-size: 12px; color: #aaa; font-family: 'Microsoft YaHei';")
        self.move_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_layout.addWidget(self.move_hint)
        
        # ===== 战斗UI区域 =====
        battle_frame = QFrame()
        battle_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        battle_layout = QVBoxLayout(battle_frame)
        battle_layout.setContentsMargins(8, 8, 8, 8)
        battle_layout.setSpacing(5)
        
        # 战斗专用按钮（初始隐藏）
        self.combat_frame = QFrame()
        self.combat_frame.setStyleSheet("background-color: #3a2a2a; border-radius: 8px; border: 1px solid #662222;")
        self.combat_frame.setVisible(False)
        combat_layout = QVBoxLayout(self.combat_frame)
        combat_layout.setContentsMargins(8, 8, 8, 8)
        combat_layout.setSpacing(5)
        combat_title = QLabel("战斗选项")
        combat_title.setStyleSheet("font-weight: bold; color: #ff9999; font-family: 'Microsoft YaHei';")
        combat_layout.addWidget(combat_title)
        combat_btn_layout = QGridLayout()
        self.attack_btn = QPushButton("⚔️ 攻击")
        self.attack_btn.setStyleSheet("font-family: 'Microsoft YaHei'; color: white;")
        self.item_btn = QPushButton("🧪 道具")
        self.item_btn.setStyleSheet("font-family: 'Microsoft YaHei'; color: white;")
        self.flee_btn = QPushButton("🏃 逃跑")
        self.flee_btn.setStyleSheet("font-family: 'Microsoft YaHei'; color: white;")
        self.combo_btn = QPushButton("💫 组合技")
        self.combo_btn.setStyleSheet("font-family: 'Microsoft YaHei'; color: white;")
        combat_btn_layout.addWidget(self.attack_btn, 0, 0, 1, 2)
        combat_btn_layout.addWidget(self.item_btn, 1, 0)
        combat_btn_layout.addWidget(self.flee_btn, 1, 1)
        combat_btn_layout.addWidget(self.combo_btn, 2, 0, 1, 2)
        combat_layout.addLayout(combat_btn_layout)
        
        # 敌人UI（初始隐藏）
        self.enemy_ui = EnemyUI()
        self.enemy_ui.setVisible(False)
        
        # 添加到战斗区域
        battle_layout.addWidget(self.combat_frame)
        battle_layout.addWidget(self.enemy_ui)
        
        # ===== 小地图区域 =====
        minimap_frame = QFrame()
        minimap_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        minimap_layout = QVBoxLayout(minimap_frame)
        minimap_layout.setContentsMargins(8, 8, 8, 8)
        minimap_layout.setSpacing(5)
        minimap_label = QLabel("🗺️ 小地图")
        minimap_label.setStyleSheet("font-weight: bold; font-family: 'Microsoft YaHei'; color: white;")
        self.minimap = MinimapWidget(self.game_map)
        self.minimap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        minimap_layout.addWidget(minimap_label)
        minimap_layout.addWidget(self.minimap)
        
        # 添加小地图点击事件
        self.minimap.map_clicked.connect(self.handle_minimap_click)
        
        # ===== 开发者模式区域 =====
        dev_frame = QFrame()
        dev_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        dev_layout = QVBoxLayout(dev_frame)
        dev_layout.setContentsMargins(8, 8, 8, 8)
        dev_layout.setSpacing(5)
        
        # 开发者模式开关
        self.dev_mode_toggle = QCheckBox("开发者模式")
        self.dev_mode_toggle.setStyleSheet("color: #aaa; font-family: 'Microsoft YaHei';")
        self.dev_mode_toggle.setChecked(DEV_MODE_ENABLED)
        self.dev_mode_toggle.stateChanged.connect(self.toggle_dev_mode)
        self.dev_mode_toggle.setVisible(DEV_MODE_ENABLED)
        dev_layout.addWidget(self.dev_mode_toggle)
        
        # 开发者模式信息区域
        self.dev_info_frame = QFrame()
        self.dev_info_frame.setStyleSheet("background-color: #262626; border-radius: 5px; border: 1px solid #555;")
        self.dev_info_frame.setVisible(DEV_MODE_ENABLED)
        dev_info_layout = QVBoxLayout(self.dev_info_frame)
        dev_info_layout.setContentsMargins(6, 6, 6, 6)
        
        # 怪物列表标题
        monster_list_title = QLabel("生成的怪物列表")
        monster_list_title.setStyleSheet("color: #ffcc00; font-weight: bold; font-family: 'Microsoft YaHei';")
        dev_info_layout.addWidget(monster_list_title)
        
        # 怪物列表区域
        self.monster_list = QLabel("")
        self.monster_list.setStyleSheet("color: #aaa; font-size: 12px; font-family: 'Microsoft YaHei';")
        self.monster_list.setWordWrap(True)
        dev_info_layout.addWidget(self.monster_list)
        
        # 添加作弊功能到开发者模式UI
        if DEV_MODE_ENABLED:
            self.add_cheat_buttons(dev_info_layout)
        
        dev_layout.addWidget(self.dev_info_frame)
        
        # ===== 组合技创建区域 =====
        combo_frame = QFrame()
        combo_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        combo_layout = QVBoxLayout(combo_frame)
        combo_layout.setContentsMargins(8, 8, 8, 8)
        combo_layout.setSpacing(5)
        
        # 组合技标题
        combo_title = QLabel("组合技系统")
        combo_title.setStyleSheet("font-weight: bold; color: #ffcc00; font-family: 'Microsoft YaHei';")
        combo_layout.addWidget(combo_title)
        
        # 组合技说明
        combo_desc = QLabel("选择2-3个技能创建组合技，顺序很重要！")
        combo_desc.setStyleSheet("color: #aaa; font-family: 'Microsoft YaHei';")
        combo_layout.addWidget(combo_desc)
        
        # 创建组合技按钮
        self.create_combo_btn = QPushButton("✨ 创建组合技")
        self.create_combo_btn.setStyleSheet("padding: 8px; background-color: #4a6fa5; color: white; font-family: 'Microsoft YaHei';")
        self.create_combo_btn.clicked.connect(self.open_skill_combo_menu)
        combo_layout.addWidget(self.create_combo_btn)
        
        # ===== 将所有UI元素添加到主UI框架 =====
        main_ui_layout.addWidget(status_frame)
        main_ui_layout.addWidget(action_frame)
        main_ui_layout.addWidget(hint_frame)
        main_ui_layout.addWidget(battle_frame)
        main_ui_layout.addWidget(minimap_frame)
        main_ui_layout.addWidget(combo_frame)
        main_ui_layout.addWidget(dev_frame)
        main_ui_layout.addStretch()
        
        # ===== 创建可滚动的右侧UI区域 =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_ui_frame)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        # 添加到右侧布局
        right_layout.addWidget(scroll_area)
        
        # 添加到主布局
        main_layout.addWidget(game_area, 5)
        main_layout.addWidget(right_panel, 3)
        
        # 信号连接
        self.inventory_btn.clicked.connect(self.open_inventory)
        self.pickup_btn.clicked.connect(self.pickup_item)
        self.skill_btn.clicked.connect(self.open_skill_menu)
        self.attack_btn.clicked.connect(self.player_attack)
        self.item_btn.clicked.connect(self.show_item_selection)
        self.flee_btn.clicked.connect(self.flee_battle)
        self.combo_btn.clicked.connect(self.use_saved_skill_combo)
        self.combo_btn.setVisible(False)
        
        # 设置定时器
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.process_movement)
        self.move_timer.start(33)  # 30FPS
        self.update_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # 确保窗口大小变化时UI能自适应
        self.resizeEvent = self.custom_resize_event
    
    def handle_minimap_click(self, x, y):
        """处理小地图点击事件"""
        if self.teleport_mode:
            # 传送到点击位置
            self.game_map.player_x = float(x)
            self.game_map.player_y = float(y)
            self.update_ui()
            self.teleport_mode = False
            self.log_message(f"已传送到 ({x}, {y})")
    
    def add_cheat_buttons(self, layout):
        """添加作弊功能按钮到开发者模式UI"""
        # 作弊功能（已移除"无限技能"）
        cheats = [
            ("一键跳关", self.skip_level),
            ("清空敌人", self.clear_enemies),
            ("完全恢复", self.full_heal),
            ("最大MP", self.max_mp),
            ("添加道具", self.add_items),
            ("传送地图", self.toggle_teleport_mode),
            ("添加Boss", self.add_boss),
            ("无敌模式", self.toggle_god_mode)
        ]
        
        # 创建按钮
        for text, func in cheats:
            btn = QPushButton(text)
            btn.setStyleSheet("padding: 8px; background-color: #3a4a6a; color: white; font-family: 'Microsoft YaHei';")
            btn.clicked.connect(func)
            layout.addWidget(btn)
    
    def toggle_teleport_mode(self):
        """切换传送模式"""
        self.teleport_mode = not self.teleport_mode
        if self.teleport_mode:
            self.log_message("传送模式已启用。点击小地图选择位置。")
        else:
            self.log_message("传送模式已禁用。")
    
    def skip_level(self):
        """跳到下一关"""
        self.current_level += 1
        self.generate_new_map()
        self.level_label.setText(f"关卡：{self.current_level}")
        self.log_message(f"已跳到第 {self.current_level} 关")
    
    def clear_enemies(self):
        """清空所有敌人"""
        for enemy in self.game_map.enemies:
            enemy.active = False
        self.log_message("所有敌人已被清除")
    
    def full_heal(self):
        """完全恢复HP"""
        self.player.hp = self.player.max_hp
        self.update_ui()
        self.log_message("玩家HP已完全恢复")
    
    def max_mp(self):
        """完全恢复MP"""
        self.player.mp = self.player.max_mp
        self.update_ui()
        self.log_message("玩家MP已完全恢复")
    
    def add_items(self):
        """添加所有道具"""
        items = create_items()
        for item in items:
            self.player.inventory.append(item)
        self.log_message("已添加所有道具到背包")
    
    def add_boss(self):
        """添加Boss到当前地图（作弊功能）"""
        # 仅在非Boss关卡中添加Boss
        if self.game_map.is_boss_level:
            self.log_message("当前是Boss关卡，不需要添加Boss")
            return
        
        # 检查是否已经有Boss
        boss_count = sum(1 for enemy in self.game_map.enemies if enemy.is_boss)
        if boss_count > 0:
            self.log_message("当前地图已有Boss")
            return
        
        # 添加Boss
        if self.game_map.add_boss_at_exit():
            self.log_message("Boss已添加到地图")
            self.update_dev_info()  # 更新开发者模式信息
        else:
            self.log_message("无法添加Boss：无法找到合适的空地")
    
    def toggle_god_mode(self):
        """切换无敌模式"""
        self.god_mode = not self.god_mode
        status = "开启" if self.god_mode else "关闭"
        self.log_message(f"无敌模式已{status}")
    
    def custom_resize_event(self, event):
        """自定义窗口大小变化事件"""
        super().resizeEvent(event)
        # 调整小地图大小以适应新窗口尺寸
        self.update_minimap_size()
    
    def update_minimap_size(self):
        """更新小地图大小"""
        # 根据窗口大小调整小地图
        if hasattr(self, 'minimap') and self.minimap:
            # 获取右侧UI区域的高度
            right_panel_height = self.centralWidget().height() - 100
            # 设置小地图高度为右侧UI区域高度的30%
            self.minimap.setMinimumHeight(int(right_panel_height * 0.3))
    
    def toggle_dev_mode(self, state):
        """切换开发者模式"""
        global DEV_MODE_ENABLED
        DEV_MODE_ENABLED = (state == Qt.CheckState.Checked.value)
        self.dev_info_frame.setVisible(DEV_MODE_ENABLED)
        if DEV_MODE_ENABLED:
            self.update_dev_info()
    
    def update_dev_info(self):
        """更新开发者模式信息"""
        if not DEV_MODE_ENABLED:
            return
            
        # 更新怪物列表
        monster_list = []
        for enemy in self.game_map.enemies:
            if enemy.active:
                # 根据是否为Boss添加不同颜色
                if enemy.is_boss:
                    monster_list.append(f"• <span style='color: #ff5555;'>{enemy.enemy.name}</span> (x:{enemy.x}, y:{enemy.y})")
                else:
                    monster_list.append(f"• {enemy.enemy.name} (x:{enemy.x}, y:{enemy.y})")
        
        if not monster_list:
            monster_list.append("• 没有生成的怪物")
        
        self.monster_list.setText("\n".join(monster_list))
    
    def set_dark_theme(self):
        """设置深色主题"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        
        palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
    
    def generate_new_map(self):
        """生成新地图"""
        self.game_map = GameMap(level=self.current_level)
        
        self.fp_view.game_map = self.game_map
        self.minimap.game_map = self.game_map
        if DEV_MODE_ENABLED:
            self.update_dev_info()
    
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        # 战斗中禁用移动和视角
        if self.in_battle:
            if key == Qt.Key.Key_Escape:
                self.close()
            return
        # 开发者模式快捷键
        if DEV_MODE_ENABLED and key == Qt.Key.Key_F1:
            self.dev_mode_toggle.setChecked(not self.dev_mode_toggle.isChecked())
            event.accept()
            return
        # 移动控制（WASD基于视角方向）
        if key == Qt.Key.Key_W:
            self.keys_pressed['w'] = True
        elif key == Qt.Key.Key_D:
            self.keys_pressed['d'] = True
        elif key == Qt.Key.Key_S:
            self.keys_pressed['s'] = True
        elif key == Qt.Key.Key_A:
            self.keys_pressed['a'] = True
        # 视角控制（IJKL键）- 直接重新渲染
        elif key == Qt.Key.Key_I:
            self.set_view_direction_immediate(90)  # 东（朝右）
            event.accept()
            return
        elif key == Qt.Key.Key_J:
            self.set_view_direction_immediate(0)  # 北（朝上）- 默认视角
            event.accept()
            return
        elif key == Qt.Key.Key_K:
            self.set_view_direction_immediate(180)  # 南（朝下）
            event.accept()
            return
        elif key == Qt.Key.Key_L:
            self.set_view_direction_immediate(270)  # 西（朝左）
            event.accept()
            return
        # 其他控制
        elif key == Qt.Key.Key_E:
            if self.fp_view.show_exit_prompt:
                self.next_level()
            else:
                self.pickup_item()
            event.accept()
            return
        elif key == Qt.Key.Key_I:
            self.open_inventory()
            event.accept()
            return
        elif key == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_W:
            self.keys_pressed['w'] = False
        elif key == Qt.Key.Key_D:
            self.keys_pressed['d'] = False
        elif key == Qt.Key.Key_S:
            self.keys_pressed['s'] = False
        elif key == Qt.Key.Key_A:
            self.keys_pressed['a'] = False
        super().keyReleaseEvent(event)
    
    def set_view_direction_immediate(self, direction):
        """立即设置视角方向并重新渲染整个场景"""
        self.player_dir = direction
        self.fp_view.player_dir = direction
        # 立即重新渲染整个场景
        self.fp_view.render_view()
        # 更新小地图
        self.minimap.render()
    
    def process_movement(self):
        """处理WASD移动逻辑 - 基于视角方向"""
        if self.in_battle:
            return
            
        current_time = QTime.currentTime().msecsSinceStartOfDay()
        if current_time - self.last_move_time < self.move_cooldown:
            return
            
        dx, dy = 0, 0
        # 获取玩家当前面向
        direction = self.player_dir
        
        # 根据当前视角方向计算移动向量
        if self.keys_pressed['w']:  # 前进
            if direction == 0:    # J (北/上)
                dx += 0.1
            elif direction == 90: # I (东/右)
                dy += 0.1
            elif direction == 180: # K (南/下)
                dx -= 0.1
            elif direction == 270: # L (西/左)
                dy -= 0.1
        if self.keys_pressed['s']:  # 后退
            if direction == 0:    # J (北/上)
                dx -= 0.1
            elif direction == 90: # I (东/右)
                dy -= 0.1
            elif direction == 180: # K (南/下)
                dx += 0.1
            elif direction == 270: # L (西/左)
                dy += 0.1
        if self.keys_pressed['d']:  # 右移
            if direction == 0:    # J (北/上)
                dy += 0.1
            elif direction == 90: # I (东/右)
                dx -= 0.1
            elif direction == 180: # K (南/下)
                dy -= 0.1
            elif direction == 270: # L (西/左)
                dx += 0.1
        if self.keys_pressed['a']:  # 左移
            if direction == 0:    # J (北/上)
                dy -= 0.1
            elif direction == 90: # I (东/右)
                dx += 0.1
            elif direction == 180: # K (南/下)
                dy += 0.1
            elif direction == 270: # L (西/左)
                dx -= 0.1
        
        # 执行移动
        if dx != 0 or dy != 0:
            if self.game_map.move_player(dx, dy):
                self.check_pickup_available()
                self.update_ui()
                self.last_move_time = current_time
    
    def check_pickup_available(self):
        x, y = int(self.game_map.player_x), int(self.game_map.player_y)
        item_spot = self.game_map.get_item_at(x, y)
        self.pickup_btn.setEnabled(bool(item_spot))
    
    def pickup_item(self):
        if self.in_battle:
            return
        x, y = int(self.game_map.player_x), int(self.game_map.player_y)
        item = self.game_map.collect_item(x, y)
        if item:
            self.player.inventory.append(item)
            self.log_message(f"获得了 {item.name}！")
            self.check_pickup_available()
            self.update_ui()
        else:
            self.log_message("这里没有东西可拾取。")
    
    def next_level(self):
        """进入下一关"""
        self.keys_pressed = {'w': False, 'a': False, 's': False, 'd': False}
        
        px, py = int(self.game_map.player_x), int(self.game_map.player_y)
        exit_x, exit_y = self.game_map.exit_point
        dist_to_exit = math.sqrt((px - exit_x)**2 + (py - exit_y)**2)
        
        if dist_to_exit < 1.5:
            # 检查是否有boss
            if self.game_map.boss_present:
                self.log_message("请先击败boss再进入下一关！")
                return
            
            # 检查是否有敌人
            if any(e.active for e in self.game_map.enemies):
                self.log_message("还有敌人未被击败！请清除所有敌人再进入下一关。")
                return
            
            # 检查是否有未拾取道具
            remaining_items = [item for item in self.game_map.items if item.active]
            if remaining_items:
                reply = QMessageBox.question(self, "确认", 
                                            f"还有 {len(remaining_items)} 个道具未拾取，确定要进入下一关吗？",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.current_level += 1
            QMessageBox.information(self, "关卡完成", f"你完成了第 {self.current_level - 1} 关！\n进入第 {self.current_level} 关……")
            self.generate_new_map()
            self.level_label.setText(f"关卡：{self.current_level}")
            self.player_dir = 0  # 重置视角为北（朝上）
            self.fp_view.player_dir = 0
            self.update_ui()
    
    def update_ui(self):
        self.hp_label.setText(f"❤️ HP: {self.player.hp}/{self.player.max_hp}")
        self.mp_label.setText(f"💙 MP: {self.player.mp}/{self.player.max_mp}")
        self.minimap.render()
        
        if not self.in_battle:
            x, y = int(self.game_map.player_x), int(self.game_map.player_y)
            enemy_spot = self.game_map.get_enemy_at(x, y)
            if enemy_spot:
                self.start_battle(enemy_spot)
        else:
            self.fp_view.scene().clear()
            # 使用高对比度的黄色
            text_item = self.fp_view.scene().addText(f"⚔️ 与 {self.current_enemy.name} 战斗中！", 
                                                   QFont("Microsoft YaHei", 20))
            text_item.setDefaultTextColor(QColor(255, 255, 0))
            
            # 战斗中更新敌人UI
            self.enemy_ui.update_enemy(
                self.current_enemy.name,
                self.current_enemy.hp,
                self.current_enemy.max_hp
            )
        
        self.update_move_buttons()
        
        # 确保第一人称视图更新
        if not self.in_battle:
            self.fp_view.render_view()
        
        # 更新开发者模式信息
        if DEV_MODE_ENABLED:
            self.update_dev_info()
    
    def update_move_buttons(self):
        """动态更新UI可见性"""
        if self.in_battle:
            self.combat_frame.setVisible(True)
            self.enemy_ui.setVisible(True)
            self.pickup_btn.setVisible(False)
            self.move_hint.setVisible(False)
            # 战斗中显示组合技按钮
            self.combo_btn.setVisible(True)
        else:
            self.combat_frame.setVisible(False)
            self.enemy_ui.setVisible(False)
            self.pickup_btn.setVisible(True)
            self.move_hint.setVisible(True)
            # 非战斗中隐藏组合技按钮
            self.combo_btn.setVisible(False)
    
    def start_battle(self, enemy_spot):
        """开始战斗，传入EnemySpot对象"""
        self.in_battle = True
        self.current_enemy_spot = enemy_spot
        # 根据类型获取敌人
        self.current_enemy = create_monster(enemy_spot.enemy_type)
        self.update_ui()
    
    def player_attack(self):
        self._perform_action("普通攻击", lambda: self._damage_enemy(self.player.get_effective_attack()))
    
    def show_item_selection(self):
        """显示道具选择对话框"""
        if not self.player.inventory:
            self.log_message("背包为空！")
            return
            
        dialog = InventoryDialog(self.player.inventory, self.player, in_battle=self.in_battle, game=self)
        if dialog.exec() and dialog.selected_item:
            self.use_selected_item(dialog.selected_item)
    
    def use_selected_item(self, item):
        """使用选中的道具"""
        if item in self.player.inventory:
            self.player.use_item(item)
            self.log_message(f"使用了 {item.name}！")
            self.update_ui()
            if self.in_battle:
                self.enemy_turn()
    
    def _damage_enemy(self, dmg):
        """造成伤害并检查是否击败敌人"""
        if not self.current_enemy or not self.current_enemy.is_alive():
            return "敌人已被击败！"
        
        self.current_enemy.hp -= dmg
        
        # 检查是否击败敌人
        if self.current_enemy.hp <= 0:
            self.current_enemy.hp = 0
            self.end_battle(victory=True)
            return f"造成 {dmg} 伤害！敌人被击败！"
        
        return f"造成 {dmg} 伤害！"
    
    def _perform_action(self, name, action_func):
        """执行战斗动作并检查战斗状态"""
        if not self.in_battle or not self.current_enemy or not self.current_enemy.is_alive():
            return
        
        msg = action_func()
        self.log_message(msg)
        self.update_ui()
        
        # 只有当敌人还活着时，才会进行敌人回合
        if self.current_enemy and self.current_enemy.is_alive():
            self.enemy_turn()
    
    def enemy_turn(self):
        """敌人回合"""
        if not self.current_enemy or not self.current_enemy.is_alive():
            return
        
        if self.player.is_alive():
            # 无敌模式下不受伤
            if self.god_mode:
                self.log_message(f"{self.current_enemy.name} 攻击了你，但你毫发无损！")
            else:
                dmg = max(1, self.current_enemy.attack - self.player.get_effective_defense() // 2)
                self.player.hp -= dmg
                self.log_message(f"{self.current_enemy.name} 造成 {dmg} 伤害！")
            
            self.update_ui()
            
            # 更新临时效果
            self.player.update_temp_effects()
            
            # 检查玩家是否死亡
            if not self.player.is_alive() and not self.god_mode:
                self.end_battle(victory=False)
    
    def flee_battle(self):
        """尝试逃跑"""
        if random.random() < 0.7:
            # 逃跑后随机移动
            self.random_move_after_flee()
            self.log_message("你成功逃跑了！")
            self.end_battle(victory=None)
        else:
            self.log_message("逃跑失败！")
            self.enemy_turn()
    
    def random_move_after_flee(self):
        """逃跑后随机向一个可移动的方向移动"""
        x, y = int(self.game_map.player_x), int(self.game_map.player_y)
        possible_moves = []
        
        # 检查所有方向
        if not self.game_map.is_wall(x, y-1):  # 上
            possible_moves.append((0, -0.5))
        if not self.game_map.is_wall(x, y+1):  # 下
            possible_moves.append((0, 0.5))
        if not self.game_map.is_wall(x-1, y):  # 左
            possible_moves.append((-0.5, 0))
        if not self.game_map.is_wall(x+1, y):  # 右
            possible_moves.append((0.5, 0))
        
        # 随机选择一个方向
        if possible_moves:
            dx, dy = random.choice(possible_moves)
            self.game_map.move_player(dx, dy)
            self.update_ui()
    
    def end_battle(self, victory):
        """结束战斗，清理所有战斗相关状态"""
        # 首先标记敌人被击败
        if self.current_enemy_spot and victory is True:
            x, y = self.current_enemy_spot.x, self.current_enemy_spot.y
            self.game_map.defeat_enemy(x, y)
        
        # 重置战斗状态
        self.in_battle = False
        self.current_enemy = None
        self.current_enemy_spot = None
        
        # 更新UI
        self.update_ui()
        
        # 根据战斗结果处理
        if victory is True:
            # 战斗胜利后恢复血量
            self.player.hp = min(self.player.max_hp, self.player.hp + 10)
            
            # 检查是否是boss战
            if hasattr(self.current_enemy, 'is_boss') and self.current_enemy.is_boss:
                # Boss掉落额外奖励
                additional_items = create_items()
                for _ in range(2):
                    item = random.choice(additional_items)
                    self.player.inventory.append(item)
                self.log_message("你击败了boss！获得特殊奖励！")
            
            self.log_message("战斗胜利！获得 10 HP 恢复。")
            self.update_ui()
        elif victory is None:
            # 逃跑成功
            self.log_message("你成功逃离了战斗。")
        elif victory is False:
            QMessageBox.critical(self, "游戏结束", "你倒下了……\n游戏结束！")
            sys.exit()
    
    def open_inventory(self):
        """打开背包查看所有道具"""
        dialog = InventoryDialog(self.player.inventory, self.player, in_battle=False, game=self)
        dialog.exec()
    
    def open_skill_menu(self):
        """打开技能菜单"""
        if not self.player.skills:
            self.log_message("没有可用技能！")
            return
            
        dialog = SkillDialog(self.player.skills, self.player, self)
        if dialog.exec() and dialog.selected_skill:
            self.use_skill(dialog.selected_skill)
    
    def open_skill_combo_menu(self):
        """打开独立的技能组合调配窗口"""
        if len(self.player.skills) < 2:
            self.log_message("需要至少2个技能才能创建组合！")
            return
            
        dialog = SkillComboDialog(self.player.skills, self.player, self)
        if dialog.exec() and dialog.selected_combo:
            # 保存组合
            self.saved_skill_combo = dialog.selected_combo
            combo_name = " + ".join(skill.name for skill in self.saved_skill_combo)
            self.log_message(f"已保存技能组合: {combo_name}")
    
    def use_saved_skill_combo(self):
        """在战斗中使用已保存的技能组合"""
        if not hasattr(self, 'saved_skill_combo') or not self.saved_skill_combo:
            self.log_message("没有已保存的技能组合！")
            return
            
        if len(self.saved_skill_combo) < 2:
            self.log_message("技能组合至少需要2个技能！")
            return
            
        # 检查MP是否足够
        total_mp = sum(skill.mp_cost for skill in self.saved_skill_combo)
        if self.player.mp < total_mp and not self.god_mode:
            self.log_message(f"魔法值不足！需要 {total_mp} MP，当前仅有 {self.player.mp} MP")
            return
            
        # 记录原始MP
        original_mp = self.player.mp
        
        # 执行技能组合
        messages = []
        enemy_defeated = False
        for skill in self.saved_skill_combo:
            msg = skill.use(self.player, self.current_enemy)
            messages.append(msg)
            # 检查敌人是否死亡
            if self.current_enemy and not self.current_enemy.is_alive():
                enemy_defeated = True
                break
        
        # 无敌模式下恢复MP
        if self.god_mode:
            self.player.mp = original_mp
            
        # 显示结果
        combo_name = " + ".join(skill.name for skill in self.saved_skill_combo)
        self.log_message(f"✨ {combo_name} 组合技 ✨\n" + "\n".join(messages))
        
        # 检查敌人是否死亡
        if enemy_defeated:
            self.end_battle(victory=True)
            return
        
        # 如果在战斗中且敌人还活着，敌人回合
        if self.in_battle and self.current_enemy and self.current_enemy.is_alive():
            self.enemy_turn()
    
    def use_skill(self, skill):
        """使用选定的技能"""
        if not skill.can_use(self.player) and not self.god_mode:
            self.log_message("魔法值不足！")
            return
            
        # 无敌模式下不消耗MP
        original_mp = self.player.mp
        msg = skill.use(self.player, self.current_enemy)
        
        # 无敌模式下恢复MP
        if self.god_mode:
            self.player.mp = original_mp
            
        self.log_message(msg)
        self.update_ui()
        
        # 检查敌人是否死亡
        if self.current_enemy and not self.current_enemy.is_alive():
            self.end_battle(victory=True)
            return
        
        # 如果在战斗中且敌人还活着，敌人回合
        if self.in_battle and self.current_enemy and self.current_enemy.is_alive():
            self.enemy_turn()
    
    def log_message(self, msg):
        """显示消息提示"""
        # 确保msg是字符串类型
        if not isinstance(msg, str):
            msg = str(msg)
        QMessageBox.information(self, "提示", msg)