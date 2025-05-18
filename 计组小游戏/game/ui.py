import pygame
import os

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 字体设置 - 减小字体大小
        pygame.font.init()
        
        # 使用系统默认字体，但用英文替代中文显示（解决中文字体问题）
        self.font_large = pygame.font.Font(pygame.font.get_default_font(), 36)  # 减小字体
        self.font_medium = pygame.font.Font(pygame.font.get_default_font(), 24)  # 减小字体
        self.font_small = pygame.font.Font(pygame.font.get_default_font(), 18)  # 减小字体
        
        # 颜色设置
        self.color_text = (50, 50, 50)
        self.color_highlight = (255, 100, 100)
        self.color_background = (240, 240, 240)
        self.color_panel = (200, 200, 200)
        self.color_button = (180, 180, 180)
        self.color_button_hover = (220, 220, 220)
        
        # UI元素状态
        self.buttons = {}
        self.active_button = None
        
        # 回调函数，用于处理按钮点击
        self.button_callbacks = {
            "start": None,
            "restart": None,
            "menu": None,
            "help": None,
            "quit": None
        }
    
    def set_callback(self, button_name, callback_function):
        """设置按钮点击的回调函数"""
        if button_name in self.button_callbacks:
            self.button_callbacks[button_name] = callback_function
    
    def handle_event(self, event):
        """处理UI相关事件"""
        if event.type == pygame.MOUSEMOTION:
            # 检查鼠标悬停在哪个按钮上
            mouse_pos = pygame.mouse.get_pos()
            self.active_button = None
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.active_button = name
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 检查是否点击按钮
            mouse_pos = pygame.mouse.get_pos()
            for name, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    self._handle_button_click(name)
                    return True  # 返回True表示处理了事件
        return False  # 返回False表示没有处理事件
    
    def _handle_button_click(self, button_name):
        """处理按钮点击事件"""
        print(f"Button clicked: {button_name}")
        
        # 如果该按钮有回调函数，调用它
        if button_name in self.button_callbacks and self.button_callbacks[button_name]:
            self.button_callbacks[button_name]()
            return True
        return False
    
    def draw(self, screen, score, time, weather):
        """绘制游戏主界面UI"""
        # 绘制顶部信息面板
        self._draw_info_panel(screen, score, time, weather)
    
    def _draw_info_panel(self, screen, score, time, weather):
        """绘制顶部信息面板"""
        # 绘制面板背景
        panel_rect = pygame.Rect(10, 10, self.width - 20, 40)
        pygame.draw.rect(screen, self.color_panel, panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)
        
        # 绘制得分
        score_text = f"Score: {score}"  # 英文
        score_surface = self.font_medium.render(score_text, True, self.color_text)
        screen.blit(score_surface, (20, 15))
        
        # 绘制时间 - 修正时间计算
        total_minutes = int(time)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        seconds = int((time - total_minutes) * 60)
        
        # 确保秒数不超过59
        if seconds >= 60:
            seconds = 59
            
        time_text = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"  # 英文
        time_surface = self.font_medium.render(time_text, True, self.color_text)
        screen.blit(time_surface, (self.width // 2 - time_surface.get_width() // 2, 15))
        
        # 绘制天气
        weather_text = f"Weather: {self._get_weather_name(weather)}"  # 英文
        weather_surface = self.font_medium.render(weather_text, True, self.color_text)
        screen.blit(weather_surface, (self.width - 20 - weather_surface.get_width(), 15))
    
    def _get_weather_name(self, weather):
        """获取天气的名称 (英文)"""
        weather_names = {
            "SUNNY": "Sunny",
            "RAINY": "Rainy",
            "FOGGY": "Foggy"
        }
        return weather_names.get(weather, "Unknown")
    
    def draw_menu(self, screen):
        """绘制游戏菜单界面"""
        # 填充背景
        screen.fill(self.color_background)
        
        # 绘制标题
        title = "Campus Delivery Simulator"  # 英文标题
        title_surface = self.font_large.render(title, True, self.color_text)
        screen.blit(title_surface, 
                   (self.width // 2 - title_surface.get_width() // 2, 100))
        
        # 绘制按钮
        buttons = [
            ("start", "Start Game", 200),  # 英文
            ("help", "Help", 300),         # 英文
            ("quit", "Quit", 400)          # 英文
        ]
        
        self.buttons = {}
        for name, text, y in buttons:
            button_width = 200
            button_height = 50
            button_x = self.width // 2 - button_width // 2
            
            button_rect = pygame.Rect(button_x, y, button_width, button_height)
            self.buttons[name] = button_rect
            
            # 绘制按钮
            color = self.color_button_hover if name == self.active_button else self.color_button
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (100, 100, 100), button_rect, 2)
            
            # 绘制按钮文本
            text_surface = self.font_medium.render(text, True, self.color_text)
            screen.blit(text_surface, 
                       (button_x + button_width // 2 - text_surface.get_width() // 2, 
                        y + button_height // 2 - text_surface.get_height() // 2))
    
    def draw_game_over(self, screen, score, time_left=0, game_completed=False):
        """绘制游戏结束界面"""
        # 创建一个半透明的面板覆盖在游戏上
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, self.width, self.height))
        screen.blit(overlay, (0, 0))
        
        # 显示游戏结束的标题
        if game_completed:
            title_text = self.font_large.render("Congratulations! Mission Completed", True, (255, 255, 100))
        else:
            title_text = self.font_large.render("Game Over", True, (255, 255, 255))
        
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 显示游戏得分
        score_text = self.font_medium.render(f"Final Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width // 2, 170))
        screen.blit(score_text, score_rect)
        
        # 显示剩余时间
        time_text = self.font_medium.render(f"Time Left: {time_left} min", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.width // 2, 210))
        screen.blit(time_text, time_rect)
        
        # 创建一个更小的"再试一次"按钮，放在屏幕下方居中
        button_width, button_height = 150, 40  # 缩小按钮尺寸
        button_x = self.width // 2 - button_width // 2
        button_y = 300  # 更靠上的位置
        
        button_color = self.color_button_hover if self.active_button == "restart" else self.color_button
        
        restart_button = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, button_color, restart_button, border_radius=5)  # 圆角更小
        pygame.draw.rect(screen, (100, 100, 100), restart_button, 2, border_radius=5)
        
        restart_text = self.font_small.render("Try Again", True, self.color_text)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        screen.blit(restart_text, restart_text_rect)
        
        # 保存按钮以便检测点击
        self.buttons = {}  # 清除之前的按钮
        self.buttons["restart"] = restart_button 