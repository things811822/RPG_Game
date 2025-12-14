# RPG冒险游戏 - PyQt6 伪3D RPG游戏

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=flat&logo=github)](https://github.com/things811822/RPG_Game)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x+-green?style=flat&logo=qt)

## 简介

这是一款基于PyQt6开发的3D RPG冒险游戏，采用伪3D第一人称视角，拥有完整的迷宫探索、战斗系统、技能系统和道具系统。游戏采用房间式地图生成算法，确保100%连通且无死路，并支持开发者模式（作弊功能）。

## 游戏特色

- **第一人称3D视角**：伪3D渲染，沉浸式迷宫探索体验
- **房间式迷宫**：智能生成的房间和走廊，100%连通
- **完整战斗系统**：回合制战斗，支持普通攻击、技能使用和道具
- **技能与道具系统**：可自定义技能效果和道具效果
- **Boss挑战**：每5关出现一个强力Boss
- **小地图系统**：实时显示玩家位置和敌人/道具分布
- **开发者模式**：按F1键开启作弊菜单（需在源码中启用）

## 安装指南

### 方法一：直接运行（推荐开发环境）

1. 克隆仓库：

```bash
git clone https://github.com/things811822/RPG_Game.git
cd RPG_Game
```

2. 创建虚拟环境（可选但推荐）：

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 运行游戏：

```bash
python src/main.py
```

### 方法二：使用预编译exe（推荐普通用户）

从[Releases页面](https://github.com/things811822/RPG_Game/releases)下载最新版本的exe文件直接运行。

## 游戏控制

| 按键 | 功能 |
|------|------|
| `W` | 向前移动 |
| `A` | 向左移动 |
| `S` | 向后移动 |
| `D` | 向右移动 |
| `I` | 视角转向北方（上） |
| `J` | 视角转向西方（左） |
| `K` | 视角转向南方（下） |
| `L` | 视角转向东方（右） |
| `E` | 拾取物品/进入下一关 |
| `ESC` | 退出游戏 |
| `F1` | （开发者模式启用后）打开作弊菜单 |

## 游戏界面


1. **第一人称视图**：显示当前视角的游戏世界
2. **状态区域**：显示当前关卡和玩家HP/MP
3. **交互按钮**：
   - **背包**：查看和使用道具
   - **拾取**：拾取当前位置的道具
   - **技能**：查看和使用技能
   - **攻击/道具/逃跑**：战斗选项
4. **小地图**：显示玩家当前位置、敌人、道具和出口
5. **提示区域**：显示操作提示

## 开发者设置

要启用开发者模式：

1. 打开文件 `src/game.py`
2. 找到以下行：

   ```python
   DEV_MODE_ENABLED = False  # 将此设置为 True 以启用开发者模式
   ```

3. 将 `False` 改为 `True`
4. 保存并重新运行游戏

启用后，按F1键即可打开作弊菜单，提供以下功能：

- 一键跳关
- 清空敌人
- 完全恢复
- 最大MP
- 添加道具
- 无限技能
- 传送地图
- 添加Boss
- 无敌模式

## 贡献指南

欢迎大家贡献代码！请遵循以下流程：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交代码 (`git commit -am 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

## 许可证

本项目采用 [MIT许可证](LICENSE) - 详情请见LICENSE文件。

## 鸣谢

- **PyQt6** - 用于GUI开发
- **PyInstaller** - 用于打包成exe
- **PyArmor** - 用于源码保护（可选）

---

> **注意**: 为了更好的游戏体验，建议使用1920x1080或更高分辨率的显示器运行本游戏。
