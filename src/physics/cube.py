import numpy as np
import torch

class Cube:
    """3D立方体对象，包含完整的物理状态
    
    坐标系统：
    - X-Y平面：水平地面
    - Z轴：垂直方向（高度）
    - 重力：沿Z轴负方向
    """
    
    def __init__(self, position, velocity, size=1.0, mass=1.0, color=None):
        """
        初始化立方体
        
        Args:
            position: [x, y, z] 位置，z为高度
            velocity: [vx, vy, vz] 速度，vz为垂直速度
            size: 立方体边长
            mass: 质量
            color: RGB颜色元组
        """
        # 位置和速度 - Z轴为垂直方向
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        
        # 旋转状态（用四元数表示，避免万向锁）
        self.rotation = np.array([1.0, 0.0, 0.0, 0.0])  # [w, x, y, z]
        self.angular_velocity = np.array([0.0, 0.0, 0.0])  # 角速度
        
        # 物理属性
        self.size = size
        self.mass = mass
        self.inertia = mass * size**2 / 6.0  # 立方体转动惯量
        
        # 材质属性
        self.restitution = 0.7  # 弹性恢复系数
        self.friction = 0.3     # 摩擦系数
        
        # 渲染属性
        self.color = color if color else (1.0, 0.0, 0.0)  # 默认红色
        
        # 历史记录（用于AI训练）
        self.history = []
        
    def get_state_vector(self):
        """获取完整状态向量 [x,y,z,vx,vy,vz,qw,qx,qy,qz,wx,wy,wz]"""
        return np.concatenate([
            self.position,
            self.velocity, 
            self.rotation,
            self.angular_velocity
        ])
    
    def set_state_vector(self, state):
        """从状态向量设置立方体状态"""
        self.position = state[:3].copy()
        self.velocity = state[3:6].copy()
        self.rotation = state[6:10].copy()
        self.angular_velocity = state[10:13].copy()
        
        # 归一化四元数
        self.rotation /= np.linalg.norm(self.rotation)
    
    def get_corners(self):
        """获取立方体8个顶点的世界坐标"""
        half_size = self.size / 2
        # 本地坐标系中的8个顶点
        local_corners = np.array([
            [-half_size, -half_size, -half_size],
            [+half_size, -half_size, -half_size],
            [+half_size, +half_size, -half_size],
            [-half_size, +half_size, -half_size],
            [-half_size, -half_size, +half_size],
            [+half_size, -half_size, +half_size],
            [+half_size, +half_size, +half_size],
            [-half_size, +half_size, +half_size],
        ])
        
        # 应用旋转
        rotated_corners = self._rotate_points(local_corners, self.rotation)
        
        # 应用平移
        world_corners = rotated_corners + self.position
        
        return world_corners
    
    def _rotate_points(self, points, quaternion):
        """使用四元数旋转点集"""
        w, x, y, z = quaternion
        
        # 四元数旋转矩阵
        rotation_matrix = np.array([
            [1-2*(y**2+z**2), 2*(x*y-w*z), 2*(x*z+w*y)],
            [2*(x*y+w*z), 1-2*(x**2+z**2), 2*(y*z-w*x)],
            [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x**2+y**2)]
        ])
        
        return np.dot(points, rotation_matrix.T)
    
    def get_bounding_box(self):
        """获取轴对齐包围盒 AABB"""
        corners = self.get_corners()
        min_corner = np.min(corners, axis=0)
        max_corner = np.max(corners, axis=0)
        return min_corner, max_corner
    
    def add_to_history(self):
        """将当前状态添加到历史记录"""
        self.history.append(self.get_state_vector().copy())
        
        # 只保留最近100帧
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_kinetic_energy(self):
        """计算动能"""
        linear_ke = 0.5 * self.mass * np.dot(self.velocity, self.velocity)
        angular_ke = 0.5 * self.inertia * np.dot(self.angular_velocity, self.angular_velocity)
        return linear_ke + angular_ke
    
    def get_potential_energy(self, gravity=9.81):
        """计算重力势能"""
        return self.mass * gravity * self.position[2]  # Z轴为高度
    
    def __repr__(self):
        return f"Cube(pos={self.position}, vel={self.velocity}, size={self.size})"
