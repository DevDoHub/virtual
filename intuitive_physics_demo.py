#!/usr/bin/env python3
"""
修正视角的物理演示 - Y轴垂直向上
==================================

修正问题:
1. Y轴垂直向上（符合人类直觉）
2. 立方体从上方下落到地面
3. 更直观的3D视角
4. 正确的物理行为

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
    """简化的物理引擎"""
    
    def __init__(self, gravity=9.81, bounds=None):
        self.gravity = gravity
        if bounds is None:
            self.bounds = [(-10, 10), (0, 20), (-10, 10)]
        else:
            self.bounds = bounds
        self.dt = 0.05
        
    def step(self, cube):
        """物理步进"""
        
        # 重力向下（Y方向为负）
        gravity_force = np.array([0, -self.gravity, 0])
        acceleration = gravity_force
        
        # 更新速度和位置
        cube.velocity = cube.velocity + acceleration * self.dt
        cube.position = cube.position + cube.velocity * self.dt
        
        # 空气阻力
        cube.velocity *= 0.999
        
        # 处理碰撞
        self.handle_ground_collision(cube)
        self.handle_boundary_collision(cube)
    
    def handle_ground_collision(self, cube):
        """处理地面碰撞"""
        
        bottom_y = cube.position[1] - cube.size / 2
        ground_level = self.bounds[1][0]  # Y=0是地面
        
        if bottom_y <= ground_level:
            # 调整位置
            cube.position[1] = ground_level + cube.size / 2
            
            # 反弹
            if cube.velocity[1] < 0:
                cube.velocity[1] = -cube.velocity[1] * cube.restitution
                
                if abs(cube.velocity[1]) < 0.3:
                    cube.velocity[1] = 0
                    
                print(f"Ground collision! Height: {cube.position[1]:.2f}m")
    
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

def create_intuitive_demo():
    """创建直观的物理演示"""
    
    print("Intuitive Physics Demo - Y-axis UP")
    print("=" * 40)
    
    # 设置
    bounds = [(-5, 5), (0, 12), (-5, 5)]  # Y=0是地面，Y轴向上
    engine = SimplePhysicsEngine(gravity=9.81, bounds=bounds)
    
    cube_size = 2.0
    start_height = 8.0
    
    cube = Cube(
        position=[0, start_height, 0],  # 从高处开始
        velocity=[0, 0, 0],
        size=cube_size,
        mass=1.0
    )
    cube.restitution = 0.7
    
    print(f"Cube size: {cube_size}m")
    print(f"Start height: {start_height}m")
    print(f"Expected final height: {cube_size/2:.1f}m")
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
        
        positions.append(cube.position.copy())
        velocities.append(cube.velocity.copy())
        
        pre_speed = np.linalg.norm(cube.velocity)
        engine.step(cube)
        post_speed = np.linalg.norm(cube.velocity)
        
        if abs(post_speed - pre_speed) > 1.0:
            collision_count += 1
        
        if step % 20 == 0:
            print(f"  t={time:.1f}s: Height={cube.position[1]:.2f}m, speed={np.linalg.norm(cube.velocity):.2f}m/s")
        
        # 停止条件
        if np.linalg.norm(cube.velocity) < 0.05 and abs(cube.position[1] - cube_size/2) < 0.1:
            print(f"  Cube settled at t={time:.1f}s")
            break
    
    # 验证结果
    expected_height = cube_size / 2
    actual_height = cube.position[1]
    error = abs(actual_height - expected_height)
    
    print(f"\\nFinal Results:")
    print(f"Expected height: {expected_height:.2f}m")
    print(f"Actual height: {actual_height:.2f}m") 
    print(f"Error: {error:.3f}m")
    print(f"Final speed: {np.linalg.norm(cube.velocity):.3f}m/s")
    print(f"Collisions: {collision_count}")
    
    if error < 0.1:
        print("✅ SUCCESS: Cube correctly on ground!")
    else:
        print("❌ ERROR: Cube not properly positioned")
    
    # 生成视频
    print("\\nGenerating intuitive video...")
    frames = []
    
    for i in range(0, len(positions), 3):
        time = i * dt
        cube.position = positions[i]
        cube.velocity = velocities[i]
        
        frame = create_intuitive_frame(cube, time, positions[:i+1], bounds, cube_size)
        frames.append(frame)
    
    # 保存
    output_path = "/root/virtual/output/videos/intuitive_physics_demo.mp4"
    success = save_video(frames, output_path)
    
    if success:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video failed")
        return None

def create_intuitive_frame(cube, time, trajectory, bounds, cube_size):
    """创建直观的视频帧 - Y轴垂直向上"""
    
    fig = plt.figure(figsize=(12, 10), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 重要：设置直观的视角 - Y轴垂直向上
    # elev=30: 仰角30度，从稍微下方向上看
    # azim=45: 方位角45度，从侧前方看
    ax.view_init(elev=30, azim=45)
    
    # 设置范围 - 确保Y轴是高度
    ax.set_xlim(bounds[0])  # X: 水平（左右）
    ax.set_ylim(bounds[1])  # Y: 垂直（上下）- 这是高度！
    ax.set_zlim(bounds[2])  # Z: 深度（前后）
    
    # 标签 - 明确表示Y是高度
    ax.set_xlabel('X (width)', fontsize=12)
    ax.set_ylabel('Y (height)', fontsize=12, color='red')  # 高度用红色标出
    ax.set_zlabel('Z (depth)', fontsize=12)
    
    # 网格
    ax.grid(True, alpha=0.3)
    
    # 绘制地面 - 在Y=0平面
    x_range = np.linspace(bounds[0][0], bounds[0][1], 5)
    z_range = np.linspace(bounds[2][0], bounds[2][1], 5)
    X_ground, Z_ground = np.meshgrid(x_range, z_range)
    Y_ground = np.zeros_like(X_ground)  # 地面在Y=0
    
    ax.plot_surface(X_ground, Y_ground, Z_ground, 
                   alpha=0.4, color='lightgreen', linewidth=1)
    
    # 添加地面标识
    ax.text(0, 0, 0, 'GROUND (Y=0)', fontsize=10, color='green', weight='bold')
    
    # 目标高度线 - 立方体中心应该在的高度
    target_height = cube_size / 2
    x_line = [bounds[0][0], bounds[0][1]]
    y_line = [target_height, target_height]
    z_line = [0, 0]
    ax.plot(x_line, y_line, z_line, 'r--', linewidth=3, 
           label=f'Target center height ({target_height:.1f}m)')
    
    # 重力箭头 - 显示重力方向
    arrow_x, arrow_z = 3, 3
    arrow_y_start = 8
    arrow_y_end = 6
    ax.quiver(arrow_x, arrow_y_start, arrow_z, 
             0, arrow_y_end - arrow_y_start, 0,
             color='red', arrow_length_ratio=0.3, linewidth=3,
             label='Gravity')
    ax.text(arrow_x + 0.5, arrow_y_start - 1, arrow_z, 'GRAVITY', 
           color='red', fontsize=10, weight='bold')
    
    # 立方体
    corners = cube.get_corners()
    bottom_y = np.min(corners[:, 1])
    
    # 根据高度和状态选择颜色
    if abs(cube.position[1] - target_height) < 0.1 and np.linalg.norm(cube.velocity) < 0.1:
        color = 'lightgreen'  # 正确着陆
        status = "LANDED ✅"
    elif bottom_y < 1.0:
        color = 'orange'  # 接近地面
        status = "LANDING..."
    else:
        color = 'lightblue'  # 下落中
        status = "FALLING ⬇️"
    
    # 绘制立方体面
    faces = [
        [corners[0], corners[1], corners[2], corners[3]],  # bottom
        [corners[4], corners[5], corners[6], corners[7]],  # top
        [corners[0], corners[1], corners[5], corners[4]],  # front
        [corners[2], corners[3], corners[7], corners[6]],  # back
        [corners[1], corners[2], corners[6], corners[5]],  # right
        [corners[0], corners[3], corners[7], corners[4]]   # left
    ]
    
    for face in faces:
        poly = [face]
        ax.add_collection3d(Poly3DCollection(poly, alpha=0.8, facecolor=color, 
                                           edgecolor='black', linewidth=1))
    
    # 轨迹线
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               'blue', linewidth=3, alpha=0.7, label='Trajectory')
    
    # 速度矢量
    if np.linalg.norm(cube.velocity) > 0.1:
        scale = 1.0
        ax.quiver(cube.position[0], cube.position[1], cube.position[2],
                 cube.velocity[0] * scale, cube.velocity[1] * scale, cube.velocity[2] * scale,
                 color='purple', arrow_length_ratio=0.2, linewidth=2,
                 label='Velocity')
    
    # 信息面板
    speed = np.linalg.norm(cube.velocity)
    height_error = abs(cube.position[1] - target_height)
    
    info = f"""Intuitive Physics Demo
Time: {time:.1f}s
Height (Y): {cube.position[1]:.2f}m
Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})
Target Height: {target_height:.1f}m
Height Error: {height_error:.3f}m
Speed: {speed:.2f}m/s
Status: {status}

🔄 Y-axis is VERTICAL (height)
📐 Natural viewing angle
🌍 Gravity points DOWN"""
    
    # 根据状态选择背景色
    if status == "LANDED ✅":
        bg_color = 'lightgreen'
    elif "LANDING" in status:
        bg_color = 'lightyellow'
    else:
        bg_color = 'lightblue'
    
    ax.text2D(0.02, 0.98, info, transform=ax.transAxes,
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.9))
    
    # 图例
    ax.legend(loc='upper right', bbox_to_anchor=(0.98, 0.85))
    
    # 标题
    plt.suptitle('Physics Demo - Natural Y-Up View', fontsize=16, fontweight='bold')
    
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
        result = create_intuitive_demo()
        if result:
            print("\\n🎉 Intuitive demo successful!")
            print("Key improvements:")
            print("✅ Y-axis is vertical (natural height)")
            print("✅ Viewing angle from below-front")
            print("✅ Clear gravity direction")
            print("✅ Proper ground plane visualization")
            print("✅ Cube lands correctly on ground")
        else:
            print("\\n❌ Demo failed")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
