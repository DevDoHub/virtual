#!/usr/bin/env python3
"""
简化修复的物理演示 - 确保立方体停在地面
=============================================

重点解决:
1. 立方体最终Y位置 = cube_size/2 (在地面上)
2. 清晰的碰撞检测
3. 正确的物理行为

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

class SimplePhysicsEngine:
    """简化的物理引擎，确保正确的地面接触"""
    
    def __init__(self, gravity=9.81, bounds=None):
        self.gravity = gravity
        if bounds is None:
            self.bounds = [(-10, 10), (0, 20), (-10, 10)]
        else:
            self.bounds = bounds
        self.dt = 0.05  # 时间步长
        
    def step(self, cube):
        """简化的物理步进"""
        
        # 应用重力
        gravity_force = np.array([0, -self.gravity, 0])
        acceleration = gravity_force  # 质量=1，所以a=F
        
        # 更新速度和位置
        cube.velocity = cube.velocity + acceleration * self.dt
        cube.position = cube.position + cube.velocity * self.dt
        
        # 简单的空气阻力
        cube.velocity *= 0.999
        
        # 处理地面碰撞
        self.handle_ground_collision(cube)
        
        # 处理边界碰撞
        self.handle_boundary_collision(cube)
    
    def handle_ground_collision(self, cube):
        """处理地面碰撞"""
        
        # 立方体底部位置
        bottom_y = cube.position[1] - cube.size / 2
        ground_level = self.bounds[1][0]  # 地面高度
        
        if bottom_y <= ground_level:
            # 调整位置：立方体中心应该在地面 + size/2
            cube.position[1] = ground_level + cube.size / 2
            
            # 反弹速度
            if cube.velocity[1] < 0:  # 只有向下时才反弹
                cube.velocity[1] = -cube.velocity[1] * cube.restitution
                
                # 如果速度太小就停止
                if abs(cube.velocity[1]) < 0.3:
                    cube.velocity[1] = 0
                    
                print(f"Ground collision! Position Y: {cube.position[1]:.2f}, Bottom Y: {bottom_y:.2f}")
    
    def handle_boundary_collision(self, cube):
        """处理边界碰撞"""
        half_size = cube.size / 2
        
        # X边界
        if cube.position[0] - half_size < self.bounds[0][0]:
            cube.position[0] = self.bounds[0][0] + half_size
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
        elif cube.position[0] + half_size > self.bounds[0][1]:
            cube.position[0] = self.bounds[0][1] - half_size
            cube.velocity[0] = -cube.velocity[0] * cube.restitution
            
        # Z边界
        if cube.position[2] - half_size < self.bounds[2][0]:
            cube.position[2] = self.bounds[2][0] + half_size
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
        elif cube.position[2] + half_size > self.bounds[2][1]:
            cube.position[2] = self.bounds[2][1] - half_size
            cube.velocity[2] = -cube.velocity[2] * cube.restitution

def create_simple_demo():
    """创建简化的物理演示"""
    
    print("Simple Fixed Physics Demo")
    print("=" * 40)
    
    # 设置
    bounds = [(-5, 5), (0, 12), (-5, 5)]  # Y=0是地面
    engine = SimplePhysicsEngine(gravity=9.81, bounds=bounds)
    
    cube_size = 2.0
    start_height = 8.0
    
    cube = Cube(
        position=[0, start_height, 0],
        velocity=[0, 0, 0],
        size=cube_size,
        mass=1.0
    )
    cube.restitution = 0.6
    
    print(f"Cube size: {cube_size}m")
    print(f"Start height: {start_height}m")
    print(f"Expected final Y: {cube_size/2:.1f}m (center when on ground)")
    print(f"Ground level: {bounds[1][0]}m")
    
    # 仿真
    dt = engine.dt
    duration = 6.0
    steps = int(duration / dt)
    
    print(f"Running {steps} steps...")
    
    positions = []
    velocities = []
    collision_count = 0
    
    for step in range(steps):
        time = step * dt
        
        # 记录状态
        positions.append(cube.position.copy())
        velocities.append(cube.velocity.copy())
        
        # 检测碰撞
        pre_speed = np.linalg.norm(cube.velocity)
        
        # 物理更新
        engine.step(cube)
        
        post_speed = np.linalg.norm(cube.velocity)
        
        if abs(post_speed - pre_speed) > 1.0:
            collision_count += 1
        
        # 进度
        if step % 20 == 0:
            print(f"  t={time:.1f}s: Y={cube.position[1]:.2f}m, speed={np.linalg.norm(cube.velocity):.2f}m/s")
        
        # 停止条件
        if np.linalg.norm(cube.velocity) < 0.05 and abs(cube.position[1] - cube_size/2) < 0.1:
            print(f"  Cube settled at t={time:.1f}s")
            break
    
    # 验证结果
    expected_y = cube_size / 2
    actual_y = cube.position[1]
    error = abs(actual_y - expected_y)
    
    print(f"\\nFinal Results:")
    print(f"Expected Y: {expected_y:.2f}m")
    print(f"Actual Y: {actual_y:.2f}m") 
    print(f"Error: {error:.3f}m")
    print(f"Final speed: {np.linalg.norm(cube.velocity):.3f}m/s")
    print(f"Collisions: {collision_count}")
    
    if error < 0.1:
        print("✅ SUCCESS: Cube correctly on ground!")
    else:
        print("❌ ERROR: Cube not properly positioned")
    
    # 生成视频
    print("\\nGenerating video...")
    frames = []
    
    for i in range(0, len(positions), 4):  # 每4帧取1帧
        time = i * dt
        cube.position = positions[i]
        cube.velocity = velocities[i]
        
        frame = create_frame(cube, time, positions[:i+1], bounds, cube_size)
        frames.append(frame)
    
    # 保存
    output_path = "/root/virtual/output/videos/simple_fixed_demo.mp4"
    success = save_video(frames, output_path)
    
    if success:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video failed")
        return None

def create_frame(cube, time, trajectory, bounds, cube_size):
    """创建视频帧"""
    
    fig = plt.figure(figsize=(10, 8), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 视角
    ax.view_init(elev=20, azim=45)
    
    # 范围
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 标签
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    
    # 网格
    ax.grid(True, alpha=0.3)
    
    # 地面
    x_range = bounds[0]
    z_range = bounds[2]
    ground_x = [x_range[0], x_range[1], x_range[1], x_range[0]]
    ground_z = [z_range[0], z_range[0], z_range[1], z_range[1]]
    ground_y = [0, 0, 0, 0]
    
    ground_verts = [list(zip(ground_x, ground_y, ground_z))]
    ax.add_collection3d(Poly3DCollection(ground_verts, alpha=0.4, facecolor='gray'))
    
    # 目标高度线
    target_y = cube_size / 2
    ax.plot([x_range[0], x_range[1]], [target_y, target_y], [0, 0], 
           'r--', linewidth=2, label=f'Target height ({target_y:.1f}m)')
    
    # 立方体
    corners = cube.get_corners()
    bottom_y = np.min(corners[:, 1])
    
    # 根据位置选择颜色
    if abs(cube.position[1] - target_y) < 0.1 and np.linalg.norm(cube.velocity) < 0.1:
        color = 'lightgreen'  # 正确位置
        status = "ON GROUND ✅"
    elif bottom_y < 0.5:
        color = 'orange'  # 接近地面
        status = "LANDING..."
    else:
        color = 'lightblue'  # 下落中
        status = "FALLING"
    
    # 绘制立方体面
    faces = [
        [corners[0], corners[1], corners[2], corners[3]],
        [corners[4], corners[5], corners[6], corners[7]], 
        [corners[0], corners[1], corners[5], corners[4]],
        [corners[2], corners[3], corners[7], corners[6]],
        [corners[1], corners[2], corners[6], corners[5]],
        [corners[0], corners[3], corners[7], corners[4]]
    ]
    
    for face in faces:
        poly = [face]
        ax.add_collection3d(Poly3DCollection(poly, alpha=0.7, facecolor=color, edgecolor='black'))
    
    # 轨迹
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'blue', linewidth=2, alpha=0.6)
    
    # 信息
    speed = np.linalg.norm(cube.velocity)
    error = abs(cube.position[1] - target_y)
    
    info = f"""Fixed Physics Demo
Time: {time:.1f}s
Position Y: {cube.position[1]:.2f}m
Target Y: {target_y:.1f}m
Error: {error:.3f}m
Speed: {speed:.2f}m/s
Status: {status}"""
    
    ax.text2D(0.02, 0.98, info, transform=ax.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    ax.legend()
    plt.tight_layout()
    
    # 转换
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    buf = buf[:, :, :3]
    
    plt.close(fig)
    return buf

def save_video(frames, output_path):
    """保存视频"""
    try:
        if not frames:
            return False
        
        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 15.0, (width, height))
        
        if not out.isOpened():
            return False
        
        for frame in frames:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        return True
        
    except Exception as e:
        print(f"Save error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = create_simple_demo()
        if result:
            print("\\n🎉 Fixed demo successful!")
            print("Now the cube properly lands on the ground!")
        else:
            print("\\n❌ Demo failed")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
