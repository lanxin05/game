import pygame
import sys
import os
from game.game_manager import GameManager

# 初始化Pygame
pygame.init()

# 游戏设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "校园快递配送模拟器"

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# 确保assets目录存在
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

def main():
    # 初始化游戏管理器
    game_manager = GameManager(screen)
    
    # 游戏主循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event)
        
        # 更新游戏状态
        game_manager.update()
        
        # 绘制游戏画面
        screen.fill((255, 255, 255))  # 白色背景
        game_manager.draw()
        pygame.display.flip()
        
        # 控制帧率
        clock.tick(60)
    
    # 退出游戏
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 