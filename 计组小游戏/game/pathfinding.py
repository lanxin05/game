import heapq
import numpy as np

class AStar:
    def __init__(self, game_map):
        self.map = game_map
    
    def find_path(self, start, end):
        """
        使用A*算法找到从起点到终点的最佳路径
        
        Args:
            start: 起点坐标元组 (x, y)，以网格为单位
            end: 终点坐标元组 (x, y)，以网格为单位
            
        Returns:
            path: 路径列表，每个元素为 (x, y) 坐标元组
                  如果没有路径，返回空列表
        """
        # 确保起点和终点在地图范围内
        if not (0 <= start[0] < self.map.width and 0 <= start[1] < self.map.height) or \
           not (0 <= end[0] < self.map.width and 0 <= end[1] < self.map.height):
            return []
        
        # 确保终点可行走
        if self.map.grid[end[1], end[0]] in [self.map.BUILDING, self.map.WATER]:
            return []
        
        # 方向数组，用于生成相邻节点
        # 8个方向：上、右、下、左、右上、右下、左下、左上
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]
        
        # 初始化开放列表和关闭列表
        open_list = []  # 优先队列，存储待考察的节点
        closed_set = set()  # 存储已考察的节点
        
        # 存储每个节点的父节点，用于重建路径
        came_from = {}
        
        # 存储从起点到每个节点的实际成本
        g_score = {start: 0}
        
        # 存储从起点到终点经过每个节点的估计总成本
        f_score = {start: self._heuristic(start, end)}
        
        # 将起点添加到开放列表
        heapq.heappush(open_list, (f_score[start], start))
        
        while open_list:
            # 从开放列表中获取f值最小的节点
            _, current = heapq.heappop(open_list)
            
            # 如果当前节点是终点，重建路径并返回
            if current == end:
                return self._reconstruct_path(came_from, end)
            
            # 将当前节点添加到关闭列表
            closed_set.add(current)
            
            # 检查所有相邻节点
            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # 检查邻居是否在地图范围内
                if not (0 <= neighbor[0] < self.map.width and 0 <= neighbor[1] < self.map.height):
                    continue
                
                # 检查邻居是否可行走
                terrain_type = self.map.grid[neighbor[1], neighbor[0]]
                if terrain_type in [self.map.BUILDING, self.map.WATER]:
                    continue
                
                # 如果邻居已经在关闭列表中，跳过
                if neighbor in closed_set:
                    continue
                
                # 计算经过当前节点到达邻居的成本
                # 对角线移动成本为√2
                if dx != 0 and dy != 0:
                    move_cost = 1.414 * self.map.TERRAIN_COSTS[terrain_type]
                else:
                    move_cost = self.map.TERRAIN_COSTS[terrain_type]
                
                tentative_g_score = g_score[current] + move_cost
                
                # 如果邻居不在开放列表中，或者找到了更优路径
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # 更新路径和成本
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, end)
                    
                    # 如果邻居不在开放列表中，添加到开放列表
                    if neighbor not in [i[1] for i in open_list]:
                        heapq.heappush(open_list, (f_score[neighbor], neighbor))
        
        # 如果开放列表为空但未找到路径，则无法到达终点
        return []
    
    def _heuristic(self, a, b):
        """
        计算两点之间的启发式距离（曼哈顿距离）
        
        Args:
            a: 第一个点的坐标 (x, y)
            b: 第二个点的坐标 (x, y)
            
        Returns:
            distance: 两点之间的估计距离
        """
        # 使用曼哈顿距离作为启发式函数
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _reconstruct_path(self, came_from, current):
        """
        从终点回溯到起点，重建完整路径
        
        Args:
            came_from: 存储每个节点的父节点的字典
            current: 终点坐标
            
        Returns:
            path: 从起点到终点的路径列表
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        
        # 反转路径，使其从起点到终点
        total_path.reverse()
        
        return total_path 