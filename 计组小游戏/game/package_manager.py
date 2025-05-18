import pygame
import random
from .pathfinding import AStar

class Package:
    def __init__(self, start_point, destination, deadline, value):
        self.start_point = start_point  # 起点 (grid_x, grid_y)
        self.destination = destination  # 目的地 (grid_x, grid_y)
        self.deadline = deadline        # 截止时间（游戏内分钟）
        self.value = value              # 包裹价值（得分）
        self.pickup_time = None         # 拾取时间
        self.status = "WAITING"         # 状态：WAITING, PICKED, DELIVERED, EXPIRED
        self.id = random.randint(10000, 99999)  # 随机包裹ID
    
    def pick_up(self, current_time):
        """拾取包裹"""
        self.pickup_time = current_time
        self.status = "PICKED"
    
    def deliver(self, current_time):
        """配送包裹"""
        self.status = "DELIVERED"
        
        # 计算分数，根据提前量给予奖励
        time_left = self.deadline - current_time
        time_bonus = max(0, time_left) / 30  # 每提前30分钟，增加一倍基础分数
        return int(self.value * (1 + time_bonus))
    
    def update(self, current_time):
        """更新包裹状态"""
        # 如果已超时且未配送，标记为过期
        if current_time > self.deadline and self.status == "WAITING":
            self.status = "EXPIRED"
            return False
        return True

class PackageManager:
    def __init__(self, game_map):
        self.map = game_map
        self.packages = []
        self.active_packages = []
        self.delivered_packages = []
        self.expired_packages = []
        
        # 包裹生成设置
        self.next_spawn_time = 0
        self.spawn_interval = 120  # 默认每120秒游戏时间生成一个新包裹
        self.max_active_packages = 5
        
        # 初始化寻路器用于检查路径可达性
        self.pathfinder = AStar(self.map)
        
    def update(self, delta_time, player, game_time):
        """更新所有包裹状态"""
        # 使用由GameManager传入的game_time
        
        # 更新包裹状态
        for package in self.packages[:]:
            package.update(game_time)
        
        # 处理拾取包裹
        self._handle_pickup(player, game_time)
        
        # 处理交付包裹
        return self._handle_delivery(player, game_time)
    
    def _handle_pickup(self, player, game_time):
        """处理玩家拾取包裹"""
        player_grid_pos = self.map.pixel_to_grid(player.x, player.y)
        
        for package in self.packages:
            if (package.status == "WAITING" and 
                player_grid_pos == package.start_point and 
                player.pickup_package()):
                package.pick_up(game_time)
                self.active_packages.append(package)
    
    def _handle_delivery(self, player, game_time):
        """处理玩家配送包裹"""
        player_grid_pos = self.map.pixel_to_grid(player.x, player.y)
        score = 0
        
        for package in self.active_packages[:]:
            if (package.status == "PICKED" and 
                player_grid_pos == package.destination and 
                player.deliver_package()):
                # 配送成功，计算得分
                points = package.deliver(game_time)
                score += points
                
                # 移动到已配送列表
                self.active_packages.remove(package)
                self.delivered_packages.append(package)
        
        return score
    
    def generate_packages(self):
        """初始化包裹列表"""
        self.packages = []
        self.active_packages = []
        self.delivered_packages = []
        self.expired_packages = []
        
        # 生成初始包裹
        for _ in range(3):
            self._generate_package()
    
    def _generate_package(self):
        """生成新包裹"""
        # 获取可能的目的地（配送点）
        destinations = self.map.delivery_points
        
        # 从起点生成包裹
        start_point = self.map.start_point
        
        # 尝试找到一个有效路径的目的地
        valid_destination = None
        valid_path = None
        max_attempts = 10  # 最多尝试次数
        
        for _ in range(max_attempts):
            # 随机选择一个目的地
            if not destinations:
                print("错误：没有可用的配送点")
                return
                
            destination = random.choice(destinations)
            
            # 检查路径可达性
            path = self.pathfinder.find_path(start_point, destination)
            if path:
                valid_destination = destination
                valid_path = path
                print(f"找到可行路径 从 {start_point} 到 {destination}, 长度: {len(path)}")
                break
        
        # 如果没有找到有效路径，打印错误
        if not valid_destination:
            print("警告：无法生成有效包裹，所有目的地都无法到达")
            return
            
        # 设置截止时间（当前时间 + 随机时长）
        deadline = random.randint(120, 240)  # 2-4小时期限
        
        # 设置价值（基于距离和截止时间）
        distance = len(valid_path)  # 使用路径长度作为实际距离
        value = int(10 + distance * 2)  # 基础分 + 距离奖励
        
        # 创建新包裹
        package = Package(start_point, valid_destination, deadline, value)
        self.packages.append(package)
        print(f"生成新包裹: ID {package.id}, 目的地: {valid_destination}, 价值: {value}")
    
    def draw(self, screen):
        """绘制所有包裹"""
        # 绘制等待中的包裹
        for package in self.packages:
            if package.status == "WAITING":
                # 在起点绘制等待中的包裹
                pos = self.map.grid_to_pixel(*package.start_point)
                pygame.draw.rect(screen, (150, 100, 50), 
                               (pos[0] - 5, pos[1] - 5, 10, 10))
                
                # 绘制包裹ID
                font = pygame.font.SysFont(None, 20)
                id_text = f"{package.id}"
                id_surface = font.render(id_text, True, (0, 0, 0))
                screen.blit(id_surface, (pos[0] - id_surface.get_width() // 2, 
                                        pos[1] - 25))
        
        # 绘制目的地标记
        for package in self.active_packages:
            # 在目的地绘制标记
            pos = self.map.grid_to_pixel(*package.destination)
            pygame.draw.circle(screen, (255, 100, 100), pos, 8, 2)
            
            # 绘制包裹ID
            font = pygame.font.SysFont(None, 20)
            id_text = f"{package.id}"
            id_surface = font.render(id_text, True, (0, 0, 0))
            screen.blit(id_surface, (pos[0] - id_surface.get_width() // 2, 
                                    pos[1] - 25)) 