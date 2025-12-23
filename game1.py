import pygame
import sys
import random
import math

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("减速带弹射器")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # 游戏状态
        self.state = "ACCELERATING"  # ACCELERATING, COLLISION, RESULT, UPGRADE
        self.score = 0
        self.high_score = 0
        self.money = 0
        
        # 车辆属性
        self.car_x = 100
        self.car_y = SCREEN_HEIGHT - 200
        self.car_width = 80
        self.car_height = 40
        self.wheel_radius = 15
        self.speed = 0
        self.max_speed = 300  # 基础最大速度
        self.acceleration = 5  # 基础加速度
        self.durability = 100  # 当前耐久度
        self.max_durability = 100  # 最大耐久度
        
        # 升级系统
        self.upgrades = {
            "engine": {"level": 1, "cost": 100, "effect": 2},  # 每级增加加速度
            "chassis": {"level": 1, "cost": 150, "effect": 20},  # 每级增加最大耐久
            "suspension": {"level": 1, "cost": 200, "effect": 0.1}  # 每级减少耐久损耗
        }
        
        # 减速带
        self.bump_x = SCREEN_WIDTH - 200
        self.bump_width = 60
        self.bump_height = 30
        
        # 物理参数
        self.gravity = 0.5
        self.car_velocity_y = 0
        self.car_jumping = False
        self.car_jump_height = 0
        self.car_angle = 0
        
        # 零件飞散效果
        self.particles = []
        self.slow_motion = False
        self.slow_motion_timer = 0
        
        # 游戏计时
        self.game_timer = 0
        self.max_game_time = 60 * 1000  # 60秒（以毫秒计）
        
        # 音效占位符（实际游戏中需要加载音效文件）
        self.sounds = {}
        
    def reset_car(self):
        """重置车辆位置和状态"""
        self.car_x = 100
        self.car_y = SCREEN_HEIGHT - 200
        self.speed = 0
        self.durability = self.max_durability
        self.car_jumping = False
        self.car_jump_height = 0
        self.car_angle = 0
        self.car_velocity_y = 0
        self.particles = []
        self.slow_motion = False
        self.slow_motion_timer = 0
        self.game_timer = 0
        
    def create_particles(self, x, y, count=5):
        """创建飞散零件粒子"""
        for _ in range(count):
            particle = {
                "x": x,
                "y": y,
                "vx": random.uniform(-5, 5),
                "vy": random.uniform(-10, -5),
                "size": random.randint(5, 15),
                "color": random.choice([RED, YELLOW, GRAY, BLACK]),
                "life": 60  # 粒子寿命（帧数）
            }
            self.particles.append(particle)
            
    def update_particles(self):
        """更新粒子效果"""
        for particle in self.particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += self.gravity
            particle["life"] -= 1
            
            if particle["life"] <= 0:
                self.particles.remove(particle)
                
    def draw_particles(self):
        """绘制粒子效果"""
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle["color"], 
                              (int(particle["x"]), int(particle["y"])), 
                              particle["size"])
    
    def calculate_damage(self, speed):
        """根据速度计算伤害"""
        # 基础伤害公式
        base_damage = speed * 0.5
        
        # 悬挂升级减少伤害
        suspension_factor = 1.0 - (self.upgrades["suspension"]["level"] - 1) * self.upgrades["suspension"]["effect"]
        
        damage = base_damage * suspension_factor
        
        # 添加随机因素
        damage *= random.uniform(0.9, 1.1)
        
        return damage
    
    def handle_collision(self):
        """处理碰撞逻辑"""
        if self.state == "ACCELERATING" and self.car_x + self.car_width >= self.bump_x:
            self.state = "COLLISION"
            self.slow_motion = True
            self.slow_motion_timer = 30  # 慢动作持续时间（帧数）
            
            # 计算伤害
            damage = self.calculate_damage(self.speed)
            self.durability -= damage
            
            # 创建飞散零件
            self.create_particles(self.car_x + self.car_width, self.car_y, int(self.speed / 30))
            
            # 车辆弹起
            self.car_jumping = True
            self.car_velocity_y = -self.speed * 0.1
            
            # 计算分数
            self.score = int(self.speed)
            if self.durability > 0:
                # 幸存
                self.money += self.score
                self.score = int(self.score * 1.0)  # 幸存系数1.0
            else:
                # 失败
                self.money += int(self.score * 0.5)  # 安慰分系数0.5
            
            # 更新最高分
            if self.score > self.high_score:
                self.high_score = self.score
    
    def buy_upgrade(self, upgrade_type):
        """购买升级"""
        upgrade = self.upgrades[upgrade_type]
        
        if self.money >= upgrade["cost"]:
            self.money -= upgrade["cost"]
            upgrade["level"] += 1
            upgrade["cost"] = int(upgrade["cost"] * 1.5)  # 每次升级后价格增加
            
            # 应用升级效果
            if upgrade_type == "engine":
                self.acceleration += upgrade["effect"]
            elif upgrade_type == "chassis":
                self.max_durability += upgrade["effect"]
                self.durability = self.max_durability
            elif upgrade_type == "suspension":
                pass  # 效果在calculate_damage中应用
    
    def draw_car(self):
        """绘制车辆"""
        # 计算车辆旋转（跳跃时）
        if self.car_jumping:
            self.car_angle = math.sin(pygame.time.get_ticks() * 0.01) * 30
            
        # 保存当前屏幕状态
        original_surface = pygame.Surface((self.car_width, self.car_height), pygame.SRCALPHA)
        
        # 绘制车身（在原始表面上）
        body_rect = pygame.Rect(0, 0, self.car_width, self.car_height)
        pygame.draw.rect(original_surface, RED, body_rect, border_radius=10)
        
        # 绘制车窗
        window_rect = pygame.Rect(10, 5, self.car_width - 20, self.car_height // 3)
        pygame.draw.rect(original_surface, BLUE, window_rect, border_radius=5)
        
        # 旋转表面
        rotated_surface = pygame.transform.rotate(original_surface, self.car_angle)
        rotated_rect = rotated_surface.get_rect(center=(self.car_x + self.car_width//2, 
                                                      self.car_y + self.car_height//2))
        
        # 绘制旋转后的车辆
        self.screen.blit(rotated_surface, rotated_rect)
        
        # 绘制车轮（不旋转）
        if not self.car_jumping:
            wheel_y = self.car_y + self.car_height - 5
            pygame.draw.circle(self.screen, BLACK, (self.car_x + 20, wheel_y), self.wheel_radius)
            pygame.draw.circle(self.screen, BLACK, (self.car_x + self.car_width - 20, wheel_y), self.wheel_radius)
    
    def draw_bump(self):
        """绘制减速带"""
        # 减速带底座
        bump_base = pygame.Rect(self.bump_x - self.bump_width//2, 
                               SCREEN_HEIGHT - 100 - self.bump_height//2,
                               self.bump_width, self.bump_height)
        pygame.draw.rect(self.screen, YELLOW, bump_base, border_radius=5)
        
        # 减速带顶部（三角形部分）
        points = [
            (self.bump_x - self.bump_width//2, SCREEN_HEIGHT - 100 - self.bump_height//2),
            (self.bump_x + self.bump_width//2, SCREEN_HEIGHT - 100 - self.bump_height//2),
            (self.bump_x, SCREEN_HEIGHT - 100 - self.bump_height)
        ]
        pygame.draw.polygon(self.screen, YELLOW, points)
        
        # 减速带纹理
        for i in range(3):
            line_x = self.bump_x - self.bump_width//4 + i * self.bump_width//4
            pygame.draw.line(self.screen, BLACK, 
                            (line_x, SCREEN_HEIGHT - 100 - self.bump_height//2),
                            (line_x, SCREEN_HEIGHT - 100 - self.bump_height + 5),
                            3)
    
    def draw_hud(self):
        """绘制游戏界面信息"""
        # 速度表
        speed_text = self.font.render(f"速度: {int(self.speed)} km/h", True, WHITE)
        self.screen.blit(speed_text, (20, 20))
        
        # 耐久度条
        durability_text = self.small_font.render("耐久度", True, WHITE)
        self.screen.blit(durability_text, (20, 60))
        
        # 耐久度条背景
        durability_bg = pygame.Rect(20, 85, 200, 20)
        pygame.draw.rect(self.screen, GRAY, durability_bg)
        
        # 当前耐久度
        durability_width = max(0, (self.durability / self.max_durability) * 200)
        durability_fg = pygame.Rect(20, 85, durability_width, 20)
        durability_color = GREEN if self.durability > 50 else YELLOW if self.durability > 20 else RED
        pygame.draw.rect(self.screen, durability_color, durability_fg)
        
        # 耐久度数值
        durability_value = self.small_font.render(f"{int(self.durability)}/{self.max_durability}", True, WHITE)
        self.screen.blit(durability_value, (100, 85))
        
        # 分数
        score_text = self.font.render(f"本次得分: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        # 最高分
        high_score_text = self.font.render(f"最高分: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 200, 60))
        
        # 金钱
        money_text = self.font.render(f"金钱: {self.money}", True, GREEN)
        self.screen.blit(money_text, (SCREEN_WIDTH - 200, 100))
        
        # 游戏时间
        time_left = max(0, (self.max_game_time - self.game_timer) // 1000)
        time_text = self.font.render(f"时间: {time_left}秒", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        # 操作提示
        if self.state == "ACCELERATING":
            hint_text = self.small_font.render("按住SPACE加速，松开减速", True, WHITE)
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 30))
    
    def draw_upgrade_screen(self):
        """绘制升级界面"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # 标题
        title = self.font.render("升级你的车辆！", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # 当前金钱
        money_text = self.font.render(f"金钱: {self.money}", True, GREEN)
        self.screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 100))
        
        # 升级选项
        upgrade_y = 150
        upgrade_types = ["engine", "chassis", "suspension"]
        upgrade_names = ["引擎升级", "底盘加固", "悬挂升级"]
        upgrade_descriptions = [
            f"增加加速度 (当前等级: {self.upgrades['engine']['level']})",
            f"增加最大耐久度 (当前等级: {self.upgrades['chassis']['level']})",
            f"减少撞击伤害 (当前等级: {self.upgrades['suspension']['level']})"
        ]
        
        for i, (upgrade_type, name, desc) in enumerate(zip(upgrade_types, upgrade_names, upgrade_descriptions)):
            y_pos = upgrade_y + i * 100
            
            # 升级框
            upgrade_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, y_pos, 400, 80)
            pygame.draw.rect(self.screen, BLUE, upgrade_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, upgrade_rect, 2, border_radius=10)
            
            # 升级名称
            name_text = self.font.render(name, True, WHITE)
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, y_pos + 10))
            
            # 升级描述
            desc_text = self.small_font.render(desc, True, YELLOW)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, y_pos + 40))
            
            # 升级价格
            cost = self.upgrades[upgrade_type]["cost"]
            cost_text = self.font.render(f"价格: {cost}", True, GREEN if self.money >= cost else RED)
            self.screen.blit(cost_text, (SCREEN_WIDTH // 2 - cost_text.get_width() // 2, y_pos + 60))
            
            # 升级按钮区域（存储在升级信息中便于点击检测）
            self.upgrades[upgrade_type]["button_rect"] = upgrade_rect
        
        # 继续游戏按钮
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, upgrade_y + 350, 200, 60)
        pygame.draw.rect(self.screen, GREEN, continue_rect, border_radius=10)
        continue_text = self.font.render("继续游戏", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, upgrade_y + 365))
        self.continue_button_rect = continue_rect
        
        # 提示
        hint_text = self.small_font.render("点击升级购买，点击继续开始下一轮", True, WHITE)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def draw_result_screen(self):
        """绘制结果界面"""
        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # 结果标题
        if self.durability > 0:
            title = self.font.render("幸存！", True, GREEN)
        else:
            title = self.font.render("车辆报废！", True, RED)
        
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # 速度显示
        speed_text = self.font.render(f"时速: {int(self.speed)} 公里/小时！", True, YELLOW)
        self.screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, 150))
        
        # 得分
        if self.durability > 0:
            score_text = self.font.render(f"得分: {self.score} (系数: 1.0)", True, GREEN)
        else:
            score_text = self.font.render(f"得分: {int(self.score * 0.5)} (系数: 0.5)", True, RED)
        
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))
        
        # 耐久度状态
        if self.durability > 0:
            durability_text = self.font.render(f"剩余耐久度: {int(self.durability)}/{self.max_durability}", True, YELLOW)
        else:
            durability_text = self.font.render("耐久度耗尽！", True, RED)
        
        self.screen.blit(durability_text, (SCREEN_WIDTH // 2 - durability_text.get_width() // 2, 250))
        
        # 获得金钱
        earned_money = self.score if self.durability > 0 else int(self.score * 0.5)
        money_text = self.font.render(f"获得金钱: {earned_money}", True, GREEN)
        self.screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 300))
        
        # 继续按钮
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 60)
        pygame.draw.rect(self.screen, GREEN, continue_rect, border_radius=10)
        continue_text = self.font.render("升级车辆", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 415))
        self.continue_button_rect = continue_rect
        
        # 提示
        hint_text = self.small_font.render("点击继续升级你的车辆", True, WHITE)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def run(self):
        """运行游戏主循环"""
        running = True
        accelerating = False
        
        while running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "ACCELERATING":
                        accelerating = True
                    elif event.key == pygame.K_r:  # 重置游戏
                        self.reset_car()
                        self.state = "ACCELERATING"
                    elif event.key == pygame.K_ESCAPE:  # 退出游戏
                        running = False
                
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and self.state == "ACCELERATING":
                        accelerating = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == "UPGRADE":
                        # 检查升级按钮
                        for upgrade_type in self.upgrades:
                            if "button_rect" in self.upgrades[upgrade_type]:
                                if self.upgrades[upgrade_type]["button_rect"].collidepoint(mouse_pos):
                                    self.buy_upgrade(upgrade_type)
                        
                        # 检查继续按钮
                        if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_pos):
                            self.reset_car()
                            self.state = "ACCELERATING"
                    
                    elif self.state == "RESULT":
                        # 检查继续按钮
                        if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_pos):
                            self.state = "UPGRADE"
            
            # 游戏逻辑更新
            if self.state == "ACCELERATING":
                # 更新游戏时间
                self.game_timer += self.clock.get_time()
                
                # 检查时间结束
                if self.game_timer >= self.max_game_time:
                    self.state = "RESULT"
                
                # 更新速度
                if accelerating:
                    self.speed = min(self.speed + self.acceleration, self.max_speed)
                else:
                    # 刹车减速
                    self.speed = max(0, self.speed - 10)
                
                # 更新车辆位置
                self.car_x += self.speed * 0.1
                
                # 检查碰撞
                self.handle_collision()
                
            elif self.state == "COLLISION":
                # 慢动作效果
                if self.slow_motion:
                    self.slow_motion_timer -= 1
                    if self.slow_motion_timer <= 0:
                        self.slow_motion = False
                        self.state = "RESULT"
                
                # 车辆跳跃物理
                if self.car_jumping:
                    self.car_velocity_y += self.gravity
                    self.car_y += self.car_velocity_y
                    
                    # 车辆落地检测
                    if self.car_y >= SCREEN_HEIGHT - 200:
                        self.car_y = SCREEN_HEIGHT - 200
                        self.car_jumping = False
                
                # 更新粒子效果
                self.update_particles()
            
            # 绘制背景
            self.screen.fill(BLACK)
            
            # 绘制赛道
            pygame.draw.rect(self.screen, GRAY, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # 绘制赛道标记
            for i in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.screen, WHITE, (i, SCREEN_HEIGHT - 60, 20, 5))
            
            # 绘制减速带
            self.draw_bump()
            
            # 绘制粒子效果
            self.draw_particles()
            
            # 绘制车辆
            self.draw_car()
            
            # 绘制游戏信息
            self.draw_hud()
            
            # 绘制结果界面
            if self.state == "RESULT":
                self.draw_result_screen()
            
            # 绘制升级界面
            elif self.state == "UPGRADE":
                self.draw_upgrade_screen()
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率（慢动作时降低帧率）
            if self.slow_motion:
                self.clock.tick(15)  # 慢动作帧率
            else:
                self.clock.tick(60)  # 正常帧率
        
        pygame.quit()
        sys.exit()

# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.run()