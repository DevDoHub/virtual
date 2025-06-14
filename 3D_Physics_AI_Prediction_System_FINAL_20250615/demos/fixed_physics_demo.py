#!/usr/bin/env python3
"""
修复的物理演示 - 确保立方体正确停在地面
============================================

修复问题:
1. 立方体最终位置应该在地面上 (Y = cube_size/2)
2. 当速度很小时应该停止运动
3. 清晰的碰撞效果
4. 正确的能量耗散

作者: GitHub Copilot
日期: 2025年6月15日
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cv2
import os
import sys
sys.path.append('/root/virtual')

from src.physics.cube import Cube
from src.physics.engine import PhysicsEngine

class FixedPhysicsEngine(PhysicsEngine):
    """修复的物理引擎，确保正确的地面碰撞"""
    
    def __init__(self, gravity=9.81, bounds=None):
        super().__init__(gravity, bounds)
        self.min_velocity_threshold = 0.1  # 最小速度阈值
        self.energy_damping = 0.99  # 能量耗散
    
    def step(self, cubes):
        """改进的物理步进"""
        for cube in cubes:
            # 应用重力和空气阻力
            forces = self._calculate_forces(cube)
            torques = self._calculate_torques(cube)
            
            # RK4积分
            self._integrate_rk4(cube, forces, torques)
            
            # 改进的碰撞处理
            self._handle_collisions_fixed(cube)
            
            # 能量耗散和静止检测
            self._apply_energy_damping(cube)
            
            # 更新历史
            cube.add_to_history()
    
    def _handle_collisions_fixed(self, cube):
        """修复的碰撞检测"""
        
        # 计算立方体的实际边界
        half_size = cube.size / 2
        
        # 地面碰撞检测 - 立方体底部
        bottom_y = cube.position[1] - half_size
        
        if bottom_y <= self.bounds[1][0]:  # 碰撞到地面
            # 调整位置：立方体中心应该在 ground + half_size
            cube.position[1] = self.bounds[1][0] + half_size
            
            # 速度反弹
            if cube.velocity[1] < 0:  # 只有向下运动时才反弹
                cube.velocity[1] = -cube.velocity[1] * cube.restitution
                
                # 如果反弹速度太小，就停止
                if abs(cube.velocity[1]) < 0.5:
                    cube.velocity[1] = 0
                
                print(f"Ground collision! New position Y: {cube.position[1]:.2f}, velocity Y: {cube.velocity[1]:.2f}")
        
        # X轴边界
        left_x = cube.position[0] - half_size
        right_x = cube.position[0] + half_size
        
        if left_x <= self.bounds[0][0]:
            cube.position[0] = self.bounds[0][0] + half_size
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
        elif right_x >= self.bounds[0][1]:
            cube.position[0] = self.bounds[0][1] - half_size
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
        
        # Z轴边界
        front_z = cube.position[2] - half_size
        back_z = cube.position[2] + half_size
        
        if front_z <= self.bounds[2][0]:
            cube.position[2] = self.bounds[2][0] + half_size
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
        elif back_z >= self.bounds[2][1]:
            cube.position[2] = self.bounds[2][1] - half_size
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
    
    def _apply_energy_damping(self, cube):
        """应用能量耗散和静止检测"""
        
        # 速度阻尼
        cube.velocity *= self.energy_damping
        cube.angular_velocity *= self.energy_damping
        
        # 静止检测
        speed = np.linalg.norm(cube.velocity)
        angular_speed = np.linalg.norm(cube.angular_velocity)
        
        if speed < self.min_velocity_threshold:
            cube.velocity *= 0
            print(f"Cube stopped due to low velocity. Final position: {cube.position}")
            
        if angular_speed < self.min_velocity_threshold:
            cube.angular_velocity *= 0

def create_fixed_demo():
    """创建修复的物理演示"""
    
    print("Fixed Physics Demo - Proper Ground Landing")
    print("=" * 50)
    
    # 物理环境
    bounds = [(-6, 6), (0, 15), (-6, 6)]  # Y轴从0开始（地面）
    engine = FixedPhysicsEngine(gravity=9.81, bounds=bounds)
    
    # 立方体设置
    cube_size = 2.0  # 2米立方体
    initial_height = 10.0  # 从10米高度开始
    
    cube = Cube(
        position=[0, initial_height, 0],
        velocity=[0, 0, 0],  # 静止开始
        size=cube_size,
        mass=1.0
    )
    cube.restitution = 0.6  # 适中的弹性
    
    print(f"Cube size: {cube_size}m")
    print(f"Initial height: {initial_height}m") 
    print(f"Expected final Y position: {cube_size/2}m (center) when on ground")
    print(f"Ground level: {bounds[1][0]}m")
    
    # 仿真参数
    fps = 20
    duration = 8.0
    dt = 1.0 / fps
    total_steps = int(duration / dt)
    
    print(f"Simulation: {fps}fps, {duration}s, {total_steps} steps")
    
    # 运行仿真
    print("Running simulation...")
    positions = []
    velocities = []
    collision_count = 0
    
    for step in range(total_steps):
        current_time = step * dt
        
        # 记录状态
        positions.append(cube.position.copy())
        velocities.append(cube.velocity.copy())
        
        # 检测碰撞
        pre_speed = np.linalg.norm(cube.velocity)
        
        # 物理步进
        engine.step([cube])
        
        post_speed = np.linalg.norm(cube.velocity)
        
        # 显著速度变化表示碰撞
        if abs(post_speed - pre_speed) > 1.0:
            collision_count += 1
            print(f"  Collision {collision_count} at t={current_time:.1f}s, Y={cube.position[1]:.2f}m")
        
        # 进度报告
        if step % 20 == 0:
            print(f"  t={current_time:.1f}s: Y={cube.position[1]:.2f}m, speed={np.linalg.norm(cube.velocity):.2f}m/s")
        
        # 如果立方体停止且在地面上，提前结束
        if np.linalg.norm(cube.velocity) < 0.01 and cube.position[1] <= cube_size/2 + 0.1:
            print(f"  Cube settled at t={current_time:.1f}s")
            break
    
    print(f"Simulation complete!")
    print(f"Final position: Y={cube.position[1]:.2f}m (should be ~{cube_size/2:.1f}m)")
    print(f"Final velocity: {np.linalg.norm(cube.velocity):.3f}m/s")
    print(f"Collisions detected: {collision_count}")
    
    # 验证最终位置
    expected_y = cube_size / 2
    actual_y = cube.position[1]
    error = abs(actual_y - expected_y)
    
    if error < 0.1:
        print(f"✅ CORRECT: Cube is properly on ground (error: {error:.3f}m)")
    else:
        print(f"❌ ERROR: Cube not on ground (error: {error:.3f}m)")
    
    # 生成视频
    print("Generating video...")
    frames = []
    
    for step in range(0, len(positions), 3):  # 每3帧取1帧
        current_time = step * dt
        cube.position = positions[step]
        cube.velocity = velocities[step]
        
        frame = create_fixed_frame(cube, current_time, positions[:step+1], bounds, cube_size)
        frames.append(frame)
    
    # 保存视频
    output_path = "/root/virtual/output/videos/fixed_physics_demo.mp4"
    success = save_video(frames, output_path)
    
    if success:
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video saved: {output_path} ({file_size:.1f} MB)")
        return output_path
    else:
        print("❌ Video save failed")
        return None

def create_fixed_frame(cube, time, trajectory, bounds, cube_size):
    """创建修复的视频帧"""
    
    fig = plt.figure(figsize=(12, 9), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 固定视角
    ax.view_init(elev=20, azim=45)
    
    # 设置范围
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 标签
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_zlabel('Z (m)', fontsize=12)
    
    # 网格
    ax.grid(True, alpha=0.3)
    
    # 绘制地面平面 - 在Y=0处
    x_ground = np.array([bounds[0][0], bounds[0][1], bounds[0][1], bounds[0][0]])
    z_ground = np.array([bounds[2][0], bounds[2][0], bounds[2][1], bounds[2][1]])
    y_ground = np.zeros(4)
    
    ground_verts = [list(zip(x_ground, y_ground, z_ground))]
    ax.add_collection3d(Poly3DCollection(ground_verts, alpha=0.5, facecolor='lightgray', edgecolor='black'))
    
    # 绘制理论地面线（立方体中心应在的高度）
    expected_y = cube_size / 2
    ax.plot([bounds[0][0], bounds[0][1]], [expected_y, expected_y], [0, 0], 
           'r--', linewidth=2, alpha=0.7, label=f'Expected center height ({expected_y:.1f}m)')
    
    # 绘制立方体
    draw_cube_with_check(ax, cube, cube_size)
    
    # 轨迹
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               'blue', linewidth=2, alpha=0.8, label='Trajectory')
    
    # 信息
    speed = np.linalg.norm(cube.velocity)
    expected_y = cube_size / 2
    position_error = abs(cube.position[1] - expected_y)
    
    info = f"""Fixed Physics Demo
Time: {time:.1f}s
Position: ({cube.position[0]:.1f}, {cube.position[1]:.2f}, {cube.position[2]:.1f})m
Speed: {speed:.2f} m/s
Expected Y: {expected_y:.1f}m
Position Error: {position_error:.3f}m"""
    
    # 根据位置误差改变颜色
    if position_error < 0.1 and speed < 0.1:
        bg_color = 'lightgreen'  # 正确停在地面
        info += "\n✅ CORRECTLY ON GROUND"
    elif cube.position[1] < expected_y + 0.5:
        bg_color = 'lightyellow'  # 接近地面
        info += "\n⚡ APPROACHING GROUND"
    else:
        bg_color = 'lightblue'  # 还在空中
        info += "\n🔄 FALLING"
    
    ax.text2D(0.02, 0.98, info, transform=ax.transAxes,
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.9))
    
    ax.legend(loc='upper right')
    plt.tight_layout()
    
    # 转换
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    buf = buf[:, :, :3]
    
    plt.close(fig)
    return buf

def draw_cube_with_check(ax, cube, cube_size):
    """绘制立方体并检查位置"""
    
    corners = cube.get_corners()
    
    # 检查底部是否接触地面
    min_y = np.min(corners[:, 1])
    expected_min_y = 0  # 地面高度
    
    # 根据是否正确接触地面选择颜色
    if abs(min_y - expected_min_y) < 0.1:
        cube_color = 'lightgreen'  # 正确在地面
    elif min_y < 1.0:
        cube_color = 'orange'  # 接近地面
    else:
        cube_color = 'lightblue'  # 还在空中
    
    # 定义6个面
    faces = [
        [corners[0], corners[1], corners[2], corners[3]],  # bottom
        [corners[4], corners[5], corners[6], corners[7]],  # top
        [corners[0], corners[1], corners[5], corners[4]],  # front
        [corners[2], corners[3], corners[7], corners[6]],  # back
        [corners[1], corners[2], corners[6], corners[5]],  # right
        [corners[0], corners[3], corners[7], corners[4]]   # left
    ]
    
    # 绘制面
    for face in faces:
        poly = [face]
        ax.add_collection3d(Poly3DCollection(poly, alpha=0.7, 
                                           facecolor=cube_color, edgecolor='black', linewidth=1))

def save_video(frames, output_path):
    """保存视频"""
    try:
        if not frames:
            return False
        
        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 10.0, (width, height))
        
        if not out.isOpened():
            return False
        
        for frame in frames:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        return True
        
    except Exception as e:
        print(f"Video save error: {e}")
        return False

if __name__ == "__main__":
    try:
        output_path = create_fixed_demo()
        if output_path:
            print(f"\n🎉 Fixed demo complete!")
            print("Key improvements:")
            print("- Cube correctly stops on ground (Y = size/2)")
            print("- Proper collision detection")
            print("- Energy damping prevents floating")
            print("- Visual verification of position")
        else:
            print("\n❌ Demo failed")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
