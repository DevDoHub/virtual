#!/usr/bin/env python3
"""
简化的清晰视频生成器 - 快速生成单个演示
=============================================

解决问题:
1. 固定摄像机视角
2. 大立方体尺寸
3. 清晰的下落和碰撞过程
4. 英文界面避免字体问题

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

def create_simple_demo():
    """创建简单清晰的物理演示"""
    
    print("Creating Simple Clear Physics Demo")
    print("=" * 50)
    
    # 创建物理环境 - 简单设置
    bounds = [(-6, 6), (0, 15), (-6, 6)]
    engine = PhysicsEngine(gravity=9.81, bounds=bounds)
    
    # 创建大立方体
    cube = Cube(
        position=[0, 12, 0],      # 从12米高度开始
        velocity=[0, 0, 0],       # 静止开始，纯下落
        size=3.0,                 # 3米大立方体，非常明显
        mass=1.0
    )
    cube.restitution = 0.7  # 适中弹性
    
    print(f"Cube: pos={cube.position}, size={cube.size}m")
    print(f"Physics: gravity={engine.gravity}, restitution={cube.restitution}")
    
    # 仿真参数
    fps = 30
    duration = 6.0
    dt = 1.0 / fps
    total_steps = int(duration / dt)
    
    print(f"Simulation: {fps}fps, {duration}s, {total_steps} steps")
    
    # 执行仿真
    print("Running simulation...")
    positions = []
    collision_count = 0
    
    for step in range(total_steps):
        current_time = step * dt
        
        # 记录碰撞前速度
        pre_vel = np.linalg.norm(cube.velocity)
        
        # 物理步进
        engine.step([cube])
        
        # 检测碰撞
        post_vel = np.linalg.norm(cube.velocity)
        if abs(post_vel - pre_vel) > 2.0:  # 速度显著变化
            collision_count += 1
            print(f"  Collision {collision_count} at t={current_time:.1f}s")
        
        # 记录位置
        positions.append(cube.position.copy())
        
        if step % 30 == 0:
            print(f"  Progress: {step/total_steps*100:.0f}%")
    
    print(f"Simulation complete! {collision_count} collisions detected")
    
    # 生成视频帧
    print("Generating video frames...")
    frames = []
    
    for step in range(0, total_steps, 2):  # 每2帧取1帧
        current_time = step * dt
        cube.position = positions[step]
        
        # 创建帧
        frame = create_simple_frame(cube, current_time, positions[:step+1], bounds)
        frames.append(frame)
        
        if step % 30 == 0:
            print(f"  Frame progress: {step/total_steps*100:.0f}%")
    
    # 保存视频
    output_path = "/root/virtual/output/videos/simple_clear_demo.mp4"
    print(f"Saving video to {output_path}...")
    
    success = save_simple_video(frames, output_path)
    
    if success:
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"SUCCESS! Video saved: {file_size:.1f} MB")
        return output_path
    else:
        print("FAILED to save video")
        return None

def create_simple_frame(cube, current_time, trajectory, bounds):
    """创建简单清晰的视频帧"""
    
    # 创建大图
    fig = plt.figure(figsize=(12, 9), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 固定视角 - 不旋转，从最佳角度观看
    ax.view_init(elev=20, azim=45)
    
    # 设置范围
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 标签
    ax.set_xlabel('X (meters)', fontsize=12)
    ax.set_ylabel('Y (meters)', fontsize=12)
    ax.set_zlabel('Z (meters)', fontsize=12)
    
    # 网格和地面
    ax.grid(True, alpha=0.3)
    
    # 绘制地面平台
    x_ground = np.array([bounds[0][0], bounds[0][1], bounds[0][1], bounds[0][0]])
    z_ground = np.array([bounds[2][0], bounds[2][0], bounds[2][1], bounds[2][1]])
    y_ground = np.zeros(4)
    ground_verts = [list(zip(x_ground, y_ground, z_ground))]
    ax.add_collection3d(Poly3DCollection(ground_verts, alpha=0.3, facecolor='gray'))
    
    # 绘制立方体
    draw_simple_cube(ax, cube)
    
    # 绘制轨迹
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               'red', linewidth=3, alpha=0.8, label='Trajectory')
    
    # 信息文本
    info = f"""Cube Fall Demo
Time: {current_time:.1f}s
Height: {cube.position[1]:.1f}m
Speed: {np.linalg.norm(cube.velocity):.1f} m/s"""
    
    ax.text2D(0.02, 0.98, info, transform=ax.transAxes,
             fontsize=14, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # 转换为图像数组
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    buf = buf[:, :, :3]  # RGB only
    
    plt.close(fig)
    return buf

def draw_simple_cube(ax, cube):
    """绘制简单明显的立方体"""
    
    # 获取立方体顶点
    corners = cube.get_corners()
    
    # 定义6个面 - 使用不同颜色
    faces = [
        [corners[0], corners[1], corners[2], corners[3]],  # bottom - blue
        [corners[4], corners[5], corners[6], corners[7]],  # top - blue
        [corners[0], corners[1], corners[5], corners[4]],  # front - red
        [corners[2], corners[3], corners[7], corners[6]],  # back - red
        [corners[1], corners[2], corners[6], corners[5]],  # right - green
        [corners[0], corners[3], corners[7], corners[4]]   # left - green
    ]
    
    colors = ['lightblue', 'lightblue', 'lightcoral', 'lightcoral', 'lightgreen', 'lightgreen']
    
    # 绘制每个面
    for face, color in zip(faces, colors):
        poly = [[face[j] for j in [0, 1, 2, 3]]]
        ax.add_collection3d(Poly3DCollection(poly, alpha=0.8, facecolor=color, edgecolor='black', linewidth=2))

def save_simple_video(frames, output_path):
    """保存视频"""
    try:
        if not frames:
            return False
            
        height, width, _ = frames[0].shape
        
        # 使用H264编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 15.0, (width, height))  # 15fps for smaller file
        
        if not out.isOpened():
            print("Error: Could not open video writer")
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
        output_path = create_simple_demo()
        if output_path:
            print(f"\n✅ Demo complete! Video: {output_path}")
            print("Features:")
            print("- Fixed camera angle (no rotation)")
            print("- Large 3m cube (easy to see)")
            print("- Clear trajectory line")
            print("- Multiple bounces")
            print("- Real-time info display")
        else:
            print("\n❌ Demo failed")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
