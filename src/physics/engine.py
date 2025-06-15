import numpy as np
from typing import List, Tuple
from .cube import Cube
from .obstacles import ObstacleManager

class PhysicsEngine:
    """3D物理引擎，处理重力、碰撞检测和数值积分"""
    
    def __init__(self, gravity=9.81, air_resistance=0.01, bounds=None):
        """
        初始化物理引擎
        
        Args:
            gravity: 重力加速度
            air_resistance: 空气阻力系数
            bounds: 场景边界 [(xmin,xmax), (ymin,ymax), (zmin,zmax)]
        """
        self.gravity = gravity
        self.air_resistance = air_resistance
        
        # 默认场景边界
        if bounds is None:
            self.bounds = [(-10, 10), (-10, 10), (0, 20)]  # x, y, z (Z轴为高度)
        else:
            self.bounds = bounds
            
        self.dt = 0.016  # 时间步长 (60 FPS)
        self.collision_epsilon = 1e-6  # 碰撞检测精度
        
        # 障碍物管理器
        self.obstacle_manager = ObstacleManager()
        
    def add_obstacles(self, scene_type='basic'):
        """添加障碍物到场景"""
        self.obstacle_manager.create_scene_obstacles(scene_type)
        
    def get_obstacles_render_data(self):
        """获取障碍物渲染数据"""
        return self.obstacle_manager.get_all_render_data()
        
    def step(self, cubes: List[Cube]):
        """执行一个物理时间步长"""
        for cube in cubes:
            # 记录历史状态
            cube.add_to_history()
            
            # 计算所有作用力
            forces = self._calculate_forces(cube)
            torques = self._calculate_torques(cube)
            
            # 使用RK4方法进行数值积分
            self._integrate_rk4(cube, forces, torques)
            
            # 碰撞检测和响应
            self._handle_collisions(cube)
            
    def _calculate_forces(self, cube: Cube) -> np.ndarray:
        """计算作用在立方体上的所有力"""
        forces = np.zeros(3)
        
        # 重力 - 沿Z轴负方向（向下）
        gravity_force = np.array([0, 0, -self.gravity * cube.mass])
        forces += gravity_force
        
        # 空气阻力（与速度相反）
        if np.linalg.norm(cube.velocity) > 0:
            drag_force = -self.air_resistance * cube.velocity * np.linalg.norm(cube.velocity)
            forces += drag_force
            
        return forces
    
    def _calculate_torques(self, cube: Cube) -> np.ndarray:
        """计算作用在立方体上的所有力矩"""
        torques = np.zeros(3)
        
        # 空气阻力对旋转的影响
        angular_drag = -0.1 * cube.angular_velocity * np.linalg.norm(cube.angular_velocity)
        torques += angular_drag
        
        return torques
    
    def _integrate_rk4(self, cube: Cube, forces: np.ndarray, torques: np.ndarray):
        """使用四阶Runge-Kutta方法进行数值积分"""
        dt = self.dt
        
        # 当前状态
        pos = cube.position.copy()
        vel = cube.velocity.copy()
        rot = cube.rotation.copy()
        ang_vel = cube.angular_velocity.copy()
        
        # RK4 for 位置和速度
        k1_vel = forces / cube.mass
        k1_pos = vel
        
        k2_vel = forces / cube.mass  # 假设力在短时间内恒定
        k2_pos = vel + 0.5 * dt * k1_vel
        
        k3_vel = forces / cube.mass
        k3_pos = vel + 0.5 * dt * k2_vel
        
        k4_vel = forces / cube.mass
        k4_pos = vel + dt * k3_vel
        
        # 更新位置和速度
        cube.velocity += dt * (k1_vel + 2*k2_vel + 2*k3_vel + k4_vel) / 6
        cube.position += dt * (k1_pos + 2*k2_pos + 2*k3_pos + k4_pos) / 6
        
        # RK4 for 旋转（四元数积分）
        ang_acc = torques / cube.inertia
        
        # 简化的角速度积分
        cube.angular_velocity += dt * ang_acc
        
        # 四元数积分
        omega = np.linalg.norm(cube.angular_velocity)
        if omega > 1e-8:
            axis = cube.angular_velocity / omega
            dtheta = omega * dt
            
            # 旋转四元数
            dq = np.array([
                np.cos(dtheta/2),
                axis[0] * np.sin(dtheta/2),
                axis[1] * np.sin(dtheta/2),
                axis[2] * np.sin(dtheta/2)
            ])
            
            # 四元数乘法
            cube.rotation = self._quaternion_multiply(cube.rotation, dq)
            cube.rotation /= np.linalg.norm(cube.rotation)  # 归一化
    
    def _quaternion_multiply(self, q1, q2):
        """四元数乘法"""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
    
    def _handle_collisions(self, cube: Cube):
        """处理碰撞检测和响应"""
        # 获取立方体包围盒
        min_corner, max_corner = cube.get_bounding_box()
        
        # 检查与障碍物的碰撞
        self._handle_obstacle_collisions(cube, min_corner, max_corner)
        
        # 检查与场景边界的碰撞
        self._handle_boundary_collision(cube, min_corner, max_corner)
    
    def _handle_obstacle_collisions(self, cube: Cube, min_corner, max_corner):
        """处理与障碍物的碰撞"""
        for obstacle in self.obstacle_manager.obstacles:
            if obstacle.check_collision(cube.position, cube.size):
                # 使用障碍物的碰撞响应方法
                new_pos, new_vel, collision_normal = obstacle.get_collision_response(
                    cube.position, cube.velocity, cube.size)
                
                # 更新立方体状态
                cube.position = new_pos
                cube.velocity = new_vel
                
                # 添加旋转效果
                cube.angular_velocity += np.cross(collision_normal, cube.velocity) * 0.1
                
                # 能量损失
                cube.velocity *= 0.95
                cube.angular_velocity *= 0.9
        
    def _handle_boundary_collision(self, cube: Cube, min_corner: np.ndarray, max_corner: np.ndarray):
        """处理与场景边界的碰撞"""
        position_changed = False
        
        # X轴边界
        if min_corner[0] < self.bounds[0][0]:
            cube.position[0] += self.bounds[0][0] - min_corner[0]
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
            cube.angular_velocity[1] += cube.velocity[0] * 0.1  # 添加旋转
            position_changed = True
            
        elif max_corner[0] > self.bounds[0][1]:
            cube.position[0] += self.bounds[0][1] - max_corner[0]
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
            cube.angular_velocity[1] += cube.velocity[0] * 0.1
            position_changed = True
        
        # Y轴边界（水平方向）
        if min_corner[1] < self.bounds[1][0]:
            cube.position[1] += self.bounds[1][0] - min_corner[1]
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            cube.angular_velocity[2] += cube.velocity[1] * 0.1  # 添加旋转
            position_changed = True
            
        elif max_corner[1] > self.bounds[1][1]:
            cube.position[1] += self.bounds[1][1] - max_corner[1]
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            cube.angular_velocity[2] += cube.velocity[1] * 0.1
            position_changed = True

        # Z轴边界（地面和天花板）
        if min_corner[2] < self.bounds[2][0]:  # 地面碰撞
            cube.position[2] += self.bounds[2][0] - min_corner[2]
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
            
            # 地面摩擦力影响水平速度和旋转
            friction_force = cube.friction * abs(cube.velocity[2])
            if np.linalg.norm(cube.velocity[[0,1]]) > 0:
                friction_dir = -cube.velocity[[0,1]] / np.linalg.norm(cube.velocity[[0,1]])
                cube.velocity[[0,1]] += friction_force * friction_dir
                
            # 碰撞产生的旋转
            cube.angular_velocity[0] += cube.velocity[1] * 0.2
            cube.angular_velocity[1] += -cube.velocity[0] * 0.2
            
            position_changed = True
            
        elif max_corner[2] > self.bounds[2][1]:  # 天花板碰撞
            cube.position[2] += self.bounds[2][1] - max_corner[2]
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
            position_changed = True
            cube.position[2] += self.bounds[2][0] - min_corner[2]
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
            cube.angular_velocity[0] += cube.velocity[2] * 0.1
            position_changed = True
            
        elif max_corner[2] > self.bounds[2][1]:
            cube.position[2] += self.bounds[2][1] - max_corner[2]
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
            cube.angular_velocity[0] += cube.velocity[2] * 0.1
            position_changed = True
            
        # 速度衰减（模拟能量损失）
        if position_changed:
            cube.velocity *= 0.98
            cube.angular_velocity *= 0.95
    
    def get_total_energy(self, cubes: List[Cube]) -> float:
        """计算系统总能量"""
        total_energy = 0
        for cube in cubes:
            total_energy += cube.get_kinetic_energy()
            total_energy += cube.get_potential_energy(self.gravity)
        return total_energy
    
    def set_time_step(self, dt: float):
        """设置时间步长"""
        self.dt = dt
        
    def reset_cube(self, cube: Cube, position, velocity):
        """重置立方体状态"""
        cube.position = np.array(position, dtype=np.float64)
        cube.velocity = np.array(velocity, dtype=np.float64)
        cube.rotation = np.array([1.0, 0.0, 0.0, 0.0])
        cube.angular_velocity = np.array([0.0, 0.0, 0.0])
        cube.history.clear()

class Obstacle:
    """障碍物类"""
    def __init__(self, position, size, shape='box'):
        """
        初始化障碍物
        
        Args:
            position: [x, y, z] 位置
            size: [width, height, depth] 尺寸或半径
            shape: 'box', 'sphere', 'platform' 形状
        """
        self.position = np.array(position)
        self.size = np.array(size) if hasattr(size, '__len__') else np.array([size, size, size])
        self.shape = shape
        self.color = (0.7, 0.3, 0.1)  # 棕色
        
    def check_collision(self, cube):
        """检查与立方体的碰撞"""
        cube_pos = cube.position
        cube_half_size = cube.size / 2
        
        if self.shape == 'box':
            # 立方体障碍物碰撞检测
            obstacle_half_size = self.size / 2
            
            # AABB碰撞检测
            overlap_x = (abs(cube_pos[0] - self.position[0]) < (cube_half_size + obstacle_half_size[0]))
            overlap_y = (abs(cube_pos[1] - self.position[1]) < (cube_half_size + obstacle_half_size[1]))
            overlap_z = (abs(cube_pos[2] - self.position[2]) < (cube_half_size + obstacle_half_size[2]))
            
            return overlap_x and overlap_y and overlap_z
            
        elif self.shape == 'sphere':
            # 球形障碍物碰撞检测
            distance = np.linalg.norm(cube_pos - self.position)
            return distance < (cube_half_size + self.size[0])
            
        elif self.shape == 'platform':
            # 平台障碍物（只有顶面碰撞）
            platform_half_size = self.size / 2
            
            # 检查是否在平台上方
            if (abs(cube_pos[0] - self.position[0]) < platform_half_size[0] and
                abs(cube_pos[1] - self.position[1]) < platform_half_size[1]):
                
                # 检查Z方向碰撞（立方体底部接触平台顶部）
                cube_bottom = cube_pos[2] - cube_half_size
                platform_top = self.position[2] + platform_half_size[2]
                
                return cube_bottom <= platform_top and cube_pos[2] > self.position[2]
        
        return False
    
    def resolve_collision(self, cube):
        """解决碰撞，调整立方体位置和速度"""
        if not self.check_collision(cube):
            return False
            
        cube_half_size = cube.size / 2
        
        if self.shape == 'box':
            # 计算重叠距离
            dx = cube.position[0] - self.position[0]
            dy = cube.position[1] - self.position[1] 
            dz = cube.position[2] - self.position[2]
            
            obstacle_half_size = self.size / 2
            overlap_x = (cube_half_size + obstacle_half_size[0]) - abs(dx)
            overlap_y = (cube_half_size + obstacle_half_size[1]) - abs(dy)
            overlap_z = (cube_half_size + obstacle_half_size[2]) - abs(dz)
            
            # 从最小重叠方向分离
            if overlap_x <= overlap_y and overlap_x <= overlap_z:
                # X方向分离
                cube.position[0] += overlap_x * (1 if dx > 0 else -1)
                cube.velocity[0] = -cube.velocity[0] * cube.restitution
            elif overlap_y <= overlap_z:
                # Y方向分离
                cube.position[1] += overlap_y * (1 if dy > 0 else -1)
                cube.velocity[1] = -cube.velocity[1] * cube.restitution
            else:
                # Z方向分离
                cube.position[2] += overlap_z * (1 if dz > 0 else -1)
                cube.velocity[2] = -cube.velocity[2] * cube.restitution
                
        elif self.shape == 'sphere':
            # 球形碰撞处理
            direction = cube.position - self.position
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction = direction / distance
                separation = (cube_half_size + self.size[0]) - distance
                cube.position += direction * separation
                
                # 反射速度
                cube.velocity = cube.velocity - 2 * np.dot(cube.velocity, direction) * direction
                cube.velocity *= cube.restitution
                
        elif self.shape == 'platform':
            # 平台碰撞处理
            platform_half_size = self.size / 2
            platform_top = self.position[2] + platform_half_size[2]
            cube.position[2] = platform_top + cube_half_size
            
            if cube.velocity[2] < 0:  # 只有向下的速度才反弹
                cube.velocity[2] = -cube.velocity[2] * cube.restitution
                # 添加一些摩擦
                cube.velocity[0] *= 0.9
                cube.velocity[1] *= 0.9
        
        return True
