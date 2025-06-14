import numpy as np
from typing import List, Tuple
from .cube import Cube

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
            self.bounds = [(-10, 10), (0, 20), (-10, 10)]  # x, y, z
        else:
            self.bounds = bounds
            
        self.dt = 0.016  # 时间步长 (60 FPS)
        self.collision_epsilon = 1e-6  # 碰撞检测精度
        
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
        
        # 重力
        gravity_force = np.array([0, -self.gravity * cube.mass, 0])
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
        
        # 检查与场景边界的碰撞
        self._handle_boundary_collision(cube, min_corner, max_corner)
        
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
        
        # Y轴边界（地面）
        if min_corner[1] < self.bounds[1][0]:
            cube.position[1] += self.bounds[1][0] - min_corner[1]
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            
            # 地面摩擦力影响水平速度和旋转
            friction_force = cube.friction * abs(cube.velocity[1])
            if np.linalg.norm(cube.velocity[[0,2]]) > 0:
                friction_dir = -cube.velocity[[0,2]] / np.linalg.norm(cube.velocity[[0,2]])
                cube.velocity[[0,2]] += friction_force * friction_dir
                
            # 碰撞产生的旋转
            cube.angular_velocity[0] += cube.velocity[2] * 0.2
            cube.angular_velocity[2] += -cube.velocity[0] * 0.2
            
            position_changed = True
            
        elif max_corner[1] > self.bounds[1][1]:
            cube.position[1] += self.bounds[1][1] - max_corner[1]
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            position_changed = True
        
        # Z轴边界
        if min_corner[2] < self.bounds[2][0]:
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
