import pygame
import random
import math
import sys
import os

def main():
    random.seed(42) # 固定随机种子，确保障碍物位置固定
    """初始化并显示一个 pygame 屏幕"""
    # 初始化 pygame
    pygame.init()
    pygame.key.stop_text_input() # 屏蔽输入法
    
    # 初始化路径
    # 获取脚本所在目录的绝对路径
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except:
        script_dir = os.getcwd()
    project_dir = os.path.dirname(script_dir)
    assets_images_dir = os.path.join(project_dir, "assets", "images")
    assets_fonts_dir = os.path.join(project_dir, "assets", "fonts")

    def resolve_asset(filename):
        """按新目录优先、旧目录兼容的顺序解析资源路径。"""
        candidates = [
            os.path.join(assets_images_dir, filename),
            os.path.join(project_dir, filename),
            os.path.join(script_dir, filename),
            os.path.join(os.getcwd(), filename),
            filename
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    # 初始化中文字体 - 使用项目目录中的 STHeiti Light.ttc
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(assets_fonts_dir, "STHeiti Light.ttc"),
        os.path.join(project_dir, "STHeiti Light.ttc"),
        os.path.join(script_dir, "STHeiti Light.ttc"),
        os.path.join(os.getcwd(), "STHeiti Light.ttc"),
        "STHeiti Light.ttc"
    ]
    
    heiti_font_path = None
    heiti_font_loaded = False
    
    # 查找字体文件
    for path in possible_paths:
        if os.path.exists(path):
            heiti_font_path = path
            break
    
    # 预加载字体文件，确保可以正常使用
    if heiti_font_path:
        try:
            # 测试加载字体
            test_font = pygame.font.Font(heiti_font_path, 20)
            test_surface = test_font.render("测试", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                heiti_font_loaded = True
                print(f"✓ 成功加载字体文件: {heiti_font_path}")
            else:
                print(f"✗ 字体文件加载成功但无法显示中文: {heiti_font_path}")
        except Exception as e:
            print(f"✗ 无法加载字体文件 {heiti_font_path}: {e}")
    else:
        print(f"✗ 未找到字体文件 STHeiti Light.ttc")
        print(f"  当前工作目录: {os.getcwd()}")
        print(f"  项目目录: {project_dir}")
        print(f"  脚本目录: {script_dir}")
        print(f"  尝试的路径: {possible_paths}")
    
    def get_chinese_font(size):
        """获取中文字体，优先使用项目目录中的 STHeiti Light.ttc"""
        # 优先使用项目目录中的 STHeiti Light.ttc 字体文件
        if heiti_font_loaded and heiti_font_path:
            try:
                font = pygame.font.Font(heiti_font_path, size)
                # 再次测试是否能显示中文
                test = font.render("中", True, (255, 255, 255))
                if test.get_width() > 0:
                    return font
            except Exception as e:
                print(f"创建字体对象失败 (size={size}): {e}")
        
        # 备用方案：尝试使用系统字体 STHeiti Light
        try:
            font = pygame.font.SysFont("STHeiti Light", size)
            test_surface = font.render("测试", True, (255, 255, 255))
            if test_surface.get_width() > 0:
                print(f"使用系统字体 STHeiti Light (size={size})")
                return font
        except Exception as e:
            pass
        
        # 最后备用：尝试其他常见中文字体
        try:
            font_names = ["STHeiti", "PingFang SC", "STKaitiSC-Regular", "SimHei", "Microsoft YaHei", "SimSun", "KaiTi", "FangSong"]
            for font_name in font_names:
                try:
                    font = pygame.font.SysFont(font_name, size)
                    test_surface = font.render("测试", True, (255, 255, 255))
                    if test_surface.get_width() > 0:
                        print(f"使用备用字体 {font_name} (size={size})")
                        return font
                except:
                    continue
        except:
            pass
        
        # 如果都失败，使用默认字体（可能无法显示中文）
        print(f"⚠ 警告：使用默认字体 (size={size})，可能无法正确显示中文")
        return pygame.font.Font(None, size)

    
    # 设置屏幕尺寸
    screen_width = 800
    screen_height = 600
    
    # 设置地图尺寸
    WORLD_BASE = 4000
    world_width = WORLD_BASE
    world_height = WORLD_BASE

    map_level = 1 # 新增：当前地图级别，1为初始地图
    max_map_level = 8  # 当前关卡组的最大地图数（关卡1对应地图1-8）
    min_map_level = 1  # 当前关卡组的最小地图数（关卡1对应地图1-3）
    current_stage = 1  # 当前选择的关卡（1-10）

    moshi = 0  # 0: 主页面, 1: 游戏模式, 2: 关卡选择页面, 3: 目录
    max_level = 10  # 最大关卡数
    tutorial_step = 0  # 教程步骤：0=未开始, 1=移动, 2=冲刺, 3=射击, 4=右键开镜, 5=换弹, 6=打开地图, 7=医疗包, 8=完成
    tutorial_completed = {
        'move': False,
        'sprint': False,
        'shoot': False,
        'aim': False,
        'reload': False,
        'map': False,
        'medkit': False
    }  # 跟踪教程完成情况
    
    # 任务系统
    current_task = None  # 当前任务：None=无任务, "kill_enemy_above"=击杀上方敌人
    task_target_enemy = None  # 任务目标敌人
    task_completed = False  # 任务是否完成
    task_completed_time = 0  # 任务完成时间（用于显示完成提示）
    
    # 创建屏幕
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # 设置窗口标题
    pygame.display.set_caption("枪战游戏 - 镜头跟随")
    
    # 设置背景颜色
    background_color = (0, 0, 0)  # 黑色

    # 主页面背景（纯色，去掉草坪图）
    menu_image = pygame.Surface((screen_width, screen_height))
    menu_image.fill((18, 22, 28))
    
    # 加载玩家图像
    try:
        player_image = pygame.image.load(resolve_asset("player_main.png")).convert_alpha()
        player_image = pygame.transform.scale(player_image, (78, 100))
    except (pygame.error, FileNotFoundError):
        print("无法加载玩家图片，尝试加载法.png")
        try:
            player_image = pygame.image.load(resolve_asset("法.png"))
            player_image = pygame.transform.scale(player_image, (50, 50))
        except (pygame.error, FileNotFoundError):
            print("无法加载法.png，使用默认方块代替")
            player_image = pygame.Surface((50, 50))
            player_image.fill((255, 0, 0))  # 红色方块

    # 加载敌人图像
    try:
        enemy_image = pygame.image.load(resolve_asset("enemy_basic.png")).convert_alpha()
        enemy_image = pygame.transform.scale(enemy_image, (78, 100))
    except (pygame.error, FileNotFoundError):
        print("无法加载敌人图片，使用默认方块代替")
        enemy_image = pygame.Surface((50, 50))
        enemy_image.fill((0, 0, 255))  # 蓝色方块
    
    # 加载高级敌人图像（使用敌人图片 + 红色色调区分，不影响透明度）
    elite_enemy_image = enemy_image.copy()
    red_tint = pygame.Surface(elite_enemy_image.get_size())
    red_tint.fill((80, 0, 0))  # 叠加红色
    elite_enemy_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    # 僵尸图像：敌人底图叠加绿色
    zombie_image = enemy_image.copy()
    green_tint = pygame.Surface(zombie_image.get_size())
    green_tint.fill((0, 90, 0))
    zombie_image.blit(green_tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    
    # 加载Boss坦克图像 (tank_blue.png)
    try:
        boss_tank_image = pygame.image.load(resolve_asset("tank_blue.png"))
        boss_tank_image = pygame.transform.scale(boss_tank_image, (100, 100))  # 玩家2倍大小
    except (pygame.error, FileNotFoundError):
        print("无法加载tank_blue.png，使用默认方块代替")
        boss_tank_image = pygame.Surface((100, 100))
        boss_tank_image.fill((0, 0, 255))  # 蓝色方块

    # 加载子弹图像 (background.png)
    bullet_image = pygame.Surface((10, 5))
    bullet_image.fill((255, 255, 0)) # 黄色方块
    
    # 加载医疗包图像 (background.png)
    try:
        medkit_image = pygame.image.load(resolve_asset("background.png"))
        medkit_image = pygame.transform.scale(medkit_image, (10 , 20))
    except (pygame.error, FileNotFoundError):
        print("无法加载background.png，使用默认方块代替")
        medkit_image = pygame.Surface((20, 20))
        medkit_image.fill((0, 255, 0))  # 绿色方块
    
    # 加载弹药箱图像 (explosion.png)
    try:
        ammo_box_image = pygame.image.load(resolve_asset("explosion.png"))
        ammo_box_image = pygame.transform.scale(ammo_box_image, (30, 30))
    except (pygame.error, FileNotFoundError):
        print("无法加载explosion.png，使用默认方块代替")
        ammo_box_image = pygame.Surface((30, 30))
        ammo_box_image.fill((255, 165, 0))  # 橙色方块
    
    # 加载准心图像
    try:
        crosshair_image = pygame.image.load(resolve_asset("准心.png")).convert_alpha()
        crosshair_image = pygame.transform.scale(crosshair_image, (180, 180))
        # 将准心变成白色
        white_crosshair = crosshair_image.copy()
        for x in range(white_crosshair.get_width()):
            for y in range(white_crosshair.get_height()):
                r, g, b, a = white_crosshair.get_at((x, y))
                if a > 0:
                    white_crosshair.set_at((x, y), (255, 255, 255, a))
        crosshair_image = white_crosshair
    except (pygame.error, FileNotFoundError):
        print("无法加载准心图片，将使用默认十字准心")
        crosshair_image = None

    # 加载装甲车图像（过场动画用，已抠图）
    try:
        armored_vehicle_image = pygame.image.load(resolve_asset("armored_vehicle.png")).convert_alpha()
        armored_vehicle_image = pygame.transform.scale(armored_vehicle_image, (350, 350))
    except (pygame.error, FileNotFoundError):
        print("无法加载装甲车图片，使用默认方块代替")
        armored_vehicle_image = pygame.Surface((120, 240), pygame.SRCALPHA)
        armored_vehicle_image.fill((160, 140, 100))

    # 玩家初始位置及属性配置 (实例化在类定义之后)
    player_start_x = world_width // 2
    player_start_y = world_height // 2
    player_speed = 5
    sprint_speed = 10 # 新增：疾跑速度
    max_player_health = 100 # 玩家最大生命值
    max_armor = 200 # 玩家最大护甲值
    max_stamina = 100 # 体力系统

    # 子弹列表
    bullets = []
    bullet_speed = 20
    enemy_bullet_speed = 9 # 敌人子弹速度（提高，更难躲避）
    last_shot_time = 0
    shoot_cooldown = 100 # 0.1秒 (毫秒)
    
    # === 新功能变量 ===
    # 击杀计数与连杀系统
    kill_count = 0          # 总击杀数
    kill_streak = 0         # 当前连杀数
    last_kill_time = 0      # 上次击杀时间
    kill_streak_timeout = 4000  # 连杀超时（4秒内再次击杀算连杀）
    streak_message = ""     # 连杀提示文字
    streak_message_time = 0 # 连杀提示显示时间
    streak_message_color = (255, 255, 255)  # 连杀提示颜色
    
    # 伤害飘字列表
    damage_numbers = []  # [(x, y, damage, creation_time, color, is_crit)]
    
    # 屏幕震动
    screen_shake_intensity = 0   # 震动强度
    screen_shake_duration = 0    # 震动持续时间
    screen_shake_start = 0       # 震动开始时间
    
    # 手雷列表
    grenades_in_air = []  # 飞行中的手雷
    grenade_cooldown = 500  # 手雷投掷冷却（毫秒）
    last_grenade_time = 0   # 上次投掷手雷时间
    
    # 闪避翻滚
    dodge_rolling = False
    dodge_roll_speed = 18      # 翻滚速度
    dodge_roll_duration = 200  # 翻滚持续时间（毫秒）
    dodge_roll_cooldown = 800  # 翻滚冷却（毫秒）
    dodge_roll_start = 0       # 翻滚开始时间
    last_dodge_roll_time = 0   # 上次翻滚时间
    dodge_roll_dx = 0          # 翻滚方向
    dodge_roll_dy = 0
    dodge_roll_invincible = True  # 翻滚时无敌
    
    # 敌人血量显示开关
    show_enemy_health = False  # 按7切换
    left_mouse_down = False # 新增：跟踪鼠标左键是否按下
    infinite_ammo = False  # 按L切换无限弹药

    # 定义 Obstacle 类
    class Obstacle(pygame.sprite.Sprite):
        """墙壁障碍物（灰色，雾效上方可见）"""
        def __init__(self, x, y, width, height, color=(128, 128, 128), outline=None, label=None):
            super().__init__()
            self.is_wall = True
            self.color = color
            self.outline = outline
            self.label = label
            self.image = pygame.Surface((width, height))
            self.image.fill(color)
            if outline:
                pygame.draw.rect(self.image, outline, (0, 0, width, height), 2)
            self.rect = self.image.get_rect(topleft=(x, y))
            
        def draw(self, surface, camera_x, camera_y):
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

    class Furniture(pygame.sprite.Sprite):
        """家具障碍物（蓝色，被雾效遮挡）"""
        BLUE = (50, 90, 180)
        BLUE_OL = (30, 60, 140)
        def __init__(self, x, y, width, height, *_args, **_kwargs):
            super().__init__()
            self.is_wall = False
            self.color = Furniture.BLUE
            self.image = pygame.Surface((width, height))
            self.image.fill(self.color)
            pygame.draw.rect(self.image, Furniture.BLUE_OL, (0, 0, width, height), 2)
            self.rect = self.image.get_rect(topleft=(x, y))
        def draw(self, surface, camera_x, camera_y):
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

    # 定义 Door 类（可交互的门，按 E 开关，带旋转动画）
    class Door(pygame.sprite.Sprite):
        def __init__(self, x, y, width, height, hinge='auto'):
            super().__init__()
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            self.is_open = False
            self.anim_progress = 0.0  # 0.0=完全关闭, 1.0=完全打开
            self.anim_speed = 0.05   # 每帧动画步进（约20帧=0.33秒开完）
            self.animating = False
            self.is_horizontal = (width >= height)
            # 铰链方向：left/right（横门）、top/bottom（竖门）
            if hinge == 'auto':
                self.hinge = 'left' if self.is_horizontal else 'top'
            else:
                self.hinge = hinge
            self.pair = None  # 配对门（双开门的另一扇）
            # 关闭状态：棕色实心门（SRCALPHA 旋转时背景透明）
            self.image_closed = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image_closed.fill((139, 69, 19, 255))
            pygame.draw.rect(self.image_closed, (101, 50, 14, 255), (0, 0, width, height), 3)
            # 打开状态：半透明
            self.image_open = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image_open.fill((139, 69, 19, 60))
            self.image = self.image_closed
            self.rect = self.image.get_rect(topleft=(x, y))

        def toggle(self):
            self.is_open = not self.is_open
            self.animating = True

        def update(self):
            """每帧调用，推进开门/关门动画"""
            if not self.animating:
                return
            if self.is_open:
                self.anim_progress = min(1.0, self.anim_progress + self.anim_speed)
                if self.anim_progress >= 1.0:
                    self.animating = False
            else:
                self.anim_progress = max(0.0, self.anim_progress - self.anim_speed)
                if self.anim_progress <= 0.0:
                    self.animating = False

        def _blit_rotated(self, surface, image, pivot_screen, origin_on_image, angle):
            """围绕铰链点旋转绘制门"""
            image_rect = image.get_rect(
                topleft=(pivot_screen[0] - origin_on_image[0],
                         pivot_screen[1] - origin_on_image[1])
            )
            offset = pygame.math.Vector2(pivot_screen) - pygame.math.Vector2(image_rect.center)
            rotated_offset = offset.rotate(-angle)
            rotated_center = (pivot_screen[0] - rotated_offset.x, pivot_screen[1] - rotated_offset.y)
            rotated_image = pygame.transform.rotate(image, angle)
            rotated_rect = rotated_image.get_rect(center=rotated_center)
            surface.blit(rotated_image, rotated_rect)

        def draw(self, surface, camera_x, camera_y):
            sx = self.rect.x - camera_x
            sy = self.rect.y - camera_y
            # 完全关闭：直接绘制
            if self.anim_progress <= 0.0:
                surface.blit(self.image_closed, (sx, sy))
                return
            # 完全打开时用半透明，动画中用实心
            use_image = self.image_open if self.anim_progress >= 1.0 else self.image_closed
            # 根据铰链方向决定旋转枢轴和角度方向
            if self.hinge == 'left':
                pivot = (sx, sy + self.height / 2)
                origin = (0, self.height / 2)
                angle = 90 * self.anim_progress
            elif self.hinge == 'right':
                pivot = (sx + self.width, sy + self.height / 2)
                origin = (self.width, self.height / 2)
                angle = -90 * self.anim_progress
            elif self.hinge == 'top':
                pivot = (sx + self.width / 2, sy)
                origin = (self.width / 2, 0)
                angle = 90 * self.anim_progress
            else:  # bottom
                pivot = (sx + self.width / 2, sy + self.height)
                origin = (self.width / 2, self.height)
                angle = -90 * self.anim_progress
            self._blit_rotated(surface, use_image, pivot, origin, angle)

    def rebuild_door_pairs(doors):
        """恢复门后重建双开门的配对关系"""
        for i, d1 in enumerate(doors):
            if d1.pair is not None:
                continue
            for j in range(i + 1, len(doors)):
                d2 = doors[j]
                if d2.pair is not None:
                    continue
                # 横向配对：left + right，同 y 同 height，x 相邻
                if d1.hinge == 'left' and d2.hinge == 'right' and d1.y == d2.y and d1.height == d2.height:
                    if d1.x + d1.width == d2.x:
                        d1.pair = d2
                        d2.pair = d1
                        break
                if d1.hinge == 'right' and d2.hinge == 'left' and d1.y == d2.y and d1.height == d2.height:
                    if d2.x + d2.width == d1.x:
                        d1.pair = d2
                        d2.pair = d1
                        break
                # 竖向配对：top + bottom，同 x 同 width，y 相邻
                if d1.hinge == 'top' and d2.hinge == 'bottom' and d1.x == d2.x and d1.width == d2.width:
                    if d1.y + d1.height == d2.y:
                        d1.pair = d2
                        d2.pair = d1
                        break
                if d1.hinge == 'bottom' and d2.hinge == 'top' and d1.x == d2.x and d1.width == d2.width:
                    if d2.y + d2.height == d1.y:
                        d1.pair = d2
                        d2.pair = d1
                        break

    def compute_visibility_polygon(px, py, obstacles, max_dist=600, num_rays=360):
        """从玩家位置射出射线，计算可见区域多边形。
        射线遇到障碍物边缘时停止，形成视野多边形。"""
        # 预先过滤：只保留视野范围内的障碍物的边
        nearby_edges = []
        for obs in obstacles:
            r = obs.rect
            if (abs(r.centerx - px) > max_dist + r.width or
                abs(r.centery - py) > max_dist + r.height):
                continue
            nearby_edges.append((r.left, r.top, r.right, r.top))
            nearby_edges.append((r.right, r.top, r.right, r.bottom))
            nearby_edges.append((r.right, r.bottom, r.left, r.bottom))
            nearby_edges.append((r.left, r.bottom, r.left, r.top))
        points = []
        two_pi = 2 * math.pi
        for i in range(num_rays):
            angle = two_pi * i / num_rays
            dx = math.cos(angle)
            dy = math.sin(angle)
            min_t = max_dist
            for x1, y1, x2, y2 in nearby_edges:
                ex = x2 - x1
                ey = y2 - y1
                denom = dx * ey - dy * ex
                if abs(denom) < 1e-10:
                    continue
                qx = x1 - px
                qy = y1 - py
                t = (qx * ey - qy * ex) / denom
                if t <= 0 or t >= min_t:
                    continue
                u = (qx * dy - qy * dx) / denom
                if 0 <= u <= 1:
                    min_t = t
            points.append((px + dx * min_t, py + dy * min_t))
        return points

    # 定义 Bullet 类
    class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y, target_x, target_y, image, is_enemy_bullet=False, speed=None, creation_time=0, target_player=None, damage=1, is_boss_bullet=False, is_rpg_bullet=False, explosion_radius=150):
            super().__init__()
            self.original_image = image # 存储原始图像
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.is_enemy_bullet = is_enemy_bullet
            self.is_boss_bullet = is_boss_bullet  # 是否是Boss子弹
            self.is_rpg_bullet = is_rpg_bullet  # 是否是RPG子弹
            self.explosion_radius = explosion_radius  # 爆炸范围（像素）
            self.creation_time = creation_time # 子弹创建时间
            self.target_player = target_player # 追踪目标玩家对象
            self.damage = damage  # 子弹伤害值

            # 如果没有指定速度，则根据子弹类型使用默认速度
            if speed is None:
                if self.is_enemy_bullet:
                    speed = enemy_bullet_speed
                else:
                    speed = bullet_speed
            
            # 计算方向向量
            dx, dy = target_x - x, target_y - y
            dist = pygame.math.Vector2(dx, dy).length()
            if dist == 0: # 避免除以零
                self.velocity = pygame.math.Vector2(0, -speed) # 默认向上
                self.angle = 90 # 默认向上，角度为90度 (Pygame的旋转是逆时针)
            else:
                self.velocity = pygame.math.Vector2(dx, dy).normalize() * speed
                # 计算子弹的旋转角度 (以度为单位)
                # math.atan2 返回弧度，需要转换为度
                # Pygame的旋转是逆时针，0度是向右。atan2(y, x) 返回的是从正x轴到(x,y)的逆时针角度。
                # 如果子弹默认朝右，那么需要旋转的角度是 -atan2(dy, dx) 来使其指向目标。
                self.angle = math.degrees(-math.atan2(dy, dx))

        def update(self, current_time=0):
            if self.is_enemy_bullet and self.target_player and (current_time - self.creation_time) <= 500:
                # 重新计算子弹方向，追踪玩家
                player_center_x = self.target_player.rect.centerx
                player_center_y = self.target_player.rect.centery

                dx, dy = player_center_x - self.rect.centerx, player_center_y - self.rect.centery
                dist = pygame.math.Vector2(dx, dy).length()

                if dist != 0:
                    # 保持原有速度，只改变方向
                    self.velocity = pygame.math.Vector2(dx, dy).normalize() * self.velocity.length()
                    self.angle = math.degrees(-math.atan2(dy, dx))

            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y
            # print(f"Bullet updated to: ({self.rect.x}, {self.rect.y})")

        def draw(self, surface, camera_x, camera_y):
            # 旋转子弹图像
            rotated_image = pygame.transform.rotate(self.original_image, self.angle)
            rotated_rect = rotated_image.get_rect(center=self.rect.center)

            # 绘制光晕效果 (更明显的渐变，矩形)
            glow_extra_width = 30
            glow_extra_height = 15
            glow_size_x = self.rect.width + glow_extra_width
            glow_size_y = self.rect.height + glow_extra_height
            
            # 创建一个临时的 Surface 来绘制和旋转辉光
            temp_glow_surface = pygame.Surface((glow_size_x, glow_size_y), pygame.SRCALPHA)

            if self.is_boss_bullet:
                glow_color = (255, 0, 0) # Boss子弹红色光晕
            elif self.is_enemy_bullet:
                glow_color = (0, 255, 0) # 普通敌人子弹绿色光晕
            else:
                glow_color = (255, 255, 0) # 玩家子弹黄色光晕

            alphas = [20, 40, 70, 100, 140, 180]
            added_widths = [30, 25, 20, 15, 10, 5]
            added_heights = [15, 12, 10, 7, 5, 2]

            for i in range(len(alphas)):
                current_width = self.rect.width + added_widths[i]
                current_height = self.rect.height + added_heights[i]
                
                rect_x = (glow_size_x - current_width) // 2
                rect_y = (glow_size_y - current_height) // 2
                
                glow_rect = pygame.Rect(rect_x, rect_y, current_width, current_height)
                pygame.draw.rect(temp_glow_surface, glow_color + (alphas[i],), glow_rect)

            # 旋转辉光 Surface
            rotated_glow_surface = pygame.transform.rotate(temp_glow_surface, self.angle)
            rotated_glow_rect = rotated_glow_surface.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery - camera_y))

            # 将旋转后的光晕 Surface 绘制到主屏幕上
            surface.blit(rotated_glow_surface, rotated_glow_rect)

            # 绘制旋转后的子弹本身
            surface.blit(rotated_image, (rotated_rect.x - camera_x, rotated_rect.y - camera_y))

    # 定义枪械类
    class Weapon:
        def __init__(self, name, damage, fire_rate, clip_size, reload_time, bullet_speed, ammo_type="通用"):
            """
            枪械类
            name: 枪械名称
            damage: 伤害值
            fire_rate: 射速（毫秒，两次射击之间的间隔）
            clip_size: 弹夹容量
            reload_time: 换弹时间（毫秒）
            bullet_speed: 子弹速度
            ammo_type: 弹药类型（用于区分不同枪械的弹药）
            """
            self.name = name
            self.damage = damage
            self.fire_rate = fire_rate
            self.clip_size = clip_size
            self.reload_time = reload_time
            self.bullet_speed = bullet_speed
            self.ammo_type = ammo_type
    
    # 定义所有可用的枪械
    weapons = {
        "手枪": Weapon("手枪", damage=50, fire_rate=600, clip_size=15, reload_time=1500, bullet_speed=25, ammo_type="手枪"),
        "步枪": Weapon("步枪", damage=20, fire_rate=100, clip_size=30, reload_time=2000, bullet_speed=32, ammo_type="步枪"),
        "冲锋枪": Weapon("冲锋枪", damage=16, fire_rate=50, clip_size=40, reload_time=1800, bullet_speed=28, ammo_type="冲锋枪"),
        "狙击枪": Weapon("狙击枪", damage=150, fire_rate=800, clip_size=5, reload_time=3000, bullet_speed=45, ammo_type="狙击枪"),
        "rpg": Weapon("rpg", damage=300, fire_rate=1200, clip_size=1, reload_time=2500, bullet_speed=35, ammo_type="rpg"),
    }

    # 定义 Player 类
    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y, image, speed, sprint_speed, max_health, max_armor, max_stamina):
            super().__init__()
            self.original_image = image  # 保存原始图片用于旋转
            self.image = image
            self.angle = 0  # 当前朝向角度
            # 碰撞框比图片小，只覆盖角色身体（去掉透明区域）
            full_rect = self.image.get_rect(topleft=(x, y))
            self.rect = full_rect.inflate(-30, -36)  # 缩小：宽48, 高64
            self.rect.center = full_rect.center
            self.speed = speed
            self.sprint_speed = sprint_speed
            self.health = max_health
            self.max_health = max_health
            self.armor = max_armor
            self.max_armor = max_armor
            self.stamina = max_stamina
            self.max_stamina = max_stamina
            self.is_sprinting = False
            self.stamina_drain_rate = 1
            self.stamina_regen_rate = 0.5
            self.last_damage_time = 0
            self.last_armor_damage_time = 0
            self.health_regen_rate = 0.1
            self.previous_rect = self.rect.copy() # 用于检测玩家是否移动

            # 枪械系统
            self.max_carried_weapons = 2  # 最多只能携带2个武器
            self.carried_weapons = ["手枪", "步枪"]  # 当前携带的武器（最多2个）
            self.current_weapon = weapons["步枪"]  # 默认使用步枪
            self.weapon_ammo = {  # 每种枪械的弹药数量
                "手枪": 60,
                "步枪": 90,
                "冲锋枪": 120,  # 未解锁，但保留弹药数据
                "狙击枪": 20,  # 未解锁，但保留弹药数据
                "rpg": 0  # RPG弹药，拾取时初始化
            }
            self.weapon_clip_bullets = {  # 每种枪械的弹夹子弹数量
                "手枪": weapons["手枪"].clip_size,
                "步枪": weapons["步枪"].clip_size,
            }
            
            # 弹夹和换弹系统（使用当前枪械的属性）
            self.max_clip_bullets = self.current_weapon.clip_size
            self.current_bullets = self.current_weapon.clip_size
            self.total_ammo = self.weapon_ammo[self.current_weapon.name]
            self.reloading = False
            self.reload_start_time = 0
            self.reload_duration = self.current_weapon.reload_time
            # 技能商城与容器拾取
            self.coins = 0       # 金币（容器拾取、用于技能商城）
            self.grenades = 0    # 手雷数量
        
        def switch_weapon(self, weapon_name):
            """切换枪械（只能切换到携带的枪械）"""
            if weapon_name in weapons and weapon_name in self.carried_weapons:
                # 保存当前枪械的弹药和弹夹子弹
                self.weapon_ammo[self.current_weapon.name] = self.total_ammo
                self.weapon_clip_bullets[self.current_weapon.name] = self.current_bullets
                
                # 切换枪械
                self.current_weapon = weapons[weapon_name]
                
                # 更新弹夹和弹药
                self.max_clip_bullets = self.current_weapon.clip_size
                self.total_ammo = self.weapon_ammo.get(weapon_name, 0)
                # 恢复弹夹子弹数（如果之前保存过，否则使用满弹夹）
                self.current_bullets = self.weapon_clip_bullets.get(weapon_name, self.current_weapon.clip_size)
                
                # 如果正在换弹，取消换弹
                if self.reloading:
                    self.reloading = False
                
                print(f"切换到 {weapon_name}，弹夹: {self.current_bullets}/{self.max_clip_bullets}，总弹药: {self.total_ammo}")
            elif weapon_name in weapons:
                print(f"{weapon_name} 尚未解锁")
        
        def switch_to_next_weapon(self, direction=1):
            """切换到下一个/上一个携带的枪械（direction: 1=下一个, -1=上一个）"""
            if len(self.carried_weapons) <= 1:
                return  # 只有一把枪或没有枪，不需要切换
            
            # 获取当前枪械在携带列表中的索引
            try:
                current_index = self.carried_weapons.index(self.current_weapon.name)
            except ValueError:
                # 如果当前枪械不在携带列表中，使用第一把
                current_index = 0
            
            # 计算下一个索引（循环）
            next_index = (current_index + direction) % len(self.carried_weapons)
            next_weapon_name = self.carried_weapons[next_index]
            
            # 切换到下一把枪
            self.switch_weapon(next_weapon_name)

        def update(self, keys, world_width, world_height, current_time, obstacles, map_level=None, min_map_level=None, infinite_ammo=False):
            # 记录当前位置，用于判断是否移动
            old_x, old_y = self.rect.x, self.rect.y
            # 给障碍碰撞一个微小收缩，避免“看起来有缝但过不去”的边缘卡住
            collision_shrink = 8

            # Movement logic
            current_speed = self.sprint_speed if self.is_sprinting else self.speed
            
            # Move X
            dx = 0
            if keys[pygame.K_a]:
                dx -= current_speed
            if keys[pygame.K_d]:
                dx += current_speed
            
            self.rect.x += dx
            # Check collision with obstacles in X
            for obstacle in obstacles:
                test_rect = obstacle.rect.inflate(-collision_shrink, -collision_shrink)
                if self.rect.colliderect(test_rect):
                    if dx > 0: # Moving right
                        self.rect.right = test_rect.left
                    if dx < 0: # Moving left
                        self.rect.left = test_rect.right

            # Move Y
            dy = 0
            if keys[pygame.K_w]:
                dy -= current_speed
            if keys[pygame.K_s]:
                dy += current_speed
            
            self.rect.y += dy
            # Check collision with obstacles in Y
            for obstacle in obstacles:
                test_rect = obstacle.rect.inflate(-collision_shrink, -collision_shrink)
                if self.rect.colliderect(test_rect):
                    if dy > 0: # Moving down
                        self.rect.bottom = test_rect.top
                    if dy < 0: # Moving up
                        self.rect.top = test_rect.bottom
            
            # Boundary checks
            self.rect.x = max(0, min(self.rect.x, world_width - self.rect.width))
            
            # Check if player goes beyond the top boundary
            if self.rect.y < 0:
                return "new_map" # Signal to generate a new map (level up)
            
            # Check if player goes beyond the bottom boundary
            # 如果是第一张地图（map_level == min_map_level），不能向下走
            if self.rect.y > world_height - self.rect.height:
                if map_level is not None and min_map_level is not None and map_level == min_map_level:
                    # 第一张地图，阻止向下移动
                    self.rect.y = world_height - self.rect.height
                    return None  # 不返回任何状态，阻止地图切换
                else:
                    return "previous_map" # Signal to go to previous map

            self.rect.y = max(0, min(self.rect.y, world_height - self.rect.height))

            # 判断玩家是否实际移动
            has_moved = (self.rect.x != old_x or self.rect.y != old_y)
            
            # 如果移动则打印位置坐标
            if has_moved:
                print(f"玩家位置: ({self.rect.x}, {self.rect.y})")

            # 护甲恢复逻辑
            if current_time - self.last_armor_damage_time > 5000: # 5秒内未受到护甲伤害
                if self.armor < self.max_armor:
                    self.armor += 0.5 # 每帧恢复1点护甲，可以调整恢复速度
                    self.armor = min(self.armor, self.max_armor)

            # Stamina logic
            if self.is_sprinting and has_moved: # 只有在冲刺且实际移动时才消耗体力
                self.stamina -= self.stamina_drain_rate
                if self.stamina <= 0:
                    self.stamina = 0
                    self.is_sprinting = False
            else:
                # 不冲刺时恢复体力
                self.stamina += self.stamina_regen_rate
                self.stamina = min(self.stamina, self.max_stamina)

            # 换弹逻辑（使用当前枪械的属性）
            if infinite_ammo:
                self.reloading = False
                self.current_bullets = self.max_clip_bullets
            if self.reloading:
                if current_time - self.reload_start_time >= self.reload_duration:
                    # 完成换弹
                    self.reloading = False
                    bullets_to_reload = min(self.max_clip_bullets - self.current_bullets, self.total_ammo)
                    self.current_bullets += bullets_to_reload
                    self.total_ammo -= bullets_to_reload
                    # 保存弹药到对应枪械
                    self.weapon_ammo[self.current_weapon.name] = self.total_ammo


        def get_muzzle_pos(self, target_world_x, target_world_y):
            """根据朝向计算枪口的世界坐标（子弹从此处发射）"""
            dx = target_world_x - self.rect.centerx
            dy = target_world_y - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
            else:
                dir_x, dir_y = 0, -1  # 默认朝上
            # 垂直于朝向的方向（右手侧）
            perp_x = -dir_y
            perp_y = dir_x
            # 原图 78×100，面朝上时枪口约在 (52, 5)，中心 (39, 50)
            # 偏移：沿朝向 ~45px，右偏 ~13px
            forward = 45
            side = 13
            muzzle_x = self.rect.centerx + forward * dir_x + side * perp_x
            muzzle_y = self.rect.centery + forward * dir_y + side * perp_y
            return muzzle_x, muzzle_y

        def draw(self, surface, camera_x, camera_y):
            # 计算玩家到鼠标的角度，旋转图片面向鼠标
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_screen_x = self.rect.centerx - camera_x
            player_screen_y = self.rect.centery - camera_y
            dx = mouse_x - player_screen_x
            dy = mouse_y - player_screen_y
            self.angle = math.degrees(math.atan2(-dy, dx)) - 90  # -90因为图片默认面朝上
            # 旋转图片
            rotated_image = pygame.transform.rotate(self.original_image, self.angle)
            rotated_rect = rotated_image.get_rect(center=(player_screen_x, player_screen_y))
            surface.blit(rotated_image, rotated_rect)

    # 定义 Enemy 类
    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y, image, health=100, drop_weapon=None):
            super().__init__()
            self.original_image = image  # 保存原始图片用于旋转（原图朝右）
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.facing_angle = 0  # 当前朝向角度（0=右，原图方向）
            self.speed = 2 # 敌人移动速度
            self.health = health # 敌人血量
            self.max_health = health  # 最大血量（用于显示血条）
            self.stop_distance = 200 # 敌人停止移动的距离（追击时靠近到此距离停下）
            self.shoot_range = 800  # 射击距离（发现即开火）
            self.active_pursuit_distance = 800 # 敌人主动追击玩家的距离
            self.retreat_distance = 0  # 后退触发距离（0=不后退，狙击手会覆盖此值）
            self.is_aggroed = False # 新增：敌人是否被攻击过，被攻击后会一直追击玩家
            self.last_shot_time = 0 # 上次射击时间
            self.shoot_cooldown = 1000 # 敌人射击冷却时间 (1秒)
            self.is_dodging = False  # 是否正在躲避子弹
            self.dodge_dx = 0
            self.dodge_dy = 0
            self.dodge_end_time = 0  # 躲避结束时间
            # 敌人弹容量系统
            self.reloading = False  # 是否正在换弹
            self.reload_start_time = 0  # 换弹开始时间
            self.reload_duration = 2000  # 默认换弹时间2秒
            # 高级敌人的掉落武器和属性
            self.drop_weapon = drop_weapon  # 掉落的武器类型（仅高级敌人）
            if drop_weapon and drop_weapon in weapons:
                # 根据掉落武器设置伤害和射速（玩家对应武器的一半）
                weapon = weapons[drop_weapon]
                # 特殊处理：不同武器有特定伤害值
                if drop_weapon == "冲锋枪":
                    self.bullet_damage = 5  # 伤害提高
                    # 冲锋枪敌人射速比玩家慢（间隔时间乘以1.5）
                    self.shoot_cooldown = int(weapon.fire_rate * 1.5)  # 50*1.5=75ms
                elif drop_weapon == "步枪":
                    self.bullet_damage = 15  # 伤害提高
                    # 步枪敌人射速比玩家慢（间隔时间乘以1.5）
                    self.shoot_cooldown = int(weapon.fire_rate * 1.5)  # 100*1.5=150ms
                elif drop_weapon == "狙击枪":
                    self.bullet_damage = 75  # 伤害提高
                    # 狙击枪敌人射速比玩家慢（间隔时间乘以1.5）
                    self.shoot_cooldown = int(weapon.fire_rate * 1.5)
                    # 狙击手视野和射程是正常的3倍
                    self.shoot_range = 800 * 3      # 2400
                    self.active_pursuit_distance = 800 * 3
                    self.stop_distance = 400         # 保持更远的距离
                    self.retreat_distance = 250       # 玩家靠近到此距离内就后退
                else:
                    self.bullet_damage = int(weapon.damage * 0.75)  # 伤害为玩家的75%
                    self.shoot_cooldown = int(weapon.fire_rate * 1.5)  # 比玩家慢1.5倍
                # 弹容量是玩家对应武器的一半
                self.max_clip_bullets = weapon.clip_size // 2
                self.current_bullets = self.max_clip_bullets  # 初始弹容量
                self.reload_duration = weapon.reload_time  # 使用武器的换弹时间
                # 调试信息
                print(f"高级敌人设置：掉落武器={drop_weapon}，玩家武器伤害={weapon.damage}，敌人伤害={self.bullet_damage}，玩家射速={weapon.fire_rate}ms，敌人射速={self.shoot_cooldown}ms，弹容量={self.max_clip_bullets}")
            else:
                # 普通敌人默认值（使用步枪的一半作为基准）
                self.bullet_damage = 25  # 伤害提高
                self.shoot_cooldown = 700  # 普通敌人射速加快（0.7秒）
                self.max_clip_bullets = weapons["步枪"].clip_size // 2  # 步枪弹容量30的一半=15
                self.current_bullets = self.max_clip_bullets
                self.reload_duration = weapons["步枪"].reload_time  # 使用步枪的换弹时间
            # 准度系统：普通敌人准度低，高级敌人准度中等
            if self.max_health == 250:  # 高级敌人
                self.accuracy_spread = 25  # 小偏移（像素），射击准度很高
                self.can_dodge = True  # 高级敌人会躲避子弹
            else:  # 普通敌人
                self.accuracy_spread = 70  # 中等偏移，射击准度提升
                self.can_dodge = False  # 普通敌人不会躲避
            # 未发现玩家时的随意走动
            self.wander_dx = 0
            self.wander_dy = 0
            self.wander_change_time = 0  # 下次改变方向的时刻（毫秒）

        def update(self, player, current_time, bullets_list, bullet_image, camera_x, camera_y, screen_width, screen_height, is_player_actively_moving, obstacles):
            # 计算敌人屏幕坐标
            enemy_screen_x = self.rect.x - camera_x
            enemy_screen_y = self.rect.y - camera_y

            # 检查敌人是否在屏幕视野内
            is_on_screen = (
                enemy_screen_x + self.rect.width > 0 and
                enemy_screen_x < screen_width and
                enemy_screen_y + self.rect.height > 0 and
                enemy_screen_y < screen_height
            )

            if is_on_screen:
                # 计算敌人与玩家的距离
                distance = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)
                # 敌人视野被障碍物遮挡：只有视线未被挡时才算“看见”玩家
                can_see_player = not is_line_blocked_by_obstacle(
                    self.rect.centerx, self.rect.centery,
                    player.rect.centerx, player.rect.centery, obstacles
                )

                # 高级敌人躲避子弹逻辑
                if self.can_dodge and not self.is_dodging:
                    for b in bullets_list:
                        if not b.is_enemy_bullet:
                            bx, by = b.rect.centerx, b.rect.centery
                            dist_to_bullet = math.sqrt((bx - self.rect.centerx)**2 + (by - self.rect.centery)**2)
                            if dist_to_bullet < 200:
                                to_enemy_dx = self.rect.centerx - bx
                                to_enemy_dy = self.rect.centery - by
                                dot = b.dx * to_enemy_dx + b.dy * to_enemy_dy
                                if dot > 0:  # 子弹正朝自己飞来
                                    self.dodge_dx = -b.dy
                                    self.dodge_dy = b.dx
                                    if random.random() < 0.5:
                                        self.dodge_dx = -self.dodge_dx
                                        self.dodge_dy = -self.dodge_dy
                                    self.is_dodging = True
                                    self.dodge_end_time = current_time + 400
                                    break

                # 躲避中：只移动不射击
                if self.is_dodging:
                    if current_time >= self.dodge_end_time:
                        self.is_dodging = False
                    else:
                        dodge_speed = self.speed * 2.5
                        norm = math.sqrt(self.dodge_dx**2 + self.dodge_dy**2)
                        if norm > 0:
                            move_x = self.dodge_dx / norm * dodge_speed
                            move_y = self.dodge_dy / norm * dodge_speed
                            self.rect.x += move_x
                            for obstacle in obstacles:
                                if self.rect.colliderect(obstacle.rect):
                                    self.rect.x -= move_x
                                    break
                            self.rect.y += move_y
                            for obstacle in obstacles:
                                if self.rect.colliderect(obstacle.rect):
                                    self.rect.y -= move_y
                                    break
                        return  # 躲避期间不射击

                # 更新朝向角度（面向玩家或移动方向）
                if can_see_player or self.is_aggroed:
                    dx_face = player.rect.centerx - self.rect.centerx
                    dy_face = player.rect.centery - self.rect.centery
                    self.facing_angle = math.degrees(math.atan2(-dy_face, dx_face))

                # 敌人移动逻辑
                # 狙击手后退：玩家靠得太近时往反方向跑
                is_retreating = (self.retreat_distance > 0 and can_see_player and distance < self.retreat_distance)
                if is_retreating:
                        retreat_speed = self.speed * 2  # 后退速度更快
                        # 远离玩家方向移动
                        dx = 0
                        if self.rect.centerx > player.rect.centerx:
                            dx = retreat_speed
                        elif self.rect.centerx < player.rect.centerx:
                            dx = -retreat_speed
                        
                        self.rect.x += dx
                        for obstacle in obstacles:
                            if self.rect.colliderect(obstacle.rect):
                                if dx > 0: self.rect.right = obstacle.rect.left
                                if dx < 0: self.rect.left = obstacle.rect.right

                        dy = 0
                        if self.rect.centery > player.rect.centery:
                            dy = retreat_speed
                        elif self.rect.centery < player.rect.centery:
                            dy = -retreat_speed
                        
                        self.rect.y += dy
                        for obstacle in obstacles:
                            if self.rect.colliderect(obstacle.rect):
                                if dy > 0: self.rect.bottom = obstacle.rect.top
                                if dy < 0: self.rect.top = obstacle.rect.bottom

                elif (self.is_aggroed or (can_see_player and distance > self.stop_distance and distance < self.active_pursuit_distance)):
                        # 正常追击
                        # Move X
                        dx = 0
                        if self.rect.x < player.rect.centerx:
                            dx = self.speed
                        elif self.rect.x > player.rect.centerx:
                            dx = -self.speed
                        
                        self.rect.x += dx
                        for obstacle in obstacles:
                            if self.rect.colliderect(obstacle.rect):
                                if dx > 0: self.rect.right = obstacle.rect.left
                                if dx < 0: self.rect.left = obstacle.rect.right

                        # Move Y
                        dy = 0
                        if self.rect.y < player.rect.centery:
                            dy = self.speed
                        elif self.rect.y > player.rect.centery:
                            dy = -self.speed
                        
                        self.rect.y += dy
                        for obstacle in obstacles:
                            if self.rect.colliderect(obstacle.rect):
                                if dy > 0: self.rect.bottom = obstacle.rect.top
                                if dy < 0: self.rect.top = obstacle.rect.bottom
                elif not can_see_player:
                    # 未发现玩家时随意走动
                    wander_speed = self.speed * 0.4
                    if current_time >= self.wander_change_time:
                        angle = random.uniform(0, 2 * math.pi)
                        self.wander_dx = math.cos(angle)
                        self.wander_dy = math.sin(angle)
                        self.wander_change_time = current_time + random.randint(1500, 3500)
                    # 漫游时朝向移动方向
                    if self.wander_dx != 0 or self.wander_dy != 0:
                        self.facing_angle = math.degrees(math.atan2(-self.wander_dy, self.wander_dx))
                    self.rect.x += self.wander_dx * wander_speed
                    for obstacle in obstacles:
                        if self.rect.colliderect(obstacle.rect):
                            self.rect.x -= self.wander_dx * wander_speed
                            self.wander_dx = -self.wander_dx
                            break
                    self.rect.y += self.wander_dy * wander_speed
                    for obstacle in obstacles:
                        if self.rect.colliderect(obstacle.rect):
                            self.rect.y -= self.wander_dy * wander_speed
                            self.wander_dy = -self.wander_dy
                            break
                
                # 敌人换弹逻辑
                if self.reloading:
                    if current_time - self.reload_start_time >= self.reload_duration:
                        # 完成换弹
                        self.reloading = False
                        self.current_bullets = self.max_clip_bullets
                
                # 敌人射击逻辑：发现玩家即开火（射程内+视线无遮挡）
                if can_see_player and distance <= self.shoot_range and current_time - self.last_shot_time > self.shoot_cooldown and not self.reloading:
                    if self.current_bullets > 0:
                        # 根据准度添加随机偏移（普通敌人偏移大，高级敌人偏移小）
                        spread = self.accuracy_spread
                        target_x = player.rect.centerx + random.randint(-spread, spread)
                        target_y = player.rect.centery + random.randint(-spread, spread)
                        # 计算枪口位置（原图朝右，枪口在前方约22像素）
                        dx_dir = target_x - self.rect.centerx
                        dy_dir = target_y - self.rect.centery
                        dist_dir = math.sqrt(dx_dir * dx_dir + dy_dir * dy_dir)
                        if dist_dir > 0:
                            muzzle_dir_x = dx_dir / dist_dir
                            muzzle_dir_y = dy_dir / dist_dir
                        else:
                            muzzle_dir_x, muzzle_dir_y = 1, 0
                        muzzle_forward = 22  # 枪口距离中心的前方偏移
                        muzzle_x = self.rect.centerx + muzzle_forward * muzzle_dir_x
                        muzzle_y = self.rect.centery + muzzle_forward * muzzle_dir_y
                        new_bullet = Bullet(muzzle_x, muzzle_y, target_x, target_y, bullet_image, is_enemy_bullet=True, speed=enemy_bullet_speed, creation_time=current_time, target_player=None, damage=self.bullet_damage)
                        bullets_list.append(new_bullet)
                        self.current_bullets -= 1
                        self.last_shot_time = current_time
                    elif self.current_bullets == 0 and not self.reloading:
                        self.reloading = True
                        self.reload_start_time = current_time

        def draw(self, surface, camera_x, camera_y):
            # 旋转敌人图片使其面向目标方向（原图朝右）
            rotated_image = pygame.transform.rotate(self.original_image, self.facing_angle)
            rotated_rect = rotated_image.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery - camera_y))
            surface.blit(rotated_image, rotated_rect)
    
    # 敌人/Boss 死亡后留下的尸体（固定位置，暗色贴图）
    class Corpse(pygame.sprite.Sprite):
        def __init__(self, x, y, image, facing_angle=0):
            super().__init__()
            # 先旋转到死亡时的朝向，再暗化
            rotated = pygame.transform.rotate(image, facing_angle)
            self.image = rotated.copy()
            # 用乘法暗化 RGB 但保留原始 alpha，避免透明区域变黑
            darken = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            darken.fill((100, 100, 100, 255))  # RGB 乘以 100/255 ≈ 0.39 来暗化，alpha 不变
            self.image.blit(darken, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.rect = self.image.get_rect(center=(x, y))
        def draw(self, surface, camera_x, camera_y):
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    # 定义Boss炮弹类（不追踪，红色，更大）
    class BossShell(pygame.sprite.Sprite):
        def __init__(self, x, y, target_x, target_y, damage=150):
            super().__init__()
            # 创建红色炮弹，比普通敌人子弹大1倍（普通是10x5，所以是20x10）
            self.image = pygame.Surface((20, 10))
            self.image.fill((255, 0, 0))  # 红色
            self.rect = self.image.get_rect(center=(x, y))
            self.damage = damage
            # 炮弹速度是敌方普通士兵的2/3
            speed = enemy_bullet_speed * 2 / 3
            # 计算方向向量（不追踪，只朝初始目标方向）
            dx, dy = target_x - x, target_y - y
            dist = pygame.math.Vector2(dx, dy).length()
            if dist == 0:
                self.velocity = pygame.math.Vector2(0, -speed)
            else:
                self.velocity = pygame.math.Vector2(dx, dy).normalize() * speed
        
        def update(self):
            self.rect.x += self.velocity.x
            self.rect.y += self.velocity.y
        
        def draw(self, surface, camera_x, camera_y):
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    # 定义Boss类（坦克）- 使用和普通敌人一样的逻辑
    class BossTank(pygame.sprite.Sprite):
        def __init__(self, x, y, image):
            super().__init__()
            self.original_image = image  # 保存原始图片用于旋转
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.facing_angle = 0  # 当前朝向角度
            self.speed = 0.5  # 移速很慢
            self.health = 500  # 血量500
            self.max_health = 500
            self.stop_distance = 200  # 停止移动的距离
            self.active_pursuit_distance = 500  # 主动追击距离
            self.is_aggroed = False
            self.last_shot_time = 0
            self.shoot_cooldown = 1000  # 射击冷却时间（1秒，和普通敌人一样）
            self.bullet_damage = 150  # 伤害150（提高）
            # Boss弹容量系统（使用步枪的一半作为基准）
            self.max_clip_bullets = weapons["步枪"].clip_size // 2  # 15发
            self.current_bullets = self.max_clip_bullets
            self.reloading = False
            self.reload_start_time = 0
            self.reload_duration = weapons["步枪"].reload_time  # 使用步枪的换弹时间
            self.wander_dx = 0
            self.wander_dy = 0
            self.wander_change_time = 0
        
        def update(self, player, current_time, bullets_list, bullet_image, camera_x, camera_y, screen_width, screen_height, is_player_actively_moving, obstacles):
            # 计算Boss屏幕坐标
            boss_screen_x = self.rect.x - camera_x
            boss_screen_y = self.rect.y - camera_y
            
            # 检查Boss是否在屏幕视野内
            is_on_screen = (
                boss_screen_x + self.rect.width > 0 and
                boss_screen_x < screen_width and
                boss_screen_y + self.rect.height > 0 and
                boss_screen_y < screen_height
            )
            
            # 计算Boss与玩家的距离（无论是否在屏幕内都计算）
            distance = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)
            # Boss视野被障碍物遮挡：只有视线未被挡时才算“看见”玩家
            can_see_player = not is_line_blocked_by_obstacle(
                self.rect.centerx, self.rect.centery,
                player.rect.centerx, player.rect.centery, obstacles
            )
            
            # 更新Boss朝向角度
            if can_see_player or self.is_aggroed:
                dx_face = player.rect.centerx - self.rect.centerx
                dy_face = player.rect.centery - self.rect.centery
                self.facing_angle = math.degrees(math.atan2(-dy_face, dx_face))

            is_pursuing = self.is_aggroed or (can_see_player and distance > self.stop_distance and distance < self.active_pursuit_distance)
            if is_pursuing:
                # Move X
                dx = 0
                if self.rect.centerx < player.rect.centerx:
                    dx = self.speed
                elif self.rect.centerx > player.rect.centerx:
                    dx = -self.speed
                
                self.rect.x += dx
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        if dx > 0: self.rect.right = obstacle.rect.left
                        if dx < 0: self.rect.left = obstacle.rect.right
                
                # Move Y
                dy = 0
                if self.rect.centery < player.rect.centery:
                    dy = self.speed
                elif self.rect.centery > player.rect.centery:
                    dy = -self.speed
                
                self.rect.y += dy
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        if dy > 0: self.rect.bottom = obstacle.rect.top
                        if dy < 0: self.rect.top = obstacle.rect.bottom
            else:
                # 未发现玩家时随意走动
                wander_speed = self.speed * 0.6
                if current_time >= self.wander_change_time:
                    angle = random.uniform(0, 2 * math.pi)
                    self.wander_dx = math.cos(angle)
                    self.wander_dy = math.sin(angle)
                    self.wander_change_time = current_time + random.randint(2000, 4500)
                # 漫游时朝向移动方向
                if self.wander_dx != 0 or self.wander_dy != 0:
                    self.facing_angle = math.degrees(math.atan2(-self.wander_dy, self.wander_dx))
                self.rect.x += self.wander_dx * wander_speed
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        self.rect.x -= self.wander_dx * wander_speed
                        self.wander_dx = -self.wander_dx
                        break
                self.rect.y += self.wander_dy * wander_speed
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        self.rect.y -= self.wander_dy * wander_speed
                        self.wander_dy = -self.wander_dy
                        break
            
            # Boss换弹和射击逻辑（只在屏幕内时执行）
            if is_on_screen:
                # Boss换弹逻辑（和普通敌人一样）
                if self.reloading:
                    if current_time - self.reload_start_time >= self.reload_duration:
                        # 完成换弹
                        self.reloading = False
                        self.current_bullets = self.max_clip_bullets
                
                # Boss射击逻辑（需要视线未被障碍物遮挡才能开火）
                if can_see_player and distance <= self.stop_distance and current_time - self.last_shot_time > self.shoot_cooldown and not self.reloading:
                    # 检查弹容量
                    if self.current_bullets > 0:
                        # 计算枪口位置
                        dx_dir = player.rect.centerx - self.rect.centerx
                        dy_dir = player.rect.centery - self.rect.centery
                        dist_dir = math.sqrt(dx_dir * dx_dir + dy_dir * dy_dir)
                        if dist_dir > 0:
                            muzzle_dir_x = dx_dir / dist_dir
                            muzzle_dir_y = dy_dir / dist_dir
                        else:
                            muzzle_dir_x, muzzle_dir_y = 1, 0
                        muzzle_forward = 25  # Boss枪口前方偏移
                        boss_muzzle_x = self.rect.centerx + muzzle_forward * muzzle_dir_x
                        boss_muzzle_y = self.rect.centery + muzzle_forward * muzzle_dir_y
                        # 使用普通子弹（标记为Boss子弹，显示红色）
                        new_bullet = Bullet(boss_muzzle_x, boss_muzzle_y, player.rect.centerx, player.rect.centery, bullet_image, is_enemy_bullet=True, speed=enemy_bullet_speed, creation_time=current_time, target_player=player, damage=self.bullet_damage, is_boss_bullet=True)
                        bullets_list.append(new_bullet)
                        self.current_bullets -= 1  # 减少弹容量
                        self.last_shot_time = current_time
                    elif self.current_bullets == 0 and not self.reloading:
                        # 弹容量用完，开始换弹
                        self.reloading = True
                        self.reload_start_time = current_time
        
        def draw(self, surface, camera_x, camera_y):
            # 旋转Boss图片使其面向目标方向
            rotated_image = pygame.transform.rotate(self.original_image, self.facing_angle)
            rotated_rect = rotated_image.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery - camera_y))
            surface.blit(rotated_image, rotated_rect)
            # 绘制血条
            bar_width = self.rect.width
            bar_height = 5
            bar_x = self.rect.x - camera_x
            bar_y = self.rect.y - camera_y - 10
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # 红色背景
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))  # 绿色血条
    
    # 定义医疗包类
    class Medkit(pygame.sprite.Sprite):
        def __init__(self, x, y, image):
            super().__init__()
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.heal_amount = 50  # 恢复的生命值
            self.used = False  # 标记是否已被使用
            
        def draw(self, surface, camera_x, camera_y):
            if not self.used:  # 只有未使用时才绘制
                surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    # 定义弹药箱类
    class AmmoBox(pygame.sprite.Sprite):
        def __init__(self, x, y, image):
            super().__init__()
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.ammo_amount = 30  # 增加的弹药数量
            self.used = False  # 标记是否已被使用
            
        def draw(self, surface, camera_x, camera_y):
            if not self.used:  # 只有未使用时才绘制
                surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    # 定义爆炸特效类
    class Explosion(pygame.sprite.Sprite):
        def __init__(self, x, y, radius, duration=500):
            """
            爆炸特效
            x, y: 爆炸中心坐标
            radius: 爆炸半径
            duration: 持续时间（毫秒）
            """
            super().__init__()
            self.x = x
            self.y = y
            self.radius = radius
            self.max_radius = radius
            self.creation_time = pygame.time.get_ticks()
            self.duration = duration
            self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        
        def update(self, current_time):
            """更新爆炸特效"""
            elapsed = current_time - self.creation_time
            if elapsed >= self.duration:
                return False  # 爆炸结束
            return True  # 继续显示
        
        def draw(self, surface, camera_x, camera_y, obstacles_list=None):
            """绘制爆炸特效"""
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.creation_time
            progress = min(elapsed / self.duration, 1.0)  # 0到1的进度
            
            # 计算当前爆炸半径（从0增长到最大半径，然后稍微收缩）
            if progress < 0.3:
                # 快速扩张阶段
                current_radius = self.max_radius * (progress / 0.3)
            elif progress < 0.7:
                # 保持最大大小
                current_radius = self.max_radius
            else:
                # 收缩阶段
                current_radius = self.max_radius * (1.0 - (progress - 0.7) / 0.3)
            
            # 计算透明度（逐渐变淡）
            alpha = int(255 * (1.0 - progress))
            
            # 屏幕坐标
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            # 绘制多层爆炸效果（从外到内）
            # 最外层：红色火焰（半透明）
            if current_radius > 5:
                outer_radius = current_radius
                outer_alpha = min(alpha, 180)
                outer_color = (255, int(50 + 100 * (1 - progress)), 0, outer_alpha)
                self._draw_circle(surface, screen_x, screen_y, outer_radius, outer_color, obstacles_list, self.x, self.y)
            
            # 外层：橙色火焰
            if current_radius > 15:
                mid_outer_radius = current_radius * 0.85
                mid_outer_alpha = min(alpha, 200)
                mid_outer_color = (255, int(100 + 100 * (1 - progress)), 0, mid_outer_alpha)
                self._draw_circle(surface, screen_x, screen_y, mid_outer_radius, mid_outer_color, obstacles_list, self.x, self.y)
            
            # 中层：黄色火焰
            if current_radius > 20:
                mid_radius = current_radius * 0.65
                mid_alpha = min(alpha, 220)
                mid_color = (255, 255, int(50 + 150 * (1 - progress)), mid_alpha)
                self._draw_circle(surface, screen_x, screen_y, mid_radius, mid_color, obstacles_list, self.x, self.y)
            
            # 内层：亮黄色/白色核心
            if current_radius > 10:
                inner_radius = current_radius * 0.35
                inner_alpha = min(alpha, 255)
                inner_color = (255, 255, min(200 + int(55 * (1 - progress)), 255), inner_alpha)
                self._draw_circle(surface, screen_x, screen_y, inner_radius, inner_color, obstacles_list, self.x, self.y)
            
            # 最内层：白色亮点
            if current_radius > 5:
                core_radius = current_radius * 0.15
                core_alpha = min(alpha, 255)
                core_color = (255, 255, 255, core_alpha)
                self._draw_circle(surface, screen_x, screen_y, core_radius, core_color, obstacles_list, self.x, self.y)
        
        def _draw_circle(self, surface, x, y, radius, color, obstacles_list=None, world_x=None, world_y=None):
            """绘制带透明度的圆形，支持障碍物遮挡"""
            if radius <= 0:
                return
            
            # 创建临时surface来绘制带透明度的圆形
            temp_surface = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (int(radius), int(radius)), int(radius))
            
            # 如果有障碍物列表，将障碍物区域的像素设为透明
            if obstacles_list and world_x is not None and world_y is not None:
                for obstacle in obstacles_list:
                    # 计算障碍物在临时surface中的位置
                    obs_left = max(0, int(obstacle.rect.left - (world_x - radius)))
                    obs_top = max(0, int(obstacle.rect.top - (world_y - radius)))
                    obs_right = min(int(radius * 2), int(obstacle.rect.right - (world_x - radius)))
                    obs_bottom = min(int(radius * 2), int(obstacle.rect.bottom - (world_y - radius)))
                    
                    # 检查障碍物是否与圆形区域重叠
                    if obs_right > obs_left and obs_bottom > obs_top:
                        # 创建一个透明矩形来覆盖障碍物区域
                        # 使用set_at逐像素设置alpha为0（虽然慢，但不需要numpy）
                        for py in range(obs_top, obs_bottom):
                            for px in range(obs_left, obs_right):
                                # 检查像素是否在圆形内（距离中心小于半径）
                                dx = px - radius
                                dy = py - radius
                                dist_sq = dx * dx + dy * dy
                                if dist_sq <= radius * radius:
                                    # 在圆形内，设为透明
                                    temp_surface.set_at((px, py), (0, 0, 0, 0))
            
            surface.blit(temp_surface, (x - radius, y - radius))
    
    # 定义武器掉落物类
    class WeaponDrop(pygame.sprite.Sprite):
        def __init__(self, x, y, weapon_name, image):
            super().__init__()
            self.weapon_name = weapon_name  # 武器名称
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.used = False  # 标记是否已被拾取
            
        def draw(self, surface, camera_x, camera_y):
            if not self.used:  # 只有未拾取时才绘制
                surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
    
    # 定义容器类：靠近按 E 花 3 秒拾取，随机获得手雷/金币/子弹
    class Container(pygame.sprite.Sprite):
        CONTAINER_SIZE = 48
        LOOT_TIME_MS = 3000
        def __init__(self, x, y):
            super().__init__()
            self.rect = pygame.Rect(x - self.CONTAINER_SIZE // 2, y - self.CONTAINER_SIZE // 2, self.CONTAINER_SIZE, self.CONTAINER_SIZE)
            self.looted = False
            # 奖励类型在首次被拾取时随机：'grenade', 'coins', 'ammo'
            self.reward_type = random.choice(['grenade', 'coins', 'ammo'])
        
        def draw(self, surface, camera_x, camera_y):
            if self.looted:
                return
            sx = self.rect.x - camera_x
            sy = self.rect.y - camera_y
            pygame.draw.rect(surface, (90, 70, 50), (sx, sy, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, (140, 110, 70), (sx, sy, self.rect.width, self.rect.height), 3)
            # 简单箱子图案
            pygame.draw.rect(surface, (60, 50, 40), (sx + 8, sy + 8, self.rect.width - 16, self.rect.height - 16))

    class KeyItem(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (8, 12), 6, 2)
            pygame.draw.rect(self.image, (255, 215, 0), (12, 10, 8, 4))
            pygame.draw.rect(self.image, (255, 215, 0), (17, 8, 2, 2))
            pygame.draw.rect(self.image, (255, 215, 0), (17, 14, 2, 2))
            self.rect = self.image.get_rect(center=(x, y))
            self.collected = False

        def draw(self, surface, camera_x, camera_y):
            if not self.collected:
                surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

    class SafeBox(pygame.sprite.Sprite):
        def __init__(self, x, y, reward_coins=35, reward_ammo=45):
            super().__init__()
            self.rect = pygame.Rect(x - 28, y - 28, 56, 56)
            self.opened = False
            self.reward_coins = reward_coins
            self.reward_ammo = reward_ammo

        def draw(self, surface, camera_x, camera_y):
            sx = self.rect.x - camera_x
            sy = self.rect.y - camera_y
            color = (55, 85, 95) if not self.opened else (70, 110, 120)
            pygame.draw.rect(surface, color, (sx, sy, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, (170, 200, 210), (sx, sy, self.rect.width, self.rect.height), 2)
            if not self.opened:
                pygame.draw.circle(surface, (230, 230, 230), (sx + 28, sy + 28), 9, 2)
            else:
                pygame.draw.line(surface, (120, 220, 120), (sx + 10, sy + 10), (sx + 46, sy + 46), 3)

    class LockedDoor(pygame.sprite.Sprite):
        def __init__(self, x, y, width=28, height=120):
            super().__init__()
            self.is_wall = True
            self.is_open = False
            self.image = pygame.Surface((width, height))
            self.image.fill((120, 90, 35))
            pygame.draw.rect(self.image, (200, 170, 80), (0, 0, width, height), 2)
            pygame.draw.circle(self.image, (220, 200, 80), (width // 2, height // 2), 6, 2)
            self.rect = self.image.get_rect(topleft=(x, y))

        def draw(self, surface, camera_x, camera_y):
            if not self.is_open:
                surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

    class Zombie(pygame.sprite.Sprite):
        def __init__(self, x, y, image):
            super().__init__()
            self.original_image = image
            self.image = image
            self.rect = self.image.get_rect(center=(x, y))
            self.facing_angle = 0
            self.speed = 1.6
            self.health = 120
            self.max_health = 120
            self.damage = 18
            self.attack_range = 46
            self.attack_cooldown = 900
            self.last_attack_time = 0

        def update(self, player, current_time, obstacles, enemy_targets=None, boss_targets=None):
            if enemy_targets is None:
                enemy_targets = []
            if boss_targets is None:
                boss_targets = []
            target = player
            target_group = "player"
            closest_enemy_dist = float("inf")
            for enemy in enemy_targets:
                if enemy.health <= 0:
                    continue
                d = math.sqrt((enemy.rect.centerx - self.rect.centerx) ** 2 + (enemy.rect.centery - self.rect.centery) ** 2)
                if d < closest_enemy_dist:
                    closest_enemy_dist = d
                    target = enemy
                    target_group = "enemy"
            for boss in boss_targets:
                if boss.health <= 0:
                    continue
                d = math.sqrt((boss.rect.centerx - self.rect.centerx) ** 2 + (boss.rect.centery - self.rect.centery) ** 2)
                if d < closest_enemy_dist:
                    closest_enemy_dist = d
                    target = boss
                    target_group = "boss"

            dx = target.rect.centerx - self.rect.centerx
            dy = target.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                dir_x = dx / dist
                dir_y = dy / dist
                self.facing_angle = math.degrees(math.atan2(-dir_y, dir_x))
            else:
                dir_x, dir_y = 0, 0

            if dist > self.attack_range:
                move_x = dir_x * self.speed
                move_y = dir_y * self.speed
                self.rect.x += int(move_x)
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        self.rect.x -= int(move_x)
                        break
                self.rect.y += int(move_y)
                for obstacle in obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        self.rect.y -= int(move_y)
                        break
            elif current_time - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = current_time
                if target_group == "player":
                    if player.armor >= self.damage:
                        player.armor -= self.damage
                    else:
                        remaining = self.damage - player.armor
                        player.armor = 0
                        player.health = max(0, player.health - remaining)
                    player.last_damage_time = current_time
                    player.last_armor_damage_time = current_time
                else:
                    target.health -= self.damage

        def draw(self, surface, camera_x, camera_y):
            rotated = pygame.transform.rotate(self.original_image, self.facing_angle)
            rr = rotated.get_rect(center=(self.rect.centerx - camera_x, self.rect.centery - camera_y))
            surface.blit(rotated, rr)
    
    # === 手雷类 ===
    class Grenade(pygame.sprite.Sprite):
        def __init__(self, x, y, target_x, target_y, explosion_radius=120, fuse_time=1500):
            """
            手雷：抛物线飞行，落地后延时爆炸
            fuse_time: 引信时间（毫秒），从投掷开始计时
            """
            super().__init__()
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (60, 120, 60), (6, 6), 6)
            pygame.draw.circle(self.image, (80, 160, 80), (6, 6), 4)
            self.rect = self.image.get_rect(center=(x, y))
            self.world_x = float(x)
            self.world_y = float(y)
            self.explosion_radius = explosion_radius
            self.creation_time = pygame.time.get_ticks()
            self.fuse_time = fuse_time
            self.exploded = False
            
            # 计算飞行方向和距离
            dx, dy = target_x - x, target_y - y
            dist = math.sqrt(dx * dx + dy * dy)
            max_throw_dist = 350  # 最大投掷距离
            if dist > max_throw_dist:
                dx = dx / dist * max_throw_dist
                dy = dy / dist * max_throw_dist
                dist = max_throw_dist
            
            # 飞行时间与距离成正比
            self.flight_time = 600 + dist * 0.8  # 毫秒
            self.start_x = float(x)
            self.start_y = float(y)
            self.end_x = x + dx
            self.end_y = y + dy
            self.height = 0  # 当前"高度"（用于视觉效果）
        
        def update(self, current_time, obstacles):
            elapsed = current_time - self.creation_time
            if elapsed >= self.fuse_time:
                self.exploded = True
                return
            
            # 飞行阶段
            if elapsed < self.flight_time:
                progress = elapsed / self.flight_time
                # 线性插值位置
                self.world_x = self.start_x + (self.end_x - self.start_x) * progress
                self.world_y = self.start_y + (self.end_y - self.start_y) * progress
                # 抛物线高度（视觉效果）
                self.height = math.sin(progress * math.pi) * 40
            else:
                self.world_x = self.end_x
                self.world_y = self.end_y
                self.height = 0
            
            self.rect.center = (int(self.world_x), int(self.world_y))
        
        def draw(self, surface, camera_x, camera_y):
            if self.exploded:
                return
            sx = int(self.world_x - camera_x)
            sy = int(self.world_y - camera_y - self.height)  # 减去高度模拟抛物线
            # 绘制阴影
            shadow_alpha = max(40, int(80 - self.height))
            shadow = pygame.Surface((14, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), (0, 0, 14, 8))
            surface.blit(shadow, (sx - 7, int(self.world_y - camera_y) - 4))
            # 绘制手雷
            surface.blit(self.image, (sx - 6, sy - 6))
            # 引信快要爆炸时闪烁红色
            elapsed = pygame.time.get_ticks() - self.creation_time
            if elapsed > self.fuse_time * 0.6:
                blink = int(elapsed / 100) % 2
                if blink:
                    pygame.draw.circle(surface, (255, 50, 50), (sx, sy), 4)
    
    # === 伤害数字飘字类 ===
    class DamageNumber:
        def __init__(self, x, y, damage, color=(255, 255, 100), is_crit=False):
            self.x = x
            self.y = y
            self.damage = damage
            self.color = color
            self.is_crit = is_crit
            self.creation_time = pygame.time.get_ticks()
            self.duration = 1000  # 持续1秒
            self.offset_x = random.randint(-15, 15)  # 随机水平偏移
            self.vy = -2.0  # 初始上升速度
        
        def update(self, current_time):
            elapsed = current_time - self.creation_time
            if elapsed >= self.duration:
                return False  # 移除
            self.y += self.vy
            self.vy += 0.03  # 轻微减速
            return True
        
        def draw(self, surface, camera_x, camera_y, font):
            elapsed = pygame.time.get_ticks() - self.creation_time
            if elapsed >= self.duration:
                return
            progress = elapsed / self.duration
            alpha = int(255 * (1.0 - progress))
            
            sx = int(self.x - camera_x + self.offset_x)
            sy = int(self.y - camera_y)
            
            # 暴击显示更大
            if self.is_crit:
                text_str = f"{self.damage}!"
            else:
                text_str = str(self.damage)
            
            text_surface = font.render(text_str, True, self.color)
            # 简单透明度效果：缩小文字
            if progress > 0.7:
                scale = 1.0 - (progress - 0.7) / 0.3 * 0.5
                new_w = max(1, int(text_surface.get_width() * scale))
                new_h = max(1, int(text_surface.get_height() * scale))
                text_surface = pygame.transform.scale(text_surface, (new_w, new_h))
            
            text_rect = text_surface.get_rect(center=(sx, sy))
            surface.blit(text_surface, text_rect)
    
    # === 连杀提示函数 ===
    def get_streak_info(streak):
        """根据连杀数返回提示文字和颜色"""
        streak_data = {
            2: ("双杀！", (255, 255, 100)),
            3: ("三连杀！", (255, 200, 50)),
            4: ("大杀特杀！", (255, 150, 0)),
            5: ("杀人如麻！", (255, 100, 0)),
            6: ("主宰比赛！", (255, 50, 50)),
            7: ("无人能挡！", (255, 0, 0)),
            8: ("超神！", (255, 0, 100)),
            9: ("超越神的存在！", (255, 0, 200)),
            10: ("传说！", (255, 50, 255)),
        }
        if streak >= 10:
            return streak_data[10]
        return streak_data.get(streak, (f"{streak}连杀！", (255, 200, 50)))
    
    # === 屏幕震动函数 ===
    def trigger_screen_shake(intensity, duration_ms):
        """触发屏幕震动"""
        nonlocal screen_shake_intensity, screen_shake_duration, screen_shake_start
        screen_shake_intensity = intensity
        screen_shake_duration = duration_ms
        screen_shake_start = pygame.time.get_ticks()
    
    def get_screen_shake_offset():
        """获取当前帧的震动偏移"""
        current = pygame.time.get_ticks()
        elapsed = current - screen_shake_start
        if elapsed >= screen_shake_duration or screen_shake_intensity <= 0:
            return 0, 0
        # 随时间衰减
        progress = elapsed / screen_shake_duration
        intensity = screen_shake_intensity * (1.0 - progress)
        ox = random.randint(int(-intensity), int(intensity))
        oy = random.randint(int(-intensity), int(intensity))
        return ox, oy
    
    def generate_map(world_width, world_height, player_rect, Obstacle_class, map_level=1):
        """地图生成函数：返回 (obstacles, roads, doors)。"""
        obstacles = []
        roads = []
        doors = []
        # 统一最小通行宽度，避免门洞/缝隙过窄导致角色难以进入
        min_passage = max(96, player_rect.width + 24)
        if 2 <= map_level <= 7:
            # ========== 地图2-7：室内楼层 ==========
            # 中央纵向走廊 + 左右房间，各层有参数化差异
            floor_names = {2: "实验室", 3: "服务器房", 4: "办公区", 5: "研发部", 6: "管理层", 7: "实验区"}
            wall = 50
            build_top, build_left = 0, 0
            build_height = world_height - 400
            build_width = world_width
            build_bottom = build_top + build_height

            # 各层参数化差异
            corr_w_table = {2: 200, 3: 240, 4: 180, 5: 220, 6: 260, 7: 200}
            h_corr_offset = {2: 0, 3: 100, 4: -100, 5: 50, 6: -50, 7: 150}
            room_door_w_table = {2: 80, 3: 100, 4: 70, 5: 90, 6: 80, 7: 110}

            corr_w = corr_w_table.get(map_level, 200)
            corr_left = (build_width - corr_w) // 2
            corr_right = corr_left + corr_w

            # 外墙（封闭）
            obstacles.append(Obstacle_class(build_left, build_top, build_width, wall))
            obstacles.append(Obstacle_class(build_left, build_top + wall, wall, build_height - wall))
            obstacles.append(Obstacle_class(build_left + build_width - wall, build_top + wall, wall, build_height - wall))
            obstacles.append(Obstacle_class(build_left, build_bottom - wall, build_width, wall))

            # 横向走廊（中部，连接左右）
            base_h_corr = 1700 + h_corr_offset.get(map_level, 0)
            h_corr_y0 = max(800, min(base_h_corr, build_bottom - 800))
            h_corr_y1 = h_corr_y0 + 100

            # 左侧区域
            left_area_x = build_left + wall
            left_area_w = corr_left - wall - left_area_x
            room_door_w = max(min_passage, room_door_w_table.get(map_level, 80))
            left_div_x = left_area_x + left_area_w // 2
            left_upper_top = build_top + wall
            left_upper_bottom = h_corr_y0
            left_upper_mid = left_upper_top + (left_upper_bottom - left_upper_top) // 2
            door_gap = min_passage
            door_y_start = left_upper_mid - door_gap // 2
            obstacles.append(Obstacle_class(left_div_x, left_upper_top, wall, door_y_start - left_upper_top))
            obstacles.append(Obstacle_class(left_div_x, door_y_start + door_gap, wall, left_upper_bottom - (door_y_start + door_gap)))
            half_w_left = left_div_x - left_area_x
            half_w_right = left_area_x + left_area_w - (left_div_x + wall)
            obstacles.append(Obstacle_class(left_area_x, left_upper_mid, (half_w_left - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(left_area_x + (half_w_left - room_door_w) // 2 + room_door_w, left_upper_mid, half_w_left - (half_w_left - room_door_w) // 2 - room_door_w, wall))
            obstacles.append(Obstacle_class(left_div_x + wall, left_upper_mid, (half_w_right - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(left_div_x + wall + (half_w_right - room_door_w) // 2 + room_door_w, left_upper_mid, half_w_right - (half_w_right - room_door_w) // 2 - room_door_w, wall))

            left_lower_top = h_corr_y1
            left_lower_bottom = build_bottom - wall
            left_lower_mid = left_lower_top + (left_lower_bottom - left_lower_top) // 2
            door_y_start2 = left_lower_mid - door_gap // 2
            obstacles.append(Obstacle_class(left_div_x, left_lower_top, wall, door_y_start2 - left_lower_top))
            obstacles.append(Obstacle_class(left_div_x, door_y_start2 + door_gap, wall, left_lower_bottom - (door_y_start2 + door_gap)))
            obstacles.append(Obstacle_class(left_area_x, left_lower_mid, (half_w_left - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(left_area_x + (half_w_left - room_door_w) // 2 + room_door_w, left_lower_mid, half_w_left - (half_w_left - room_door_w) // 2 - room_door_w, wall))
            obstacles.append(Obstacle_class(left_div_x + wall, left_lower_mid, (half_w_right - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(left_div_x + wall + (half_w_right - room_door_w) // 2 + room_door_w, left_lower_mid, half_w_right - (half_w_right - room_door_w) // 2 - room_door_w, wall))

            # 右侧区域（对称）
            right_area_x = corr_right + wall
            right_area_w = (build_left + build_width - wall) - right_area_x
            right_div_x = right_area_x + right_area_w // 2
            half_w_right_l = right_div_x - right_area_x
            half_w_right_r = right_area_x + right_area_w - (right_div_x + wall)
            right_upper_mid = left_upper_mid
            door_y_start_r = right_upper_mid - door_gap // 2
            obstacles.append(Obstacle_class(right_div_x, left_upper_top, wall, door_y_start_r - left_upper_top))
            obstacles.append(Obstacle_class(right_div_x, door_y_start_r + door_gap, wall, left_upper_bottom - (door_y_start_r + door_gap)))
            obstacles.append(Obstacle_class(right_area_x, right_upper_mid, (half_w_right_l - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(right_area_x + (half_w_right_l - room_door_w) // 2 + room_door_w, right_upper_mid, half_w_right_l - (half_w_right_l - room_door_w) // 2 - room_door_w, wall))
            obstacles.append(Obstacle_class(right_div_x + wall, right_upper_mid, (half_w_right_r - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(right_div_x + wall + (half_w_right_r - room_door_w) // 2 + room_door_w, right_upper_mid, half_w_right_r - (half_w_right_r - room_door_w) // 2 - room_door_w, wall))
            right_lower_mid = left_lower_mid
            door_y_start_r2 = right_lower_mid - door_gap // 2
            obstacles.append(Obstacle_class(right_div_x, left_lower_top, wall, door_y_start_r2 - left_lower_top))
            obstacles.append(Obstacle_class(right_div_x, door_y_start_r2 + door_gap, wall, left_lower_bottom - (door_y_start_r2 + door_gap)))
            obstacles.append(Obstacle_class(right_area_x, right_lower_mid, (half_w_right_l - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(right_area_x + (half_w_right_l - room_door_w) // 2 + room_door_w, right_lower_mid, half_w_right_l - (half_w_right_l - room_door_w) // 2 - room_door_w, wall))
            obstacles.append(Obstacle_class(right_div_x + wall, right_lower_mid, (half_w_right_r - room_door_w) // 2, wall))
            obstacles.append(Obstacle_class(right_div_x + wall + (half_w_right_r - room_door_w) // 2 + room_door_w, right_lower_mid, half_w_right_r - (half_w_right_r - room_door_w) // 2 - room_door_w, wall))

            # 中央走廊左右墙（分段留门洞）
            seg_door = max(100, min_passage + 8)
            upper_door_y = left_upper_mid - seg_door // 2
            obstacles.append(Obstacle_class(corr_left - wall, build_top + wall, wall, upper_door_y - (build_top + wall)))
            obstacles.append(Obstacle_class(corr_left - wall, upper_door_y + seg_door, wall, h_corr_y0 - (upper_door_y + seg_door)))
            lower_door_y = left_lower_mid - seg_door // 2
            obstacles.append(Obstacle_class(corr_left - wall, h_corr_y1, wall, lower_door_y - h_corr_y1))
            obstacles.append(Obstacle_class(corr_left - wall, lower_door_y + seg_door, wall, build_bottom - wall - (lower_door_y + seg_door)))
            obstacles.append(Obstacle_class(corr_right, build_top + wall, wall, upper_door_y - (build_top + wall)))
            obstacles.append(Obstacle_class(corr_right, upper_door_y + seg_door, wall, h_corr_y0 - (upper_door_y + seg_door)))
            obstacles.append(Obstacle_class(corr_right, h_corr_y1, wall, lower_door_y - h_corr_y1))
            obstacles.append(Obstacle_class(corr_right, lower_door_y + seg_door, wall, build_bottom - wall - (lower_door_y + seg_door)))

            # 横走廊左右墙
            obstacles.append(Obstacle_class(left_area_x, h_corr_y0 - wall, left_div_x - left_area_x - room_door_w, wall))
            obstacles.append(Obstacle_class(left_div_x + wall, h_corr_y0 - wall, corr_left - wall - (left_div_x + wall), wall))
            obstacles.append(Obstacle_class(left_area_x, h_corr_y1, left_div_x - left_area_x - room_door_w, wall))
            obstacles.append(Obstacle_class(left_div_x + wall, h_corr_y1, corr_left - wall - (left_div_x + wall), wall))
            obstacles.append(Obstacle_class(corr_right + wall, h_corr_y0 - wall, right_div_x - (corr_right + wall), wall))
            obstacles.append(Obstacle_class(right_div_x + wall + room_door_w, h_corr_y0 - wall, build_left + build_width - wall - (right_div_x + wall + room_door_w), wall))
            obstacles.append(Obstacle_class(corr_right + wall, h_corr_y1, right_div_x - (corr_right + wall), wall))
            obstacles.append(Obstacle_class(right_div_x + wall + room_door_w, h_corr_y1, build_left + build_width - wall - (right_div_x + wall + room_door_w), wall))

            return obstacles, roads, doors

        if map_level == 8:
            # ========== 地图8：天台 - Boss层 ==========
            wall = 50
            build_top, build_left = 0, 0
            build_width = world_width
            build_height = world_height - 400
            build_bottom = build_top + build_height
            # 外墙
            obstacles.append(Obstacle_class(build_left, build_top, build_width, wall))
            obstacles.append(Obstacle_class(build_left, build_top + wall, wall, build_height - wall))
            obstacles.append(Obstacle_class(build_left + build_width - wall, build_top + wall, wall, build_height - wall))
            obstacles.append(Obstacle_class(build_left, build_bottom - wall, build_width, wall))
            # 天台中央有几个掩体
            cx, cy = build_width // 2, build_height // 2
            obstacles.append(Obstacle_class(cx - 300, cy - 200, 150, wall))
            obstacles.append(Obstacle_class(cx + 150, cy - 200, 150, wall))
            obstacles.append(Obstacle_class(cx - 300, cy + 200, 150, wall))
            obstacles.append(Obstacle_class(cx + 150, cy + 200, 150, wall))
            obstacles.append(Obstacle_class(cx - 25, cy - 400, wall, 200))
            obstacles.append(Obstacle_class(cx - 25, cy + 200, wall, 200))
            return obstacles, roads, doors

        if map_level != 1:
            return obstacles, roads, doors
        # ========== 地图1：参考布局（仅布局不还原细节）==========
        # 底部出生区、中央入口通道、大中央大厅、贯穿左右的主横走廊、左右两侧竖向房间
        wall = 50
        build_top, build_left = 0, 0
        build_height = world_height - 400
        build_width = world_width
        build_bottom = build_top + build_height
        entrance_w = 200
        entrance_left = (build_width - entrance_w) // 2

        # ----- 外墙 -----
        obstacles.append(Obstacle_class(build_left, build_top, build_width, wall))
        obstacles.append(Obstacle_class(build_left, build_top + wall, wall, build_height - wall))
        obstacles.append(Obstacle_class(build_left + build_width - wall, build_top + wall, wall, build_height - wall))
        if entrance_left > 0:
            obstacles.append(Obstacle_class(build_left, build_bottom - wall, entrance_left, wall))
        if entrance_left + entrance_w < build_width:
            obstacles.append(Obstacle_class(build_left + entrance_left + entrance_w, build_bottom - wall, build_width - entrance_left - entrance_w, wall))

        # ----- 中央大厅（大矩形，底边留入口，左右边在横走廊高度留口）-----
        ch_left, ch_right = 700, 3300
        ch_top, ch_bottom = 1100, 2500
        h_corr_y0, h_corr_y1 = 1800, 1900  # 主横走廊 y 范围
        # 中央大厅左墙（横走廊处断开）
        obstacles.append(Obstacle_class(ch_left, ch_top, wall, h_corr_y0 - ch_top))
        obstacles.append(Obstacle_class(ch_left, h_corr_y1, wall, ch_bottom - h_corr_y1))
        # 中央大厅右墙
        obstacles.append(Obstacle_class(ch_right - wall, ch_top, wall, h_corr_y0 - ch_top))
        obstacles.append(Obstacle_class(ch_right - wall, h_corr_y1, wall, ch_bottom - h_corr_y1))
        # 中央大厅上墙
        obstacles.append(Obstacle_class(ch_left, ch_top, ch_right - ch_left, wall))
        # 中央大厅下墙（入口处断开）
        mid_x = (ch_left + ch_right) // 2
        if ch_left < entrance_left:
            obstacles.append(Obstacle_class(ch_left, ch_bottom - wall, entrance_left - ch_left, wall))
        if entrance_left + entrance_w < ch_right:
            obstacles.append(Obstacle_class(entrance_left + entrance_w, ch_bottom - wall, ch_right - (entrance_left + entrance_w), wall))

        # ----- 中央大厅最下面房间竖着分为 2:3:2（两道竖墙，留门洞）-----
        ch_bottom_room_y0 = h_corr_y1
        ch_bottom_room_y1 = ch_bottom - wall
        ch_bottom_room_w = ch_right - ch_left
        part_2 = ch_bottom_room_w * 2 // 7
        part_3 = ch_bottom_room_w * 3 // 7
        part_2_r = ch_bottom_room_w - part_2 - part_3
        div1_x = ch_left + part_2
        div2_x = ch_left + part_2 + part_3
        room_h = ch_bottom_room_y1 - ch_bottom_room_y0
        door_y_gap = min_passage
        door_y0 = ch_bottom_room_y0 + (room_h - door_y_gap) // 2
        door_y1 = door_y0 + door_y_gap
        obstacles.append(Obstacle_class(div1_x, ch_bottom_room_y0, wall, door_y0 - ch_bottom_room_y0))
        obstacles.append(Obstacle_class(div1_x, door_y1, wall, ch_bottom_room_y1 - door_y1))
        obstacles.append(Obstacle_class(div2_x, ch_bottom_room_y0, wall, door_y0 - ch_bottom_room_y0))
        obstacles.append(Obstacle_class(div2_x, door_y1, wall, ch_bottom_room_y1 - door_y1))

        # ----- 左翼：竖条房间，主横走廊从中穿过 -----
        left_wing_x = build_left + wall
        left_wing_w = ch_left - left_wing_x - wall  # 到中央大厅左墙
        # 左翼与中央大厅之间的竖墙（横走廊处断开）
        obstacles.append(Obstacle_class(ch_left - wall, build_top + wall, wall, h_corr_y0 - (build_top + wall)))
        obstacles.append(Obstacle_class(ch_left - wall, h_corr_y1, wall, build_bottom - wall - h_corr_y1))
        door_w = min_passage
        # 左翼与横走廊之间的横墙（留出入口，使上/中/下房间都能进走廊）
        half = (left_wing_w - door_w) // 2
        obstacles.append(Obstacle_class(left_wing_x, h_corr_y0 - wall, half, wall))
        obstacles.append(Obstacle_class(left_wing_x + half + door_w, h_corr_y0 - wall, left_wing_w - half - door_w, wall))
        obstacles.append(Obstacle_class(left_wing_x, h_corr_y1, half, wall))
        obstacles.append(Obstacle_class(left_wing_x + half + door_w, h_corr_y1, left_wing_w - half - door_w, wall))
        # 左翼上房间内再分（横墙留门洞）
        left_mid_y = build_top + wall + (h_corr_y0 - wall - (build_top + wall)) // 2
        obstacles.append(Obstacle_class(left_wing_x, left_mid_y, (left_wing_w - door_w) // 2, wall))
        obstacles.append(Obstacle_class(left_wing_x + (left_wing_w - door_w) // 2 + door_w, left_mid_y, left_wing_w - (left_wing_w - door_w) // 2 - door_w, wall))

        # ----- 右翼：对称 -----
        right_wing_w = (build_left + build_width - wall) - (ch_right + wall)
        right_wing_x = ch_right + wall
        # right_wing_w 已由上式自动按世界尺寸计算
        obstacles.append(Obstacle_class(ch_right, build_top + wall, wall, h_corr_y0 - (build_top + wall)))
        obstacles.append(Obstacle_class(ch_right, h_corr_y1, wall, build_bottom - wall - h_corr_y1))
        # 右翼与横走廊之间的横墙（留出入口）
        half_r = (right_wing_w - door_w) // 2
        obstacles.append(Obstacle_class(right_wing_x, h_corr_y0 - wall, half_r, wall))
        obstacles.append(Obstacle_class(right_wing_x + half_r + door_w, h_corr_y0 - wall, right_wing_w - half_r - door_w, wall))
        obstacles.append(Obstacle_class(right_wing_x, h_corr_y1, half_r, wall))
        obstacles.append(Obstacle_class(right_wing_x + half_r + door_w, h_corr_y1, right_wing_w - half_r - door_w, wall))
        right_mid_y = build_top + wall + (h_corr_y0 - wall - (build_top + wall)) // 2
        obstacles.append(Obstacle_class(right_wing_x, right_mid_y, (right_wing_w - door_w) // 2, wall))
        obstacles.append(Obstacle_class(right_wing_x + (right_wing_w - door_w) // 2 + door_w, right_mid_y, right_wing_w - (right_wing_w - door_w) // 2 - door_w, wall))

        # ----- 中央大厅上方：顶区与大厅之间的横墙（留通道）-----
        top_wall_y = ch_top - wall
        gap_w = max(120, min_passage + 24)
        # 左段：左翼右边界到中央大厅左墙，中间留门
        seg_w = ch_left - left_wing_x
        if seg_w > gap_w:
            obstacles.append(Obstacle_class(left_wing_x, top_wall_y, (seg_w - gap_w) // 2, wall))
            obstacles.append(Obstacle_class(left_wing_x + (seg_w - gap_w) // 2 + gap_w, top_wall_y, seg_w - (seg_w - gap_w) // 2 - gap_w, wall))
        # 右段：中央大厅右墙到右翼右边界，中间留门
        seg_w = (build_left + build_width - wall) - ch_right
        if seg_w > gap_w:
            obstacles.append(Obstacle_class(ch_right, top_wall_y, (seg_w - gap_w) // 2, wall))
            obstacles.append(Obstacle_class(ch_right + (seg_w - gap_w) // 2 + gap_w, top_wall_y, seg_w - (seg_w - gap_w) // 2 - gap_w, wall))

        # ----- 上方中央大厅竖向分隔（与下方 2:3:2 对齐）-----
        upper_hall_y0 = ch_top + wall
        upper_hall_y1 = h_corr_y0
        upper_h = upper_hall_y1 - upper_hall_y0
        upper_door_gap = min_passage
        upper_door_y0 = upper_hall_y0 + (upper_h - upper_door_gap) // 2
        upper_door_y1 = upper_door_y0 + upper_door_gap
        # 左竖墙（x=div1_x，与下方对齐）
        obstacles.append(Obstacle_class(div1_x, upper_hall_y0, wall, upper_door_y0 - upper_hall_y0))
        obstacles.append(Obstacle_class(div1_x, upper_door_y1, wall, upper_hall_y1 - upper_door_y1))
        # 右竖墙（x=div2_x，与下方对齐）
        obstacles.append(Obstacle_class(div2_x, upper_hall_y0, wall, upper_door_y0 - upper_hall_y0))
        obstacles.append(Obstacle_class(div2_x, upper_door_y1, wall, upper_hall_y1 - upper_door_y1))

        # ----- 上方中央大厅左右"2"区：横向走廊（平移到主横走廊缺口上方）-----
        corr_gap = min_passage  # 走廊通道高度
        corr_bot_wall_y = h_corr_y0 - wall        # 下墙紧贴主走廊上沿 (1750)
        corr_top_wall_y = corr_bot_wall_y - corr_gap - wall  # 上墙 (1620)
        # 左侧"2"区（ch_left+wall 到 div1_x）
        lx0 = ch_left + wall
        lw = div1_x - lx0
        obstacles.append(Obstacle_class(lx0, corr_bot_wall_y, lw, wall))   # y=1750 保留
        # 右侧"2"区（div2_x+wall 到 ch_right-wall）
        rx0 = div2_x + wall
        rw = (ch_right - wall) - rx0
        obstacles.append(Obstacle_class(rx0, corr_bot_wall_y, rw, wall))   # y=1750 保留

        # ----- 下方中央大厅左右"2"区：横向走廊（主横走廊缺口下方）-----
        lower_corr_top_wall_y = h_corr_y1                          # y=1900
        # 左侧"2"区
        obstacles.append(Obstacle_class(lx0, lower_corr_top_wall_y, lw, wall))  # y=1900 保留
        # 右侧"2"区
        obstacles.append(Obstacle_class(rx0, lower_corr_top_wall_y, rw, wall))  # y=1900 保留

        # ----- 左翼走廊下方：横墙分出下半区（留门洞）-----
        left_lower_y0 = h_corr_y1 + wall   # 1950
        left_lower_y1 = build_bottom - wall  # 3550
        left_lower_mid = left_lower_y0 + (left_lower_y1 - left_lower_y0) // 2
        obstacles.append(Obstacle_class(left_wing_x, left_lower_mid, (left_wing_w - door_w) // 2, wall))
        obstacles.append(Obstacle_class(left_wing_x + (left_wing_w - door_w) // 2 + door_w, left_lower_mid, left_wing_w - (left_wing_w - door_w) // 2 - door_w, wall))

        # ----- 右翼走廊下方：对称横墙（留门洞）-----
        right_lower_y0 = h_corr_y1 + wall
        right_lower_y1 = build_bottom - wall
        right_lower_mid = right_lower_y0 + (right_lower_y1 - right_lower_y0) // 2
        obstacles.append(Obstacle_class(right_wing_x, right_lower_mid, (right_wing_w - door_w) // 2, wall))
        obstacles.append(Obstacle_class(right_wing_x + (right_wing_w - door_w) // 2 + door_w, right_lower_mid, right_wing_w - (right_wing_w - door_w) // 2 - door_w, wall))

        # ========== 在所有缺口处创建门 ==========
        dt = 20  # 门厚度
        wo = (wall - dt) // 2  # 墙厚与门厚的偏移量，用于居中
        corr_h = h_corr_y1 - h_corr_y0  # 走廊缺口高度 100

        # --- 辅助：创建一对对开门（互相配对，联动开关）---
        def add_double_h(x, y, total_w, h):
            """横向对开门：左扇铰链在左，右扇铰链在右"""
            half = total_w // 2
            d1 = Door(x, y, half, h, hinge='left')
            d2 = Door(x + half, y, total_w - half, h, hinge='right')
            d1.pair = d2
            d2.pair = d1
            doors.append(d1)
            doors.append(d2)

        def add_double_v(x, y, w, total_h):
            """竖向对开门：上扇铰链在上，下扇铰链在下"""
            half = total_h // 2
            d1 = Door(x, y, w, half, hinge='top')
            d2 = Door(x, y + half, w, total_h - half, hinge='bottom')
            d1.pair = d2
            d2.pair = d1
            doors.append(d1)
            doors.append(d2)

        # 1. 外墙底部入口（双开横门，entrance_w=200）
        add_double_h(entrance_left, build_bottom - wall + wo, entrance_w, dt)
        # 2. 中央大厅左墙 - 主横走廊缺口（单扇竖门）
        doors.append(Door(ch_left + wo, h_corr_y0, dt, corr_h))
        # 3. 中央大厅右墙 - 主横走廊缺口（单扇竖门）
        doors.append(Door(ch_right - wall + wo, h_corr_y0, dt, corr_h))
        # 4. 中央大厅下墙 - 入口缺口（双开横门，entrance_w=200）
        add_double_h(entrance_left, ch_bottom - wall + wo, entrance_w, dt)
        # 5. 下方房间 - 第一道竖墙门洞（单扇小门）
        doors.append(Door(div1_x + wo, door_y0, dt, door_y_gap))
        # 6. 下方房间 - 第二道竖墙门洞（单扇小门）
        doors.append(Door(div2_x + wo, door_y0, dt, door_y_gap))
        # 7. 左翼上走廊门（单扇小门）
        doors.append(Door(left_wing_x + half, h_corr_y0 - wall + wo, door_w, dt))
        # 8. 左翼下走廊门（单扇小门）
        doors.append(Door(left_wing_x + half, h_corr_y1 + wo, door_w, dt))
        # 9. 左翼上房间横墙门洞（单扇小门）
        doors.append(Door(left_wing_x + (left_wing_w - door_w) // 2, left_mid_y + wo, door_w, dt))
        # 10. （已删除，与#2重复）
        # 11. 右翼上走廊门（单扇小门）
        doors.append(Door(right_wing_x + half_r, h_corr_y0 - wall + wo, door_w, dt))
        # 12. 右翼下走廊门（单扇小门）
        doors.append(Door(right_wing_x + half_r, h_corr_y1 + wo, door_w, dt))
        # 13. 右翼上房间横墙门洞（单扇小门）
        doors.append(Door(right_wing_x + (right_wing_w - door_w) // 2, right_mid_y + wo, door_w, dt))
        # 14. （已删除，与#3重复）
        # 15. 顶区左段门（单扇横门）
        seg_w_left = ch_left - left_wing_x
        doors.append(Door(left_wing_x + (seg_w_left - gap_w) // 2, top_wall_y + wo, gap_w, dt))
        # 16. 顶区右段门（单扇横门）
        seg_w_right = (build_left + build_width - wall) - ch_right
        doors.append(Door(ch_right + (seg_w_right - gap_w) // 2, top_wall_y + wo, gap_w, dt))
        # 17. 上方中央大厅 - 第一道竖墙门洞（单扇小门）
        doors.append(Door(div1_x + wo, upper_door_y0, dt, upper_door_gap))
        # 18. 上方中央大厅 - 第二道竖墙门洞（单扇小门）
        doors.append(Door(div2_x + wo, upper_door_y0, dt, upper_door_gap))
        # 19. 左翼下方横墙门洞（单扇小门）
        doors.append(Door(left_wing_x + (left_wing_w - door_w) // 2, left_lower_mid + wo, door_w, dt))
        # 20. 右翼下方横墙门洞（单扇小门）
        doors.append(Door(right_wing_x + (right_wing_w - door_w) // 2, right_lower_mid + wo, door_w, dt))

        return obstacles, roads, doors

    # 在障碍物附近生成医疗包（用于地图 2-9）；当前已清空，不生成任何物品
    def generate_medkits_near_obstacles(obstacles_list, count=3):
        return []
    
    # 生成弹药箱函数；当前已清空，不生成任何物品
    def generate_ammo_boxes(obstacles_list, count=4):
        return []
    
    # 生成容器位置：在障碍物附近随机不重叠位置，每张地图若干容器
    def generate_container_positions(obstacles_list, world_width, world_height, count=6):
        out = []
        size = Container.CONTAINER_SIZE + 20
        margin = 80
        for _ in range(count * 3):  # 多试几次
            if len(out) >= count:
                break
            x = random.randint(margin, world_width - margin)
            y = random.randint(margin, world_height - margin)
            rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
            if any(rect.colliderect(o.rect) for o in obstacles_list if hasattr(o, 'rect')):
                continue
            if any(abs(x - px) < size and abs(y - py) < size for px, py in out):
                continue
            out.append((x, y))
        return out

    def generate_zombies_for_map(obstacles_list, zombie_img, count=6):
        zombies = []
        z_rect = zombie_img.get_rect()
        zw, zh = z_rect.width, z_rect.height
        margin = max(zw, zh) // 2 + 10
        for _ in range(count * 6):
            if len(zombies) >= count:
                break
            x = random.randint(margin, world_width - margin)
            y = random.randint(margin, world_height - 450)
            test_rect = pygame.Rect(x - zw // 2, y - zh // 2, zw, zh)
            if test_rect.colliderect(player.rect):
                continue
            if any(test_rect.colliderect(o.rect) for o in obstacles_list):
                continue
            if any(test_rect.colliderect(z.rect.inflate(20, 20)) for z in zombies):
                continue
            zombies.append(Zombie(x, y, zombie_img))
        return zombies

    def pick_free_rect(obstacles_list, width, height, used_rects=None, attempts=300):
        if used_rects is None:
            used_rects = []
        margin = 80
        for _ in range(attempts):
            x = random.randint(margin, world_width - width - margin)
            y = random.randint(margin, world_height - height - 500)
            rect = pygame.Rect(x, y, width, height)
            if rect.colliderect(player.rect.inflate(220, 220)):
                continue
            if any(rect.colliderect(o.rect) for o in obstacles_list):
                continue
            if any(rect.colliderect(u) for u in used_rects):
                continue
            return rect
        return None
    
    def generate_medkits_for_stage1(player_pos, enemies_list, obstacles_list, count=3):
        """为关卡1生成医疗包；当前已清空，不生成任何物品"""
        return []

    # 实例化 Player
    player = Player(player_start_x, player_start_y, player_image, player_speed, sprint_speed, max_player_health, max_armor, max_stamina)

    # 保存每个地图的数据（障碍物、道路、敌人）
    maps_data = {}  # 格式: {map_level: {'obstacles': [...], 'roads': [...], 'enemies': [...]}}
    
    # 生成第一张地图的障碍物和马路（使用正确的随机种子）
    random.seed(42 + map_level)  # map_level = 1，所以是 random.seed(43)，但为了保持一致性，应该用42+1
    initial_obstacles, initial_roads, initial_doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
    obstacles = list(initial_obstacles) # 当前地图的障碍物
    roads = list(initial_roads) # 当前地图的道路
    doors = list(initial_doors) # 当前地图的门
    
    # 门关闭时作为碰撞体加入 obstacles
    for door in doors:
        if not door.is_open:
            obstacles.append(door)
    
    # 保存第一张地图的数据（只保存位置和大小信息）
    maps_data[map_level] = {
        'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in initial_obstacles],
        'roads': [(r.x, r.y, r.width, r.height) for r in roads],
        'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
    }

    # 地图1：出生点在大楼外面，地图最下面中心，正对大楼入口
    if map_level == 1:
        player.rect.x = world_width // 2 - player.rect.width // 2
        player.rect.y = world_height - player.rect.height - 50

    # 生成敌人的辅助函数；地图1和地图2在大楼内各房间随机位置生成
    def _get_floor_rooms(ml):
        """获取指定楼层的房间列表，用于敌人生成"""
        wall = 50
        build_bottom = world_height - 400
        corr_w_table = {2: 200, 3: 240, 4: 180, 5: 220, 6: 260, 7: 200}
        h_corr_offset = {2: 0, 3: 100, 4: -100, 5: 50, 6: -50, 7: 150}
        corr_w = corr_w_table.get(ml, 200)
        corr_left = (world_width - corr_w) // 2
        corr_right = corr_left + corr_w
        base_h_corr = 1700 + h_corr_offset.get(ml, 0)
        h_corr_y0 = max(800, min(base_h_corr, build_bottom - 800))
        h_corr_y1 = h_corr_y0 + 100
        left_area_x = wall
        left_area_w = corr_left - wall - left_area_x
        left_div_x = left_area_x + left_area_w // 2
        left_upper_top = wall
        left_upper_bottom = h_corr_y0
        left_upper_mid = left_upper_top + (left_upper_bottom - left_upper_top) // 2
        left_lower_top = h_corr_y1
        left_lower_bottom = build_bottom - wall
        left_lower_mid = left_lower_top + (left_lower_bottom - left_lower_top) // 2
        right_area_x = corr_right + wall
        right_area_w = (world_width - wall) - right_area_x
        right_div_x = right_area_x + right_area_w // 2
        rooms = [
            (left_area_x, left_upper_top, left_div_x - left_area_x, left_upper_mid - left_upper_top),
            (left_area_x, left_upper_mid + wall, left_div_x - left_area_x, left_upper_bottom - left_upper_mid - wall),
            (left_div_x + wall, left_upper_top, left_area_x + left_area_w - left_div_x - wall, left_upper_mid - left_upper_top),
            (left_div_x + wall, left_upper_mid + wall, left_area_x + left_area_w - left_div_x - wall, left_upper_bottom - left_upper_mid - wall),
            (left_area_x, left_lower_top, left_div_x - left_area_x, left_lower_mid - left_lower_top),
            (left_area_x, left_lower_mid + wall, left_div_x - left_area_x, left_lower_bottom - left_lower_mid - wall),
            (left_div_x + wall, left_lower_top, left_area_x + left_area_w - left_div_x - wall, left_lower_mid - left_lower_top),
            (left_div_x + wall, left_lower_mid + wall, left_area_x + left_area_w - left_div_x - wall, left_lower_bottom - left_lower_mid - wall),
            (right_area_x, left_upper_top, right_div_x - right_area_x, left_upper_mid - left_upper_top),
            (right_area_x, left_upper_mid + wall, right_div_x - right_area_x, left_upper_bottom - left_upper_mid - wall),
            (right_div_x + wall, left_upper_top, right_area_x + right_area_w - right_div_x - wall, left_upper_mid - left_upper_top),
            (right_div_x + wall, left_upper_mid + wall, right_area_x + right_area_w - right_div_x - wall, left_upper_bottom - left_upper_mid - wall),
            (right_area_x, left_lower_top, right_div_x - right_area_x, left_lower_mid - left_lower_top),
            (right_area_x, left_lower_mid + wall, right_div_x - right_area_x, left_lower_bottom - left_lower_mid - wall),
            (right_div_x + wall, left_lower_top, right_area_x + right_area_w - right_div_x - wall, left_lower_mid - left_lower_top),
            (right_div_x + wall, left_lower_mid + wall, right_area_x + right_area_w - right_div_x - wall, left_lower_bottom - left_lower_mid - wall),
        ]
        return rooms

    def generate_enemies_for_map(obstacles_list, player_rect, enemy_img, current_map_level=1):
        if 2 <= current_map_level <= 7:
            rooms_list = _get_floor_rooms(current_map_level)
            enemy_rect = enemy_img.get_rect()
            ew, eh = enemy_rect.width, enemy_rect.height
            margin = max(ew, eh) // 2 + 5
            def random_pos_floor(room, obs_list):
                left, top, w, h = room
                if w <= margin * 2 or h <= margin * 2:
                    return (left + w // 2, top + h // 2)
                for _ in range(50):
                    cx = random.randint(left + margin, left + w - margin)
                    cy = random.randint(top + margin, top + h - margin)
                    test_rect = pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh)
                    if not any(test_rect.colliderect(o.rect) for o in obs_list):
                        return (cx, cy)
                return (left + w // 2, top + h // 2)
            result = []
            base_count = 2 + (current_map_level - 2)  # 楼层越高敌人越多
            for room in rooms_list:
                count = random.randint(base_count, base_count + 2)
                enemy_hp = 100 + (current_map_level - 2) * 20  # 越高层血越多
                for _ in range(count):
                    cx, cy = random_pos_floor(room, obstacles_list)
                    result.append(Enemy(cx, cy, enemy_img, health=enemy_hp))
            return result
        if current_map_level == 8:
            # Boss层：少量普通敌人作为小兵
            enemy_rect = enemy_img.get_rect()
            ew, eh = enemy_rect.width, enemy_rect.height
            result = []
            cx_center = world_width // 2
            cy_center = (world_height - 400) // 2
            for _ in range(8):
                ex = cx_center + random.randint(-800, 800)
                ey = cy_center + random.randint(-600, 600)
                test_rect = pygame.Rect(ex - ew // 2, ey - eh // 2, ew, eh)
                if not any(test_rect.colliderect(o.rect) for o in obstacles_list):
                    result.append(Enemy(ex, ey, enemy_img, health=200))
            return result
        if current_map_level != 1:
            return []
        # 地图1：房间区域 (left, top, width, height)，与 generate_map 布局一致
        wall = 50
        ch_left, ch_right = 700, 3300
        ch_top, ch_bottom = 1100, 2500
        h_corr_y0, h_corr_y1 = 1800, 1900
        build_bottom = 3600  # world_height - 400 约 3600
        ch_bottom_room_w = ch_right - ch_left
        part_2 = ch_bottom_room_w * 2 // 7
        part_3 = ch_bottom_room_w * 3 // 7
        div1_x = ch_left + part_2
        div2_x = ch_left + part_2 + part_3
        left_wing_x = wall
        right_wing_x = ch_right + wall
        left_wing_w = ch_left - left_wing_x - wall
        right_wing_w = 3950 - right_wing_x  # build_left + build_width - wall - right_wing_x
        rooms = [
            (ch_left + wall, ch_top + wall, div1_x - (ch_left + wall), h_corr_y0 - (ch_top + wall)),   # 中央大厅上方左
            (div1_x + wall, ch_top + wall, div2_x - div1_x - wall * 2, h_corr_y0 - (ch_top + wall)), # 中央大厅上方中
            (div2_x + wall, ch_top + wall, ch_right - div2_x - wall * 2, h_corr_y0 - (ch_top + wall)), # 中央大厅上方右
            (ch_left + wall, h_corr_y1 + wall, div1_x - (ch_left + wall), ch_bottom - h_corr_y1 - wall * 2), # 中央下方左
            (div1_x + wall, h_corr_y1 + wall, div2_x - div1_x - wall * 2, ch_bottom - h_corr_y1 - wall * 2),   # 中央下方中
            (div2_x + wall, h_corr_y1 + wall, ch_right - div2_x - wall * 2, ch_bottom - h_corr_y1 - wall * 2), # 中央下方右
            (left_wing_x + wall, ch_top + wall, left_wing_w - wall * 2, h_corr_y0 - (ch_top + wall)),  # 左翼上
            (left_wing_x + wall, h_corr_y1 + wall, left_wing_w - wall * 2, build_bottom - h_corr_y1 - wall * 2), # 左翼下
            (right_wing_x + wall, ch_top + wall, right_wing_w - wall * 2, h_corr_y0 - (ch_top + wall)), # 右翼上
            (right_wing_x + wall, h_corr_y1 + wall, right_wing_w - wall * 2, build_bottom - h_corr_y1 - wall * 2), # 右翼下
        ]
        enemy_rect = enemy_img.get_rect()
        ew, eh = enemy_rect.width, enemy_rect.height
        margin = max(ew, eh) // 2 + 5

        def random_pos_in_room(room, obstacles_list):
            left, top, w, h = room
            if w <= margin * 2 or h <= margin * 2:
                return (left + w // 2, top + h // 2)
            for _ in range(50):
                cx = random.randint(left + margin, left + w - margin) if w > margin * 2 else left + w // 2
                cy = random.randint(top + margin, top + h - margin) if h > margin * 2 else top + h // 2
                test_rect = pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh)
                if not any(test_rect.colliderect(o.rect) for o in obstacles_list):
                    return (cx, cy)
            return (left + w // 2, top + h // 2)

        result = []
        for room in rooms:
            count = random.randint(2, 3)  # 每个房间生成 2~3 个敌人
            for _ in range(count):
                cx, cy = random_pos_in_room(room, obstacles_list)
                result.append(Enemy(cx, cy, enemy_img, health=100))
        return result
    
    # 检查两点之间的线段是否被障碍物阻挡
    def is_line_blocked_by_obstacle(start_x, start_y, end_x, end_y, obstacles_list):
        """
        检查从起点到终点的线段是否与任何障碍物相交
        返回True如果被阻挡，False如果没有阻挡
        使用线段-矩形相交检测
        """
        # 对每个障碍物检查线段是否与其矩形相交
        for obstacle in obstacles_list:
            rect = obstacle.rect
            
            # 快速排除：如果起点和终点都在障碍物的同一侧，则不相交
            # 检查起点和终点是否都在障碍物左侧
            if start_x < rect.left and end_x < rect.left:
                continue
            # 检查起点和终点是否都在障碍物右侧
            if start_x > rect.right and end_x > rect.right:
                continue
            # 检查起点和终点是否都在障碍物上方
            if start_y < rect.top and end_y < rect.top:
                continue
            # 检查起点和终点是否都在障碍物下方
            if start_y > rect.bottom and end_y > rect.bottom:
                continue
            
            # 如果起点或终点在障碍物内，则被阻挡
            if rect.collidepoint(start_x, start_y) or rect.collidepoint(end_x, end_y):
                return True
            
            # 检查线段是否与矩形的四条边相交
            # 线段参数方程: P(t) = start + t * (end - start), t in [0, 1]
            dx = end_x - start_x
            dy = end_y - start_y
            
            # 检查与矩形的四条边是否相交
            # 左边缘: x = rect.left
            if dx != 0:
                t = (rect.left - start_x) / dx
                if 0 <= t <= 1:
                    y = start_y + t * dy
                    if rect.top <= y <= rect.bottom:
                        return True
            
            # 右边缘: x = rect.right
            if dx != 0:
                t = (rect.right - start_x) / dx
                if 0 <= t <= 1:
                    y = start_y + t * dy
                    if rect.top <= y <= rect.bottom:
                        return True
            
            # 上边缘: y = rect.top
            if dy != 0:
                t = (rect.top - start_y) / dy
                if 0 <= t <= 1:
                    x = start_x + t * dx
                    if rect.left <= x <= rect.right:
                        return True
            
            # 下边缘: y = rect.bottom
            if dy != 0:
                t = (rect.bottom - start_y) / dy
                if 0 <= t <= 1:
                    x = start_x + t * dx
                    if rect.left <= x <= rect.right:
                        return True
        
        return False  # 没有被阻挡
    
    # RPG范围伤害函数
    def apply_explosion_damage(explosion_x, explosion_y, explosion_radius, base_damage, enemies_list, boss_list, obstacles_list):
        """
        应用爆炸范围伤害，伤害随距离衰减
        explosion_x, explosion_y: 爆炸中心坐标
        explosion_radius: 爆炸范围（像素）
        base_damage: 基础伤害值
        enemies_list: 敌人列表
        boss_list: Boss列表
        obstacles_list: 障碍物列表（用于检测阻挡）
        """
        nonlocal kill_count, kill_streak, last_kill_time, streak_message, streak_message_time, streak_message_color
        # 创建爆炸特效
        explosion = Explosion(explosion_x, explosion_y, explosion_radius, duration=500)
        explosions.append(explosion)
        
        explosion_center = pygame.math.Vector2(explosion_x, explosion_y)
        damaged_enemies = []
        damaged_bosses = []
        current_time = pygame.time.get_ticks()
        
        # 对敌人造成范围伤害
        for enemy in enemies_list[:]:
            enemy_center = pygame.math.Vector2(enemy.rect.centerx, enemy.rect.centery)
            distance = explosion_center.distance_to(enemy_center)
            
            if distance <= explosion_radius:
                # 检查是否被障碍物阻挡
                if is_line_blocked_by_obstacle(explosion_x, explosion_y, enemy.rect.centerx, enemy.rect.centery, obstacles_list):
                    continue  # 被障碍物阻挡，跳过这个敌人
                # 伤害衰减：距离越远伤害越低，最小伤害为基础伤害的20%
                # 衰减公式：damage = base_damage * (1 - distance / explosion_radius) * 0.8 + base_damage * 0.2
                damage_multiplier = 1.0 - (distance / explosion_radius) * 0.8
                damage = int(base_damage * damage_multiplier)
                if damage < int(base_damage * 0.2):  # 确保最小伤害
                    damage = int(base_damage * 0.2)
                
                enemy.health -= damage
                enemy.is_aggroed = True
                damaged_enemies.append((enemy, damage))
                # 爆炸伤害飘字（橙色）
                damage_numbers.append(DamageNumber(enemy.rect.centerx, enemy.rect.top, damage, (255, 160, 50)))
                
                if enemy.health <= 0:
                    # 爆炸击杀奖励
                    kill_count += 1
                    coin_reward = 5 if enemy.max_health == 100 else 15
                    player.coins += coin_reward
                    if current_time - last_kill_time < kill_streak_timeout:
                        kill_streak += 1
                    else:
                        kill_streak = 1
                    last_kill_time = current_time
                    if kill_streak >= 2:
                        streak_message, streak_message_color = get_streak_info(kill_streak)
                        streak_message_time = current_time
                    damage_numbers.append(DamageNumber(enemy.rect.centerx, enemy.rect.top - 20, coin_reward, (255, 215, 0), is_crit=True))
                    # 检查是否是高级敌人，如果是则掉落对应武器
                    if enemy.max_health == 250:
                        if not hasattr(enemy, 'drop_weapon') or not enemy.drop_weapon:
                            enemy.drop_weapon = get_random_elite_weapon()
                        weapon_drop = WeaponDrop(enemy.rect.centerx, enemy.rect.centery, enemy.drop_weapon, elite_enemy_image)
                        weapon_drops_for_current_map.append(weapon_drop)
                        print(f"高级敌人被爆炸击杀！掉落{enemy.drop_weapon}！")
                    corpses_for_current_map.append(Corpse(enemy.rect.centerx, enemy.rect.centery, enemy.original_image, enemy.facing_angle))
                    enemies_list.remove(enemy)
        
        # 对Boss造成范围伤害
        for boss in boss_list[:]:
            boss_center = pygame.math.Vector2(boss.rect.centerx, boss.rect.centery)
            distance = explosion_center.distance_to(boss_center)
            
            if distance <= explosion_radius:
                # 检查是否被障碍物阻挡
                if is_line_blocked_by_obstacle(explosion_x, explosion_y, boss.rect.centerx, boss.rect.centery, obstacles_list):
                    continue  # 被障碍物阻挡，跳过这个Boss
                # 伤害衰减
                damage_multiplier = 1.0 - (distance / explosion_radius) * 0.8
                damage = int(base_damage * damage_multiplier)
                if damage < int(base_damage * 0.2):
                    damage = int(base_damage * 0.2)
                
                boss.health -= damage
                boss.is_aggroed = True
                damaged_bosses.append((boss, damage))
                damage_numbers.append(DamageNumber(boss.rect.centerx, boss.rect.top, damage, (255, 100, 100)))
                
                if boss.health <= 0:
                    kill_count += 1
                    player.coins += 50
                    if current_time - last_kill_time < kill_streak_timeout:
                        kill_streak += 1
                    else:
                        kill_streak = 1
                    last_kill_time = current_time
                    if kill_streak >= 2:
                        streak_message, streak_message_color = get_streak_info(kill_streak)
                        streak_message_time = current_time
                    damage_numbers.append(DamageNumber(boss.rect.centerx, boss.rect.top - 30, 50, (255, 215, 0), is_crit=True))
                    weapon_drop = WeaponDrop(boss.rect.centerx, boss.rect.centery, "rpg", boss_tank_image)
                    weapon_drops_for_current_map.append(weapon_drop)
                    print(f"Boss被爆炸击杀！掉落rpg武器！")
                    corpses_for_current_map.append(Corpse(boss.rect.centerx, boss.rect.centery, boss.original_image, boss.facing_angle))
                    boss_list.remove(boss)
        
        return damaged_enemies, damaged_bosses
    
    # 生成高级敌人的函数
    def get_random_elite_weapon():
        """随机选择高级敌人掉落武器：40%步枪，50%冲锋枪，10%狙击枪"""
        rand = random.random()
        if rand < 0.4:
            return "步枪"
        elif rand < 0.9:  # 0.4到0.9之间，即50%
            return "冲锋枪"
        else:  # 0.9到1.0之间，即10%
            return "狙击枪"
    
    def generate_elite_enemies_for_map(obstacles_list, player_rect, elite_enemy_img, count=4, current_map_level=1):
        """生成高级敌人；各楼层在房间随机位置生成"""
        if 2 <= current_map_level <= 7:
            rooms_list = _get_floor_rooms(current_map_level)
            elite_rect = elite_enemy_img.get_rect()
            ew, eh = elite_rect.width, elite_rect.height
            margin = max(ew, eh) // 2 + 5
            def random_pos_elite_floor(room, obs_list):
                left, top, w, h = room
                if w <= margin * 2 or h <= margin * 2:
                    return (left + w // 2, top + h // 2)
                for _ in range(50):
                    cx = random.randint(left + margin, left + w - margin)
                    cy = random.randint(top + margin, top + h - margin)
                    test_rect = pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh)
                    if not any(test_rect.colliderect(o.rect) for o in obs_list):
                        return (cx, cy)
                return (left + w // 2, top + h // 2)
            result = []
            elite_count = count + (current_map_level - 1)  # 越高层精英越多
            elite_hp = 250 + (current_map_level - 2) * 30
            for _ in range(elite_count):
                room = random.choice(rooms_list)
                cx, cy = random_pos_elite_floor(room, obstacles_list)
                drop_weapon = get_random_elite_weapon()
                result.append(Enemy(cx, cy, elite_enemy_img, health=elite_hp, drop_weapon=drop_weapon))
            return result
        if current_map_level == 8:
            return []  # Boss层不生成精英敌人
        if current_map_level != 1:
            return []
        # 复用与普通敌人相同的房间定义
        wall = 50
        ch_left, ch_right = 700, 3300
        ch_top, ch_bottom = 1100, 2500
        h_corr_y0, h_corr_y1 = 1800, 1900
        build_bottom = 3600
        ch_bottom_room_w = ch_right - ch_left
        part_2 = ch_bottom_room_w * 2 // 7
        part_3 = ch_bottom_room_w * 3 // 7
        div1_x = ch_left + part_2
        div2_x = ch_left + part_2 + part_3
        left_wing_x = wall
        right_wing_x = ch_right + wall
        left_wing_w = ch_left - left_wing_x - wall
        right_wing_w = 3950 - right_wing_x
        rooms_elite = [
            (ch_left + wall, ch_top + wall, div1_x - (ch_left + wall), h_corr_y0 - (ch_top + wall)),
            (div1_x + wall, ch_top + wall, div2_x - div1_x - wall * 2, h_corr_y0 - (ch_top + wall)),
            (div2_x + wall, ch_top + wall, ch_right - div2_x - wall * 2, h_corr_y0 - (ch_top + wall)),
            (ch_left + wall, h_corr_y1 + wall, div1_x - (ch_left + wall), ch_bottom - h_corr_y1 - wall * 2),
            (div1_x + wall, h_corr_y1 + wall, div2_x - div1_x - wall * 2, ch_bottom - h_corr_y1 - wall * 2),
            (div2_x + wall, h_corr_y1 + wall, ch_right - div2_x - wall * 2, ch_bottom - h_corr_y1 - wall * 2),
            (left_wing_x + wall, ch_top + wall, left_wing_w - wall * 2, h_corr_y0 - (ch_top + wall)),
            (left_wing_x + wall, h_corr_y1 + wall, left_wing_w - wall * 2, build_bottom - h_corr_y1 - wall * 2),
            (right_wing_x + wall, ch_top + wall, right_wing_w - wall * 2, h_corr_y0 - (ch_top + wall)),
            (right_wing_x + wall, h_corr_y1 + wall, right_wing_w - wall * 2, build_bottom - h_corr_y1 - wall * 2),
        ]
        elite_rect = elite_enemy_img.get_rect()
        ew, eh = elite_rect.width, elite_rect.height
        margin = max(ew, eh) // 2 + 5

        def random_pos_in_room_elite(room, obstacles_list):
            left, top, w, h = room
            if w <= margin * 2 or h <= margin * 2:
                return (left + w // 2, top + h // 2)
            for _ in range(50):
                cx = random.randint(left + margin, left + w - margin) if w > margin * 2 else left + w // 2
                cy = random.randint(top + margin, top + h - margin) if h > margin * 2 else top + h // 2
                test_rect = pygame.Rect(cx - ew // 2, cy - eh // 2, ew, eh)
                if not any(test_rect.colliderect(o.rect) for o in obstacles_list):
                    return (cx, cy)
            return (left + w // 2, top + h // 2)

        result = []
        # 从房间中随机选 count 个房间各生成一个高级敌人（可重复房间）
        for _ in range(count):
            room = random.choice(rooms_elite)
            cx, cy = random_pos_in_room_elite(room, obstacles_list)
            drop_weapon = get_random_elite_weapon()
            result.append(Enemy(cx, cy, elite_enemy_img, health=250, drop_weapon=drop_weapon))
        return result
    
    # 生成第一张地图的敌人（地图1在大楼内固定位置）
    enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
    print(f"地图1：生成了 {len(enemies)} 个普通敌人")
    
    # 生成高级敌人（血量250，地图1固定位置）
    elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
    print(f"地图1：生成了 {len(elite_enemies)} 个高级敌人")
    enemies.extend(elite_enemies)  # 将高级敌人添加到敌人列表
    print(f"地图1：总共 {len(enemies)} 个敌人")
    
    # 保存第一张地图的敌人数据（保存敌人的位置和类型信息，以便后续重新创建）
    enemy_data = []
    for enemy in enemies:
        # 保存敌人位置和血量（用于区分普通敌人和高级敌人）
        enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
    maps_data[map_level]['enemies'] = enemy_data
    
    # 验证高级敌人数量
    elite_count = sum(1 for e in enemies if e.health == 250)
    normal_count = sum(1 for e in enemies if e.health == 100)
    print(f"地图1验证：普通敌人 {normal_count} 个，高级敌人 {elite_count} 个")

    enemy_bullets = [] # 新增：敌人子弹列表
    medkits_for_current_map = []  # 所有地图的医疗包列表（包括地图1）
    ammo_boxes_for_current_map = []  # 所有地图的弹药箱列表
    weapon_drops_for_current_map = []  # 所有地图的武器掉落物列表
    containers_for_current_map = []   # 当前地图的容器（按 E 花 3 秒拾取，得手雷/金币/子弹）
    zombies_for_current_map = []  # 当前地图僵尸
    safes_for_current_map = []  # 当前地图保险箱
    locked_doors_for_current_map = []  # 当前地图钥匙门
    key_item_for_current_map = None  # 当前地图钥匙
    player_has_key = False
    dynamic_content_map_level = None
    corpses_for_current_map = []  # 当前地图上的尸体（敌人/Boss 死后留下）
    explosions = []  # 爆炸特效列表
    boss_list = []  # Boss列表
    boss_list = []  # Boss列表
    
    # 为地图1生成多个医疗包
    if map_level == 1:
        player_pos = (player.rect.centerx, player.rect.centery)
        medkit_positions = generate_medkits_for_stage1(player_pos, enemies, obstacles, count=3)
        for x, y in medkit_positions:
            medkits_for_current_map.append(Medkit(x, y, medkit_image))
        print(f"地图1生成了 {len(medkits_for_current_map)} 个医疗包")
    
    # 为所有地图生成弹药箱（每张地图4个）
    ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
    for x, y in ammo_box_positions:
        ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
    print(f"地图{map_level}生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
    # 生成当前地图的容器
    container_positions = generate_container_positions(obstacles, world_width, world_height, count=6)
    for x, y in container_positions:
        containers_for_current_map.append(Container(x, y))
    print(f"地图{map_level}生成了 {len(containers_for_current_map)} 个容器")

    # 游戏主循环
    running = True
    clock = pygame.time.Clock()
    right_mouse_down = False
    camera_x = player.rect.x - screen_width // 2
    camera_y = player.rect.y - screen_height // 2
    is_map_open = False # 新增：控制地图显示状态
    radar_on = False  # 按 N 开启/关闭雷达：网格屏、中心红点、旋转绿色扇形、发现敌人可切回
    radar_angle = 0.0  # 雷达扇形当前旋转角度（弧度）
    looting_container = None   # 正在拾取的容器（按 E 花 3 秒）
    looting_start_time = 0
    is_shop_open = False  # 按 B 打开技能商城
    camera_transition_frames = 0 # 新增：相机过渡帧数，用于避免地图切换时的抖动
    is_paused = False  # 新增：暂停状态
    loading_screen = False  # 进入关卡时显示加载界面
    loading_progress = 0.0   # 加载进度 0~1
    intro_screen = False     # 加载完成后的入场剧情
    intro_start_time = 0     # 入场动画开始时间，用于逐行显示文字
    cutscene_driving = False  # 装甲车行驶过场动画
    cutscene_driving_start = 0  # 过场动画开始时间
    cutscene_vehicle_y = 0    # 装甲车当前Y位置
    elevator_animating = False        # 电梯动画进行中
    elevator_animation_start_time = 0
    elevator_target_map = 0           # 电梯目标楼层
    ELEVATOR_ANIMATION_DURATION = 2500  # 电梯动画时长（毫秒）
    elevator_ui_open = False          # 电梯楼层选择UI是否打开
    request_elevator_go = False       # 请求乘电梯前往 elevator_target_map

    # 楼层名称
    FLOOR_NAMES = {1: "1F 大厅", 2: "2F 实验室", 3: "3F 服务器房", 4: "4F 办公区",
                   5: "5F 研发部", 6: "6F 管理层", 7: "7F 实验区", 8: "8F 天台"}

    # 所有楼层共用一个电梯位置（世界坐标）
    def _elevator_rects():
        scale = world_width // WORLD_BASE
        return pygame.Rect(300 * scale, 30 * scale, 140 * scale, 120 * scale)
    elevator_rect = pygame.Rect(300, 30, 140, 120)

    def setup_dynamic_content_for_map(current_map_level):
        nonlocal zombies_for_current_map, safes_for_current_map, locked_doors_for_current_map
        nonlocal key_item_for_current_map, player_has_key, dynamic_content_map_level
        # 清理旧地图的门锁碰撞体
        for ld in locked_doors_for_current_map:
            if ld in obstacles:
                obstacles.remove(ld)
        safes_for_current_map = []
        locked_doors_for_current_map = []
        key_item_for_current_map = None
        player_has_key = False
        used = []

        key_rect = pick_free_rect(obstacles, 24, 24, used_rects=used)
        if key_rect:
            used.append(key_rect.inflate(80, 80))
            key_item_for_current_map = KeyItem(key_rect.centerx, key_rect.centery)

        lock_rect = pick_free_rect(obstacles, 28, 120, used_rects=used)
        if lock_rect:
            used.append(lock_rect.inflate(100, 100))
            lock = LockedDoor(lock_rect.x, lock_rect.y, lock_rect.width, lock_rect.height)
            locked_doors_for_current_map.append(lock)
            obstacles.append(lock)

        safe_rect = pick_free_rect(obstacles, 56, 56, used_rects=used)
        if safe_rect:
            safes_for_current_map.append(
                SafeBox(safe_rect.centerx, safe_rect.centery,
                        reward_coins=25 + current_map_level * 5,
                        reward_ammo=35 + current_map_level * 5)
            )

        zombie_count = 4 if current_map_level == 1 else (6 if 2 <= current_map_level <= 7 else 3)
        zombies_for_current_map = generate_zombies_for_map(obstacles, zombie_image, count=zombie_count)
        dynamic_content_map_level = current_map_level

    while running:
        current_time = pygame.time.get_ticks() # 获取当前时间
        # 根据当前世界尺寸更新电梯矩形（关卡1扩大时需缩放）
        elevator_rect = _elevator_rects()
        if dynamic_content_map_level != map_level:
            setup_dynamic_content_for_map(map_level)
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 如果在主页面 (moshi=0)，按下空格键进入目录
            elif moshi == 0 and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    moshi = 3  # 进入目录
            # 在目录页面 (moshi=3)
            elif moshi == 3:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    moshi = 0  # ESC 返回主页面
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    btn_w, btn_h = 200, 56
                    center_x = screen_width // 2
                    story_y = screen_height // 2 + 60
                    story_rect = pygame.Rect(center_x - btn_w // 2, story_y, btn_w, btn_h)
                    achievement_rect = pygame.Rect(center_x - btn_w // 2, story_y + btn_h + 20, btn_w, btn_h)
                    if story_rect.collidepoint(mouse_x, mouse_y):
                        moshi = 2  # 故事模式 -> 关卡选择
                    elif achievement_rect.collidepoint(mouse_x, mouse_y):
                        pass  # 成就（暂不跳转）
            # 在关卡选择页面 (moshi=2)
            elif moshi == 2:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # ESC 返回目录
                        moshi = 3
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_9:  # 数字键1-9选择关卡
                        selected_level = event.key - pygame.K_1 + 1
                        if selected_level <= max_level:
                            current_stage = selected_level  # 记录当前选择的关卡
                            # 如果选择关卡1，设置地图范围为1-3，并将世界尺寸扩大
                            if selected_level == 1:
                                map_level = 1
                                min_map_level = 1
                                max_map_level = 8
                            elif selected_level == 2:
                                # 关卡2对应地图4-6
                                map_level = 4
                                min_map_level = 4
                                max_map_level = 6
                            else:
                                map_level = selected_level
                                min_map_level = selected_level
                                max_map_level = selected_level  # 其他关卡只对应一个地图
                            
                            # 如果是关卡1，开启教程
                            if selected_level == 1:
                                tutorial_step = 1  # 开始教程第一步：移动
                                tutorial_completed = {
                                    'move': False,
                                    'sprint': False,
                                    'shoot': False,
                                    'aim': False,
                                    'reload': False,
                                    'map': False,
                                    'medkit': False
                                }
                            moshi = 1  # 进入游戏
                            loading_screen = True
                            loading_progress = 0.0
                            # 检查地图数据是否已存在
                            if map_level in maps_data:
                                # 使用已保存的地图数据
                                obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                                roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                                # 恢复门
                                if 'doors' in maps_data[map_level]:
                                    doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                                    for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                        if is_open:
                                            doors[i].toggle()
                                    rebuild_door_pairs(doors)
                                    for door in doors:
                                        if not door.is_open:
                                            obstacles.append(door)
                                else:
                                    doors = []
                                # 恢复敌人（根据血量判断是普通敌人还是高级敌人）
                                enemies = []
                                has_elite_enemies = False  # 检查是否有高级敌人
                                is_old_format = False  # 检查是否是旧格式
                                for enemy_info in maps_data[map_level]['enemies']:
                                    if len(enemy_info) == 3:  # 新格式：包含血量
                                        x, y, health = enemy_info
                                        if health == 250:  # 高级敌人
                                            drop_weapon = get_random_elite_weapon()
                                            enemies.append(Enemy(x, y, elite_enemy_image, health=250, drop_weapon=drop_weapon))
                                            has_elite_enemies = True
                                        else:  # 普通敌人
                                            enemies.append(Enemy(x, y, enemy_image, health=100))
                                    else:  # 旧格式：只有位置
                                        x, y = enemy_info
                                        enemies.append(Enemy(x, y, enemy_image, health=100))
                                        is_old_format = True
                                
                                # 如果是旧格式或没有高级敌人，重新生成高级敌人并更新保存数据
                                if is_old_format or not has_elite_enemies:
                                    print(f"地图{map_level}检测到旧格式或缺少高级敌人，正在生成高级敌人...")
                                    elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                    enemies.extend(elite_enemies)
                                    print(f"地图{map_level}已生成{len(elite_enemies)}个高级敌人")
                                    # 更新保存数据
                                    enemy_data = []
                                    for enemy in enemies:
                                        enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                    maps_data[map_level]['enemies'] = enemy_data
                                else:
                                    # 统计敌人数量
                                    normal_count = sum(1 for e in enemies if e.health == 100)
                                    elite_count = sum(1 for e in enemies if e.health == 250)
                                    print(f"地图{map_level}恢复敌人：普通敌人{normal_count}个，高级敌人{elite_count}个")
                                containers_for_current_map.clear()
                                for _x, _y in generate_container_positions(obstacles, world_width, world_height, 6):
                                    containers_for_current_map.append(Container(_x, _y))
                            else:
                                # 生成新地图
                                random.seed(42 + map_level)
                                obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                                for door in doors:
                                    if not door.is_open:
                                        obstacles.append(door)
                                enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                                # 生成高级敌人（血量250）
                                elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                enemies.extend(elite_enemies)
                                # 保存地图数据（包含敌人类型信息）
                                enemy_data = []
                                for enemy in enemies:
                                    enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                maps_data[map_level] = {
                                    'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                                    'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                                    'enemies': enemy_data,
                                    'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                                }
                                containers_for_current_map.clear()
                                for _x, _y in generate_container_positions(obstacles, world_width, world_height, 6):
                                    containers_for_current_map.append(Container(_x, _y))
                            # 为地图 2-9 生成随机医疗包
                                medkits_for_current_map.clear()
                                weapon_drops_for_current_map.clear()
                                corpses_for_current_map.clear()
                            if 2 <= map_level <= 9:
                                positions = generate_medkits_near_obstacles(obstacles, count=3)
                                for x, y in positions:
                                    medkits_for_current_map.append(Medkit(x, y, medkit_image))
                                print(f"地图 {map_level} 生成了 {len(medkits_for_current_map)} 个医疗包，坐标: {positions}")
                            # 为所有地图生成弹药箱（每张地图4个）
                            ammo_boxes_for_current_map.clear()
                            weapon_drops_for_current_map.clear()
                            corpses_for_current_map.clear()
                            ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                            for x, y in ammo_box_positions:
                                ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                            print(f"地图 {map_level} 生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
                            # 重置玩家位置和状态
                            if map_level == 1:
                                player.rect.x = world_width // 2 - player.rect.width // 2
                                player.rect.y = world_height - player.rect.height - 50
                            else:
                                player.rect.x = world_width // 2
                                player.rect.y = world_height // 2
                            # 开局满血满甲
                            if current_stage == 1:
                                player.health = player.max_health
                                player.armor = player.max_armor
                                # 在出生点附近生成多个医疗包（远离玩家，不在敌人视野内）
                                player_pos = (player.rect.centerx, player.rect.centery)
                                medkit_positions = generate_medkits_for_stage1(player_pos, enemies, obstacles, count=3)
                                medkits_for_current_map.clear()
                                corpses_for_current_map.clear()
                                for x, y in medkit_positions:
                                    medkits_for_current_map.append(Medkit(x, y, medkit_image))
                                print(f"关卡1：玩家生命值={player.health}, 护甲值={player.armor}, 生成了 {len(medkits_for_current_map)} 个医疗包")
                            else:
                                player.health = player.max_health
                                player.armor = player.max_armor
                                # 重置医疗包状态（仅在第一关）
                                if map_level == 1:
                                    for m in medkits_for_current_map:
                                        m.used = False
                            player.stamina = player.max_stamina
                            # 使用当前枪械的属性重置弹药
                            player.max_clip_bullets = player.current_weapon.clip_size
                            player.current_bullets = player.current_weapon.clip_size
                            player.total_ammo = player.weapon_ammo.get(player.current_weapon.name, 0)
                            player.reloading = False
                            camera_x = player.rect.x - screen_width // 2
                            camera_y = player.rect.y - screen_height // 2
                    elif event.key == pygame.K_0:  # 数字键0选择第10关
                        if 10 <= max_level:
                            current_stage = 10  # 记录当前选择的关卡
                            map_level = 10
                            min_map_level = 10
                            max_map_level = 10  # 第10关只对应一个地图
                            moshi = 1
                            # 检查地图数据是否已存在
                            if map_level in maps_data:
                                # 使用已保存的地图数据
                                obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                                roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                                # 恢复门
                                if 'doors' in maps_data[map_level]:
                                    doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                                    for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                        if is_open:
                                            doors[i].toggle()
                                    rebuild_door_pairs(doors)
                                    for door in doors:
                                        if not door.is_open:
                                            obstacles.append(door)
                                else:
                                    doors = []
                                # 恢复敌人（根据血量判断是普通敌人还是高级敌人）
                                enemies = []
                                has_elite_enemies = False  # 检查是否有高级敌人
                                is_old_format = False  # 检查是否是旧格式
                                for enemy_info in maps_data[map_level]['enemies']:
                                    if len(enemy_info) == 3:  # 新格式：包含血量
                                        x, y, health = enemy_info
                                        if health == 250:  # 高级敌人
                                            drop_weapon = get_random_elite_weapon()
                                            enemies.append(Enemy(x, y, elite_enemy_image, health=250, drop_weapon=drop_weapon))
                                            has_elite_enemies = True
                                        else:  # 普通敌人
                                            enemies.append(Enemy(x, y, enemy_image, health=100))
                                    else:  # 旧格式：只有位置
                                        x, y = enemy_info
                                        enemies.append(Enemy(x, y, enemy_image, health=100))
                                        is_old_format = True
                                
                                # 如果是旧格式或没有高级敌人，重新生成高级敌人并更新保存数据
                                if is_old_format or not has_elite_enemies:
                                    print(f"地图{map_level}检测到旧格式或缺少高级敌人，正在生成高级敌人...")
                                    elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                    enemies.extend(elite_enemies)
                                    print(f"地图{map_level}已生成{len(elite_enemies)}个高级敌人")
                                    # 更新保存数据
                                    enemy_data = []
                                    for enemy in enemies:
                                        enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                    maps_data[map_level]['enemies'] = enemy_data
                                else:
                                    # 统计敌人数量
                                    normal_count = sum(1 for e in enemies if e.health == 100)
                                    elite_count = sum(1 for e in enemies if e.health == 250)
                                    print(f"地图{map_level}恢复敌人：普通敌人{normal_count}个，高级敌人{elite_count}个")
                            else:
                                # 生成新地图
                                random.seed(42 + map_level)
                                obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                                for door in doors:
                                    if not door.is_open:
                                        obstacles.append(door)
                                enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                                # 生成高级敌人（血量250）
                                elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                enemies.extend(elite_enemies)
                                # 保存地图数据（包含敌人类型信息）
                                enemy_data = []
                                for enemy in enemies:
                                    enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                maps_data[map_level] = {
                                    'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                                    'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                                    'enemies': enemy_data,
                                    'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                                }
                            # 第 10 关不生成随机医疗包（保持单张地图）
                            # 重置玩家位置和状态
                            if map_level == 1:
                                player.rect.x = world_width // 2 - player.rect.width // 2
                                player.rect.y = world_height - player.rect.height - 50
                            else:
                                player.rect.x = world_width // 2
                                player.rect.y = world_height // 2
                            player.health = player.max_health
                            player.armor = player.max_armor
                            player.stamina = player.max_stamina
                            # 使用当前枪械的属性重置弹药
                            player.max_clip_bullets = player.current_weapon.clip_size
                            player.current_bullets = player.current_weapon.clip_size
                            player.total_ammo = player.weapon_ammo.get(player.current_weapon.name, 0)
                            player.reloading = False
                            camera_x = player.rect.x - screen_width // 2
                            camera_y = player.rect.y - screen_height // 2
                            # 重置医疗包状态（仅在第一关）
                            if map_level == 1:
                                for m in medkits_for_current_map:
                                    m.used = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 鼠标点击选择关卡
                    if event.button == 1:  # 左键点击
                        mouse_x, mouse_y = event.pos
                        # 计算按钮位置
                        button_width = 150
                        button_height = 60
                        button_spacing = 20
                        start_x = (screen_width - (5 * button_width + 4 * button_spacing)) // 2
                        start_y = 200
                        
                        # 检查点击了哪个关卡按钮
                        for i in range(1, max_level + 1):
                            row = (i - 1) // 5
                            col = (i - 1) % 5
                            x = start_x + col * (button_width + button_spacing)
                            y = start_y + row * (button_height + button_spacing)
                            button_rect = pygame.Rect(x, y, button_width, button_height)
                            
                            if button_rect.collidepoint(mouse_x, mouse_y):
                                selected_level = i
                                current_stage = selected_level  # 记录当前选择的关卡
                                # 如果选择关卡1，设置地图范围为1-3并扩大世界尺寸
                                if selected_level == 1:
                                    map_level = 1
                                    min_map_level = 1
                                    max_map_level = 3
                                elif selected_level == 2:
                                    # 关卡2对应地图4-6
                                    map_level = 4
                                    min_map_level = 4
                                    max_map_level = 6
                                else:
                                    map_level = selected_level
                                    min_map_level = selected_level
                                    max_map_level = selected_level  # 其他关卡只对应一个地图
                                
                                # 如果是关卡1，开启教程
                                if selected_level == 1:
                                    tutorial_step = 1  # 开始教程第一步：移动
                                    tutorial_completed = {
                                        'move': False,
                                        'sprint': False,
                                        'shoot': False,
                                        'aim': False,
                                        'reload': False,
                                        'medkit': False
                                    }
                                moshi = 1  # 进入游戏
                                loading_screen = True
                                loading_progress = 0.0
                                # 检查地图数据是否已存在
                                if map_level in maps_data:
                                    # 使用已保存的地图数据
                                    obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                                    roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                                    # 恢复门
                                    if 'doors' in maps_data[map_level]:
                                        doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                                        for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                            if is_open:
                                                doors[i].toggle()
                                        rebuild_door_pairs(doors)
                                        for door in doors:
                                            if not door.is_open:
                                                obstacles.append(door)
                                    else:
                                        doors = []
                                    # 恢复敌人（根据血量判断是普通敌人还是高级敌人）
                                    enemies = []
                                    has_elite_enemies = False  # 检查是否有高级敌人
                                    is_old_format = False  # 检查是否是旧格式
                                    for enemy_info in maps_data[map_level]['enemies']:
                                        if len(enemy_info) == 3:  # 新格式：包含血量
                                            x, y, health = enemy_info
                                            if health == 250:  # 高级敌人
                                                drop_weapon = get_random_elite_weapon()
                                                enemies.append(Enemy(x, y, elite_enemy_image, health=250, drop_weapon=drop_weapon))
                                                has_elite_enemies = True
                                            else:  # 普通敌人
                                                enemies.append(Enemy(x, y, enemy_image, health=100))
                                        else:  # 旧格式：只有位置
                                            x, y = enemy_info
                                            enemies.append(Enemy(x, y, enemy_image, health=100))
                                            is_old_format = True
                                    
                                    # 如果是旧格式或没有高级敌人，重新生成高级敌人并更新保存数据
                                    if is_old_format or not has_elite_enemies:
                                        print(f"地图{map_level}检测到旧格式或缺少高级敌人，正在生成高级敌人...")
                                        elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                        enemies.extend(elite_enemies)
                                        print(f"地图{map_level}已生成{len(elite_enemies)}个高级敌人")
                                        # 更新保存数据
                                        enemy_data = []
                                        for enemy in enemies:
                                            enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                        maps_data[map_level]['enemies'] = enemy_data
                                    else:
                                        # 统计敌人数量
                                        normal_count = sum(1 for e in enemies if e.health == 100)
                                        elite_count = sum(1 for e in enemies if e.health == 250)
                                        print(f"地图{map_level}恢复敌人：普通敌人{normal_count}个，高级敌人{elite_count}个")
                                else:
                                    # 生成新地图
                                    random.seed(42 + map_level)
                                    obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                                    for door in doors:
                                        if not door.is_open:
                                            obstacles.append(door)
                                    enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                                    # 生成高级敌人（血量250）
                                    elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                    enemies.extend(elite_enemies)
                                    # 保存地图数据（包含敌人类型信息）
                                    enemy_data = []
                                    for enemy in enemies:
                                        enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                    maps_data[map_level] = {
                                        'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                                        'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                                        'enemies': enemy_data,
                                        'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                                    }
                                # 为地图 2-9 生成随机医疗包
                                medkits_for_current_map.clear()
                                weapon_drops_for_current_map.clear()
                                corpses_for_current_map.clear()
                                if 2 <= map_level <= 9:
                                    positions = generate_medkits_near_obstacles(obstacles, count=3)
                                    for x, y in positions:
                                        medkits_for_current_map.append(Medkit(x, y, medkit_image))
                                    print(f"地图 {map_level} 生成了 {len(medkits_for_current_map)} 个医疗包")
                                # 为所有地图生成弹药箱（每张地图4个）
                                ammo_boxes_for_current_map.clear()
                                ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                                for x, y in ammo_box_positions:
                                    ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                                print(f"地图 {map_level} 生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
                                # 重置玩家位置和状态
                                if map_level == 1:
                                    player.rect.x = world_width // 2 - player.rect.width // 2
                                    player.rect.y = world_height - player.rect.height - 50
                                else:
                                    player.rect.x = world_width // 2
                                    player.rect.y = world_height // 2
                                # 开局满血满甲
                                if current_stage == 1:
                                    player.health = player.max_health
                                    player.armor = player.max_armor
                                    # 在出生点附近生成多个医疗包（远离玩家，不在敌人视野内）
                                    player_pos = (player.rect.centerx, player.rect.centery)
                                    medkit_positions = generate_medkits_for_stage1(player_pos, enemies, obstacles, count=3)
                                    medkits_for_current_map.clear()
                                    corpses_for_current_map.clear()
                                    for x, y in medkit_positions:
                                        medkits_for_current_map.append(Medkit(x, y, medkit_image))
                                    print(f"关卡1：玩家生命值={player.health}, 护甲值={player.armor}, 生成了 {len(medkits_for_current_map)} 个医疗包")
                                    # 为关卡1生成弹药箱
                                    ammo_boxes_for_current_map.clear()
                                    ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                                    for x, y in ammo_box_positions:
                                        ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                                    print(f"关卡1生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
                                else:
                                    player.health = player.max_health
                                    player.armor = player.max_armor
                                    # 重置医疗包状态（仅在第一关）
                                    if map_level == 1:
                                        for m in medkits_for_current_map:
                                            m.used = False
                                player.stamina = player.max_stamina
                                # 使用当前枪械的属性重置弹药
                                player.max_clip_bullets = player.current_weapon.clip_size
                                player.current_bullets = player.current_weapon.clip_size
                                player.total_ammo = player.weapon_ammo.get(player.current_weapon.name, 0)
                                player.reloading = False
                                camera_x = player.rect.x - screen_width // 2
                                camera_y = player.rect.y - screen_height // 2
                                break
            # 在游戏模式下，处理按键按下事件
            elif moshi == 1 and event.type == pygame.KEYDOWN:
                # 入场动画时只响应空格键
                if intro_screen:
                    if event.key == pygame.K_SPACE:
                        intro_screen = False
                        # 第一关：进入装甲车行驶过场动画
                        if current_stage == 1:
                            cutscene_driving = True
                            cutscene_driving_start = current_time
                            cutscene_vehicle_y = screen_height + 100  # 从屏幕下方开始
                elif cutscene_driving:
                    if event.key == pygame.K_SPACE:
                        cutscene_driving = False  # 按空格跳过过场动画，直接进入游戏
                # 电梯楼层选择UI打开时，按ESC关闭
                elif elevator_ui_open:
                    if event.key == pygame.K_ESCAPE:
                        elevator_ui_open = False
                        pygame.mouse.set_visible(False)
                # 如果暂停，只处理暂停菜单的按键
                elif is_paused:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        is_paused = False
                        pygame.mouse.set_visible(False)
                else:
                    # 暂停/继续游戏（ESC 或 P 键）
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        is_paused = not is_paused
                        if is_paused:
                            pygame.mouse.set_visible(True)  # 暂停时显示鼠标
                        else:
                            pygame.mouse.set_visible(False)  # 继续时隐藏鼠标
                    elif event.key == pygame.K_SPACE:
                        # 只有当体力足够时才能疾跑
                        if player.stamina > 0:
                            player.is_sprinting = True
                    elif event.key == pygame.K_TAB: # 新增：按下Tab键切换地图显示
                        is_map_open = not is_map_open
                        if is_map_open:
                            radar_on = False  # 打开地图时关闭雷达
                    elif event.key == pygame.K_n:  # 按 N 开启/关闭雷达
                        radar_on = not radar_on
                        if radar_on:
                            is_map_open = False  # 打开雷达时关闭地图
                        # 更新教程状态（如果正在进行教程）- 延迟到关闭地图时再完成
                        if current_stage == 1 and tutorial_step == 6 and not tutorial_completed.get('map', False):
                            if is_map_open:
                                print("教程：地图已打开，查看颜色说明后关闭地图继续")
                            else:
                                # 只有关闭地图时才完成这一步
                                tutorial_completed['map'] = True
                                tutorial_step = 7
                                print("教程：打开地图操作完成")
                    elif event.key == pygame.K_r: # 按下R键换弹
                        if (not infinite_ammo and
                            not player.reloading and
                            player.current_bullets < player.max_clip_bullets and
                            player.total_ammo > 0):
                            player.reloading = True
                            player.reload_start_time = current_time
                            player.reload_duration = player.current_weapon.reload_time
                    elif event.key == pygame.K_l:  # 按 L 开启/关闭无限弹药
                        infinite_ammo = not infinite_ammo
                        if infinite_ammo:
                            player.reloading = False
                            player.current_bullets = player.max_clip_bullets
                        print(f"无限弹药: {'开启' if infinite_ammo else '关闭'}")
                    elif is_shop_open and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        idx = event.key - pygame.K_1
                        items = [(50, "grenade", 3), (30, "medkit", 1), (40, "ammo", 30)]
                        if idx < len(items):
                            price, kind, amount = items[idx]
                            if player.coins >= price:
                                player.coins -= price
                                if kind == "grenade":
                                    player.grenades += amount
                                    print(f"购买手雷 x{amount}，剩余金币: {player.coins}")
                                elif kind == "medkit":
                                    player.health = min(player.health + 50, player.max_health)
                                    print(f"购买医疗包，恢复 50 生命，剩余金币: {player.coins}")
                                else:
                                    wn = player.current_weapon.name
                                    player.weapon_ammo[wn] = player.weapon_ammo.get(wn, 0) + amount
                                    player.total_ammo = player.weapon_ammo[wn]
                                    print(f"购买弹药 +{amount}，剩余金币: {player.coins}")
                    elif event.key == pygame.K_7:  # 按7切换敌人血量显示
                        show_enemy_health = not show_enemy_health
                        print(f"敌人血量显示: {'开启' if show_enemy_health else '关闭'}")
                    elif event.key == pygame.K_1: # 切换到第一个武器
                        if len(player.carried_weapons) > 0:
                            player.switch_weapon(player.carried_weapons[0])
                    elif event.key == pygame.K_2: # 切换到第二个武器
                        if len(player.carried_weapons) > 1:
                            player.switch_weapon(player.carried_weapons[1])
                    elif event.key == pygame.K_e: # 按下E键开/关门 或 乘电梯
                        player_cx = player.rect.centerx
                        player_cy = player.rect.centery
                        # 任何楼层：站在电梯上按E打开楼层选择UI
                        if current_stage == 1 and 1 <= map_level <= 8 and player.rect.colliderect(elevator_rect) and not elevator_ui_open:
                            elevator_ui_open = True
                            pygame.mouse.set_visible(True)
                        if not elevator_ui_open:
                            # 优先检查容器（靠近按 E 开始 3 秒拾取）
                            for c in containers_for_current_map:
                                if c.looted:
                                    continue
                                dist = math.sqrt((player_cx - c.rect.centerx)**2 + (player_cy - c.rect.centery)**2)
                                if dist < 100:
                                    looting_container = c
                                    looting_start_time = current_time
                                    break
                            if looting_container is None:
                                handled_special = False
                                # 钥匙拾取
                                if key_item_for_current_map and not key_item_for_current_map.collected:
                                    d_key = math.sqrt(
                                        (player_cx - key_item_for_current_map.rect.centerx) ** 2 +
                                        (player_cy - key_item_for_current_map.rect.centery) ** 2
                                    )
                                    if d_key < 100:
                                        key_item_for_current_map.collected = True
                                        player_has_key = True
                                        handled_special = True
                                        print("已拾取钥匙，可开启门锁和保险箱")
                                # 门锁交互
                                if not handled_special and locked_doors_for_current_map:
                                    nearest_lock = None
                                    nearest_lock_dist = float('inf')
                                    for lock in locked_doors_for_current_map:
                                        if lock.is_open:
                                            continue
                                        dist_lock = math.sqrt(
                                            (player_cx - lock.rect.centerx) ** 2 +
                                            (player_cy - lock.rect.centery) ** 2
                                        )
                                        if dist_lock < nearest_lock_dist:
                                            nearest_lock_dist = dist_lock
                                            nearest_lock = lock
                                    if nearest_lock and nearest_lock_dist < 100:
                                        handled_special = True
                                        if not player_has_key:
                                            print("门锁需要钥匙")
                                        else:
                                            nearest_lock.is_open = True
                                            if nearest_lock in obstacles:
                                                obstacles.remove(nearest_lock)
                                            print("已用钥匙打开门锁")
                                # 保险箱交互
                                if not handled_special and safes_for_current_map:
                                    for safe in safes_for_current_map:
                                        if safe.opened:
                                            continue
                                        dist_safe = math.sqrt(
                                            (player_cx - safe.rect.centerx) ** 2 +
                                            (player_cy - safe.rect.centery) ** 2
                                        )
                                        if dist_safe < 100:
                                            handled_special = True
                                            if not player_has_key:
                                                print("保险箱需要钥匙")
                                            else:
                                                safe.opened = True
                                                player.coins += safe.reward_coins
                                                wn = player.current_weapon.name
                                                player.weapon_ammo[wn] = player.weapon_ammo.get(wn, 0) + safe.reward_ammo
                                                player.total_ammo = player.weapon_ammo[wn]
                                                print(f"打开保险箱：金币 +{safe.reward_coins}，{wn}弹药 +{safe.reward_ammo}")
                                            break

                                if handled_special:
                                    continue
                                nearest_door = None
                                nearest_dist = float('inf')
                                for door in doors:
                                    door_cx = door.rect.centerx
                                    door_cy = door.rect.centery
                                    dist = ((player_cx - door_cx) ** 2 + (player_cy - door_cy) ** 2) ** 0.5
                                    if dist < nearest_dist:
                                        nearest_dist = dist
                                        nearest_door = door
                                if nearest_door and nearest_dist < 100:
                                    # Toggle 最近的门 + 配对门（双开门联动）
                                    doors_to_toggle = [nearest_door]
                                    if nearest_door.pair and nearest_door.pair in doors:
                                        doors_to_toggle.append(nearest_door.pair)
                                    for d in doors_to_toggle:
                                        d.toggle()
                                        if d.is_open:
                                            if d in obstacles:
                                                obstacles.remove(d)
                                        else:
                                            if d not in obstacles:
                                                obstacles.append(d)
                                    # 更新 maps_data 中门的状态
                                    if map_level in maps_data:
                                        maps_data[map_level]['doors'] = [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                                else:
                                    # 未操作门时：按 E 拾取医疗包/弹药箱/武器
                                    if map_level == 1:
                                        for m in medkits_for_current_map:
                                            if m.used:
                                                continue
                                            distance = math.sqrt((player.rect.centerx - m.rect.centerx)**2 + (player.rect.centery - m.rect.centery)**2)
                                            if distance < 100:  # 距离小于100像素时可以拾取
                                                player.health += m.heal_amount
                                                player.health = min(player.health, player.max_health)
                                                m.used = True
                                                print(f"使用医疗包，恢复 {m.heal_amount} 点生命值")
                                                if current_stage == 1 and tutorial_step == 7 and not tutorial_completed.get('medkit', False):
                                                    tutorial_completed['medkit'] = True
                                                    tutorial_step = 8
                                                    print("教程：医疗包操作完成，教程结束")
                                                break
                                    elif 2 <= map_level <= 9:
                                        for m in medkits_for_current_map:
                                            if m.used:
                                                continue
                                            dx = player.rect.centerx - m.rect.centerx
                                            dy = player.rect.centery - m.rect.centery
                                            if dx * dx + dy * dy < 100 * 100:
                                                player.health += m.heal_amount
                                                player.health = min(player.health, player.max_health)
                                                m.used = True
                                                print(f"使用医疗包，恢复 {m.heal_amount} 点生命值")
                                                break
                                    for ammo_box in ammo_boxes_for_current_map:
                                        if ammo_box.used:
                                            continue
                                        dx = player.rect.centerx - ammo_box.rect.centerx
                                        dy = player.rect.centery - ammo_box.rect.centery
                                        if dx * dx + dy * dy < 100 * 100:
                                            player.total_ammo += ammo_box.ammo_amount
                                            ammo_box.used = True
                                            print(f"拾取弹药箱，获得 {ammo_box.ammo_amount} 发弹药，当前总弹药: {player.total_ammo}")
                                            break
                                    for weapon_drop in weapon_drops_for_current_map:
                                        if weapon_drop.used:
                                            continue
                                        dx = player.rect.centerx - weapon_drop.rect.centerx
                                        dy = player.rect.centery - weapon_drop.rect.centery
                                        if dx * dx + dy * dy < 100 * 100:
                                            weapon_name = weapon_drop.weapon_name
                                            if weapon_name not in player.carried_weapons:
                                                current_weapon_name = player.current_weapon.name
                                                if len(player.carried_weapons) >= player.max_carried_weapons:
                                                    player.carried_weapons.remove(current_weapon_name)
                                                    print(f"获得{weapon_name}！替换了当前使用的{current_weapon_name}")
                                                else:
                                                    print(f"获得{weapon_name}！")
                                                player.carried_weapons.append(weapon_name)
                                                if player.weapon_ammo.get(weapon_name, 0) == 0:
                                                    if weapon_name == "冲锋枪":
                                                        player.weapon_ammo["冲锋枪"] = 120
                                                    elif weapon_name == "步枪":
                                                        player.weapon_ammo["步枪"] = 90
                                                    elif weapon_name == "狙击枪":
                                                        player.weapon_ammo["狙击枪"] = 20
                                                    elif weapon_name == "rpg":
                                                        player.weapon_ammo["rpg"] = 5
                                                if weapon_name not in player.weapon_clip_bullets:
                                                    player.weapon_clip_bullets[weapon_name] = weapons[weapon_name].clip_size
                                                player.switch_weapon(weapon_name)
                                                print(f"拾取{weapon_name}！已切换到{weapon_name}")
                                            else:
                                                print(f"你已经携带了{weapon_name}")
                                            weapon_drop.used = True
                                            break
                    elif event.key == pygame.K_b:  # 按 B 打开/关闭技能商城
                        if not is_map_open and not radar_on:
                            is_shop_open = not is_shop_open
                    elif event.key == pygame.K_g:  # 按 G 投掷手雷
                        if player.grenades > 0 and current_time - last_grenade_time > grenade_cooldown:
                            mouse_x, mouse_y = pygame.mouse.get_pos()
                            target_world_x = mouse_x + camera_x
                            target_world_y = mouse_y + camera_y
                            new_grenade = Grenade(player.rect.centerx, player.rect.centery, target_world_x, target_world_y)
                            grenades_in_air.append(new_grenade)
                            player.grenades -= 1
                            last_grenade_time = current_time
                            print(f"投掷手雷！剩余: {player.grenades}")
                    elif event.key == pygame.K_q:  # 按 Q 闪避翻滚
                        if not dodge_rolling and current_time - last_dodge_roll_time > dodge_roll_cooldown and player.stamina >= 20:
                            keys_state = pygame.key.get_pressed()
                            # 根据当前按键方向确定翻滚方向
                            dx, dy = 0, 0
                            if keys_state[pygame.K_a]: dx -= 1
                            if keys_state[pygame.K_d]: dx += 1
                            if keys_state[pygame.K_w]: dy -= 1
                            if keys_state[pygame.K_s]: dy += 1
                            if dx == 0 and dy == 0:
                                # 如果没按方向键，朝鼠标反方向翻滚
                                mx, my = pygame.mouse.get_pos()
                                dx = -(mx - (player.rect.centerx - camera_x))
                                dy = -(my - (player.rect.centery - camera_y))
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist > 0:
                                dodge_roll_dx = dx / dist
                                dodge_roll_dy = dy / dist
                            else:
                                dodge_roll_dx, dodge_roll_dy = 0, -1
                            dodge_rolling = True
                            dodge_roll_start = current_time
                            last_dodge_roll_time = current_time
                            player.stamina -= 20  # 消耗20点体力
                            print("闪避翻滚！")
            # 在游戏模式下，处理按键松开事件
            elif moshi == 1 and event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.is_sprinting = False
            # 鼠标按下事件 (moshi=1)
            elif moshi == 1 and event.type == pygame.MOUSEBUTTONDOWN:
                # 电梯楼层选择UI的鼠标点击处理
                if elevator_ui_open and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    panel_w, panel_h = 280, 420
                    panel_x = (screen_width - panel_w) // 2
                    panel_y = (screen_height - panel_h) // 2
                    btn_w, btn_h = 240, 38
                    btn_x = panel_x + (panel_w - btn_w) // 2
                    btn_start_y = panel_y + 50
                    clicked_floor = 0
                    for fl in range(1, 9):
                        by = btn_start_y + (fl - 1) * (btn_h + 6)
                        btn_rect = pygame.Rect(btn_x, by, btn_w, btn_h)
                        if btn_rect.collidepoint(mouse_x, mouse_y) and fl != map_level:
                            clicked_floor = fl
                            break
                    if clicked_floor > 0:
                        elevator_ui_open = False
                        elevator_target_map = clicked_floor
                        request_elevator_go = True
                        pygame.mouse.set_visible(False)
                    else:
                        # 点击面板外部关闭UI
                        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
                        if not panel_rect.collidepoint(mouse_x, mouse_y):
                            elevator_ui_open = False
                            pygame.mouse.set_visible(False)
                # 如果暂停，处理暂停菜单的鼠标点击
                elif is_paused:
                    if event.button == 1:  # 左键点击
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        button_width = 300
                        button_height = 80
                        button_y_start = 180  # 与绘制部分保持一致
                        
                        # 检查是否点击了继续游戏按钮
                        continue_button_rect = pygame.Rect(
                            screen_width // 2 - button_width // 2,
                            button_y_start,
                            button_width,
                            button_height
                        )
                        if continue_button_rect.collidepoint(mouse_x, mouse_y):
                            is_paused = False
                            pygame.mouse.set_visible(False)
                        
                        # 检查是否点击了结束游戏按钮
                        quit_button_rect = pygame.Rect(
                            screen_width // 2 - button_width // 2,
                            button_y_start + button_height + 30,
                            button_width,
                            button_height
                        ) 
                        if quit_button_rect.collidepoint(mouse_x, mouse_y):
                            is_paused = False
                            moshi = 2  # 退出本关，回到关卡选择页面
                            pygame.mouse.set_visible(True)
                else:
                    # 右键按下
                    if event.button == 3:
                        right_mouse_down = True
                    # 左键按下
                    elif event.button == 1:
                        left_mouse_down = True
                    # 滚轮向上，切换到上一把枪
                    elif event.button == 4:
                        if not is_paused:  # 只在非暂停状态下切换武器
                            player.switch_to_next_weapon(-1)
                    # 滚轮向下，切换到下一把枪
                    elif event.button == 5:
                        if not is_paused:  # 只在非暂停状态下切换武器
                            player.switch_to_next_weapon(1)
            
            # 鼠标右键松开
            elif moshi == 1 and event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    right_mouse_down = False
                # 左键松开
                elif event.button == 1:
                    left_mouse_down = False
        
        if moshi == 0:
            screen.blit(menu_image, (0, 0))
            start_font = get_chinese_font(48)
            start_text = start_font.render("按空格开始", True, (230, 230, 230))
            start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2 + 120))
            screen.blit(start_text, start_rect)
        elif moshi == 3:
            # 目录页面：白色背景，上方留空给游戏名，下方两个按钮
            screen.fill((255, 255, 255))
            btn_w, btn_h = 200, 56
            center_x = screen_width // 2
            story_y = screen_height // 2 + 60  # 往下平移，上方留空
            story_rect = pygame.Rect(center_x - btn_w // 2, story_y, btn_w, btn_h)
            achievement_rect = pygame.Rect(center_x - btn_w // 2, story_y + btn_h + 20, btn_w, btn_h)
            pygame.draw.rect(screen, (70, 130, 180), story_rect)
            pygame.draw.rect(screen, (100, 100, 100), story_rect, 2)
            story_text = get_chinese_font(28).render("故事模式", True, (255, 255, 255))
            screen.blit(story_text, story_text.get_rect(center=story_rect.center))
            pygame.draw.rect(screen, (90, 90, 90), achievement_rect)
            pygame.draw.rect(screen, (120, 120, 120), achievement_rect, 2)
            achievement_text = get_chinese_font(28).render("成就", True, (255, 255, 255))
            screen.blit(achievement_text, achievement_text.get_rect(center=achievement_rect.center))
        elif moshi == 2:
            # 关卡选择页面
            screen.fill((30, 30, 30))  # 深灰色背景
            
            # 标题
            title_font = get_chinese_font(60)
            title_text = title_font.render("选择关卡", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(screen_width // 2, 80))
            screen.blit(title_text, title_rect)
            
            # 关卡按钮
            button_width = 150
            button_height = 60
            button_spacing = 20
            start_x = (screen_width - (5 * button_width + 4 * button_spacing)) // 2
            start_y = 200
            
            font = get_chinese_font(40)
            hint_font = get_chinese_font(15)
            
            for i in range(1, max_level + 1):
                row = (i - 1) // 5
                col = (i - 1) % 5
                x = start_x + col * (button_width + button_spacing)
                y = start_y + row * (button_height + button_spacing)
                
                # 绘制关卡按钮
                button_rect = pygame.Rect(x, y, button_width, button_height)
                pygame.draw.rect(screen, (60, 60, 60), button_rect)  # 按钮背景
                pygame.draw.rect(screen, (150, 150, 150), button_rect, 3)  # 按钮边框
                
                # 关卡文字
                level_text = font.render(f"关卡 {i}", True, (255, 255, 255))
                text_rect = level_text.get_rect(center=button_rect.center)
                screen.blit(level_text, text_rect)
            
            # 提示文字
            hint_text1 = hint_font.render("按数字键 1-9 选择关卡，按 ESC 返回", True, (200, 200, 200))
            hint_rect1 = hint_text1.get_rect(center=(screen_width // 2, screen_height - 80))
            screen.blit(hint_text1, hint_rect1)
            
            if max_level >= 10:
                hint_text2 = hint_font.render("按数字键 0 选择第10关", True, (200, 200, 200))
                hint_rect2 = hint_text2.get_rect(center=(screen_width // 2, screen_height - 40))
                screen.blit(hint_text2, hint_rect2)
        elif moshi == 1:
            # 进入关卡时的加载界面：黑屏 + 底部进度条 + 右上角 Loading
            if loading_screen:
                screen.fill((0, 0, 0))
                loading_progress = min(1.0, loading_progress + 0.03)
                # 右上角 Loading
                load_font = get_chinese_font(28)
                load_text = load_font.render("Loading", True, (200, 200, 200))
                load_rect = load_text.get_rect(topright=(screen_width - 20, 20))
                screen.blit(load_text, load_rect)
                # 最下方简单进度条
                bar_margin = 60
                bar_h = 8
                bar_y = screen_height - bar_margin
                bar_x = bar_margin
                bar_w = screen_width - bar_margin * 2
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, int(bar_w * loading_progress), bar_h))
                if loading_progress >= 1.0:
                    loading_screen = False
                    intro_screen = True  # 加载完成后进入入场动画
                    intro_start_time = current_time  # 记录开始时间，用于逐行显示
                pygame.display.flip()
                clock.tick(60)
                continue
            # 入场动画：黑屏 + 剧情文字逐行出现，按空格进入下一阶段
            if intro_screen:
                screen.fill((0, 0, 0))
                intro_font = get_chinese_font(26)
                lines = [
                    "公元后 xxxx 年，全球丧尸爆发。",
                    "文明秩序崩塌，幸存者据点逐一沦陷。",
                    "情报显示，一切的源头都指向这家公司，",
                    "藏着不可告人的秘密。",
                    "你奉命潜入这栋大楼，查明真相。"
                ]
                # 根据经过时间决定显示几行（每行约 1.2 秒出现）
                elapsed = current_time - intro_start_time
                line_interval_ms = 1200
                lines_to_show = min(len(lines), max(1, 1 + int(elapsed / line_interval_ms)))
                line_height = 42
                start_y = (screen_height - len(lines) * line_height) // 2 - 20
                for i in range(lines_to_show):
                    line = lines[i]
                    surf = intro_font.render(line, True, (220, 220, 220))
                    rect = surf.get_rect(centerx=screen_width // 2, y=start_y + i * line_height)
                    screen.blit(surf, rect)
                hint_font = get_chinese_font(22)
                hint = hint_font.render("按 空格键 跳过剧情", True, (160, 160, 160))
                hint_rect = hint.get_rect(center=(screen_width // 2, screen_height - 80))
                screen.blit(hint, hint_rect)
                pygame.display.flip()
                clock.tick(60)
                continue
            # 装甲车行驶过场动画（第一关专属）
            if cutscene_driving:
                screen.fill((0, 0, 0))
                elapsed_cs = current_time - cutscene_driving_start

                # 上尉对话内容及出现时间 (毫秒, 说话人, 内容)
                dialogues = [
                    (1500,  "上尉", "都打起精神来，我们快到了。"),
                    (4500,  "上尉", "情报显示，这次丧尸爆发的源头指向前方那家公司。"),
                    (7500,  "上尉", "里面藏着不可告人的秘密，上面要我们查明真相。"),
                    (10500, "上尉", "你的任务是潜入这栋大楼，找到一切有用的情报。"),
                    (13500, "上尉", "注意，楼内有大量雇佣兵把守，弹药省着点用。"),
                    (16000, "你",   "明白，长官。"),
                ]
                CUTSCENE_DURATION = 18000  # 延长到18秒

                # 绘制马路背景
                road_w = 300
                road_x = (screen_width - road_w) // 2
                pygame.draw.rect(screen, (60, 60, 60), (road_x, 0, road_w, screen_height))  # 灰色路面
                # 道路边线
                pygame.draw.rect(screen, (200, 200, 200), (road_x, 0, 4, screen_height))  # 左边线
                pygame.draw.rect(screen, (200, 200, 200), (road_x + road_w - 4, 0, 4, screen_height))  # 右边线
                # 道路中线（虚线，滚动效果）
                dash_len = 40
                gap_len = 30
                scroll_offset = (elapsed_cs // 4) % (dash_len + gap_len)
                center_line_x = screen_width // 2 - 2
                y = -dash_len + scroll_offset
                while y < screen_height:
                    pygame.draw.rect(screen, (255, 255, 0), (center_line_x, int(y), 4, dash_len))
                    y += dash_len + gap_len

                # 道路两侧绘制树木/路灯装饰（滚动）
                decor_scroll = (elapsed_cs // 3) % 200
                for dy in range(-200, screen_height + 200, 200):
                    tree_y = dy + decor_scroll
                    pygame.draw.circle(screen, (30, 80, 30), (road_x - 40, int(tree_y)), 20)
                    pygame.draw.rect(screen, (80, 50, 20), (road_x - 44, int(tree_y) + 15, 8, 20))
                    pygame.draw.circle(screen, (30, 80, 30), (road_x + road_w + 40, int(tree_y)), 20)
                    pygame.draw.rect(screen, (80, 50, 20), (road_x + road_w + 36, int(tree_y) + 15, 8, 20))

                # 装甲车固定在屏幕中心，轻微颠簸效果
                vehicle_x = screen_width // 2 - 175
                vehicle_y = screen_height // 2 - 175 + math.sin(elapsed_cs / 200.0) * 3
                screen.blit(armored_vehicle_image, (vehicle_x, int(vehicle_y)))

                # 绘制对话框：找到当前应该显示的对话
                current_dialogue = None
                for i, (t, speaker, text) in enumerate(dialogues):
                    next_t = dialogues[i + 1][0] if i + 1 < len(dialogues) else t + 2500
                    if t <= elapsed_cs < next_t:
                        current_dialogue = (t, speaker, text)
                        break

                if current_dialogue:
                    d_time, d_speaker, d_text = current_dialogue
                    # 对话框淡入效果（前300毫秒）
                    fade_in = min(1.0, (elapsed_cs - d_time) / 300.0)

                    # 对话框背景
                    dlg_w = 600
                    dlg_h = 80
                    dlg_x = (screen_width - dlg_w) // 2
                    dlg_y = screen_height - 130
                    dlg_surface = pygame.Surface((dlg_w, dlg_h), pygame.SRCALPHA)
                    dlg_surface.fill((0, 0, 0, int(180 * fade_in)))
                    # 边框
                    border_color = (100, 180, 255) if d_speaker == "上尉" else (120, 255, 120)
                    pygame.draw.rect(dlg_surface, (*border_color, int(255 * fade_in)), (0, 0, dlg_w, dlg_h), 2)
                    screen.blit(dlg_surface, (dlg_x, dlg_y))

                    # 说话人名字
                    name_font = get_chinese_font(20)
                    name_color = (100, 180, 255) if d_speaker == "上尉" else (120, 255, 120)
                    name_surf = name_font.render(f"【{d_speaker}】", True, name_color)
                    name_surf.set_alpha(int(255 * fade_in))
                    screen.blit(name_surf, (dlg_x + 15, dlg_y + 10))

                    # 对话内容（打字机效果：逐字显示）
                    chars_to_show = min(len(d_text), int((elapsed_cs - d_time) / 60))
                    text_font = get_chinese_font(22)
                    text_surf = text_font.render(d_text[:chars_to_show], True, (230, 230, 230))
                    text_surf.set_alpha(int(255 * fade_in))
                    screen.blit(text_surf, (dlg_x + 15, dlg_y + 42))

                # 对话结束后屏幕逐渐变黑（18秒~20秒）
                FADE_START = CUTSCENE_DURATION  # 18秒开始渐黑
                FADE_DURATION = 2000  # 2秒完成渐黑
                if elapsed_cs >= FADE_START:
                    fade_alpha = min(255, int(255 * (elapsed_cs - FADE_START) / FADE_DURATION))
                    fade_surface = pygame.Surface((screen_width, screen_height))
                    fade_surface.fill((0, 0, 0))
                    fade_surface.set_alpha(fade_alpha)
                    screen.blit(fade_surface, (0, 0))

                # 绘制"按空格跳过"提示
                skip_hint_font = get_chinese_font(20)
                skip_hint = skip_hint_font.render("按 空格键 跳过剧情", True, (140, 140, 140))
                skip_hint_rect = skip_hint.get_rect(bottomright=(screen_width - 30, screen_height - 20))
                screen.blit(skip_hint, skip_hint_rect)

                # 渐黑完成后结束过场动画，进入游戏
                if elapsed_cs >= FADE_START + FADE_DURATION:
                    cutscene_driving = False

                pygame.display.flip()
                clock.tick(60)
                continue
            # 如果暂停，只绘制暂停菜单，不更新游戏逻辑
            if is_paused:
                # 绘制灰色背景
                screen.fill((128, 128, 128))  # 灰色背景
                
                # 绘制暂停菜单
                try:
                    pause_font = get_chinese_font(60)
                except:
                    pause_font = pygame.font.Font(None, 60)
                pause_title = pause_font.render("游戏暂停", True, (255, 255, 255))
                title_rect = pause_title.get_rect(center=(screen_width // 2, 100))
                screen.blit(pause_title, title_rect)
                
                # 绘制菜单选项按钮
                try:
                    menu_font = get_chinese_font(50)
                    map_font = get_chinese_font(40)
                except:
                    menu_font = pygame.font.Font(None, 50)
                    map_font = pygame.font.Font(None, 40)
                button_width = 300
                button_height = 80
                button_y_start = 180  # 从标题下方开始
                
                # 继续游戏按钮
                continue_button_rect = pygame.Rect(
                    screen_width // 2 - button_width // 2,
                    button_y_start,
                    button_width,
                    button_height
                )
                pygame.draw.rect(screen, (100, 150, 100), continue_button_rect)  # 绿色按钮
                pygame.draw.rect(screen, (255, 255, 255), continue_button_rect, 3)  # 白色边框
                continue_text = menu_font.render("继续游戏", True, (255, 255, 255))
                continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
                screen.blit(continue_text, continue_text_rect)
                
                # 结束游戏按钮
                quit_button_rect = pygame.Rect(
                    screen_width // 2 - button_width // 2,
                    button_y_start + button_height + 30,
                    button_width,
                    button_height
                )
                pygame.draw.rect(screen, (150, 100, 100), quit_button_rect)  # 红色按钮
                pygame.draw.rect(screen, (255, 255, 255), quit_button_rect, 3)  # 白色边框
                quit_text = menu_font.render("结束游戏", True, (255, 255, 255))
                quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
                screen.blit(quit_text, quit_text_rect)
                
                # 暂停时需要更新屏幕显示
                pygame.display.flip()
                clock.tick(60)
                continue
            else:
                # 游戏正常进行时的逻辑
                # 隐藏鼠标光标（电梯UI打开时显示鼠标）
                if not elevator_ui_open:
                    pygame.mouse.set_visible(False)
                
                # 获取当前按键状态
                keys = pygame.key.get_pressed()

                # 电梯UI打开时冻结玩家和游戏逻辑
                if elevator_ui_open:
                    map_status = None
                else:
                    # 更新玩家
                    map_status = player.update(
                        keys, world_width, world_height, current_time,
                        obstacles, map_level, min_map_level, infinite_ammo
                    )
                # 电梯动画中：将玩家限制在电梯范围内
                if elevator_animating:
                    er = elevator_rect
                    player.rect.x = max(er.left, min(player.rect.x, er.right - player.rect.width))
                    player.rect.y = max(er.top, min(player.rect.y, er.bottom - player.rect.height))
                
                # 教程系统：检测玩家操作并更新教程步骤（仅关卡1）
                if current_stage == 1 and tutorial_step > 0 and tutorial_step < 8:
                    # 检测移动操作
                    if tutorial_step == 1 and not tutorial_completed['move']:
                        if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
                            tutorial_completed['move'] = True
                            tutorial_step = 2
                            print("教程：移动操作完成")
                    
                    # 检测冲刺操作
                    elif tutorial_step == 2 and not tutorial_completed['sprint']:
                        if keys[pygame.K_SPACE]:
                            tutorial_completed['sprint'] = True
                            tutorial_step = 3
                            print("教程：冲刺操作完成")
                    
                    # 检测射击操作
                    elif tutorial_step == 3 and not tutorial_completed['shoot']:
                        if left_mouse_down:
                            tutorial_completed['shoot'] = True
                            tutorial_step = 4
                            print("教程：射击操作完成")
                    
                    # 检测右键开镜操作
                    elif tutorial_step == 4 and not tutorial_completed.get('aim', False):
                        if right_mouse_down:
                            tutorial_completed['aim'] = True
                            tutorial_step = 5
                            print("教程：右键开镜操作完成")
                    
                    # 检测换弹操作
                    elif tutorial_step == 5 and not tutorial_completed['reload']:
                        if keys[pygame.K_r]:
                            tutorial_completed['reload'] = True
                            tutorial_step = 6
                            print("教程：换弹操作完成")
                    
                    # 检测打开地图操作
                    elif tutorial_step == 6 and not tutorial_completed.get('map', False):
                        if is_map_open:
                            tutorial_completed['map'] = True
                            tutorial_step = 7
                            print("教程：打开地图操作完成")
                    
                    # 检测医疗包操作（医疗包使用已在事件处理中检测，这里只检查是否靠近医疗包）
                    elif tutorial_step == 7 and not tutorial_completed.get('medkit', False):
                        # 教程检测已在事件处理中完成，这里不需要重复检测
                        pass
                    
                    # 教程完成后，初始化第一个任务
                    if current_stage == 1 and tutorial_step == 8 and current_task is None:
                        # 初始化第一个任务：击杀玩家上方的最近敌人
                        current_task = "kill_enemy_above"
                        task_completed = False
                        task_target_enemy = None
                        # 找到玩家上方的最近敌人
                        player_y = player.rect.centery
                        min_distance = float('inf')
                        for enemy in enemies:
                            if enemy.rect.centery < player_y:  # 敌人在玩家上方
                                dx = enemy.rect.centerx - player.rect.centerx
                                dy = enemy.rect.centery - player.rect.centery
                                distance = math.sqrt(dx * dx + dy * dy)
                                if distance < min_distance:
                                    min_distance = distance
                                    task_target_enemy = enemy
                        if task_target_enemy:
                            print(f"任务：击杀玩家上方的敌人，坐标: ({task_target_enemy.rect.centerx}, {task_target_enemy.rect.centery})")
                        else:
                            print("任务：未找到玩家上方的敌人")

                # 容器拾取进度：保持靠近 3 秒后发放奖励，离开则取消
                if looting_container is not None:
                    dist = math.sqrt((player.rect.centerx - looting_container.rect.centerx)**2 + (player.rect.centery - looting_container.rect.centery)**2)
                    if dist > 120:
                        looting_container = None
                    elif current_time - looting_start_time >= Container.LOOT_TIME_MS:
                        c = looting_container
                        c.looted = True
                        if c.reward_type == 'grenade':
                            n = random.randint(1, 2)
                            player.grenades += n
                            print(f"从容器获得 {n} 枚手雷，当前手雷: {player.grenades}")
                        elif c.reward_type == 'coins':
                            n = random.randint(15, 45)
                            player.coins += n
                            print(f"从容器获得 {n} 金币，当前金币: {player.coins}")
                        else:
                            wn = player.current_weapon.name
                            add = random.randint(20, 40)
                            player.weapon_ammo[wn] = player.weapon_ammo.get(wn, 0) + add
                            player.total_ammo = player.weapon_ammo[wn]
                            print(f"从容器获得 {add} 发{wn}弹药，当前总弹药: {player.total_ammo}")
                        looting_container = None

                # 统一电梯系统：从楼层选择UI启动，动画结束后切换楼层
                if request_elevator_go and not elevator_animating:
                    request_elevator_go = False
                    # 保存当前地图数据
                    maps_data[map_level] = {
                        'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                        'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                        'enemies': [(e.rect.x, e.rect.y, e.health) for e in enemies],
                        'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                    }
                    elevator_animating = True
                    elevator_animation_start_time = current_time
                if elevator_animating and (current_time - elevator_animation_start_time >= ELEVATOR_ANIMATION_DURATION):
                    elevator_animating = False
                    old_map = map_level
                    map_level = elevator_target_map
                    print(f"乘电梯从{old_map}层到达{map_level}层（{FLOOR_NAMES.get(map_level, '')}）")
                    # 加载或生成目标楼层
                    if map_level in maps_data:
                        obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                        roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                        if 'doors' in maps_data[map_level]:
                            doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                            for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                if is_open:
                                    doors[i].toggle()
                            rebuild_door_pairs(doors)
                            for door in doors:
                                if not door.is_open:
                                    obstacles.append(door)
                        else:
                            doors = []
                        enemies = []
                        has_elite_enemies = False
                        is_old_format = False
                        for enemy_info in maps_data[map_level]['enemies']:
                            if len(enemy_info) == 3:
                                x, y, health = enemy_info
                                if health >= 250:
                                    drop_weapon = get_random_elite_weapon()
                                    enemies.append(Enemy(x, y, elite_enemy_image, health=health, drop_weapon=drop_weapon))
                                    has_elite_enemies = True
                                else:
                                    enemies.append(Enemy(x, y, enemy_image, health=health))
                            else:
                                x, y = enemy_info[:2]
                                enemies.append(Enemy(x, y, enemy_image, health=100))
                                is_old_format = True
                        if is_old_format or not has_elite_enemies:
                            elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                            enemies.extend(elite_enemies)
                            maps_data[map_level]['enemies'] = [(e.rect.x, e.rect.y, e.health) for e in enemies]
                    else:
                        random.seed(42 + map_level)
                        obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                        for door in doors:
                            if not door.is_open:
                                obstacles.append(door)
                        enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                        elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                        enemies.extend(elite_enemies)
                        maps_data[map_level] = {
                            'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                            'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                            'enemies': [(e.rect.x, e.rect.y, e.health) for e in enemies],
                            'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                        }
                    # Boss在第8层
                    if current_stage == 1 and map_level == 8:
                        boss_list.clear()
                        boss = BossTank(world_width // 2, (world_height - 400) // 2, boss_tank_image)
                        attempts = 0
                        while attempts < 100 and any(boss.rect.colliderect(o.rect) for o in obstacles):
                            boss.rect.centerx = world_width // 2 + random.randint(-200, 200)
                            boss.rect.centery = (world_height - 400) // 2 + random.randint(-200, 200)
                            attempts += 1
                        print(f"第8层天台：生成了Boss")
                    else:
                        boss_list.clear()
                    # 清理并重新生成物品
                    bullets.clear()
                    corpses_for_current_map.clear()
                    weapon_drops_for_current_map.clear()
                    medkits_for_current_map.clear()
                    ammo_boxes_for_current_map.clear()
                    containers_for_current_map.clear()
                    for _x, _y in generate_container_positions(obstacles, world_width, world_height, 6):
                        containers_for_current_map.append(Container(_x, _y))
                    if 2 <= map_level <= 8:
                        positions = generate_medkits_near_obstacles(obstacles, count=3)
                        for x, y in positions:
                            medkits_for_current_map.append(Medkit(x, y, medkit_image))
                    ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                    for x, y in ammo_box_positions:
                        ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                    # 玩家出现在电梯附近
                    player.rect.centerx = elevator_rect.centerx
                    player.rect.centery = elevator_rect.centery + elevator_rect.height
                    camera_x = player.rect.x - screen_width // 2
                    camera_y = player.rect.y - screen_height // 2
                    camera_x = max(0, min(camera_x, world_width - screen_width))
                    camera_y = max(0, min(camera_y, world_height - screen_height))
                    camera_transition_frames = 5

                if map_status == "new_map":
                    # 检查是否已达到当前关卡组的最大地图数
                    if map_level >= max_map_level:
                        # 已达到最大地图，阻止继续前进，将玩家移回当前地图
                        player.rect.y = 10  # 将玩家移回地图顶部
                        print(f"已到达最大地图 {max_map_level}，无法继续前进")
                    else:
                        map_level += 1
                        print(f"进入地图 {map_level}/{max_map_level}")
                        # 检查该地图是否已存在
                        if map_level in maps_data:
                            # 使用已保存的地图数据
                            obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                            roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                            # 恢复门
                            if 'doors' in maps_data[map_level]:
                                doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                                for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                    if is_open:
                                        doors[i].toggle()
                                rebuild_door_pairs(doors)
                                for door in doors:
                                    if not door.is_open:
                                        obstacles.append(door)
                            else:
                                doors = []
                            # 恢复敌人（根据血量判断是普通敌人还是高级敌人）
                            enemies = []
                            has_elite_enemies = False
                            is_old_format = False
                            for enemy_info in maps_data[map_level]['enemies']:
                                if len(enemy_info) == 3:  # 新格式：包含血量
                                    x, y, health = enemy_info
                                    if health == 250:  # 高级敌人
                                        drop_weapon = get_random_elite_weapon()
                                        enemies.append(Enemy(x, y, elite_enemy_image, health=250, drop_weapon=drop_weapon))
                                        has_elite_enemies = True
                                    else:  # 普通敌人
                                        enemies.append(Enemy(x, y, enemy_image, health=100))
                                else:  # 旧格式：只有位置
                                    x, y = enemy_info
                                    enemies.append(Enemy(x, y, enemy_image, health=100))
                                    is_old_format = True
                            
                            # 如果是旧格式或没有高级敌人，重新生成高级敌人并更新保存数据
                            if is_old_format or not has_elite_enemies:
                                elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                                enemies.extend(elite_enemies)
                                # 更新保存数据
                                enemy_data = []
                                for enemy in enemies:
                                    enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                                maps_data[map_level]['enemies'] = enemy_data
                            
                            # 如果是第一关第8层天台，恢复或生成Boss
                            if current_stage == 1 and map_level == 8:
                                boss_list.clear()
                                boss_x = world_width // 2
                                boss_y = (world_height - 400) // 2
                                boss = BossTank(boss_x, boss_y, boss_tank_image)
                                attempts = 0
                                while attempts < 100 and any(boss.rect.colliderect(o.rect) for o in obstacles):
                                    boss_x = world_width // 2 + random.randint(-200, 200)
                                    boss_y = (world_height - 400) // 2 + random.randint(-200, 200)
                                    boss.rect.centerx = boss_x
                                    boss.rect.centery = boss_y
                                    attempts += 1
                                print(f"第8层天台：生成了Boss，位置: ({boss.rect.centerx}, {boss.rect.centery})")
                            else:
                                boss_list.clear()
                        else:
                            # 生成新地图
                            random.seed(42 + map_level)
                            obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                            for door in doors:
                                if not door.is_open:
                                    obstacles.append(door)
                            enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                            elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                            enemies.extend(elite_enemies)
                            if current_stage == 1 and map_level == 8:
                                boss_list.clear()
                                boss_x = world_width // 2
                                boss_y = (world_height - 400) // 2
                                boss = BossTank(boss_x, boss_y, boss_tank_image)
                                attempts = 0
                                while attempts < 100 and any(boss.rect.colliderect(o.rect) for o in obstacles):
                                    boss_x = world_width // 2 + random.randint(-200, 200)
                                    boss_y = (world_height - 400) // 2 + random.randint(-200, 200)
                                    boss.rect.centerx = boss_x
                                    boss.rect.centery = boss_y
                                    attempts += 1
                                print(f"第8层天台：生成了Boss，位置: ({boss.rect.centerx}, {boss.rect.centery})")
                            else:
                                boss_list.clear()
                            # 保存地图数据（包含敌人类型信息）
                            enemy_data = []
                            for enemy in enemies:
                                enemy_data.append((enemy.rect.x, enemy.rect.y, enemy.health))
                            maps_data[map_level] = {
                                'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles],
                                'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                                'enemies': enemy_data
                            }
                        # 为地图 2-9 生成随机医疗包
                        medkits_for_current_map.clear()
                        corpses_for_current_map.clear()
                        if 2 <= map_level <= 9:
                            positions = generate_medkits_near_obstacles(obstacles, count=3)
                            for x, y in positions:
                                medkits_for_current_map.append(Medkit(x, y, medkit_image))
                            print(f"地图 {map_level} 生成了 {len(medkits_for_current_map)} 个医疗包")
                        # 为所有地图生成弹药箱（每张地图4个）
                        ammo_boxes_for_current_map.clear()
                        ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                        for x, y in ammo_box_positions:
                            ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                        print(f"地图 {map_level} 生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
                        # Reset player position to the bottom of the new map
                        player.rect.y = world_height - player.rect.height - 10 # A little offset from the very bottom
                        player.rect.x = world_width // 2 # Center horizontally
                        # Reset camera position immediately to avoid jitter
                        camera_x = player.rect.x - screen_width // 2
                        camera_y = player.rect.y - screen_height // 2
                        # Clamp camera to world bounds
                        camera_x = max(0, min(camera_x, world_width - screen_width))
                        camera_y = max(0, min(camera_y, world_height - screen_height))
                        # Set camera transition flag to skip smooth interpolation for a few frames
                        camera_transition_frames = 5
                elif map_status == "previous_map":
                    # 检查是否已达到当前关卡组的最小地图数
                    if map_level <= min_map_level:
                        # 已达到最小地图，阻止继续后退，将玩家移回当前地图
                        player.rect.y = world_height - player.rect.height - 10  # 将玩家移回地图底部
                        print(f"已到达最小地图 {min_map_level}，无法继续后退")
                    else:
                        map_level -= 1
                        print(f"返回地图 {map_level}/{max_map_level}")
                        # 使用已保存的地图数据（地图数据应该已经存在）
                        if map_level in maps_data:
                            obstacles = [Obstacle(x, y, w, h) for x, y, w, h in maps_data[map_level]['obstacles']]
                            roads = [pygame.Rect(x, y, w, h) for x, y, w, h in maps_data[map_level]['roads']]
                            # 恢复门
                            if 'doors' in maps_data[map_level]:
                                doors = [Door(x, y, w, h, hinge=hg) for x, y, w, h, is_open, hg in maps_data[map_level]['doors']]
                                for i, (x, y, w, h, is_open, hg) in enumerate(maps_data[map_level]['doors']):
                                    if is_open:
                                        doors[i].toggle()
                                rebuild_door_pairs(doors)
                                for door in doors:
                                    if not door.is_open:
                                        obstacles.append(door)
                            else:
                                doors = []
                            # 恢复敌人（根据血量判断是普通敌人还是高级敌人）
                            enemies = []
                            for enemy_info in maps_data[map_level]['enemies']:
                                if len(enemy_info) == 3:  # 新格式：包含血量
                                    x, y, health = enemy_info
                                    if health == 250:  # 高级敌人
                                        drop_weapon = get_random_elite_weapon()
                                        enemies.append(Enemy(x, y, elite_enemy_image, health=250, drop_weapon=drop_weapon))
                                    else:  # 普通敌人
                                        enemies.append(Enemy(x, y, enemy_image, health=100))
                                else:  # 旧格式：只有位置
                                    x, y = enemy_info
                                    enemies.append(Enemy(x, y, enemy_image, health=100))
                        else:
                            # 如果数据不存在（理论上不应该发生），重新生成
                            random.seed(42 + map_level)
                            obstacles, roads, doors = generate_map(world_width, world_height, player.rect, Obstacle, map_level)
                            for door in doors:
                                if not door.is_open:
                                    obstacles.append(door)
                            enemies = generate_enemies_for_map(obstacles, player.rect, enemy_image, map_level)
                            elite_enemies = generate_elite_enemies_for_map(obstacles, player.rect, elite_enemy_image, count=4, current_map_level=map_level)
                            enemies.extend(elite_enemies)
                            # 保存地图数据（只保存位置和大小信息）
                            maps_data[map_level] = {
                                'obstacles': [(o.rect.x, o.rect.y, o.rect.width, o.rect.height) for o in obstacles if not isinstance(o, Door)],
                                'roads': [(r.x, r.y, r.width, r.height) for r in roads],
                                'enemies': [(e.rect.x, e.rect.y, e.health) for e in enemies],
                                'doors': [(d.x, d.y, d.width, d.height, d.is_open, d.hinge) for d in doors]
                            }
                        # 为地图 2-9 生成随机医疗包
                        medkits_for_current_map.clear()
                        corpses_for_current_map.clear()
                        if 2 <= map_level <= 9:
                            positions = generate_medkits_near_obstacles(obstacles, count=3)
                            for x, y in positions:
                                medkits_for_current_map.append(Medkit(x, y, medkit_image))
                        print(f"地图 {map_level} 生成了 {len(medkits_for_current_map)} 个医疗包，坐标: {positions}")
                    # 为所有地图生成弹药箱（每张地图4个）
                    ammo_boxes_for_current_map.clear()
                    ammo_box_positions = generate_ammo_boxes(obstacles, count=4)
                    for x, y in ammo_box_positions:
                        ammo_boxes_for_current_map.append(AmmoBox(x, y, ammo_box_image))
                    print(f"地图 {map_level} 生成了 {len(ammo_boxes_for_current_map)} 个弹药箱")
                    player.rect.y = 10 # 将玩家放置在地图顶部
                    player.rect.x = world_width // 2 # Center horizontally
                    # 如果返回第一张地图，重置医疗包状态（如果已被使用）
                    if map_level == 1:
                        for m in medkits_for_current_map:
                            m.used = False  # 重置医疗包，可以再次使用
                    # Reset camera position immediately to avoid jitter
                    camera_x = player.rect.x - screen_width // 2
                    camera_y = player.rect.y - screen_height // 2
                    # Clamp camera to world bounds
                    camera_x = max(0, min(camera_x, world_width - screen_width))
                    camera_y = max(0, min(camera_y, world_height - screen_height))
                    # Set camera transition flag to skip smooth interpolation for a few frames
                    camera_transition_frames = 5

            # 判断玩家是否正在主动移动
            is_player_actively_moving = False
            if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
                is_player_actively_moving = True

            # 摄像机跟随逻辑
            if right_mouse_down:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # 根据当前武器类型设置拖动视野倍数
                if player.current_weapon.name == "狙击枪":
                    drag_multiplier = 3.0  # 狙击枪拖动视野是步枪的3倍
                elif player.current_weapon.name == "步枪":
                    drag_multiplier = 1.0  # 步枪基准值
                else:
                    drag_multiplier = 1.0  # 其他武器使用默认值
                # 计算鼠标在世界坐标中的位置（根据武器类型调整拖动范围）
                target_camera_x = player.rect.x - screen_width // 2 + (mouse_x - screen_width // 2) * drag_multiplier
                target_camera_y = player.rect.y - screen_height // 2 + (mouse_y - screen_height // 2) * drag_multiplier
                # 限制摄像机范围
                target_camera_x = max(0, min(target_camera_x, world_width - screen_width))
                target_camera_y = max(0, min(target_camera_y, world_height - screen_height))
                # 平滑移动摄像机
                camera_x += (target_camera_x - camera_x) * 0.2
                camera_y += (target_camera_y - camera_y) * 0.2
            else:
                camera_x += ((player.rect.x - screen_width // 2) - camera_x) * 0.2
                camera_y += ((player.rect.y - screen_height // 2) - camera_y) * 0.2
            camera_x = max(0, min(camera_x, world_width - screen_width))
            camera_y = max(0, min(camera_y, world_height - screen_height))
            # 屏幕震动偏移
            shake_ox, shake_oy = get_screen_shake_offset()
            camera_x += shake_ox
            camera_y += shake_oy
            # 各层底板颜色
            floor_colors = {1: (50, 50, 50), 2: (40, 45, 50), 3: (35, 45, 55), 4: (45, 45, 40),
                           5: (40, 50, 45), 6: (50, 45, 45), 7: (38, 42, 52), 8: (30, 35, 45)}
            floor_color = floor_colors.get(map_level, background_color) if current_stage == 1 else background_color
            screen.fill(floor_color)
            
            if is_map_open:
                # 绘制全屏地图
                map_surface = pygame.Surface((screen_width, screen_height))
                map_surface.fill((50, 50, 50)) # 地图背景色

                # 计算全屏地图的缩放比例
                scale_x = screen_width / world_width
                scale_y = screen_height / world_height

                # 绘制全屏地图上的障碍物（不显示门）
                for obstacle in obstacles:
                    if isinstance(obstacle, Door):
                        continue
                    map_obstacle_rect = pygame.Rect(
                        obstacle.rect.x * scale_x,
                        obstacle.rect.y * scale_y,
                        obstacle.rect.width * scale_x,
                        obstacle.rect.height * scale_y
                    )
                    pygame.draw.rect(map_surface, (128, 128, 128), map_obstacle_rect)

                # 绘制全屏地图上的玩家
                map_player_rect = pygame.Rect(
                    player.rect.x * scale_x,
                    player.rect.y * scale_y,
                    player.rect.width * scale_x,
                    player.rect.height * scale_y
                )
                pygame.draw.rect(map_surface, (0, 255, 0), map_player_rect) # 绿色表示玩家

                # 小地图/全屏地图不再显示敌人

                # 所有楼层：全屏地图上绘制电梯位置（青色）
                if current_stage == 1 and 1 <= map_level <= 8:
                    map_elevator_rect = pygame.Rect(
                        elevator_rect.x * scale_x, elevator_rect.y * scale_y,
                        elevator_rect.width * scale_x, elevator_rect.height * scale_y
                    )
                    pygame.draw.rect(map_surface, (0, 200, 220), map_elevator_rect)

                # 绘制全屏地图上的医疗包（蓝色标记）
                # 地图1的医疗包
                if map_level == 1:
                    for m in medkits_for_current_map:
                        if not m.used:
                            map_medkit_rect = pygame.Rect(
                                m.rect.x * scale_x,
                                m.rect.y * scale_y,
                                m.rect.width * scale_x,
                                m.rect.height * scale_y
                            )
                            pygame.draw.rect(map_surface, (0, 0, 255), map_medkit_rect) # 蓝色表示医疗包
                
                # 地图2-9的随机医疗包
                if 2 <= map_level <= 9:
                    for medkit_item in medkits_for_current_map:
                        if not medkit_item.used:
                            map_medkit_rect = pygame.Rect(
                                medkit_item.rect.x * scale_x,
                                medkit_item.rect.y * scale_y,
                                medkit_item.rect.width * scale_x,
                                medkit_item.rect.height * scale_y
                            )
                            pygame.draw.rect(map_surface, (0, 0, 255), map_medkit_rect) # 蓝色表示医疗包
                
                # 绘制全屏地图上的弹药箱（橙色标记）
                for ammo_box in ammo_boxes_for_current_map:
                    if not ammo_box.used:
                        map_ammo_rect = pygame.Rect(
                            ammo_box.rect.x * scale_x,
                            ammo_box.rect.y * scale_y,
                            ammo_box.rect.width * scale_x,
                            ammo_box.rect.height * scale_y
                        )
                        pygame.draw.rect(map_surface, (255, 165, 0), map_ammo_rect) # 橙色表示弹药箱

                screen.blit(map_surface, (0, 0))
                
                # 如果正在进行教程步骤6，显示地图颜色说明
                if current_stage == 1 and tutorial_step == 6:
                    tutorial_font = get_chinese_font(30)
                    tutorial_hint_font = get_chinese_font(24)
                    
                    # 增大背景框以容纳更多文字
                    tutorial_bg = pygame.Surface((screen_width - 40, 140))
                    tutorial_bg.set_alpha(220)
                    tutorial_bg.fill((20, 20, 30))
                    screen.blit(tutorial_bg, (20, screen_height - 160))
                    
                    # 绘制标题
                    title_text = tutorial_font.render("新手教程：地图说明", True, (100, 200, 255))
                    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height - 130))
                    screen.blit(title_text, title_rect)
                    
                    # 绘制颜色说明（分行显示）
                    color_hint1 = tutorial_hint_font.render("绿色=玩家  灰色=障碍物", True, (255, 255, 255))
                    color_hint2 = tutorial_hint_font.render("蓝色=医疗包  橙色=弹药箱", True, (255, 255, 255))
                    hint_rect1 = color_hint1.get_rect(center=(screen_width // 2, screen_height - 100))
                    hint_rect2 = color_hint2.get_rect(center=(screen_width // 2, screen_height - 70))
                    screen.blit(color_hint1, hint_rect1)
                    screen.blit(color_hint2, hint_rect2)
                    
                    # 绘制关闭提示
                    close_hint = tutorial_hint_font.render("按 TAB 键关闭地图继续", True, (255, 200, 100))
                    close_rect = close_hint.get_rect(center=(screen_width // 2, screen_height - 40))
                    screen.blit(close_hint, close_rect)
            elif radar_on:
                # 雷达界面：全屏网格、中心红球（玩家）、旋转绿色扇形（约30%屏）、敌人为点，发现附近敌人可按 N 切回
                radar_angle += 0.03  # 扇形持续转动
                if radar_angle > 2 * math.pi:
                    radar_angle -= 2 * math.pi
                cx, cy = screen_width // 2, screen_height // 2
                screen.fill((18, 22, 28))
                grid_step = 24
                for x in range(0, screen_width + 1, grid_step):
                    pygame.draw.line(screen, (45, 55, 62), (x, 0), (x, screen_height))
                for y in range(0, screen_height + 1, grid_step):
                    pygame.draw.line(screen, (45, 55, 62), (0, y), (screen_width, y))
                # 绿色三角延伸到屏幕边缘（与开地图一样，雷达下不显示墙/掩体，只显示网格与扇形）
                radar_radius = min(screen_width, screen_height) // 2
                sector_angle = math.pi / 4
                x1 = cx + radar_radius * math.cos(radar_angle)
                y1 = cy - radar_radius * math.sin(radar_angle)
                x2 = cx + radar_radius * math.cos(radar_angle + sector_angle)
                y2 = cy - radar_radius * math.sin(radar_angle + sector_angle)
                pygame.draw.polygon(screen, (0, 200, 80), [(cx, cy), (x1, y1), (x2, y2)])
                pygame.draw.circle(screen, (255, 50, 50), (cx, cy), 14)
                pygame.draw.circle(screen, (200, 30, 30), (cx, cy), 10)
                world_range = 800
                nearby_count = 0
                for enemy in enemies:
                    dx = enemy.rect.centerx - player.rect.centerx
                    dy = enemy.rect.centery - player.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < world_range and dist > 0:
                        nearby_count += 1
                        rx = cx + dx / world_range * radar_radius
                        ry = cy - dy / world_range * radar_radius
                        pygame.draw.circle(screen, (255, 180, 50), (int(rx), int(ry)), 6)
                for boss in boss_list:
                    dx = boss.rect.centerx - player.rect.centerx
                    dy = boss.rect.centery - player.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < world_range and dist > 0:
                        nearby_count += 1
                        rx = cx + dx / world_range * radar_radius
                        ry = cy - dy / world_range * radar_radius
                        pygame.draw.circle(screen, (255, 100, 50), (int(rx), int(ry)), 8)
                for zombie in zombies_for_current_map:
                    dx = zombie.rect.centerx - player.rect.centerx
                    dy = zombie.rect.centery - player.rect.centery
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < world_range and dist > 0:
                        nearby_count += 1
                        rx = cx + dx / world_range * radar_radius
                        ry = cy - dy / world_range * radar_radius
                        pygame.draw.circle(screen, (120, 255, 120), (int(rx), int(ry)), 6)
                if nearby_count > 0:
                    radar_font = get_chinese_font(22)
                    hint = radar_font.render("发现附近敌人  按 N 切回正常", True, (255, 220, 100))
                    hr = hint.get_rect(center=(screen_width // 2, screen_height - 28))
                    screen.blit(hint, hr)
                else:
                    radar_font = get_chinese_font(20)
                    hint = radar_font.render("按 N 关闭雷达", True, (120, 140, 150))
                    hr = hint.get_rect(center=(screen_width // 2, screen_height - 24))
                    screen.blit(hint, hr)
            else:
                # 绘制马路
                for road in roads:
                    # 将世界坐标转换为屏幕坐标
                    screen_road_rect = pygame.Rect(road.x - camera_x, road.y - camera_y, road.width, road.height)
                    pygame.draw.rect(screen, (100, 100, 100), screen_road_rect)

                grid_size = 100
                for x in range(0, world_width, grid_size):
                    screen_x = x - camera_x
                    if 0 <= screen_x <= screen_width:
                        pygame.draw.line(screen, (100, 100, 100), (screen_x, 0), (screen_x, screen_height))
                for y in range(0, world_height, grid_size):
                    screen_y = y - camera_y
                    if 0 <= screen_y <= screen_height:
                        pygame.draw.line(screen, (100, 100, 100), (0, screen_y), (screen_width, screen_y))
                
                # 绘制障碍物
                for obstacle in obstacles:
                    obstacle.draw(screen, camera_x, camera_y)

                # 更新门动画 & 绘制门
                for door in doors:
                    door.update()
                    door.draw(screen, camera_x, camera_y)

                # 所有楼层：绘制电梯
                if current_stage == 1 and 1 <= map_level <= 8:
                    elevator_screen_rect = pygame.Rect(elevator_rect.x - camera_x, elevator_rect.y - camera_y, elevator_rect.width, elevator_rect.height)
                    pygame.draw.rect(screen, (80, 80, 90), elevator_screen_rect)
                    pygame.draw.rect(screen, (0, 200, 220), elevator_screen_rect, 2)
                    # 电梯标志文字
                    elev_font = get_chinese_font(16)
                    elev_text = elev_font.render("电梯[E]", True, (200, 220, 255))
                    elev_text_rect = elev_text.get_rect(centerx=elevator_screen_rect.centerx, bottom=elevator_screen_rect.top - 4)
                    screen.blit(elev_text, elev_text_rect)

                # 绘制容器（箱子）
                for c in containers_for_current_map:
                    c.draw(screen, camera_x, camera_y)
                # 绘制钥匙/保险箱
                if key_item_for_current_map:
                    key_item_for_current_map.draw(screen, camera_x, camera_y)
                for safe in safes_for_current_map:
                    safe.draw(screen, camera_x, camera_y)
                # 拾取进度条（正在拾取时）
                if looting_container is not None:
                    elapsed = current_time - looting_start_time
                    progress = min(1.0, elapsed / Container.LOOT_TIME_MS)
                    bar_w, bar_h = 200, 14
                    bar_x = screen_width // 2 - bar_w // 2
                    bar_y = screen_height // 2 - 60
                    pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
                    pygame.draw.rect(screen, (0, 180, 80), (bar_x, bar_y, int(bar_w * progress), bar_h))
                    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2)
                    loot_font = get_chinese_font(18)
                    txt = loot_font.render("拾取中... %.1f秒" % (3.0 - elapsed/1000.0), True, (220, 220, 220))
                    screen.blit(txt, (bar_x, bar_y - 22))

                # 绘制玩家
                player.draw(screen, camera_x, camera_y)
                
                # 绘制所有地图的医疗包（包括地图1）
                for m in medkits_for_current_map:
                    m.draw(screen, camera_x, camera_y)
                
                # 绘制所有地图的弹药箱
                for ammo_box in ammo_boxes_for_current_map:
                    ammo_box.draw(screen, camera_x, camera_y)
                
                # 绘制所有地图的武器掉落物
                for weapon_drop in weapon_drops_for_current_map:
                    if not weapon_drop.used:
                        weapon_drop.draw(screen, camera_x, camera_y)
                
                # 教程步骤7：绘制箭头指向最近的医疗包
                if current_stage == 1 and tutorial_step == 7 and map_level == 1:
                    # 找到最近的未使用医疗包
                    nearest_medkit = None
                    min_distance = float('inf')
                    for m in medkits_for_current_map:
                        if m.used:
                            continue
                        dx = m.rect.centerx - player.rect.centerx
                        dy = m.rect.centery - player.rect.centery
                        distance = math.sqrt(dx * dx + dy * dy)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_medkit = m
                    
                    # 只有当距离大于150像素时才显示箭头
                    if nearest_medkit and min_distance > 150:
                        # 计算玩家和医疗包的屏幕坐标
                        player_screen_x = player.rect.centerx - camera_x
                        player_screen_y = player.rect.centery - camera_y
                        medkit_screen_x = nearest_medkit.rect.centerx - camera_x
                        medkit_screen_y = nearest_medkit.rect.centery - camera_y
                        
                        # 如果医疗包在屏幕内，直接绘制箭头
                        if 0 <= medkit_screen_x <= screen_width and 0 <= medkit_screen_y <= screen_height:
                            # 计算方向向量
                            dx = medkit_screen_x - player_screen_x
                            dy = medkit_screen_y - player_screen_y
                            distance = math.sqrt(dx * dx + dy * dy)
                            
                            if distance > 0:
                                # 归一化方向向量
                                dx_norm = dx / distance
                                dy_norm = dy / distance
                                
                                # 箭头起点（玩家位置稍微偏移）
                                arrow_start_x = player_screen_x + dx_norm * 30
                                arrow_start_y = player_screen_y + dy_norm * 30
                                
                                # 箭头终点（医疗包位置稍微偏移）
                                arrow_end_x = medkit_screen_x - dx_norm * 20
                                arrow_end_y = medkit_screen_y - dy_norm * 20
                                
                                # 绘制箭头线
                                arrow_color = (255, 255, 0)  # 黄色箭头
                                pygame.draw.line(screen, arrow_color, (arrow_start_x, arrow_start_y), 
                                               (arrow_end_x, arrow_end_y), 3)
                                
                                # 绘制箭头头部（三角形）
                                arrow_head_size = 15
                                angle = math.atan2(dy, dx)
                                
                                # 箭头头部的三个点
                                head_point1 = (arrow_end_x, arrow_end_y)
                                head_point2 = (
                                    arrow_end_x - arrow_head_size * math.cos(angle - math.pi / 6),
                                    arrow_end_y - arrow_head_size * math.sin(angle - math.pi / 6)
                                )
                                head_point3 = (
                                    arrow_end_x - arrow_head_size * math.cos(angle + math.pi / 6),
                                    arrow_end_y - arrow_head_size * math.sin(angle + math.pi / 6)
                                )
                                
                                pygame.draw.polygon(screen, arrow_color, [head_point1, head_point2, head_point3])
                        else:
                            # 医疗包在屏幕外，箭头指向屏幕边缘
                            # 计算方向向量
                            dx = medkit_screen_x - player_screen_x
                            dy = medkit_screen_y - player_screen_y
                            distance = math.sqrt(dx * dx + dy * dy)
                            
                            if distance > 0:
                                # 归一化方向向量
                                dx_norm = dx / distance
                                dy_norm = dy / distance
                                
                                # 箭头起点（玩家位置）
                                arrow_start_x = player_screen_x
                                arrow_start_y = player_screen_y
                                
                                # 计算箭头终点（屏幕边缘）
                                # 找到与屏幕边缘的交点
                                edge_x = arrow_start_x
                                edge_y = arrow_start_y
                                
                                # 检查各个边缘
                                if dx_norm > 0:  # 向右
                                    t = (screen_width - arrow_start_x) / dx_norm if dx_norm != 0 else float('inf')
                                    if t > 0:
                                        test_y = arrow_start_y + dy_norm * t
                                        if 0 <= test_y <= screen_height:
                                            edge_x = screen_width
                                            edge_y = test_y
                                elif dx_norm < 0:  # 向左
                                    t = -arrow_start_x / dx_norm if dx_norm != 0 else float('inf')
                                    if t > 0:
                                        test_y = arrow_start_y + dy_norm * t
                                        if 0 <= test_y <= screen_height:
                                            edge_x = 0
                                            edge_y = test_y
                                
                                if dy_norm > 0:  # 向下
                                    t = (screen_height - arrow_start_y) / dy_norm if dy_norm != 0 else float('inf')
                                    if t > 0:
                                        test_x = arrow_start_x + dx_norm * t
                                        if 0 <= test_x <= screen_width:
                                            if abs(test_x - arrow_start_x) < abs(edge_x - arrow_start_x) or edge_x == arrow_start_x:
                                                edge_x = test_x
                                                edge_y = screen_height
                                elif dy_norm < 0:  # 向上
                                    t = -arrow_start_y / dy_norm if dy_norm != 0 else float('inf')
                                    if t > 0:
                                        test_x = arrow_start_x + dx_norm * t
                                        if 0 <= test_x <= screen_width:
                                            if abs(test_x - arrow_start_x) < abs(edge_x - arrow_start_x) or edge_x == arrow_start_x:
                                                edge_x = test_x
                                                edge_y = 0
                                
                                # 绘制箭头线
                                arrow_color = (255, 255, 0)  # 黄色箭头
                                pygame.draw.line(screen, arrow_color, (arrow_start_x, arrow_start_y), 
                                               (edge_x, edge_y), 3)
                                
                                # 绘制箭头头部
                                angle = math.atan2(edge_y - arrow_start_y, edge_x - arrow_start_x)
                                arrow_head_size = 15
                                
                                head_point1 = (edge_x, edge_y)
                                head_point2 = (
                                    edge_x - arrow_head_size * math.cos(angle - math.pi / 6),
                                    edge_y - arrow_head_size * math.sin(angle - math.pi / 6)
                                )
                                head_point3 = (
                                    edge_x - arrow_head_size * math.cos(angle + math.pi / 6),
                                    edge_y - arrow_head_size * math.sin(angle + math.pi / 6)
                                )
                                
                                pygame.draw.polygon(screen, arrow_color, [head_point1, head_point2, head_point3])

                # 技能商城覆盖层（按 B 打开，金币购买手雷/医疗/弹药）
                if is_shop_open:
                    overlay = pygame.Surface((screen_width, screen_height))
                    overlay.set_alpha(200)
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, (0, 0))
                    panel_w, panel_h = 340, 300
                    panel = pygame.Rect((screen_width - panel_w) // 2, (screen_height - panel_h) // 2, panel_w, panel_h)
                    pygame.draw.rect(screen, (50, 45, 60), panel)
                    pygame.draw.rect(screen, (180, 160, 200), panel, 3)
                    shop_font = get_chinese_font(26)
                    shop_small = get_chinese_font(20)
                    title = shop_font.render("技能商城  金币: %d" % player.coins, True, (255, 220, 100))
                    screen.blit(title, (panel.x + 20, panel.y + 16))
                    # 商品 1: 手雷 x3  50金
                    # 商品 2: 医疗包 1 30金
                    # 商品 3: 弹药 +30 40金
                    items = [
                        ("[1] 手雷 x3", 50, "grenade"),
                        ("[2] 医疗包 x1", 30, "medkit"),
                        ("[3] 弹药 +30", 40, "ammo"),
                    ]
                    for i, (name, price, kind) in enumerate(items):
                        y = panel.y + 62 + i * 56
                        txt = shop_small.render("%s  %d 金币" % (name, price), True, (255, 255, 255))
                        screen.blit(txt, (panel.x + 24, y))
                        if player.coins < price:
                            pygame.draw.rect(screen, (80, 70, 70), (panel.x + panel_w - 90, y - 2, 70, 28))
                            need = shop_small.render("金币不足", True, (200, 100, 100))
                            screen.blit(need, (panel.x + panel_w - 86, y))
                    hint = shop_small.render("按 B 关闭", True, (160, 160, 180))
                    screen.blit(hint, (panel.x + panel_w - 100, panel.y + panel_h - 32))

            if not is_map_open and not radar_on and not is_shop_open:
                # 如果鼠标左键按下且冷却时间已过，则连续发射子弹（使用当前枪械的属性）
                if left_mouse_down:
                    # 使用当前枪械的射速
                    weapon_fire_rate = player.current_weapon.fire_rate
                    if (current_time - last_shot_time > weapon_fire_rate and
                        (infinite_ammo or player.current_bullets > 0) and
                        not player.reloading):
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        # 将屏幕坐标转换为世界坐标
                        target_world_x = mouse_x + camera_x
                        target_world_y = mouse_y + camera_y
                        
                        # 使用当前枪械的子弹速度和伤害
                        weapon_bullet_speed = player.current_weapon.bullet_speed
                        weapon_damage = player.current_weapon.damage
                        # 计算枪口位置（对应人物图片的枪口）
                        muzzle_x, muzzle_y = player.get_muzzle_pos(target_world_x, target_world_y)
                        # 如果是RPG，创建带爆炸属性的子弹
                        is_rpg = (player.current_weapon.name == "rpg")
                        new_bullet = Bullet(muzzle_x, muzzle_y, target_world_x, target_world_y, bullet_image, is_enemy_bullet=False, speed=weapon_bullet_speed, damage=weapon_damage, is_rpg_bullet=is_rpg, explosion_radius=150)
                        bullets.append(new_bullet)
                        if not infinite_ammo:
                            player.current_bullets -= 1 # 射击后减少子弹数量
                        else:
                            player.current_bullets = player.max_clip_bullets

                        last_shot_time = current_time

                # 更新和绘制子弹
                for bullet in bullets:
                    bullet.update()
                    bullet.draw(screen, camera_x, camera_y)
                
                # 更新和绘制爆炸特效
                for explosion in explosions[:]:
                    if explosion.update(current_time):
                        explosion.draw(screen, camera_x, camera_y, obstacles)
                    else:
                        explosions.remove(explosion)

                # 移除超出世界边界的子弹（RPG子弹超出边界时触发爆炸）
                bullets_to_remove = []
                for bullet in bullets:
                    if bullet.rect.x < 0 or bullet.rect.x > world_width or bullet.rect.y < 0 or bullet.rect.y > world_height:
                        # 如果是RPG子弹，在边界位置触发爆炸
                        if bullet.is_rpg_bullet:
                            # 将子弹位置限制在世界边界内
                            explosion_x = max(0, min(bullet.rect.centerx, world_width))
                            explosion_y = max(0, min(bullet.rect.centery, world_height))
                            apply_explosion_damage(explosion_x, explosion_y, bullet.explosion_radius, bullet.damage, enemies, boss_list, obstacles)
                        bullets_to_remove.append(bullet)
                for bullet in bullets_to_remove:
                    bullets.remove(bullet)

                # 子弹与障碍物碰撞检测
                for bullet in bullets[:]:
                    for obstacle in obstacles:
                        if bullet.rect.colliderect(obstacle.rect):
                            # 如果是RPG子弹，触发范围伤害
                            if bullet.is_rpg_bullet:
                                apply_explosion_damage(bullet.rect.centerx, bullet.rect.centery, bullet.explosion_radius, bullet.damage, enemies, boss_list, obstacles)
                            bullets.remove(bullet)
                            break

                # 子弹与敌人碰撞检测
                for bullet in bullets[:]: # 遍历副本，允许在循环中修改原列表
                    # 检测与普通敌人和高级敌人的碰撞
                    for enemy in enemies[:]:
                        if pygame.sprite.collide_rect(bullet, enemy):
                            # 如果是RPG子弹，触发范围伤害
                            if bullet.is_rpg_bullet:
                                apply_explosion_damage(bullet.rect.centerx, bullet.rect.centery, bullet.explosion_radius, bullet.damage, enemies, boss_list, obstacles)
                                trigger_screen_shake(10, 400)  # RPG爆炸震动
                                bullets.remove(bullet)
                            else:
                                # 普通子弹直接造成伤害
                                enemy.health -= bullet.damage # 敌人受到伤害（使用子弹的伤害值）
                                enemy.is_aggroed = True # 敌人被攻击后进入追击模式
                                # 伤害飘字
                                damage_numbers.append(DamageNumber(enemy.rect.centerx, enemy.rect.top, int(bullet.damage), (255, 255, 100)))
                                if enemy.health <= 0:
                                    # === 击杀计数和连杀系统 ===
                                    kill_count += 1
                                    coin_reward = 5 if enemy.max_health == 100 else 15  # 普通5金币，高级15金币
                                    player.coins += coin_reward
                                    # 连杀判定
                                    if current_time - last_kill_time < kill_streak_timeout:
                                        kill_streak += 1
                                    else:
                                        kill_streak = 1
                                    last_kill_time = current_time
                                    if kill_streak >= 2:
                                        streak_message, streak_message_color = get_streak_info(kill_streak)
                                        streak_message_time = current_time
                                    # 检查是否是高级敌人，如果是则掉落对应武器
                                    if enemy.max_health == 250:
                                        # 如果没有drop_weapon，随机生成一个
                                        if not hasattr(enemy, 'drop_weapon') or not enemy.drop_weapon:
                                            enemy.drop_weapon = get_random_elite_weapon()
                                            print(f"警告：高级敌人没有掉落武器，已随机分配: {enemy.drop_weapon}")
                                        # 在敌人位置生成武器掉落物（使用敌人记录的掉落武器）
                                        weapon_drop = WeaponDrop(enemy.rect.centerx, enemy.rect.centery, enemy.drop_weapon, elite_enemy_image)
                                        weapon_drops_for_current_map.append(weapon_drop)
                                        print(f"高级敌人掉落{enemy.drop_weapon}！位置: ({enemy.rect.centerx}, {enemy.rect.centery})，掉落物数量: {len(weapon_drops_for_current_map)}")
                                    # 检查是否是任务目标敌人
                                    if current_task == "kill_enemy_above" and enemy == task_target_enemy and not task_completed:
                                        task_completed = True
                                        task_completed_time = current_time
                                        task_target_enemy = None
                                        print("任务完成：已击杀玩家上方的敌人！")
                                    # 击杀飘字（金色大字）
                                    damage_numbers.append(DamageNumber(enemy.rect.centerx, enemy.rect.top - 20, coin_reward, (255, 215, 0), is_crit=True))
                                    corpses_for_current_map.append(Corpse(enemy.rect.centerx, enemy.rect.centery, enemy.original_image, enemy.facing_angle))
                                    enemies.remove(enemy)
                                bullets.remove(bullet)
                            break # 子弹击中敌人，跳出内层循环
                    # 检测与Boss的碰撞（在同一个子弹循环内）
                    if bullet in bullets:  # 如果子弹还没有被移除
                        for boss in boss_list[:]:
                            if pygame.sprite.collide_rect(bullet, boss):
                                # 如果是RPG子弹，触发范围伤害
                                if bullet.is_rpg_bullet:
                                    apply_explosion_damage(bullet.rect.centerx, bullet.rect.centery, bullet.explosion_radius, bullet.damage, enemies, boss_list, obstacles)
                                    trigger_screen_shake(10, 400)
                                    bullets.remove(bullet)
                                else:
                                    # 普通子弹直接造成伤害
                                    boss.health -= bullet.damage
                                    boss.is_aggroed = True
                                    # Boss伤害飘字（红色）
                                    damage_numbers.append(DamageNumber(boss.rect.centerx, boss.rect.top, int(bullet.damage), (255, 100, 100)))
                                    if boss.health <= 0:
                                        # === Boss击杀奖励 ===
                                        kill_count += 1
                                        player.coins += 50  # Boss奖励50金币
                                        if current_time - last_kill_time < kill_streak_timeout:
                                            kill_streak += 1
                                        else:
                                            kill_streak = 1
                                        last_kill_time = current_time
                                        if kill_streak >= 2:
                                            streak_message, streak_message_color = get_streak_info(kill_streak)
                                            streak_message_time = current_time
                                        damage_numbers.append(DamageNumber(boss.rect.centerx, boss.rect.top - 30, 50, (255, 215, 0), is_crit=True))
                                        # Boss掉落RPG武器
                                        weapon_drop = WeaponDrop(boss.rect.centerx, boss.rect.centery, "rpg", boss_tank_image)
                                        weapon_drops_for_current_map.append(weapon_drop)
                                        print(f"Boss被击败！掉落rpg武器！位置: ({boss.rect.centerx}, {boss.rect.centery})")
                                        corpses_for_current_map.append(Corpse(boss.rect.centerx, boss.rect.centery, boss.original_image, boss.facing_angle))
                                        boss_list.remove(boss)
                                    bullets.remove(bullet)
                                break

                # 子弹与僵尸碰撞检测
                for bullet in bullets[:]:
                    for zombie in zombies_for_current_map[:]:
                        if pygame.sprite.collide_rect(bullet, zombie):
                            if bullet.is_rpg_bullet:
                                apply_explosion_damage(
                                    bullet.rect.centerx, bullet.rect.centery,
                                    bullet.explosion_radius, bullet.damage,
                                    enemies, boss_list, obstacles
                                )
                                trigger_screen_shake(10, 400)
                                if bullet in bullets:
                                    bullets.remove(bullet)
                            else:
                                zombie.health -= bullet.damage
                                damage_numbers.append(
                                    DamageNumber(zombie.rect.centerx, zombie.rect.top, int(bullet.damage), (120, 255, 120))
                                )
                                if zombie.health <= 0:
                                    kill_count += 1
                                    coin_reward = 3
                                    player.coins += coin_reward
                                    if current_time - last_kill_time < kill_streak_timeout:
                                        kill_streak += 1
                                    else:
                                        kill_streak = 1
                                    last_kill_time = current_time
                                    if kill_streak >= 2:
                                        streak_message, streak_message_color = get_streak_info(kill_streak)
                                        streak_message_time = current_time
                                    damage_numbers.append(
                                        DamageNumber(zombie.rect.centerx, zombie.rect.top - 18, coin_reward, (255, 215, 0), is_crit=True)
                                    )
                                    corpses_for_current_map.append(
                                        Corpse(zombie.rect.centerx, zombie.rect.centery, zombie.original_image, zombie.facing_angle)
                                    )
                                    zombies_for_current_map.remove(zombie)
                                if bullet in bullets:
                                    bullets.remove(bullet)
                            break

                # 先绘制尸体（在活着的敌人下方）
                for corpse in corpses_for_current_map:
                    corpse.draw(screen, camera_x, camera_y)
                # 更新和绘制敌人
                for enemy in enemies:
                    # 传递 player 对象而不是坐标
                    enemy.update(player, current_time, enemy_bullets, bullet_image, camera_x, camera_y, screen_width, screen_height, is_player_actively_moving, obstacles)
                    enemy.draw(screen, camera_x, camera_y)
                    # 按7显示敌人血条和血量
                    if show_enemy_health:
                        ex = enemy.rect.x - camera_x
                        ey = enemy.rect.y - camera_y - 14
                        ew = enemy.rect.width
                        bar_h = 5
                        hp_ratio = max(0, enemy.health / enemy.max_health)
                        pygame.draw.rect(screen, (80, 0, 0), (ex, ey, ew, bar_h))
                        pygame.draw.rect(screen, (0, 255, 0), (ex, ey, int(ew * hp_ratio), bar_h))
                        pygame.draw.rect(screen, (200, 200, 200), (ex, ey, ew, bar_h), 1)
                        hp_font = get_chinese_font(14)
                        hp_txt = hp_font.render(f"{int(enemy.health)}/{int(enemy.max_health)}", True, (255, 255, 255))
                        hp_rect = hp_txt.get_rect(midbottom=(ex + ew // 2, ey - 1))
                        screen.blit(hp_txt, hp_rect)

                # 更新和绘制僵尸
                for zombie in zombies_for_current_map:
                    zombie.update(player, current_time, obstacles, enemies, boss_list)
                    zombie.draw(screen, camera_x, camera_y)
                    if show_enemy_health:
                        zx = zombie.rect.x - camera_x
                        zy = zombie.rect.y - camera_y - 12
                        zw = zombie.rect.width
                        hp_ratio = max(0, zombie.health / zombie.max_health)
                        pygame.draw.rect(screen, (80, 0, 0), (zx, zy, zw, 5))
                        pygame.draw.rect(screen, (80, 220, 80), (zx, zy, int(zw * hp_ratio), 5))
                        pygame.draw.rect(screen, (200, 200, 200), (zx, zy, zw, 5), 1)

                # 僵尸与敌人/Boss互殴后的死亡清理
                for enemy in enemies[:]:
                    if enemy.health <= 0:
                        corpses_for_current_map.append(Corpse(enemy.rect.centerx, enemy.rect.centery, enemy.original_image, enemy.facing_angle))
                        enemies.remove(enemy)
                for boss in boss_list[:]:
                    if boss.health <= 0:
                        corpses_for_current_map.append(Corpse(boss.rect.centerx, boss.rect.centery, boss.original_image, boss.facing_angle))
                        boss_list.remove(boss)
                
                # 更新和绘制Boss（使用和普通敌人一样的逻辑）
                for boss in boss_list:
                    boss.update(player, current_time, enemy_bullets, bullet_image, camera_x, camera_y, screen_width, screen_height, is_player_actively_moving, obstacles)
                    boss.draw(screen, camera_x, camera_y)
                    # 按7也显示Boss血量数字
                    if show_enemy_health:
                        bx = boss.rect.x - camera_x
                        by = boss.rect.y - camera_y - 18
                        bw = boss.rect.width
                        hp_font = get_chinese_font(16)
                        hp_txt = hp_font.render(f"{int(boss.health)}/{int(boss.max_health)}", True, (255, 255, 255))
                        hp_rect = hp_txt.get_rect(midbottom=(bx + bw // 2, by))
                        screen.blit(hp_txt, hp_rect)

                # 更新和绘制敌人子弹
                for bullet in enemy_bullets:
                    bullet.update(current_time) # 传递当前时间用于追踪
                    bullet.draw(screen, camera_x, camera_y)
                
                # 移除超出屏幕的敌人子弹
                enemy_bullets = [bullet for bullet in enemy_bullets if screen.get_rect().colliderect(bullet.rect.move(-camera_x, -camera_y))]

                # 敌人子弹与障碍物碰撞检测
                for bullet in enemy_bullets[:]:
                    for obstacle in obstacles:
                        if bullet.rect.colliderect(obstacle.rect):
                            enemy_bullets.remove(bullet)
                            break
                # 敌人子弹可误伤僵尸
                for bullet in enemy_bullets[:]:
                    hit_zombie = False
                    for zombie in zombies_for_current_map[:]:
                        if bullet.rect.colliderect(zombie.rect):
                            zombie.health -= bullet.damage
                            if zombie.health <= 0:
                                corpses_for_current_map.append(
                                    Corpse(zombie.rect.centerx, zombie.rect.centery, zombie.original_image, zombie.facing_angle)
                                )
                                zombies_for_current_map.remove(zombie)
                            hit_zombie = True
                            break
                    if hit_zombie and bullet in enemy_bullets:
                        enemy_bullets.remove(bullet)

                # 玩家与敌人碰撞检测
                for enemy in enemies[:]:
                    if player.rect.colliderect(enemy.rect):
                        pass # 敌人碰到玩家不再造成伤害

                # === 手雷更新与爆炸 ===
                for grenade in grenades_in_air[:]:
                    grenade.update(current_time, obstacles)
                    if grenade.exploded:
                        # 手雷爆炸，造成范围伤害
                        apply_explosion_damage(int(grenade.world_x), int(grenade.world_y), grenade.explosion_radius, 200, enemies, boss_list, obstacles)
                        trigger_screen_shake(8, 300)
                        grenades_in_air.remove(grenade)
                    else:
                        grenade.draw(screen, camera_x, camera_y)
                
                # === 闪避翻滚更新 ===
                if dodge_rolling:
                    elapsed = current_time - dodge_roll_start
                    if elapsed >= dodge_roll_duration:
                        dodge_rolling = False
                    else:
                        collision_shrink = 8
                        # 翻滚移动
                        move_x = dodge_roll_dx * dodge_roll_speed
                        move_y = dodge_roll_dy * dodge_roll_speed
                        player.rect.x += int(move_x)
                        for obstacle in obstacles:
                            test_rect = obstacle.rect.inflate(-collision_shrink, -collision_shrink)
                            if player.rect.colliderect(test_rect):
                                player.rect.x -= int(move_x)
                                break
                        player.rect.y += int(move_y)
                        for obstacle in obstacles:
                            test_rect = obstacle.rect.inflate(-collision_shrink, -collision_shrink)
                            if player.rect.colliderect(test_rect):
                                player.rect.y -= int(move_y)
                                break
                        # 翻滚期间玩家半透明效果（通过不受伤实现无敌）
                
                # === 伤害飘字更新 ===
                damage_numbers = [dn for dn in damage_numbers if dn.update(current_time)]

                # 记录范围内最近的可交互物品（提示在雾效之后统一画在物品上方）
                prompt_medkit = None
                prompt_ammo_box = None
                prompt_weapon_drop = None
                prompt_key_item = None
                prompt_safe = None
                prompt_locked_door = None
                if map_level == 1:
                    for m in medkits_for_current_map:
                        if m.used:
                            continue
                        d = math.sqrt((player.rect.centerx - m.rect.centerx)**2 + (player.rect.centery - m.rect.centery)**2)
                        if d < 100:
                            prompt_medkit = m
                            break
                if 2 <= map_level <= 9 and prompt_medkit is None:
                    for m in medkits_for_current_map:
                        if m.used:
                            continue
                        dx = player.rect.centerx - m.rect.centerx
                        dy = player.rect.centery - m.rect.centery
                        if dx*dx + dy*dy < 100*100:
                            prompt_medkit = m
                            break
                for ammo_box in ammo_boxes_for_current_map:
                    if ammo_box.used:
                        continue
                    dx = player.rect.centerx - ammo_box.rect.centerx
                    dy = player.rect.centery - ammo_box.rect.centery
                    if dx*dx + dy*dy < 100*100:
                        prompt_ammo_box = ammo_box
                        break
                for weapon_drop in weapon_drops_for_current_map:
                    if weapon_drop.used:
                        continue
                    dx = player.rect.centerx - weapon_drop.rect.centerx
                    dy = player.rect.centery - weapon_drop.rect.centery
                    if dx*dx + dy*dy < 100*100:
                        prompt_weapon_drop = weapon_drop
                        break
                prompt_container = None
                for c in containers_for_current_map:
                    if c.looted:
                        continue
                    dx = player.rect.centerx - c.rect.centerx
                    dy = player.rect.centery - c.rect.centery
                    if dx*dx + dy*dy < 100*100:
                        prompt_container = c
                        break
                if key_item_for_current_map and not key_item_for_current_map.collected:
                    dx = player.rect.centerx - key_item_for_current_map.rect.centerx
                    dy = player.rect.centery - key_item_for_current_map.rect.centery
                    if dx * dx + dy * dy < 100 * 100:
                        prompt_key_item = key_item_for_current_map
                for safe in safes_for_current_map:
                    if safe.opened:
                        continue
                    dx = player.rect.centerx - safe.rect.centerx
                    dy = player.rect.centery - safe.rect.centery
                    if dx * dx + dy * dy < 100 * 100:
                        prompt_safe = safe
                        break
                for lock in locked_doors_for_current_map:
                    if lock.is_open:
                        continue
                    dx = player.rect.centerx - lock.rect.centerx
                    dy = player.rect.centery - lock.rect.centery
                    if dx * dx + dy * dy < 100 * 100:
                        prompt_locked_door = lock
                        break

                # 敌人子弹与玩家碰撞检测
                for bullet in enemy_bullets[:]:
                    if player.rect.colliderect(bullet.rect):
                        # 翻滚时无敌，子弹穿过玩家
                        if dodge_rolling and dodge_roll_invincible:
                            continue
                        enemy_bullets.remove(bullet)
                        damage = bullet.damage  # 使用子弹的伤害值（高级敌人20，普通敌人10）
                        if player.armor >= damage:
                            player.armor -= damage
                        else:
                            remaining_damage = damage - player.armor
                            player.armor = 0
                            player.health -= remaining_damage
                        player.last_damage_time = pygame.time.get_ticks()
                        player.last_armor_damage_time = pygame.time.get_ticks() # 更新上次护甲受伤害时间
                        player.health = max(0, player.health) # 确保生命值不低于0
                        # 受伤屏幕震动
                        trigger_screen_shake(4, 150)
                
                        break

                # ===== 视野盲区（Fog of War）=====
                fog_max_dist = int(math.sqrt(screen_width ** 2 + screen_height ** 2))
                vis_points = compute_visibility_polygon(
                    player.rect.centerx, player.rect.centery, obstacles,
                    max_dist=fog_max_dist, num_rays=360
                )
                screen_points = [(x - camera_x, y - camera_y) for x, y in vis_points]
                # 雾效：SRCALPHA + BLEND_RGBA_SUB，完全不透明遮挡
                fog = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                fog.fill((0, 0, 0, 255))  # 完全不透明黑雾
                if len(screen_points) >= 3:
                    hole = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                    hole.fill((0, 0, 0, 0))
                    pygame.draw.polygon(hole, (0, 0, 0, 255), screen_points)
                    fog.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
                screen.blit(fog, (0, 0))
                # 雾效之上只重绘墙壁和门（is_wall=True），家具（Furniture）被雾遮挡
                for obstacle in obstacles:
                    if getattr(obstacle, 'is_wall', False):
                        obstacle.draw(screen, camera_x, camera_y)
                for door in doors:
                    door.draw(screen, camera_x, camera_y)

                # 雾效之上重绘体力条，避免被遮住
                stamina_bar_width = 200
                stamina_bar_height = 20
                stamina_bar_x = screen_width - stamina_bar_width - 10
                stamina_bar_y = 10
                pygame.draw.rect(screen, (50, 50, 50), (stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height), 2)
                current_stamina_width = (player.stamina / player.max_stamina) * stamina_bar_width
                pygame.draw.rect(screen, (255, 255, 255), (stamina_bar_x, stamina_bar_y, current_stamina_width, stamina_bar_height))

                # 绘制当前枪械和子弹数量
                bullet_font = get_chinese_font(24)
                weapon_text = bullet_font.render(f"枪械: {player.current_weapon.name}", True, (255, 255, 0))  # 黄色显示枪械名称
                screen.blit(weapon_text, (10, 10)) # 左上角显示
                
                ammo_total_text = "∞" if infinite_ammo else str(player.total_ammo)
                bullet_text = bullet_font.render(f"弹药: {player.current_bullets}/{ammo_total_text}", True, (255, 255, 255))
                screen.blit(bullet_text, (10, 40)) # 在枪械名称下方显示
                
                # 绘制当前地图信息
                map_font = get_chinese_font(24)
                map_text = map_font.render(f"地图: {map_level}/{max_map_level}", True, (255, 255, 255))
                screen.blit(map_text, (10, 70)) # 在弹药下方显示
                # 金币与手雷（技能商城用）
                coin_grenade = map_font.render("金币: %d  手雷: %d  [B]商城" % (player.coins, player.grenades), True, (255, 215, 0))
                screen.blit(coin_grenade, (10, 100))
                
                # 击杀数显示
                kill_text = map_font.render(f"击杀: {kill_count}", True, (255, 80, 80))
                screen.blit(kill_text, (10, 130))
                
                # 翻滚冷却指示
                dodge_cd_remaining = max(0, dodge_roll_cooldown - (current_time - last_dodge_roll_time))
                if dodge_cd_remaining > 0:
                    dodge_text = map_font.render(f"[Q]翻滚 {dodge_cd_remaining/1000:.1f}s", True, (150, 150, 150))
                else:
                    dodge_text = map_font.render("[Q]翻滚 就绪", True, (100, 255, 100))
                screen.blit(dodge_text, (10, 160))
                key_text = map_font.render(f"钥匙: {'已获得' if player_has_key else '未获得'}", True, (255, 230, 120))
                screen.blit(key_text, (10, 190))
                
                # === 连杀提示（屏幕中央大字） ===
                if streak_message and current_time - streak_message_time < 2000:
                    streak_progress = (current_time - streak_message_time) / 2000.0
                    streak_font_size = 48 if kill_streak < 5 else 60
                    streak_font = get_chinese_font(streak_font_size)
                    # 文字缩放动画
                    if streak_progress < 0.1:
                        scale_factor = streak_progress / 0.1
                    elif streak_progress > 0.8:
                        scale_factor = 1.0 - (streak_progress - 0.8) / 0.2
                    else:
                        scale_factor = 1.0
                    streak_surface = streak_font.render(streak_message, True, streak_message_color)
                    if scale_factor < 1.0:
                        new_w = max(1, int(streak_surface.get_width() * scale_factor))
                        new_h = max(1, int(streak_surface.get_height() * scale_factor))
                        streak_surface = pygame.transform.scale(streak_surface, (new_w, new_h))
                    streak_rect = streak_surface.get_rect(center=(screen_width // 2, screen_height // 3))
                    # 绘制文字阴影
                    shadow = streak_font.render(streak_message, True, (0, 0, 0))
                    if scale_factor < 1.0:
                        shadow = pygame.transform.scale(shadow, (new_w, new_h))
                    shadow_rect = shadow.get_rect(center=(screen_width // 2 + 2, screen_height // 3 + 2))
                    screen.blit(shadow, shadow_rect)
                    screen.blit(streak_surface, streak_rect)
                
                # === 伤害飘字绘制 ===
                dmg_font = get_chinese_font(20)
                for dn in damage_numbers:
                    dn.draw(screen, camera_x, camera_y, dmg_font)
                
                # === 翻滚时玩家闪烁效果 ===
                if dodge_rolling:
                    roll_elapsed = current_time - dodge_roll_start
                    if int(roll_elapsed / 50) % 2 == 0:
                        # 在玩家位置画白色半透明圈表示翻滚
                        roll_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                        pygame.draw.circle(roll_surface, (255, 255, 255, 80), (30, 30), 30)
                        px = player.rect.centerx - camera_x - 30
                        py = player.rect.centery - camera_y - 30
                        screen.blit(roll_surface, (px, py))
                
                # 绘制武器图标（只显示携带的武器）
                # 武器颜色定义
                weapon_colors = {
                    "手枪": (180, 180, 180),    # 银灰色
                    "步枪": (100, 150, 100),    # 军绿色
                    "冲锋枪": (80, 80, 80),     # 深灰色
                    "狙击枪": (139, 90, 43),    # 棕色
                    "rpg": (200, 50, 50),       # 红色
                }
                icon_size = 50
                icon_spacing = 10
                icon_start_x = 10
                icon_start_y = 100
                
                for i, weapon_name in enumerate(player.carried_weapons[:2]):  # 只显示前两个武器
                    icon_x = icon_start_x + i * (icon_size + icon_spacing)
                    icon_y = icon_start_y
                    
                    # 获取武器颜色
                    weapon_color = weapon_colors.get(weapon_name, (150, 150, 150))
                    
                    # 如果是当前武器，绘制高亮边框
                    if weapon_name == player.current_weapon.name:
                        # 绘制金色高亮边框
                        pygame.draw.rect(screen, (255, 215, 0), (icon_x - 3, icon_y - 3, icon_size + 6, icon_size + 6), 3)
                    
                    # 绘制武器图标背景
                    pygame.draw.rect(screen, (40, 40, 40), (icon_x, icon_y, icon_size, icon_size))
                    
                    # 根据武器类型绘制不同形状的图标
                    if weapon_name == "手枪":
                        # 绘制手枪形状（小矩形+握把）
                        pygame.draw.rect(screen, weapon_color, (icon_x + 10, icon_y + 15, 30, 12))
                        pygame.draw.rect(screen, weapon_color, (icon_x + 15, icon_y + 25, 10, 15))
                    elif weapon_name == "步枪":
                        # 绘制步枪形状（长矩形+枪托）
                        pygame.draw.rect(screen, weapon_color, (icon_x + 5, icon_y + 18, 40, 10))
                        pygame.draw.rect(screen, weapon_color, (icon_x + 35, icon_y + 22, 10, 15))
                        pygame.draw.rect(screen, weapon_color, (icon_x + 5, icon_y + 15, 8, 5))  # 瞄准镜
                    elif weapon_name == "冲锋枪":
                        # 绘制冲锋枪形状（中等长度+弹匣）
                        pygame.draw.rect(screen, weapon_color, (icon_x + 8, icon_y + 18, 34, 10))
                        pygame.draw.rect(screen, weapon_color, (icon_x + 18, icon_y + 28, 8, 12))  # 弹匣
                        pygame.draw.rect(screen, weapon_color, (icon_x + 32, icon_y + 22, 8, 12))  # 握把
                    elif weapon_name == "狙击枪":
                        # 绘制狙击枪形状（长枪身+大瞄准镜）
                        pygame.draw.rect(screen, weapon_color, (icon_x + 3, icon_y + 20, 44, 8))
                        pygame.draw.rect(screen, weapon_color, (icon_x + 38, icon_y + 23, 8, 15))  # 枪托
                        pygame.draw.ellipse(screen, (100, 100, 200), (icon_x + 8, icon_y + 12, 12, 12))  # 瞄准镜
                    elif weapon_name == "rpg":
                        # 绘制RPG形状（粗管+火箭弹头）
                        pygame.draw.rect(screen, weapon_color, (icon_x + 8, icon_y + 18, 30, 14))
                        pygame.draw.polygon(screen, (255, 100, 50), [
                            (icon_x + 38, icon_y + 25),
                            (icon_x + 48, icon_y + 18),
                            (icon_x + 48, icon_y + 32)
                        ])  # 火箭弹头
                        pygame.draw.rect(screen, (100, 100, 100), (icon_x + 15, icon_y + 32, 10, 8))  # 握把
                    
                    # 绘制快捷键数字
                    key_font = get_chinese_font(14)
                    key_text = key_font.render(str(i + 1), True, (255, 255, 255))
                    screen.blit(key_text, (icon_x + 3, icon_y + 3))
                
                # 绘制任务系统
                if current_task == "kill_enemy_above":
                    # 如果任务目标敌人不存在或已死亡，重新查找
                    if task_target_enemy is None or task_target_enemy not in enemies:
                        task_target_enemy = None
                        player_y = player.rect.centery
                        min_distance = float('inf')
                        for enemy in enemies:
                            if enemy.rect.centery < player_y:  # 敌人在玩家上方
                                dx = enemy.rect.centerx - player.rect.centerx
                                dy = enemy.rect.centery - player.rect.centery
                                distance = math.sqrt(dx * dx + dy * dy)
                                if distance < min_distance:
                                    min_distance = distance
                                    task_target_enemy = enemy
                    
                    # 显示任务UI
                    task_font = get_chinese_font(24)
                    if task_completed:
                        # 任务完成提示（显示3秒）
                        if current_time - task_completed_time < 3000:
                            task_text = task_font.render("任务完成：已击杀上方敌人！", True, (0, 255, 0))
                            task_bg = pygame.Surface((task_text.get_width() + 20, task_text.get_height() + 10))
                            task_bg.set_alpha(200)
                            task_bg.fill((0, 0, 0))
                            screen.blit(task_bg, (screen_width // 2 - task_text.get_width() // 2 - 10, 80))
                            screen.blit(task_text, (screen_width // 2 - task_text.get_width() // 2, 85))
                    else:
                        # 显示当前任务
                        if task_target_enemy:
                            task_text = task_font.render("任务：击杀上方的敌人", True, (255, 255, 0))
                            task_bg = pygame.Surface((task_text.get_width() + 20, task_text.get_height() + 10))
                            task_bg.set_alpha(200)
                            task_bg.fill((0, 0, 0))
                            screen.blit(task_bg, (10, 80))
                            screen.blit(task_text, (20, 85))
                        else:
                            task_text = task_font.render("任务：未找到上方敌人", True, (255, 200, 0))
                            task_bg = pygame.Surface((task_text.get_width() + 20, task_text.get_height() + 10))
                            task_bg.set_alpha(200)
                            task_bg.fill((0, 0, 0))
                            screen.blit(task_bg, (10, 80))
                            screen.blit(task_text, (20, 85))

                # 绘制生命值条
                health_bar_width = 200
                health_bar_height = 20
                health_bar_x = screen_width - health_bar_width - 10
                health_bar_y = stamina_bar_y + stamina_bar_height + 10 # 放在体力条下方
                pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2) # 边框
                current_health_width = (player.health / player.max_health) * health_bar_width
                pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, current_health_width, health_bar_height)) # 红色生命值

                # 绘制护甲条
                armor_bar_width = 200
                armor_bar_height = 20
                armor_bar_x = screen_width - armor_bar_width - 10
                armor_bar_y = health_bar_y + health_bar_height + 10 # 护甲条在生命值条下方
                pygame.draw.rect(screen, (50, 50, 50), (armor_bar_x, armor_bar_y, armor_bar_width, armor_bar_height), 2) # 边框
                current_armor_width = (player.armor / player.max_armor) * armor_bar_width
                pygame.draw.rect(screen, (0, 0, 255), (armor_bar_x, armor_bar_y, current_armor_width, armor_bar_height)) # 蓝色护甲值
                
                # 所有提示画在物品上方，雾效之后绘制，确保不被遮挡
                def draw_hint_above(screen, world_x, world_y, text, color=(255, 255, 255), camera_x=0, camera_y=0, offset_y=-35):
                    sx = world_x - camera_x
                    sy = world_y - camera_y + offset_y
                    font = get_chinese_font(12)
                    surf = font.render(text, True, color)
                    rect = surf.get_rect(center=(sx, sy))
                    bg = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
                    bg.fill((0, 0, 0, 180))
                    screen.blit(bg, (rect.x - 10, rect.y - 5))
                    screen.blit(surf, rect)

                if doors:
                    player_cx = player.rect.centerx
                    player_cy = player.rect.centery
                    # 所有楼层：站在电梯上显示提示
                    near_elevator = False
                    if current_stage == 1 and 1 <= map_level <= 8 and player.rect.colliderect(elevator_rect):
                        near_elevator = True
                        draw_hint_above(screen, elevator_rect.centerx, elevator_rect.centery,
                                        "按 E 选择楼层", (200, 220, 255), camera_x, camera_y, -45)
                    if not near_elevator:
                        nearest_door = None
                        nearest_dist = float('inf')
                        for door in doors:
                            door_cx = door.rect.centerx
                            door_cy = door.rect.centery
                            dist = ((player_cx - door_cx) ** 2 + (player_cy - door_cy) ** 2) ** 0.5
                            if dist < 100 and dist < nearest_dist:
                                nearest_dist = dist
                                nearest_door = door
                        if nearest_door:
                            hint_text = "[E] 关门" if nearest_door.is_open else "[E] 开门"
                            draw_hint_above(screen, nearest_door.rect.centerx, nearest_door.rect.centery,
                                            hint_text, (255, 255, 100), camera_x, camera_y, -35)
                if prompt_container:
                    draw_hint_above(screen, prompt_container.rect.centerx, prompt_container.rect.centery,
                                    "按 E 拾取 (3秒)", (200, 255, 150), camera_x, camera_y, -40)
                if prompt_key_item:
                    draw_hint_above(screen, prompt_key_item.rect.centerx, prompt_key_item.rect.top,
                                    "按 E 拾取钥匙", (255, 230, 120), camera_x, camera_y, -30)
                if prompt_safe:
                    safe_hint = "按 E 打开保险箱" if player_has_key else "需要钥匙才能开保险箱"
                    draw_hint_above(screen, prompt_safe.rect.centerx, prompt_safe.rect.top,
                                    safe_hint, (170, 230, 230), camera_x, camera_y, -30)
                if prompt_locked_door:
                    lock_hint = "按 E 开启门锁" if player_has_key else "门锁需要钥匙"
                    draw_hint_above(screen, prompt_locked_door.rect.centerx, prompt_locked_door.rect.top,
                                    lock_hint, (255, 215, 120), camera_x, camera_y, -30)
                if prompt_medkit:
                    draw_hint_above(screen, prompt_medkit.rect.centerx, prompt_medkit.rect.top,
                                    "按 E 键使用医疗包", (255, 255, 255), camera_x, camera_y, -30)
                if prompt_ammo_box:
                    draw_hint_above(screen, prompt_ammo_box.rect.centerx, prompt_ammo_box.rect.top,
                                    "按 E 键拾取弹药箱 (+30)", (255, 255, 255), camera_x, camera_y, -30)
                if prompt_weapon_drop:
                    name = prompt_weapon_drop.weapon_name
                    if name in player.carried_weapons:
                        draw_hint_above(screen, prompt_weapon_drop.rect.centerx, prompt_weapon_drop.rect.top,
                                        f"按 E 键拾取{name} (已携带)", (200, 200, 200), camera_x, camera_y, -30)
                    else:
                        draw_hint_above(screen, prompt_weapon_drop.rect.centerx, prompt_weapon_drop.rect.top,
                                        f"按 E 键拾取{name}", (255, 255, 0), camera_x, camera_y, -30)

                # 绘制教程提示（仅关卡1）
                if current_stage == 1 and tutorial_step > 0 and tutorial_step < 8:
                    tutorial_font = get_chinese_font(30)
                    tutorial_hint_font = get_chinese_font(24)
                    
                    # 根据当前教程步骤显示提示
                    tutorial_messages = {
                        1: ("新手教程：移动", "使用 W/A/S/D 键移动角色", (100, 200, 255)),
                        2: ("新手教程：冲刺", "按住空格键进行冲刺（消耗体力）", (100, 200, 255)),
                        3: ("新手教程：射击", "按住鼠标左键进行射击", (100, 200, 255)),
                        4: ("新手教程：开镜", "按住鼠标右键进行开镜瞄准", (100, 200, 255)),
                        5: ("新手教程：换弹", "按 R 键进行换弹", (100, 200, 255)),
                        6: ("新手教程：地图", "按 TAB 键打开地图查看位置", (100, 200, 255)),
                        7: ("新手教程：医疗包", "靠近医疗包后按 E 键使用", (100, 200, 255))
                    }
                    
                    # 如果是教程步骤6，显示地图颜色说明
                    if tutorial_step == 6:
                        # 增大背景框以容纳更多文字
                        tutorial_bg = pygame.Surface((screen_width - 40, 160))
                        tutorial_bg.set_alpha(220)
                        tutorial_bg.fill((20, 20, 30))
                        screen.blit(tutorial_bg, (20, screen_height - 180))
                        
                        # 绘制标题
                        title_text = tutorial_font.render("新手教程：地图", True, (100, 200, 255))
                        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height - 150))
                        screen.blit(title_text, title_rect)
                        
                        # 绘制操作提示
                        if not is_map_open and not radar_on:
                            hint_text = tutorial_hint_font.render("按 TAB 键打开地图查看位置", True, (255, 255, 255))
                            hint_rect = hint_text.get_rect(center=(screen_width // 2, screen_height - 120))
                            screen.blit(hint_text, hint_rect)
                        else:
                            close_hint = tutorial_hint_font.render("按 TAB 键关闭地图继续", True, (255, 200, 100))
                            close_rect = close_hint.get_rect(center=(screen_width // 2, screen_height - 120))
                            screen.blit(close_hint, close_rect)
                        
                        # 绘制颜色说明（分行显示）
                        color_hint1 = tutorial_hint_font.render("绿色=玩家  红色=敌人", True, (255, 255, 255))
                        color_hint2 = tutorial_hint_font.render("灰色=障碍物  蓝色=医疗包", True, (255, 255, 255))
                        hint_rect1 = color_hint1.get_rect(center=(screen_width // 2, screen_height - 90))
                        hint_rect2 = color_hint2.get_rect(center=(screen_width // 2, screen_height - 60))
                        screen.blit(color_hint1, hint_rect1)
                        screen.blit(color_hint2, hint_rect2)
                    elif tutorial_step in tutorial_messages:
                        title, hint, color = tutorial_messages[tutorial_step]
                        
                        # 创建半透明背景
                        tutorial_bg = pygame.Surface((screen_width - 40, 100))
                        tutorial_bg.set_alpha(200)
                        tutorial_bg.fill((20, 20, 30))
                        
                        # 绘制背景
                        screen.blit(tutorial_bg, (20, screen_height - 120))
                        
                        # 绘制标题
                        title_text = tutorial_font.render(title, True, color)
                        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height - 90))
                        screen.blit(title_text, title_rect)
                        
                        # 绘制提示
                        hint_text = tutorial_hint_font.render(hint, True, (255, 255, 255))
                        hint_rect = hint_text.get_rect(center=(screen_width // 2, screen_height - 55))
                        screen.blit(hint_text, hint_rect)
                
                # 绘制伤害边框效果（受到伤害后0.5秒内显示半透明黑色边框）
                damage_duration = 500  # 0.5秒
                if current_time - player.last_damage_time < damage_duration:
                    border_thickness = 20  # 边框厚度
                    # 创建半透明黑色表面用于边框
                    border_surface = pygame.Surface((screen_width, border_thickness))
                    border_surface.set_alpha(180)  # 半透明
                    border_surface.fill((0, 0, 0))  # 黑色
                    
                    # 绘制上边框
                    screen.blit(border_surface, (0, 0))
                    # 绘制下边框
                    screen.blit(border_surface, (0, screen_height - border_thickness))
                    
                    # 绘制左右边框
                    border_surface_vertical = pygame.Surface((border_thickness, screen_height))
                    border_surface_vertical.set_alpha(180)
                    border_surface_vertical.fill((0, 0, 0))
                    # 左边框
                    screen.blit(border_surface_vertical, (0, 0))
                    # 右边框
                    screen.blit(border_surface_vertical, (screen_width - border_thickness, 0))
                
                # 绘制准星（仅在游戏模式且未打开地图/雷达时显示）
                if not is_map_open and not radar_on:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # 如果正在换弹，显示旋转的加载箭头
                    if player.reloading:
                        # 计算旋转角度（基于换弹进度，顺时针旋转）
                        reload_progress = (current_time - player.reload_start_time) / player.reload_duration
                        rotation_angle = reload_progress * 360  # 0-360度
                        
                        # 箭头大小
                        arrow_radius = 25  # 箭头距离中心的距离
                        arrow_size = 8  # 箭头大小
                        
                        # 绘制4个箭头，围绕中心旋转（类似加载图标）
                        arrow_color = (255, 255, 255)  # 白色箭头
                        num_arrows = 4  # 箭头数量
                        
                        for i in range(num_arrows):
                            # 每个箭头之间的角度间隔
                            base_angle = (360 / num_arrows) * i
                            # 加上旋转角度（顺时针，所以是负的）
                            angle = math.radians(base_angle - rotation_angle)
                            
                            # 计算箭头位置
                            arrow_x = mouse_x + arrow_radius * math.cos(angle)
                            arrow_y = mouse_y + arrow_radius * math.sin(angle)
                            
                            # 绘制箭头（三角形）
                            arrow_points = []
                            # 箭头指向中心
                            center_angle = angle + math.pi  # 指向中心的方向
                            
                            # 箭头的三个点
                            # 箭头尖端（指向中心）
                            tip_x = arrow_x + arrow_size * math.cos(center_angle)
                            tip_y = arrow_y + arrow_size * math.sin(center_angle)
                            
                            # 箭头左侧点
                            left_angle = center_angle + math.pi * 0.7
                            left_x = arrow_x + arrow_size * 0.5 * math.cos(left_angle)
                            left_y = arrow_y + arrow_size * 0.5 * math.sin(left_angle)
                            
                            # 箭头右侧点
                            right_angle = center_angle - math.pi * 0.7
                            right_x = arrow_x + arrow_size * 0.5 * math.cos(right_angle)
                            right_y = arrow_y + arrow_size * 0.5 * math.sin(right_angle)
                            
                            arrow_points = [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
                            pygame.draw.polygon(screen, arrow_color, arrow_points)
                        
                        # 可选：绘制中心小圆点
                        pygame.draw.circle(screen, arrow_color, (int(mouse_x), int(mouse_y)), 3)
                    else:
                        # 正常情况显示准心
                        if crosshair_image:
                            ch_rect = crosshair_image.get_rect(center=(mouse_x, mouse_y))
                            screen.blit(crosshair_image, ch_rect)
                        else:
                            # 备用：绘制默认十字准星
                            crosshair_size = 20
                            crosshair_thickness = 2
                            crosshair_color = (255, 255, 255)
                            pygame.draw.line(screen, crosshair_color, 
                                           (mouse_x - crosshair_size, mouse_y), 
                                           (mouse_x + crosshair_size, mouse_y), 
                                           crosshair_thickness)
                            pygame.draw.line(screen, crosshair_color, 
                                           (mouse_x, mouse_y - crosshair_size), 
                                           (mouse_x, mouse_y + crosshair_size), 
                                           crosshair_thickness)
                            pygame.draw.circle(screen, crosshair_color, (mouse_x, mouse_y), 2)
                # 电梯动画：除玩家和电梯外全屏黑色，只露出电梯与玩家
                if elevator_animating:
                    screen_copy = screen.copy()
                    screen.fill((0, 0, 0))
                    elevator_screen_rect = pygame.Rect(elevator_rect.x - camera_x, elevator_rect.y - camera_y, elevator_rect.width, elevator_rect.height)
                    player_screen_rect = pygame.Rect(player.rect.x - camera_x, player.rect.y - camera_y, player.rect.width, player.rect.height)
                    screen.blit(screen_copy, elevator_screen_rect, elevator_screen_rect)
                    screen.blit(screen_copy, player_screen_rect, player_screen_rect)
                    # 显示目标楼层提示
                    elev_anim_font = get_chinese_font(28)
                    target_name = FLOOR_NAMES.get(elevator_target_map, f"{elevator_target_map}F")
                    elev_anim_text = elev_anim_font.render(f"前往 {target_name} ...", True, (200, 220, 255))
                    screen.blit(elev_anim_text, elev_anim_text.get_rect(center=(screen_width // 2, screen_height - 60)))

                # 电梯楼层选择UI
                if elevator_ui_open and not elevator_animating:
                    # 半透明遮罩
                    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 140))
                    screen.blit(overlay, (0, 0))
                    # 面板
                    panel_w, panel_h = 280, 420
                    panel_x = (screen_width - panel_w) // 2
                    panel_y = (screen_height - panel_h) // 2
                    pygame.draw.rect(screen, (40, 45, 55), (panel_x, panel_y, panel_w, panel_h))
                    pygame.draw.rect(screen, (0, 200, 220), (panel_x, panel_y, panel_w, panel_h), 2)
                    # 标题
                    ui_title_font = get_chinese_font(24)
                    ui_title = ui_title_font.render("选择楼层", True, (0, 220, 240))
                    screen.blit(ui_title, ui_title.get_rect(centerx=screen_width // 2, top=panel_y + 14))
                    # 楼层按钮
                    btn_w, btn_h = 240, 38
                    btn_x = panel_x + (panel_w - btn_w) // 2
                    btn_start_y = panel_y + 50
                    mouse_pos = pygame.mouse.get_pos()
                    ui_btn_font = get_chinese_font(20)
                    for fl in range(1, 9):
                        by = btn_start_y + (fl - 1) * (btn_h + 6)
                        btn_rect = pygame.Rect(btn_x, by, btn_w, btn_h)
                        is_current = (fl == map_level)
                        is_hover = btn_rect.collidepoint(mouse_pos) and not is_current
                        if is_current:
                            bg_color = (80, 80, 40)
                            border_color = (220, 200, 60)
                            text_color = (220, 200, 60)
                        elif is_hover:
                            bg_color = (60, 80, 100)
                            border_color = (0, 200, 220)
                            text_color = (255, 255, 255)
                        else:
                            bg_color = (50, 55, 65)
                            border_color = (100, 110, 130)
                            text_color = (180, 190, 200)
                        pygame.draw.rect(screen, bg_color, btn_rect)
                        pygame.draw.rect(screen, border_color, btn_rect, 1)
                        floor_name = FLOOR_NAMES.get(fl, f"{fl}F")
                        label = f"{floor_name}{'  (当前)' if is_current else ''}"
                        txt_surf = ui_btn_font.render(label, True, text_color)
                        screen.blit(txt_surf, txt_surf.get_rect(center=btn_rect.center))
                    # 底部提示
                    ui_hint_font = get_chinese_font(16)
                    ui_hint = ui_hint_font.render("点击选择楼层 / ESC 取消", True, (120, 130, 150))
                    screen.blit(ui_hint, ui_hint.get_rect(centerx=screen_width // 2, bottom=panel_y + panel_h - 8))

                # HUD：当前楼层显示（左上角）
                if current_stage == 1 and 1 <= map_level <= 8 and not elevator_ui_open:
                    floor_hud_font = get_chinese_font(18)
                    floor_hud_text = floor_hud_font.render(FLOOR_NAMES.get(map_level, ""), True, (200, 220, 255))
                    screen.blit(floor_hud_text, (10, 10))
        else:
            # 非游戏模式时显示鼠标光标
            pygame.mouse.set_visible(True)
        
        pygame.display.flip()
        clock.tick(60)
    
    # 退出 pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
