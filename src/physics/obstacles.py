#!/usr/bin/env python3
"""
障碍物类定义
支持各种形状的3D障碍物
"""

import numpy as np

class Obstacle:
    """3D障碍物基类"""
    
    def __init__(self, position, size, color=(0.5, 0.5, 0.5), obstacle_type='box'):
        """
        初始化障碍物
        
        Args:
            position: [x, y, z] 位置
            size: 尺寸参数 (对于box是[width, height, depth])
            color: RGB颜色
            obstacle_type: 障碍物类型 ('box', 'sphere', 'platform')
        """
        self.position = np.array(position, dtype=float)
        self.size = size if isinstance(size, (list, tuple)) else [size, size, size]
        self.color = color
        self.obstacle_type = obstacle_type
        
    def check_collision(self, cube_pos, cube_size):
        """
        检查立方体是否与障碍物碰撞
        
        Args:
            cube_pos: 立方体位置
            cube_size: 立方体尺寸
            
        Returns:
            bool: 是否碰撞
        """
        if self.obstacle_type == 'box':
            return self._check_box_collision(cube_pos, cube_size)
        elif self.obstacle_type == 'sphere':
            return self._check_sphere_collision(cube_pos, cube_size)
        elif self.obstacle_type == 'platform':
            return self._check_platform_collision(cube_pos, cube_size)
        return False
    
    def _check_box_collision(self, cube_pos, cube_size):
        """检查与方形障碍物的碰撞"""
        # AABB碰撞检测
        cube_half = cube_size / 2
        obs_half = np.array(self.size) / 2
        
        # 计算最小和最大边界
        cube_min = cube_pos - cube_half
        cube_max = cube_pos + cube_half
        obs_min = self.position - obs_half
        obs_max = self.position + obs_half
        
        # 检查每个轴的重叠
        overlap_x = cube_max[0] > obs_min[0] and cube_min[0] < obs_max[0]
        overlap_y = cube_max[1] > obs_min[1] and cube_min[1] < obs_max[1]
        overlap_z = cube_max[2] > obs_min[2] and cube_min[2] < obs_max[2]
        
        return overlap_x and overlap_y and overlap_z
    
    def _check_sphere_collision(self, cube_pos, cube_size):
        """检查与球形障碍物的碰撞"""
        # 计算立方体到球心的最近距离
        cube_half = cube_size / 2
        
        # 找到立方体上最接近球心的点
        closest_point = np.clip(self.position, 
                               cube_pos - cube_half, 
                               cube_pos + cube_half)
        
        # 计算距离
        distance = np.linalg.norm(self.position - closest_point)
        radius = self.size[0]  # 球的半径
        
        return distance < radius
    
    def _check_platform_collision(self, cube_pos, cube_size):
        """检查与平台的碰撞（只检查上表面）"""
        cube_bottom = cube_pos[2] - cube_size / 2
        platform_top = self.position[2] + self.size[2] / 2
        platform_bottom = self.position[2] - self.size[2] / 2
        
        # 检查高度范围
        if cube_bottom <= platform_top and cube_bottom >= platform_bottom:
            # 检查XY平面的重叠
            cube_half = cube_size / 2
            platform_half_x = self.size[0] / 2
            platform_half_y = self.size[1] / 2
            
            overlap_x = (cube_pos[0] + cube_half > self.position[0] - platform_half_x and 
                        cube_pos[0] - cube_half < self.position[0] + platform_half_x)
            overlap_y = (cube_pos[1] + cube_half > self.position[1] - platform_half_y and 
                        cube_pos[1] - cube_half < self.position[1] + platform_half_y)
            
            return overlap_x and overlap_y
        
        return False
    
    def get_collision_response(self, cube_pos, cube_vel, cube_size):
        """
        计算碰撞响应
        
        Args:
            cube_pos: 立方体位置
            cube_vel: 立方体速度
            cube_size: 立方体尺寸
            
        Returns:
            tuple: (new_position, new_velocity, collision_normal)
        """
        if self.obstacle_type == 'platform':
            return self._platform_collision_response(cube_pos, cube_vel, cube_size)
        elif self.obstacle_type == 'sphere':
            return self._sphere_collision_response(cube_pos, cube_vel, cube_size)
        else:
            return self._box_collision_response(cube_pos, cube_vel, cube_size)
    
    def _platform_collision_response(self, cube_pos, cube_vel, cube_size):
        """平台碰撞响应 - 增强版"""
        # 将立方体放置在平台上方
        platform_top = self.position[2] + self.size[2] / 2
        new_pos = cube_pos.copy()
        new_pos[2] = platform_top + cube_size / 2 + 0.1  # 稍微离开表面
        
        # 增强的反弹效果
        new_vel = cube_vel.copy()
        if new_vel[2] < 0:  # 向下运动
            # 更强的反弹，并增加一些随机性
            bounce_factor = 0.8 + np.random.uniform(-0.1, 0.1)  
            new_vel[2] = -new_vel[2] * bounce_factor
            
            # 给水平方向添加一些扩散
            horizontal_boost = np.random.uniform(-0.5, 0.5, 2)
            new_vel[0] += horizontal_boost[0]
            new_vel[1] += horizontal_boost[1]
        
        normal = np.array([0, 0, 1])  # 向上的法向量
        return new_pos, new_vel, normal
    
    def _box_collision_response(self, cube_pos, cube_vel, cube_size):
        """方形障碍物碰撞响应 - 增强版"""
        # 计算碰撞方向
        direction = cube_pos - self.position
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction = direction / distance
        else:
            direction = np.array([1, 0, 0])  # 默认方向
        
        # 将立方体推出障碍物
        push_distance = (cube_size + max(self.size)) / 2 + 0.2
        new_pos = self.position + direction * push_distance
        
        # 增强的反弹速度
        velocity_magnitude = np.linalg.norm(cube_vel)
        
        # 计算反射速度
        velocity_dot_normal = np.dot(cube_vel, direction)
        new_vel = cube_vel - 2 * velocity_dot_normal * direction
        
        # 增加弹性和一些随机扰动
        bounce_factor = 0.75 + np.random.uniform(-0.1, 0.1)
        new_vel *= bounce_factor
        
        # 添加一些旋转效应（通过速度扰动模拟）
        spin_effect = np.random.uniform(-0.3, 0.3, 3)
        new_vel += spin_effect
        
        return new_pos, new_vel, direction
    
    def _sphere_collision_response(self, cube_pos, cube_vel, cube_size):
        """球形障碍物碰撞响应 - 增强版"""
        # 计算从球心到立方体的方向
        direction = cube_pos - self.position
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction = direction / distance
        else:
            direction = np.array([1, 0, 0])  # 默认方向
        
        # 将立方体推出球形障碍物
        sphere_radius = self.size[0]  # 球的半径
        push_distance = sphere_radius + cube_size / 2 + 0.15
        new_pos = self.position + direction * push_distance
        
        # 球形碰撞的反弹效果（最自然的反弹）
        velocity_magnitude = np.linalg.norm(cube_vel)
        
        # 完美反射
        velocity_dot_normal = np.dot(cube_vel, direction)
        reflected_vel = cube_vel - 2 * velocity_dot_normal * direction
        
        # 球形表面有更好的弹性
        bounce_factor = 0.85 + np.random.uniform(-0.05, 0.05)
        new_vel = reflected_vel * bounce_factor
        
        # 球形表面添加轻微的切向力（模拟旋转）
        tangent = np.cross(direction, [0, 0, 1])
        if np.linalg.norm(tangent) > 0:
            tangent = tangent / np.linalg.norm(tangent)
            spin_force = np.random.uniform(-0.2, 0.2)
            new_vel += spin_force * tangent
        
        return new_pos, new_vel, direction
    
    def get_render_data(self):
        """获取渲染数据"""
        if self.obstacle_type == 'box':
            return self._get_box_render_data()
        elif self.obstacle_type == 'sphere':
            return self._get_sphere_render_data()
        elif self.obstacle_type == 'platform':
            return self._get_platform_render_data()
    
    def _get_box_render_data(self):
        """获取方形障碍物的渲染数据"""
        half_size = np.array(self.size) / 2
        corners = np.array([
            self.position + [-half_size[0], -half_size[1], -half_size[2]],
            self.position + [+half_size[0], -half_size[1], -half_size[2]],
            self.position + [+half_size[0], +half_size[1], -half_size[2]],
            self.position + [-half_size[0], +half_size[1], -half_size[2]],
            self.position + [-half_size[0], -half_size[1], +half_size[2]],
            self.position + [+half_size[0], -half_size[1], +half_size[2]],
            self.position + [+half_size[0], +half_size[1], +half_size[2]],
            self.position + [-half_size[0], +half_size[1], +half_size[2]],
        ])
        
        faces = [
            [corners[0], corners[1], corners[2], corners[3]],  # 底面
            [corners[4], corners[5], corners[6], corners[7]],  # 顶面
            [corners[0], corners[1], corners[5], corners[4]],  # 前面
            [corners[2], corners[3], corners[7], corners[6]],  # 后面
            [corners[1], corners[2], corners[6], corners[5]],  # 右面
            [corners[0], corners[3], corners[7], corners[4]]   # 左面
        ]
        
        return {'type': 'box', 'faces': faces, 'color': self.color}
    
    def _get_sphere_render_data(self):
        """获取球形障碍物的渲染数据"""
        return {
            'type': 'sphere', 
            'center': self.position, 
            'radius': self.size[0], 
            'color': self.color
        }
    
    def _get_platform_render_data(self):
        """获取平台的渲染数据"""
        # 平台渲染类似于扁平的方形
        return self._get_box_render_data()

class ObstacleManager:
    """障碍物管理器"""
    
    def __init__(self):
        self.obstacles = []
    
    def add_obstacle(self, obstacle):
        """添加障碍物"""
        self.obstacles.append(obstacle)
    
    def create_scene_obstacles(self, scene_type='basic'):
        """创建预设的障碍物场景"""
        self.obstacles.clear()
        
        if scene_type == 'basic':
            # 基础场景：几个平台
            self.add_obstacle(Obstacle([2, 0, 5], [3, 3, 0.5], color=(0.8, 0.4, 0.2), obstacle_type='platform'))
            self.add_obstacle(Obstacle([-2, 2, 8], [2, 2, 0.5], color=(0.2, 0.8, 0.4), obstacle_type='platform'))
            self.add_obstacle(Obstacle([0, 0, 3], [1, 1, 0.5], color=(0.2, 0.2, 0.8), obstacle_type='sphere'))
            
        elif scene_type == 'complex':
            # 复杂场景：多层障碍物
            self.add_obstacle(Obstacle([0, 0, 3], [4, 1, 0.5], color=(0.8, 0.4, 0.2), obstacle_type='platform'))
            self.add_obstacle(Obstacle([3, -2, 6], [2, 2, 0.5], color=(0.2, 0.8, 0.4), obstacle_type='platform'))
            self.add_obstacle(Obstacle([-3, 1, 9], [2, 2, 0.5], color=(0.4, 0.2, 0.8), obstacle_type='platform'))
            self.add_obstacle(Obstacle([1, 3, 12], [1.5, 1.5, 0.5], color=(0.8, 0.8, 0.2), obstacle_type='platform'))
            self.add_obstacle(Obstacle([0, 0, 5], [0.7, 0.7, 0.7], color=(0.9, 0.1, 0.1), obstacle_type='sphere'))
            
        elif scene_type == 'bouncy_obstacles':
            # 弹性场景的障碍物 - 创建更戏剧性的交互
            # 第一层：两个平台形成通道
            self.add_obstacle(Obstacle([-2, 0, 4], [2, 2, 0.4], color=(0.9, 0.3, 0.1), obstacle_type='platform'))
            self.add_obstacle(Obstacle([2, 0, 6], [2, 2, 0.4], color=(0.9, 0.5, 0.1), obstacle_type='platform'))
            
            # 第二层：弹跳板
            self.add_obstacle(Obstacle([0, 2, 8], [1.5, 3, 0.3], color=(0.1, 0.9, 0.3), obstacle_type='platform'))
            
            # 第三层：方形障碍物作为最终撞击目标
            self.add_obstacle(Obstacle([1, -1, 10], [1.2, 1.2, 1.2], color=(0.1, 0.5, 0.9), obstacle_type='box'))
            
            # 球形障碍物作为最后的缓冲
            self.add_obstacle(Obstacle([-1, 1, 2], [0.8, 0.8, 0.8], color=(0.8, 0.1, 0.9), obstacle_type='sphere'))
    
    def check_collisions(self, cube):
        """检查立方体与所有障碍物的碰撞"""
        for obstacle in self.obstacles:
            if obstacle.check_collision(cube.position, cube.size):
                # 处理碰撞
                new_pos, new_vel, normal = obstacle.get_collision_response(
                    cube.position, cube.velocity, cube.size)
                cube.position = new_pos
                cube.velocity = new_vel
                return True, obstacle
        return False, None
    
    def get_all_render_data(self):
        """获取所有障碍物的渲染数据"""
        return [obs.get_render_data() for obs in self.obstacles]
