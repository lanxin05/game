import pygame
import numpy as np

class Map:
    # 地形类型常量
    GRASS = 0
    ROAD = 1
    BUILDING = 2
    WATER = 3
    DELIVERY_POINT = 4
    START_POINT = 5
    
    # 地形成本 (用于寻路算法)
    TERRAIN_COSTS = {
        GRASS: 3,     # 草地行走较慢
        ROAD: 1,      # 道路行走最快
        BUILDING: -1, # 建筑物不可通行
        WATER: -1,    # 水域不可通行
        DELIVERY_POINT: 1,  # 配送点和道路一样快
        START_POINT: 1,     # 起点和道路一样快
    }
    
    # 地形颜色
    TERRAIN_COLORS = {
        GRASS: (100, 200, 100),        # 绿色
        ROAD: (180, 180, 180),         # 灰色
        BUILDING: (150, 80, 80),       # 红褐色
        WATER: (100, 150, 255),        # 蓝色
        DELIVERY_POINT: (255, 200, 0), # 黄色
        START_POINT: (50, 200, 50)     # 深绿色
    }
    
    def __init__(self, width=25, height=18):
        self.width = width
        self.height = height
        self.cell_size = 30
        
        # 创建地图数据
        self.grid = np.zeros((height, width), dtype=int)
        self.delivery_points = []
        self.start_point = (1, 1)  # 默认起点
        
        # 初始化默认地图
        self.generate_default_map()
    
    def generate_default_map(self):
        """生成默认的校园地图"""
        # 填充草地
        self.grid.fill(self.GRASS)
        
        # 创建主干道路网络
        middle_row = self.height // 2
        middle_col = self.width // 2
        
        # 水平主路
        self.grid[middle_row, :] = self.ROAD
        # 垂直主路
        self.grid[:, middle_col] = self.ROAD
        
        # 添加一些次要道路
        for i in range(3, self.width, 5):
            if i != middle_col:
                self.grid[2:self.height-2, i] = self.ROAD
        
        for i in range(3, self.height, 4):
            if i != middle_row:
                self.grid[i, 2:self.width-2] = self.ROAD
        
        # 设置起点
        self.grid[1, 1] = self.START_POINT
        self.start_point = (1, 1)
        
        # 确保起点有通路
        self.grid[1, 2:middle_col] = self.ROAD  # 从起点到中央垂直道路的水平连接
        self.grid[1:middle_row, middle_col] = self.ROAD  # 确保垂直道路延伸到顶部
        
        # 添加一些建筑物
        buildings = [
            (3, 3, 3, 2),     # (行, 列, 高度, 宽度)
            (3, 15, 4, 3),
            (10, 5, 3, 4),
            (12, 15, 4, 3),
            (7, 20, 3, 3)
        ]
        
        for b in buildings:
            row, col, height, width = b
            self.grid[row:row+height, col:col+width] = self.BUILDING
        
        # 添加一个水域
        self.grid[12:15, 1:4] = self.WATER
        
        # 设置配送点
        delivery_points = [
            (5, 16),
            (10, 9),
            (13, 18)
        ]
        
        self.delivery_points = []  # 清空现有配送点
        
        for point in delivery_points:
            row, col = point
            
            # 确保配送点周围有道路
            self._ensure_road_connection(row, col)
            
            # 设置配送点
            self.grid[row, col] = self.DELIVERY_POINT
            self.delivery_points.append((col, row))  # 注意：存储为(x,y)格式
    
    def _ensure_road_connection(self, row, col):
        """确保给定位置连接到道路网络"""
        # 找到最近的道路点
        road_found = False
        search_radius = 1
        
        # 向外扩散寻找附近的道路
        while not road_found and search_radius < 5:
            # 检查周围一圈的格子
            for r in range(row-search_radius, row+search_radius+1):
                for c in range(col-search_radius, col+search_radius+1):
                    # 检查是否在地图范围内
                    if 0 <= r < self.height and 0 <= c < self.width:
                        if self.grid[r, c] == self.ROAD:
                            # 找到了道路，创建连接
                            self._create_road_connection(row, col, r, c)
                            road_found = True
                            return
            
            search_radius += 1
        
        # 如果没找到附近的道路，连接到中央道路
        middle_row = self.height // 2
        middle_col = self.width // 2
        self._create_road_connection(row, col, middle_row, col)  # 垂直连接
        self._create_road_connection(middle_row, col, middle_row, middle_col)  # 水平连接
    
    def _create_road_connection(self, row1, col1, row2, col2):
        """在两点之间创建道路连接"""
        # 简单的直线连接
        if row1 == row2:  # 水平连接
            start_col = min(col1, col2)
            end_col = max(col1, col2)
            for c in range(start_col, end_col + 1):
                if self.grid[row1, c] not in [self.DELIVERY_POINT, self.START_POINT]:
                    self.grid[row1, c] = self.ROAD
        else:  # 垂直连接
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            for r in range(start_row, end_row + 1):
                if self.grid[r, col1] not in [self.DELIVERY_POINT, self.START_POINT]:
                    self.grid[r, col1] = self.ROAD
    
    def get_terrain_type(self, x, y):
        """获取指定位置的地形类型"""
        # 将像素坐标转换为网格坐标
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        
        # 检查坐标是否在地图范围内
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y, grid_x]
        return -1  # 超出地图范围
    
    def get_terrain_cost(self, x, y):
        """获取指定位置的通行成本"""
        terrain_type = self.get_terrain_type(x, y)
        return self.TERRAIN_COSTS.get(terrain_type, -1)
    
    def is_walkable(self, x, y):
        """检查指定位置是否可行走"""
        cost = self.get_terrain_cost(x, y)
        return cost > 0
    
    def grid_to_pixel(self, grid_x, grid_y):
        """将网格坐标转换为像素坐标(中心点)"""
        return (grid_x * self.cell_size + self.cell_size // 2, 
                grid_y * self.cell_size + self.cell_size // 2)
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """将像素坐标转换为网格坐标"""
        return (pixel_x // self.cell_size, pixel_y // self.cell_size)
    
    def draw(self, screen):
        """绘制地图"""
        # 绘制每个网格单元
        for y in range(self.height):
            for x in range(self.width):
                terrain_type = self.grid[y, x]
                color = self.TERRAIN_COLORS.get(terrain_type, (0, 0, 0))
                
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                  self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # 网格线 