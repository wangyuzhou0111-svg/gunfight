# Repository Guidelines

## 项目结构与模块组织
当前仓库是 `pygame` 项目，已采用以下结构：
- `src/main.py`：游戏入口。
- `src/game/`：核心逻辑模块（如 `player.py`、`enemy.py`、`ui.py`）。
- `assets/images/`：图片资源。
- `tests/`：自动化测试。

在未完成迁移前，可继续运行现有结构，但新文件优先按上面目录放置。

## 文件命名与文件位置优化
统一使用小写英文文件名，避免空格和中文文件名，减少跨平台路径问题。
已完成映射（历史名称 -> 当前名称）：
- `尚尸.py` -> `src/main.py`
- `主人物.png` -> `assets/images/player_main.png`
- `普通敌人.png` -> `assets/images/enemy_basic.png`
- `装甲车.png` -> `assets/images/armored_vehicle.png`
- `地图 1.png` -> `assets/images/map_01.png`

命名规则：
- Python 文件：`snake_case.py`
- 资源文件：`类别_用途_序号`（如 `map_floor_01.png`）
- 禁止同义重复命名（如 `enemy.png`、`enemy_new.png`）

## 构建、测试与开发命令
建议使用 Python 3.11+。
- `python3 -m pip install pygame`：安装依赖。
- `python3 src/main.py`
- `python3 -m py_compile src/main.py`：语法检查。

## 代码风格与命名规范
- 遵循 PEP 8，4 空格缩进。
- 函数/变量用 `snake_case`，类名用 `PascalCase`，常量用 `UPPER_SNAKE_CASE`。
- 重复逻辑抽函数，避免超长函数继续膨胀。

可用时执行：
- `python3 -m black src/`
- `python3 -m ruff check src/`

## 测试指南
当前以手工验证为主：移动、射击、切图、UI、资源加载失败回退。
新增自动化测试时使用 `pytest`，命名 `tests/test_*.py`。

## 提交与 PR 规范
- 提交格式：`type(scope): summary`，如 `refactor(assets): rename image files`。
- 每次提交只做一类改动（代码、资源、重构分开提交）。
- PR 必含：变更说明、验证步骤、界面改动截图/录屏、关联 issue。

## 资源与配置说明
- 统一使用项目相对路径或基于 `__file__` 的路径。
- 新增资源必须放入 `assets/images/`，禁止散落在仓库根目录。
