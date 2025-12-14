import sys
import random
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QGridLayout, QSizePolicy,
    QFrame, QSpacerItem, QScrollArea, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QTime, QPoint
from PyQt6.QtGui import QKeyEvent, QFont, QColor, QLinearGradient, QPalette, QBrush, QPainter

from src.ui.skill_dialog import SkillDialog
from .player import Player
from .map import GameMap
from .battle import Enemy
from .ui.first_person_view import FirstPersonView
from .ui.minimap_widget import MinimapWidget
from .ui.enemy_ui import EnemyUI
from .ui.inventory_dialog import InventoryDialog
from .systems.skills import create_skills
from .systems.items import create_items
from .systems.monsters import create_monster

DEV_MODE_ENABLED = False  # 将此设置为 True 以启用开发者模式

class CheatMenu(QDialog):
    """修复中文显示问题的作弊菜单"""
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle("作弊菜单")
        # 设置窗口标志：确保在所有窗口之上
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Tool)
        
        # 设置全局字体
        font = QFont("Microsoft YaHei", 9)
        self.setFont(font)
        
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(30, 30, 40, 0.95);
                border: 2px solid #ffcc00;
                border-radius: 8px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4a6fa5;
                color: white;
                border: 1px solid #3a5a80;
                padding: 8px;
                margin: 5px;
                font-size: 12px;
                border-radius: 4px;
                min-height: 30px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5a7fb5;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("🎮 开发者作弊菜单")
        title.setStyleSheet("color: #ffcc00; font-size: 16px; font-weight: bold;")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 作弊选项
        cheats = [
            ("一键跳关", self.skip_level),
            ("清空敌人", self.clear_enemies),
            ("完全恢复", self.full_heal),
            ("最大MP", self.max_mp),
            ("添加道具", self.add_items),
            ("无限技能", self.infinite_skills),
            ("传送地图", self.teleport_map),
            ("添加Boss", self.add_boss),
            ("无敌模式", self.toggle_god_mode)
        ]
        
        # 创建按钮并设置字体
        for text, func in cheats:
            btn = QPushButton(text)
            btn.setFont(QFont("Microsoft YaHei", 10))
            btn.setStyleSheet("background-color: #3a4a6a;")
            btn.setMinimumHeight(35)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(func)
            layout.addWidget(btn)
        
        # 关闭按钮
        close_btn = QPushButton("❌ 关闭")
        close_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        close_btn.setStyleSheet("background-color: #a03030; margin-top: 15px;")
        close_btn.setMinimumHeight(35)
        close_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # 设置大小
        self.setFixedSize(340, 480)
        
        # 默认隐藏
        self.setVisible(False)
    
    def position_at_center(self):
        """将窗口定位到屏幕中央，确保在所有窗口之上"""
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        # 计算屏幕中央位置
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        
        # 确保不被任务栏遮挡
        if y + self.height() > screen_geometry.height():
            y = screen_geometry.height() - self.height() - 20
            
        # 确保窗口在最前
        self.move(x, y)
        self.raise_()
        self.activateWindow()
    
    def skip_level(self):
        """跳到下一关"""
        self.game.current_level += 1
        self.game.generate_new_map()
        self.game.level_label.setText(f"关卡：{self.game.current_level}")
        self.game.log_message(f"已跳到第 {self.game.current_level} 关")
    
    def clear_enemies(self):
        """清空所有敌人"""
        for enemy in self.game.game_map.enemies:
            enemy.active = False
        self.game.log_message("所有敌人已被清除")
    
    def full_heal(self):
        """完全恢复HP"""
        self.game.player.hp = self.game.player.max_hp
        self.game.update_ui()
        self.game.log_message("玩家HP已完全恢复")
    
    def max_mp(self):
        """完全恢复MP"""
        self.game.player.mp = self.game.player.max_mp
        self.game.update_ui()
        self.game.log_message("玩家MP已完全恢复")
    
    def add_items(self):
        """添加所有道具"""
        items = create_items()
        for item in items:
            self.game.player.inventory.append(item)
        self.game.log_message("已添加所有道具到背包")
    
    def infinite_skills(self):
        """无限技能（不消耗MP）"""
        for skill in self.game.player.skills:
            skill.mp_cost = 0
        self.game.update_skill_buttons()
        self.game.log_message("技能MP消耗已设为0")
    
    def teleport_map(self):
        """传送到地图任意位置"""
        # 简单实现：传送到地图中心
        size = self.game.game_map.size
        center_x = size // 2
        center_y = size // 2
        
        # 找到最近的空地
        for r in range(5):
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    x, y = center_x + dx, center_y + dy
                    if 1 <= x < size-1 and 1 <= y < size-1 and not self.game.game_map.is_wall(x, y):
                        self.game.game_map.player_x = float(x)
                        self.game.game_map.player_y = float(y)
                        self.game.update_ui()
                        self.game.log_message(f"已传送到 ({x}, {y})")
                        return
    
    def add_boss(self):
        """添加Boss到当前地图"""
        self.game.game_map.add_boss()
        self.game.log_message("Boss已添加到地图")
    
    def toggle_god_mode(self):
        """切换无敌模式"""
        self.game.god_mode = not getattr(self.game, 'god_mode', False)
        status = "开启" if self.game.god_mode else "关闭"
        self.game.log_message(f"无敌模式已{status}")

class RPGGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 RPG 冒险 - 完整系统")
        self.resize(1400, 800)
        
        # 设置深色主题
        self.set_dark_theme()
        
        # 主要游戏对象
        self.player = Player()
        self.current_level = 1
        self.in_battle = False
        self.current_enemy = None
        self.god_mode = False  # 无敌模式
        
        # 控制相关
        self.keys_pressed = {'w': False, 'a': False, 's': False, 'd': False}
        self.move_speed = 0.1
        self.last_move_time = 0
        self.move_cooldown = 100
        self.player_dir = 0  # 0: North, 90: East, 180: South, 270: West
        
        # 生成初始地图
        self.game_map = GameMap(level=self.current_level)
        
        # 开发者模式
        self.cheat_menu = CheatMenu(self, self) if DEV_MODE_ENABLED else None
        
        # 设置中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ===== 第一人称视图区域 =====
        self.fp_view = FirstPersonView(self.game_map, self)
        
        # ===== 右侧面板 =====
        right_panel = QWidget()
        right_panel.setMaximumWidth(320)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 5, 10, 10)
        right_layout.setSpacing(12)
        
        # --- 顶部状态区域 ---
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 10, 10, 10)
        status_layout.setSpacing(8)
        
        self.level_label = QLabel(f"关卡：{self.current_level}")
        self.level_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700;")
        
        self.hp_label = QLabel("❤️ HP: 100/100")
        self.hp_label.setStyleSheet("font-size: 13px; color: #ff5555;")
        
        self.mp_label = QLabel("💙 MP: 50/50")
        self.mp_label.setStyleSheet("font-size: 13px; color: #55aaff;")
        
        status_layout.addWidget(self.level_label)
        status_layout.addWidget(self.hp_label)
        status_layout.addWidget(self.mp_label)
        
        # --- 交互按钮区域 ---
        action_frame = QFrame()
        action_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(10, 10, 10, 10)
        action_layout.setSpacing(10)
        
        # 基础按钮（始终显示）
        self.inventory_btn = QPushButton("🎒 背包")
        self.inventory_btn.setStyleSheet("padding: 8px;")
        
        self.pickup_btn = QPushButton("✅ 拾取 (E)")
        self.pickup_btn.setEnabled(False)
        self.pickup_btn.setStyleSheet("padding: 8px;")
        
        self.skill_btn = QPushButton("✨ 技能")
        self.skill_btn.setStyleSheet("padding: 8px;")
        
        # 战斗专用按钮（初始隐藏）
        self.combat_frame = QFrame()
        self.combat_frame.setStyleSheet("background-color: #3a2a2a; border-radius: 8px; border: 1px solid #662222;")
        self.combat_frame.setVisible(False)
        combat_layout = QVBoxLayout(self.combat_frame)
        combat_layout.setContentsMargins(10, 10, 10, 10)
        combat_layout.setSpacing(8)
        
        combat_title = QLabel("战斗选项")
        combat_title.setStyleSheet("font-weight: bold; color: #ff9999;")
        combat_layout.addWidget(combat_title)
        
        combat_btn_layout = QGridLayout()
        self.attack_btn = QPushButton("⚔️ 攻击")
        self.item_btn = QPushButton("🧪 道具")
        self.flee_btn = QPushButton("🏃 逃跑")
        
        combat_btn_layout.addWidget(self.attack_btn, 0, 0, 1, 2)
        combat_btn_layout.addWidget(self.item_btn, 1, 0)
        combat_btn_layout.addWidget(self.flee_btn, 1, 1)
        combat_layout.addLayout(combat_btn_layout)
        
        # 敌人UI（初始隐藏）
        self.enemy_ui = EnemyUI()
        self.enemy_ui.setVisible(False)
        
        # 添加到交互区域
        action_layout.addWidget(self.inventory_btn)
        action_layout.addWidget(self.pickup_btn)
        action_layout.addWidget(self.skill_btn)
        action_layout.addWidget(self.combat_frame)
        action_layout.addWidget(self.enemy_ui)
        
        # --- 小地图区域 ---
        minimap_frame = QFrame()
        minimap_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 8px; border: 1px solid #444;")
        minimap_layout = QVBoxLayout(minimap_frame)
        minimap_layout.setContentsMargins(10, 10, 10, 10)
        minimap_layout.setSpacing(8)
        
        minimap_label = QLabel("🗺️ 小地图")
        minimap_label.setStyleSheet("font-weight: bold;")
        
        self.minimap = MinimapWidget(self.game_map)
        self.minimap.setMinimumHeight(250)
        
        minimap_layout.addWidget(minimap_label)
        minimap_layout.addWidget(self.minimap)
        
        # --- 提示区域 ---
        hint_frame = QFrame()
        hint_frame.setStyleSheet("background-color: #262626; border-radius: 8px; border: 1px solid #444;")
        hint_layout = QVBoxLayout(hint_frame)
        hint_layout.setContentsMargins(10, 10, 10, 10)
        
        self.move_hint = QLabel("移动：WASD | 视角：IJKL")
        self.move_hint.setStyleSheet("font-size: 12px; color: #aaa;")
        self.move_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        hint_layout.addWidget(self.move_hint)
        
        # 添加所有区域到右侧面板
        right_layout.addWidget(status_frame)
        right_layout.addWidget(action_frame)
        right_layout.addWidget(minimap_frame)
        right_layout.addWidget(hint_frame)
        right_layout.addStretch()
        
        # 添加到主布局
        main_layout.addWidget(self.fp_view, 5)
        main_layout.addWidget(right_panel, 1)
        
        # 信号连接
        self.inventory_btn.clicked.connect(self.open_inventory)
        self.pickup_btn.clicked.connect(self.pickup_item)
        self.skill_btn.clicked.connect(self.open_skill_menu)
        self.attack_btn.clicked.connect(self.player_attack)
        self.item_btn.clicked.connect(self.show_item_selection)
        self.flee_btn.clicked.connect(self.flee_battle)

        # 设置定时器
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.process_movement)
        self.move_timer.start(33)  # 30FPS

        self.update_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

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

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        
        # 战斗中禁用移动和视角
        if self.in_battle:
            if key == Qt.Key.Key_Escape:
                self.close()
            return
        
        # 开发者模式快捷键
        if DEV_MODE_ENABLED and key == Qt.Key.Key_F1:
            if self.cheat_menu:
                self.cheat_menu.setVisible(not self.cheat_menu.isVisible())
                if self.cheat_menu.isVisible():
                    self.cheat_menu.position_at_center()
            event.accept()
            return
        
        # 移动控制（WASD只移动，不改变视角方向）
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
            self.set_view_direction_immediate(0)  # 北
            event.accept()
            return
        elif key == Qt.Key.Key_J:
            self.set_view_direction_immediate(270)  # 西
            event.accept()
            return
        elif key == Qt.Key.Key_K:
            self.set_view_direction_immediate(180)  # 南
            event.accept()
            return
        elif key == Qt.Key.Key_L:
            self.set_view_direction_immediate(90)  # 东
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
            # 退出作弊菜单
            if self.cheat_menu and self.cheat_menu.isVisible():
                self.cheat_menu.setVisible(False)
            else:
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
        """处理WASD移动逻辑（基于小地图方向）"""
        if self.in_battle:
            return
            
        current_time = QTime.currentTime().msecsSinceStartOfDay()
        if current_time - self.last_move_time < self.move_cooldown:
            return
            
        dx, dy = 0, 0
        
        # 基于小地图方向移动（上=W，下=S，左=A，右=D）
        if self.keys_pressed['w']:
            dy -= self.move_speed
        if self.keys_pressed['s']:
            dy += self.move_speed
        if self.keys_pressed['a']:
            dx -= self.move_speed
        if self.keys_pressed['d']:
            dx += self.move_speed
        
        # 归一化
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx / length * self.move_speed
            dy = dy / length * self.move_speed
        
        # 执行移动
        if dx != 0 or dy != 0:
            if self.game_map.move_player(dx, dy):
                self.check_pickup_available()
                self.update_ui()  # 确保更新UI和视图
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
            self.player_dir = 0
            self.fp_view.player_dir = 0
            
            # 清除临时效果
            self.player.clear_temp_effects()
            
            self.update_ui()

    def update_ui(self):
        self.hp_label.setText(f"❤️ HP: {self.player.hp}/{self.player.max_hp}")
        self.mp_label.setText(f"💙 MP: {self.player.mp}/{self.player.max_mp}")
        self.minimap.render()

        if not self.in_battle:
            x, y = int(self.game_map.player_x), int(self.game_map.player_y)
            enemy_spot = self.game_map.get_enemy_at(x, y)
            if enemy_spot:
                self.start_battle(enemy_spot.enemy_type)
        else:
            self.fp_view.scene().clear()
            self.fp_view.scene().addText(f"⚔️ 与 {self.current_enemy.name} 战斗中！", QFont("Arial", 20))
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

    def update_move_buttons(self):
        """动态更新UI可见性"""
        if self.in_battle:
            self.combat_frame.setVisible(True)
            self.enemy_ui.setVisible(True)
            self.pickup_btn.setVisible(False)
            self.move_hint.setVisible(False)
        else:
            self.combat_frame.setVisible(False)
            self.enemy_ui.setVisible(False)
            self.pickup_btn.setVisible(True)
            self.move_hint.setVisible(True)

    def start_battle(self, enemy_type):
        self.in_battle = True
        # 根据类型获取敌人
        self.current_enemy = create_monster(enemy_type)
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
        self.current_enemy.hp -= dmg
        return f"造成 {dmg} 伤害！"

    def _perform_action(self, name, action_func):
        if not self.in_battle or not self.current_enemy.is_alive():
            return
        msg = action_func()
        self.log_message(msg)
        self.update_ui()
        if not self.current_enemy.is_alive():
            self.end_battle(victory=True)
            return
        self.enemy_turn()

    def enemy_turn(self):
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
            
            if not self.player.is_alive() and not self.god_mode:
                self.end_battle(victory=False)

    def flee_battle(self):
        if random.random() < 0.7:
            self.log_message("你成功逃跑了！")
            self.end_battle(victory=None)
        else:
            self.log_message("逃跑失败！")
            self.enemy_turn()

    def end_battle(self, victory):
        self.in_battle = False
        self.update_ui()
        
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
            x, y = int(self.game_map.player_x), int(self.game_map.player_y)
            self.game_map.defeat_enemy(x, y)
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
        
        if self.current_enemy and not self.current_enemy.is_alive():
            self.end_battle(victory=True)
            return
            
        if self.in_battle:
            self.enemy_turn()

    def log_message(self, msg):
        """显示消息提示"""
        # 确保msg是字符串类型
        if not isinstance(msg, str):
            msg = str(msg)
        QMessageBox.information(self, "提示", msg)