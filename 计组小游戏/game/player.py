import pygame

class Player:
    def __init__(self, game_map):
        self.map = game_map
        
        # 玩家位置(像素坐标)
        start_x, start_y = self.map.grid_to_pixel(*self.map.start_point)
        self.x = start_x
        self.y = start_y
        
        # 玩家状态
        self.speed = 150  # 像素/秒
        self.radius = 10  # 玩家半径
        self.color = (0, 0, 255)  # 蓝色
        self.carrying_package = False
        self.max_packages = 3
        self.current_packages = 0
        
        # 移动状态
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        
        # 路径跟随
        self.current_path = []
        self.follow_path = False
        self.path_index = 0
        
        # 添加A*寻路器引用
        self.pathfinder = None
    
    def set_pathfinder(self, pathfinder):
        """设置寻路器引用"""
        self.pathfinder = pathfinder
    
    def reset(self):
        """重置玩家到初始状态"""
        start_x, start_y = self.map.grid_to_pixel(*self.map.start_point)
        self.x = start_x
        self.y = start_y
        self.carrying_package = False
        self.current_packages = 0
        self.current_path = []
        self.follow_path = False
    
    def handle_event(self, event):
        """处理玩家输入事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = True
                
            # 路径跟随切换
            if event.key == pygame.K_p:
                # 获取当前玩家的网格坐标
                current_grid = self.map.pixel_to_grid(self.x, self.y)
                # 确保坐标是整数
                current_grid = (int(current_grid[0]), int(current_grid[1]))
                print("当前位置:", current_grid)
                
                # 如果有寻路器
                if self.pathfinder:
                    # 如果玩家正在携带包裹，寻找到最近的配送点
                    if self.carrying_package:
                        nearest_point = None
                        min_distance = float('inf')
                        
                        # 找出最近的配送点
                        for point in self.map.delivery_points:
                            # 检查到该点的路径是否存在
                            path = self.pathfinder.find_path(current_grid, point)
                            if path:  # 如果存在路径
                                dist = len(path)  # 使用路径长度作为距离
                                if dist < min_distance:
                                    min_distance = dist
                                    nearest_point = point
                        
                        if nearest_point:
                            print("寻找路径到配送点:", nearest_point)
                            path = self.pathfinder.find_path(current_grid, nearest_point)
                            if path:
                                self.current_path = path
                                self.path_index = 0
                                self.follow_path = True
                                print("已计算路径，长度:", len(path))
                            else:
                                print("无法找到到配送点的路径")
                        else:
                            print("未找到可到达的配送点")
                    else:
                        # 如果没有携带包裹，寻找回快递站的路径
                        start_point = self.map.start_point
                        print("寻找路径回快递站:", start_point)
                        path = self.pathfinder.find_path(current_grid, start_point)
                        if path:
                            self.current_path = path
                            self.path_index = 0
                            self.follow_path = True
                            print("已计算回快递站的路径，长度:", len(path))
                        else:
                            print("无法找到回快递站的路径")
                else:
                    # 如果没有寻路器
                    print("寻路器未设置")
                    # 仅切换显示/隐藏路径状态
                    self.follow_path = not self.follow_path
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = False
    
    def update(self, delta_time):
        """更新玩家状态"""
        # 如果正在跟随路径
        if self.follow_path and self.current_path and self.path_index < len(self.current_path):
            self._follow_path(delta_time)
        else:
            # 根据用户输入移动
            self._move_by_input(delta_time)
    
    def _move_by_input(self, delta_time):
        """根据用户输入移动"""
        dx, dy = 0, 0
        
        if self.moving_left:
            dx -= 1
        if self.moving_right:
            dx += 1
        if self.moving_up:
            dy -= 1
        if self.moving_down:
            dy += 1
            
        # 标准化向量，使对角线移动不会更快
        if dx != 0 and dy != 0:
            magnitude = (dx**2 + dy**2)**0.5
            dx /= magnitude
            dy /= magnitude
        
        # 计算新位置
        new_x = self.x + dx * self.speed * delta_time
        new_y = self.y + dy * self.speed * delta_time
        
        # 检查新位置是否可行走
        if self.map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            # 尝试水平移动
            if self.map.is_walkable(new_x, self.y):
                self.x = new_x
            # 尝试垂直移动
            elif self.map.is_walkable(self.x, new_y):
                self.y = new_y
    
    def _follow_path(self, delta_time):
        """跟随预先计算的路径"""
        if not self.current_path or self.path_index >= len(self.current_path):
            self.follow_path = False
            return
            
        # 获取当前目标点
        target_x, target_y = self.map.grid_to_pixel(*self.current_path[self.path_index])
        
        # 计算到目标的向量
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果足够接近目标，则移动到下一个点
        if distance < 5:
            self.path_index += 1
            return
            
        # 标准化向量
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # 计算新位置
        new_x = self.x + dx * self.speed * delta_time
        new_y = self.y + dy * self.speed * delta_time
        
        # 移动玩家
        self.x = new_x
        self.y = new_y
    
    def set_path(self, path):
        """设置要跟随的路径"""
        self.current_path = path
        self.path_index = 0
        self.follow_path = True
    
    def draw(self, screen):
        """绘制玩家"""
        # 绘制玩家圆形
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # 如果有包裹，绘制在玩家上方
        if self.carrying_package:
            pygame.draw.rect(screen, (150, 100, 50), 
                            (int(self.x) - 5, int(self.y) - 20, 10, 10))
        
        # 如果有路径且显示路径开启，绘制路径
        if self.current_path and self.follow_path:
            for i in range(self.path_index, len(self.current_path) - 1):
                start_pos = self.map.grid_to_pixel(*self.current_path[i])
                end_pos = self.map.grid_to_pixel(*self.current_path[i + 1])
                pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)
    
    def pickup_package(self):
        """尝试拾取包裹"""
        if self.current_packages < self.max_packages:
            self.current_packages += 1
            self.carrying_package = True
            return True
        return False
    
    def deliver_package(self):
        """尝试交付包裹"""
        if self.carrying_package and self.current_packages > 0:
            self.current_packages -= 1
            if self.current_packages == 0:
                self.carrying_package = False
            return True
        return False 