import pygame
from .map import Map
from .player import Player
from .pathfinding import AStar
from .ui import UI
from .package_manager import PackageManager

class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.game_state = "GAMEPLAY"  # 可选状态: PREVIEW, MENU, GAMEPLAY, PAUSE, GAMEOVER
        
        # 游戏组件
        self.map = Map()
        self.player = Player(self.map)
        self.pathfinder = AStar(self.map)
        self.ui = UI(screen)
        self.package_manager = PackageManager(self.map)
        
        # 设置Player的pathfinder引用
        self.player.set_pathfinder(self.pathfinder)
        
        # 连接UI按钮回调
        self.ui.set_callback("restart", self.start_game)
        
        # 游戏变量
        self.score = 0
        self.time = 480  # 以分钟为单位，8小时工作日
        self.weather = "SUNNY"  # 可选: SUNNY, RAINY, FOGGY
        
        # 定时器设置
        self.timer = pygame.time.get_ticks()
        
        # 预览模式设置
        self.preview_images = []
        self.current_preview = 0
        self.load_preview_images()
        
        # 开始游戏
        self.package_manager.generate_packages()
        
        # 记录游戏完成状态(用于显示不同的结束信息)
        self.game_completed = False
        self.time_bonus = 0
    
    def load_preview_images(self):
        """加载预览图像，实际开发中应替换为实际游戏截图"""
        # 创建模拟的预览图像
        preview1 = self.create_preview_image("校园地图与快递路线")
        preview2 = self.create_preview_image("角色与交互界面")
        preview3 = self.create_preview_image("寻路算法演示")
        
        self.preview_images = [preview1, preview2, preview3]
    
    def create_preview_image(self, title):
        """创建一个模拟的预览图像"""
        # 创建一个与屏幕大小相同的surface
        preview = pygame.Surface(self.screen.get_size())
        preview.fill((240, 240, 240))  # 浅灰背景
        
        # 绘制模拟的地图（绿色和灰色的网格）
        cell_size = 30
        cols = preview.get_width() // cell_size
        rows = preview.get_height() // cell_size - 2  # 留出空间给标题
        
        # 绘制网格
        for row in range(rows):
            for col in range(cols):
                color = (100, 200, 100) if (row + col) % 2 == 0 else (180, 220, 180)  # 交替的绿色
                
                # 绘制一些灰色"道路"
                if row == rows // 2 or col == cols // 2:
                    color = (180, 180, 180)
                
                rect = pygame.Rect(col * cell_size, row * cell_size + 60, cell_size, cell_size)
                pygame.draw.rect(preview, color, rect)
                pygame.draw.rect(preview, (220, 220, 220), rect, 1)
        
        # 如果是寻路演示，绘制路径
        if title == "寻路算法演示":
            # 模拟起点和终点
            start = (2, 3)
            end = (cols - 3, rows - 3)
            
            # 模拟路径
            path = [(2, 3), (3, 3), (4, 3), (5, 3), (6, 4), (7, 5), 
                   (8, 6), (9, 7), (10, 8), (11, 9), (12, 10), (cols-3, rows-3)]
            
            # 绘制路径
            for i in range(len(path) - 1):
                start_pos = (path[i][0] * cell_size + cell_size // 2, 
                            path[i][1] * cell_size + 60 + cell_size // 2)
                end_pos = (path[i+1][0] * cell_size + cell_size // 2, 
                          path[i+1][1] * cell_size + 60 + cell_size // 2)
                pygame.draw.line(preview, (255, 0, 0), start_pos, end_pos, 3)
            
            # 绘制起点和终点
            pygame.draw.circle(preview, (0, 0, 255), 
                              (start[0] * cell_size + cell_size // 2, 
                               start[1] * cell_size + 60 + cell_size // 2), 
                              10)
            pygame.draw.circle(preview, (255, 0, 0), 
                              (end[0] * cell_size + cell_size // 2, 
                               end[1] * cell_size + 60 + cell_size // 2), 
                              10)
        
        # 如果是角色界面，绘制角色和UI
        if title == "角色与交互界面":
            # 绘制角色
            pygame.draw.circle(preview, (0, 0, 255), 
                              (preview.get_width() // 2, 
                               preview.get_height() // 2), 
                              15)
            
            # 绘制简单的UI元素
            pygame.draw.rect(preview, (50, 50, 50), 
                            (10, 10, preview.get_width() - 20, 40))
            pygame.draw.rect(preview, (200, 200, 200), 
                            (20, 15, 150, 30))
            pygame.draw.rect(preview, (200, 200, 200), 
                            (preview.get_width() - 170, 15, 150, 30))
        
        # 如果是地图预览，添加一些建筑物
        if title == "校园地图与快递路线":
            # 绘制一些建筑
            buildings = [
                (100, 150, 100, 80),
                (300, 120, 120, 100),
                (500, 200, 100, 100),
                (200, 350, 150, 70),
                (450, 400, 120, 90)
            ]
            
            for building in buildings:
                pygame.draw.rect(preview, (150, 80, 80), building)
                pygame.draw.rect(preview, (100, 50, 50), building, 2)
            
            # 绘制一些快递点
            delivery_points = [(150, 200), (400, 300), (550, 450)]
            for point in delivery_points:
                pygame.draw.circle(preview, (255, 200, 0), point, 8)
                pygame.draw.circle(preview, (200, 150, 0), point, 8, 2)
        
        # 添加标题
        font = pygame.font.SysFont(None, 36)
        title_surface = font.render(title, True, (0, 0, 0))
        preview.blit(title_surface, 
                    (preview.get_width() // 2 - title_surface.get_width() // 2, 20))
        
        # 添加提示信息
        font_small = pygame.font.SysFont(None, 24)
        hint = font_small.render("按空格键切换预览图", True, (80, 80, 80))
        preview.blit(hint, 
                   (preview.get_width() // 2 - hint.get_width() // 2, 
                    preview.get_height() - 30))
        
        return preview
    
    def handle_event(self, event):
        """处理游戏事件"""
        if self.game_state == "PREVIEW":
            # 在预览模式中，空格键切换预览图像
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.current_preview = (self.current_preview + 1) % len(self.preview_images)
        else:
            # 在游戏模式中，将事件传递给相应的对象
            self.player.handle_event(event)
            self.ui.handle_event(event)
    
    def update(self):
        """更新游戏状态"""
        # 计算时间流逝
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.timer) / 1000.0  # 转换为秒
        self.timer = current_time
        
        if self.game_state == "GAMEPLAY":
            # 更新游戏内容
            self.player.update(delta_time)
            
            # 计算游戏已经过的时间（分钟）
            game_time = 480 - self.time
            
            # 将游戏时间传递给包裹管理器
            score = self.package_manager.update(delta_time, self.player, game_time)
            self.score += score
            
            # 检查是否所有包裹都已配送完毕
            all_delivered = True
            active_packages = len(self.package_manager.active_packages)
            waiting_packages = sum(1 for p in self.package_manager.packages if p.status == "WAITING")
            
            if active_packages > 0 or waiting_packages > 0:
                all_delivered = False
                
            # 如果所有包裹已配送完毕，并且玩家回到起点 - 提前完成任务
            if all_delivered and not self.player.carrying_package:
                player_pos = self.map.pixel_to_grid(self.player.x, self.player.y)
                if player_pos == self.map.start_point:
                    self.game_state = "GAMEOVER"
                    # 提前完成奖励
                    self.time_bonus = int(self.time)
                    self.score += self.time_bonus
                    self.game_completed = True
                    print(f"恭喜！所有包裹配送完成！获得时间奖励: {self.time_bonus}")
                    print(f"最终得分: {self.score}")
            
            # 减少游戏时间 - 使用正常的游戏时间流逝速度
            self.time -= delta_time / 60.0  # 换算为游戏内分钟，每60秒真实时间过去1分钟游戏时间
            
            # 检查游戏是否结束(时间用完)
            if self.time <= 0:
                self.time = 0
                self.game_state = "GAMEOVER"
                self.game_completed = False
                delivered = len(self.package_manager.delivered_packages)
                remaining = active_packages + waiting_packages
                print("工作日结束！")
                print(f"成功配送: {delivered} 个包裹, 未配送: {remaining} 个包裹")
                print(f"最终得分: {self.score}")
    
    def draw(self):
        """绘制游戏画面"""
        if self.game_state == "PREVIEW":
            # 绘制预览画面
            self.screen.blit(self.preview_images[self.current_preview], (0, 0))
        elif self.game_state == "GAMEPLAY":
            # 绘制游戏画面
            self.map.draw(self.screen)
            self.package_manager.draw(self.screen)
            self.player.draw(self.screen)
            self.ui.draw(self.screen, self.score, self.time, self.weather)
        elif self.game_state == "MENU":
            # 绘制菜单画面
            self.ui.draw_menu(self.screen)
        elif self.game_state == "GAMEOVER":
            # 先绘制游戏场景作为背景
            self.map.draw(self.screen)
            self.package_manager.draw(self.screen)
            self.player.draw(self.screen)
            
            # 再绘制游戏结束界面
            self.ui.draw_game_over(self.screen, self.score, int(self.time), self.game_completed)
    
    def start_game(self):
        """开始新游戏"""
        self.game_state = "GAMEPLAY"
        self.score = 0
        self.time = 480
        self.weather = "SUNNY"
        self.player.reset()
        self.package_manager.generate_packages()
        self.timer = pygame.time.get_ticks()  # 重置定时器
        self.game_completed = False
        self.time_bonus = 0
        print("开始新游戏！") 