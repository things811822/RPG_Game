from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QLinearGradient, QPainterPath, QColor, QBrush, QPen, QFont, QKeyEvent
import math
import sys

class FirstPersonView(QGraphicsView):
    def __init__(self, game_map, parent=None):
        super().__init__(parent)
        self.game_map = game_map
        self.setScene(QGraphicsScene())
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background:black;")
        self.setFixedSize(800, 600)
        
        # 视角相关
        self.player_dir = 0  # 0: North, 90: East, 180: South, 270: West
        
        # 添加出口提示
        self.show_exit_prompt = False
        
        # 设置窗口焦点
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 立即渲染初始视图
        if self.game_map is not None:
            self.render_view()

    def render_view(self):
        """渲染第一人称视角"""
        if self.game_map is None:
            return
            
        try:
            # 记录当前焦点项
            current_focus = self.scene().focusItem()
            
            # 清空场景
            self.scene().clear()
            
            # 获取玩家位置
            px, py = self.game_map.player_x, self.game_map.player_y
            
            # 检查玩家位置有效性
            if px < 0 or py < 0 or px >= self.game_map.size or py >= self.game_map.size:
                px, py = 1, 1
            
            # 天空盒 - 渐变蓝色
            sky_gradient = QLinearGradient(0, 0, 0, 300)
            sky_gradient.setColorAt(0, QColor(20, 20, 100))
            sky_gradient.setColorAt(1, QColor(60, 60, 180))
            self.scene().addRect(0, 0, 800, 300, QPen(Qt.GlobalColor.darkBlue), QBrush(sky_gradient))

            # 地面 - 草地
            ground_brush = QBrush(QColor(0, 80, 0))
            self.scene().addRect(0, 500, 800, 100, QPen(Qt.GlobalColor.darkGreen), ground_brush)

            # 伪3D墙壁渲染
            num_rays = 120  # 射线数量
            for i in range(num_rays):
                # 计算射线角度 (视野范围60度)
                ray_angle = math.radians(self.player_dir + 30 * (i / num_rays - 0.5))
                sin_a = math.sin(ray_angle)
                cos_a = math.cos(ray_angle)
                
                # 检测墙壁
                wall_hit = self.cast_ray(px, py, sin_a, cos_a)
                
                if wall_hit:
                    x, y, dist, wall_type = wall_hit
                    
                    # 透视投影计算
                    wall_height = min(800, 400 / max(0.1, dist))
                    wall_top = 300 - wall_height / 2
                    wall_width = 800 / num_rays
                    wall_x = i * wall_width
                    
                    # 根据距离和类型调整颜色
                    if wall_type == "vertical":
                        base_color = QColor(100, 100, 100)
                        texture_offset = x
                    else:  # horizontal
                        base_color = QColor(120, 120, 120)
                        texture_offset = y
                    
                    # 根据距离调整亮度
                    brightness_factor = max(0.3, 1 - dist / 10)
                    r = int(base_color.red() * brightness_factor)
                    g = int(base_color.green() * brightness_factor)
                    b = int(base_color.blue() * brightness_factor)
                    wall_color = QColor(r, g, b)
                    
                    # 绘制墙壁
                    self.draw_wall_trapezoid(wall_x, wall_top, wall_width, wall_height, wall_color, wall_type, texture_offset)
            
            # 检查是否靠近出口
            self.show_exit_prompt = False
            exit_x, exit_y = self.game_map.exit_point
            dist_to_exit = math.sqrt((px - exit_x)**2 + (py - exit_y)**2)
            
            if dist_to_exit < 1.5:
                self.show_exit_prompt = True
                prompt_text = self.scene().addText("🚪 按 E 进入下一关", QFont("Microsoft YaHei", 24))
                prompt_text.setDefaultTextColor(QColor(255, 255, 100))
                prompt_text.setPos(250, 400)
            
            # 恢复焦点
            if current_focus:
                current_focus.setFocus()
                
        except Exception as e:
            print(f"渲染视图出错: {e}")
            # 添加错误提示
            error_text = self.scene().addText(f"渲染错误: {str(e)}", QFont("Arial", 16))
            error_text.setDefaultTextColor(QColor(255, 100, 100))
            error_text.setPos(200, 300)
    
    def cast_ray(self, px, py, sin_a, cos_a):
        """投射射线并返回与墙壁的交点"""
        try:
            step = 0.1
            max_dist = 10
            dist = step
            
            while dist <= max_dist:
                # 计算射线上的点
                x = px + dist * cos_a
                y = py + dist * sin_a
                
                # 检查是否击中墙壁
                if self.game_map.is_wall(int(x), int(y)):
                    wall_type = "vertical" if abs(cos_a) > abs(sin_a) else "horizontal"
                    return (x, y, dist, wall_type)
                
                dist += step
            
            return None
        except Exception as e:
            print(f"射线投射错误: {e}")
            return None

    def draw_wall_trapezoid(self, x, y, width, height, color, wall_type, texture_offset):
        """绘制梯形墙壁（模拟透视效果）"""
        try:
            # 顶部宽度
            if height > 400:
                top_width = width * 0.5
            elif height > 200:
                top_width = width * 0.7
            else:
                top_width = width * 0.9
            
            # 创建梯形路径
            path = QPainterPath()
            path.moveTo(x + (width - top_width) / 2, y)
            path.lineTo(x + (width + top_width) / 2, y)
            path.lineTo(x + width, y + height)
            path.lineTo(x, y + height)
            path.closeSubpath()
            
            # 绘制墙壁
            self.scene().addPath(path, QPen(color.darker(150)), QBrush(color))
            
            # 添加砖墙纹理
            if height > 30:
                brick_height = 8
                num_bricks = max(1, int(height / brick_height))
                
                for i in range(num_bricks):
                    brick_y = y + i * brick_height
                    offset = 0 if (i + int(texture_offset * 2)) % 2 == 0 else width * 0.25
                    
                    if i > 0:
                        self.scene().addLine(x, brick_y, x + width, brick_y, QPen(QColor(50, 50, 50), 0.5))
                    
                    for j in range(1, int(width / 15) + 1):
                        brick_x = x + j * 15 + offset
                        if brick_x <= x + width:
                            self.scene().addLine(brick_x, brick_y, brick_x, brick_y + brick_height, QPen(QColor(50, 50, 50), 0.3))
        except Exception as e:
            print(f"绘制墙壁错误: {e}")