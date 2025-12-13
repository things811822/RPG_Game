import sys
import random
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QGridLayout, QSizePolicy,
    QFrame, QSpacerItem, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QKeyEvent, QFont, QColor, QLinearGradient, QPalette, QBrush

from .player import Player
from .map import GameMap, EnemySpot, ItemSpot
from .battle import Enemy
from .ui.first_person_view import FirstPersonView
from .ui.minimap_widget import MinimapWidget
from .ui.enemy_ui import EnemyUI
from .ui.inventory_dialog import InventoryDialog
from .systems.skills import Skill
from .systems.items import Item

class RPGGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 RPG 冒险 - 小键盘直接渲染")
        self.resize(1400, 800)
        
        # 设置深色主题
        self.set_dark_theme()
        
        # 主要游戏对象
        self.player = Player()
        self.game_map = GameMap()
        self.current_level = 1
        self.in_battle = False
        self.current_enemy = None
        
        # 控制相关
        self.keys_pressed = {'w': False, 'a': False, 's': False, 'd': False}
        self.move_speed = 0.1
        self.last_move_time = 0
        self.move_cooldown = 100
        self.player_dir = 0  # 0: North, 90: East, 180: South, 270: West
        
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
        self.skill1_btn = QPushButton()
        self.skill2_btn = QPushButton()
        
        combat_btn_layout.addWidget(self.attack_btn, 0, 0)
        combat_btn_layout.addWidget(self.item_btn, 0, 1)
        combat_btn_layout.addWidget(self.flee_btn, 1, 0, 1, 2)
        combat_btn_layout.addWidget(self.skill1_btn, 2, 0)
        combat_btn_layout.addWidget(self.skill2_btn, 2, 1)
        combat_layout.addLayout(combat_btn_layout)
        
        # 敌人UI（初始隐藏）
        self.enemy_ui = EnemyUI()
        self.enemy_ui.setVisible(False)
        
        # 添加到交互区域
        action_layout.addWidget(self.inventory_btn)
        action_layout.addWidget(self.pickup_btn)
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
        
        self.move_hint = QLabel("移动：WASD | 视角：小键盘方向键")
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
        self.attack_btn.clicked.connect(self.player_attack)
        self.item_btn.clicked.connect(self.show_item_selection)
        self.flee_btn.clicked.connect(self.flee_battle)
        self.skill1_btn.clicked.connect(lambda: self.use_skill(0))
        self.skill2_btn.clicked.connect(lambda: self.use_skill(1))

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

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        
        # 战斗中禁用移动和视角
        if self.in_battle:
            if key == Qt.Key.Key_Escape:
                self.close()
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
        
        # 视角控制（小键盘方向键）- 直接重新渲染
        elif key == Qt.Key.Key_Up:
            self.set_view_direction_immediate(0)  # 北
            event.accept()
            return
        elif key == Qt.Key.Key_Right:
            self.set_view_direction_immediate(90)  # 东
            event.accept()
            return
        elif key == Qt.Key.Key_Down:
            self.set_view_direction_immediate(180)  # 南
            event.accept()
            return
        elif key == Qt.Key.Key_Left:
            self.set_view_direction_immediate(270)  # 西
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
        """处理WASD移动逻辑"""
        if self.in_battle:
            return
            
        current_time = QTime.currentTime().msecsSinceStartOfDay()
        if current_time - self.last_move_time < self.move_cooldown:
            return
            
        dx, dy = 0, 0
        rad = math.radians(self.player_dir)
        
        # 根据当前视角方向移动（不改变视角方向）
        if self.keys_pressed['w']:
            dx += math.sin(rad)
            dy += math.cos(rad)
        if self.keys_pressed['d']:
            dx += math.cos(rad)
            dy -= math.sin(rad)
        if self.keys_pressed['s']:
            dx -= math.sin(rad)
            dy -= math.cos(rad)
        if self.keys_pressed['a']:
            dx -= math.cos(rad)
            dy += math.sin(rad)
        
        # 归一化
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx / length * self.move_speed
            dy = dy / length * self.move_speed
        
        # 执行移动（不改变视角方向）
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
            if any(e.active for e in self.game_map.enemies):
                self.log_message("还有敌人未被击败！请清除所有敌人再进入下一关。")
                return
                
            self.current_level += 1
            QMessageBox.information(self, "关卡完成", f"你完成了第 {self.current_level - 1} 关！\n进入第 {self.current_level} 关……")
            self.game_map = GameMap()
            self.fp_view.game_map = self.game_map
            self.minimap.game_map = self.game_map
            self.level_label.setText(f"关卡：{self.current_level}")
            self.player_dir = 0
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
                self.start_battle(enemy_spot.enemy_type)
        else:
            self.fp_view.scene().clear()
            self.fp_view.scene().addText(f"⚔️ 与 {self.current_enemy.name} 战斗中！", QFont("Arial", 20))

        self.update_skill_buttons()
        self.update_move_buttons()
        
        # 确保第一人称视图更新
        if not self.in_battle:
            self.fp_view.render_view()

    def update_skill_buttons(self):
        skills = self.player.skills
        if len(skills) > 0:
            s1 = skills[0]
            self.skill1_btn.setText(f"✨ {s1.name} (MP:{s1.mp_cost})")
            self.skill1_btn.setEnabled(s1.can_use(self.player))
        else:
            self.skill1_btn.hide()
        if len(skills) > 1:
            s2 = skills[1]
            self.skill2_btn.setText(f"✨ {s2.name} (MP:{s2.mp_cost})")
            self.skill2_btn.setEnabled(s2.can_use(self.player))
        else:
            self.skill2_btn.hide()

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
        enemy_data = {
            "goblin": ("哥布林", 30, 8, 2),
            "skeleton": ("骷髅兵", 40, 12, 3),
            "spider": ("巨蜘蛛", 50, 15, 1),
            "orc": ("兽人", 60, 18, 4)
        }
        name, hp, atk, df = enemy_data[enemy_type]
        self.current_enemy = Enemy(name, hp, atk, df)
        self.enemy_ui.update_enemy(name, hp, hp)
        self.update_ui()

    def player_attack(self):
        self._perform_action("普通攻击", lambda: self._damage_enemy(self.player.attack))

    def use_skill(self, idx):
        if idx >= len(self.player.skills):
            return
        skill = self.player.skills[idx]
        if not skill.can_use(self.player):
            self.log_message("魔法值不足！")
            return
        msg = skill.use(self.player, self.current_enemy)
        self.log_message(msg)
        self.update_enemy_ui()
        if not self.current_enemy.is_alive():
            self.end_battle(victory=True)
            return
        self.enemy_turn()

    def show_item_selection(self):
        """显示道具选择对话框"""
        if not self.player.inventory:
            self.log_message("背包为空！")
            return
            
        dialog = InventoryDialog(self.player.inventory, self)
        if dialog.exec():
            selected_item = dialog.selected_item
            if selected_item:
                self.use_selected_item(selected_item)

    def use_selected_item(self, item):
        """使用选中的道具"""
        if self.in_battle and item in self.player.inventory:
            self.player.use_item(item)
            self.log_message(f"使用了 {item.name}！")
            self.enemy_turn()
        elif not self.in_battle and item in self.player.inventory:
            self.player.use_item(item)
            self.log_message(f"使用了 {item.name}！")
            self.update_ui()

    def _damage_enemy(self, dmg):
        self.current_enemy.hp -= dmg
        return f"造成 {dmg} 伤害！"

    def _perform_action(self, name, action_func):
        if not self.in_battle or not self.current_enemy.is_alive():
            return
        msg = action_func()
        self.log_message(msg)
        self.update_enemy_ui()
        if not self.current_enemy.is_alive():
            self.end_battle(victory=True)
            return
        self.enemy_turn()

    def update_enemy_ui(self):
        if self.current_enemy:
            self.enemy_ui.update_enemy(
                self.current_enemy.name,
                self.current_enemy.hp,
                self.current_enemy.max_hp
            )

    def enemy_turn(self):
        if not self.current_enemy or not self.current_enemy.is_alive():
            return

        if self.player.is_alive():
            dmg = self.current_enemy.attack
            self.player.hp -= dmg
            self.log_message(f"{self.current_enemy.name} 造成 {dmg} 伤害！")
            self.update_ui()
            if not self.player.is_alive():
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
            self.player.hp = min(self.player.max_hp, self.player.hp + 10)
            self.log_message("战斗胜利！获得 10 HP 恢复。")
            x, y = int(self.game_map.player_x), int(self.game_map.player_y)
            self.game_map.defeat_enemy(x, y)
            self.update_ui()
        elif victory is False:
            QMessageBox.critical(self, "Game Over", "你倒下了……\n游戏结束！")
            sys.exit()

    def open_inventory(self):
        """打开背包查看所有道具"""
        if not self.player.inventory:
            self.log_message("背包为空！")
            return
            
        dialog = InventoryDialog(self.player.inventory, self)
        dialog.exec()

    def log_message(self, msg):
        QMessageBox.information(self, "提示", msg)