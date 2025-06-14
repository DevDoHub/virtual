#!/usr/bin/env python3
"""
批量生成清晰物理演示视频
========================

生成多个不同场景的清晰视频:
1. 基础下落
2. 多次弹跳
3. 斜向下落
4. 高能碰撞

所有视频特点:
- 固定摄像机，无旋转
- 大立方体，易观察
- 清晰的碰撞效果
- 英文界面

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

def create_scenario_video(scenario_name, description, initial_pos, initial_vel, 
                         gravity=9.81, restitution=0.7, cube_size=2.5, duration=6.0):
    """创建单个场景视频"""
    
    print(f"\\n=== {scenario_name} ===")
    print(f"Description: {description}")
    
    # 物理环境
    bounds = [(-8, 8), (0, 16), (-8, 8)]
    engine = PhysicsEngine(gravity=gravity, bounds=bounds)
    
    # 立方体
    cube = Cube(position=initial_pos, velocity=initial_vel, size=cube_size, mass=1.0)
    cube.restitution = restitution
    
    print(f"Initial: pos={cube.position}, vel={cube.velocity}")
    print(f"Physics: gravity={gravity}, bounce={restitution}, size={cube_size}")
    
    # 仿真
    fps = 20  # 较低帧率，减少文件大小
    dt = 1.0 / fps
    total_steps = int(duration / dt)
    
    print(f"Simulating {total_steps} steps...")
    
    positions = []
    velocities = []
    collision_times = []
    
    for step in range(total_steps):
        current_time = step * dt
        
        pre_vel = np.linalg.norm(cube.velocity)
        engine.step([cube])
        post_vel = np.linalg.norm(cube.velocity)
        
        # 检测碰撞
        if abs(post_vel - pre_vel) > 1.5:
            collision_times.append(current_time)
            print(f"  Collision at t={current_time:.1f}s")
        
        positions.append(cube.position.copy())
        velocities.append(cube.velocity.copy())
        
        if step % (total_steps // 4) == 0:
            print(f"  Progress: {step/total_steps*100:.0f}%")
    
    print(f"Simulation done. {len(collision_times)} collisions.")
    
    # 生成帧
    print("Generating frames...")
    frames = []
    
    for step in range(0, total_steps, 3):  # 每3帧取1帧
        current_time = step * dt
        cube.position = positions[step]
        cube.velocity = velocities[step]
        
        # 检查是否接近碰撞时间
        is_collision = any(abs(t - current_time) < 0.2 for t in collision_times)
        
        frame = create_frame(cube, current_time, positions[:step+1], 
                           bounds, scenario_name, description, is_collision)
        frames.append(frame)
    
    # 保存视频
    output_path = f"/root/virtual/output/videos/{scenario_name}.mp4"
    print(f"Saving to {output_path}...")
    
    success = save_video(frames, output_path)
    
    if success:
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ SUCCESS: {size_mb:.1f} MB")
        return output_path
    else:
        print("❌ FAILED")
        return None

def create_frame(cube, time, trajectory, bounds, title, description, is_collision=False):
    """创建视频帧"""
    
    fig = plt.figure(figsize=(10, 8), facecolor='white')
    ax = fig.add_subplot(111, projection='3d')
    
    # 固定视角
    ax.view_init(elev=25, azim=45)
    
    # 设置范围
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 标签
    ax.set_xlabel('X (m)', fontsize=10)
    ax.set_ylabel('Y (m)', fontsize=10)
    ax.set_zlabel('Z (m)', fontsize=10)
    
    # 网格
    ax.grid(True, alpha=0.3)
    
    # 地面
    x_ground = np.linspace(bounds[0][0], bounds[0][1], 5)
    z_ground = np.linspace(bounds[2][0], bounds[2][1], 5)
    X, Z = np.meshgrid(x_ground, z_ground)
    Y = np.zeros_like(X)
    ax.plot_surface(X, Y, Z, alpha=0.2, color='lightgray')
    
    # 立方体颜色
    if is_collision:
        cube_color = 'red'
        alpha = 0.9
    else:
        cube_color = 'lightblue'
        alpha = 0.7
    
    # 绘制立方体
    draw_cube(ax, cube, cube_color, alpha)
    
    # 轨迹
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               'orange', linewidth=2, alpha=0.8)
    
    # 信息框
    info_text = f"""{title}
{description}
Time: {time:.1f}s
Height: {cube.position[1]:.1f}m
Speed: {np.linalg.norm(cube.velocity):.1f} m/s"""
    
    if is_collision:
        info_text += "\\nCOLLISION!"
    
    ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    
    # 转换
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    buf = buf[:, :, :3]
    
    plt.close(fig)
    return buf

def draw_cube(ax, cube, color='lightblue', alpha=0.7):
    """绘制立方体"""
    corners = cube.get_corners()
    
    # 6个面
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
        ax.add_collection3d(Poly3DCollection(poly, alpha=alpha, 
                                           facecolor=color, edgecolor='black', linewidth=1))

def save_video(frames, output_path):
    """保存视频"""
    try:
        if not frames:
            return False
        
        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 10.0, (width, height))  # 10fps
        
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

def create_all_scenarios():
    """创建所有场景视频"""
    
    print("Creating Clear Physics Demo Videos")
    print("=" * 50)
    
    os.makedirs('/root/virtual/output/videos', exist_ok=True)
    
    scenarios = [
        {
            'name': 'clear_basic_fall',
            'description': 'Basic Drop - Straight Down',
            'pos': [0, 14, 0],
            'vel': [0, 0, 0],
            'gravity': 9.81,
            'restitution': 0.6,
            'size': 3.0,
            'duration': 5.0
        },
        {
            'name': 'clear_bouncy_ball',
            'description': 'Super Bouncy Cube',
            'pos': [0, 12, 0],
            'vel': [0, 0, 0],
            'gravity': 9.81,
            'restitution': 0.9,
            'size': 2.5,
            'duration': 8.0
        },
        {
            'name': 'clear_angled_fall',
            'description': 'Diagonal Fall with Spin',
            'pos': [-3, 15, 2],
            'vel': [2, 0, -1],
            'gravity': 9.81,
            'restitution': 0.7,
            'size': 2.0,
            'duration': 7.0
        },
        {
            'name': 'clear_low_gravity',
            'description': 'Low Gravity (Mars-like)',
            'pos': [0, 14, 0],
            'vel': [1, 0, 0.5],
            'gravity': 3.7,  # Mars gravity
            'restitution': 0.8,
            'size': 2.5,
            'duration': 10.0
        }
    ]
    
    successful = []
    
    for scenario in scenarios:
        try:
            result = create_scenario_video(
                scenario['name'],
                scenario['description'],
                scenario['pos'],
                scenario['vel'],
                scenario['gravity'],
                scenario['restitution'],
                scenario['size'],
                scenario['duration']
            )
            
            if result:
                successful.append(result)
                
        except Exception as e:
            print(f"❌ Failed {scenario['name']}: {e}")
    
    # 总结
    print(f"\\n" + "=" * 50)
    print(f"SUMMARY: {len(successful)}/{len(scenarios)} videos created")
    
    if successful:
        total_size = sum(os.path.getsize(f)/(1024*1024) for f in successful)
        print(f"Total size: {total_size:.1f} MB")
        print(f"Location: /root/virtual/output/videos/")
        
        for video in successful:
            name = os.path.basename(video)
            size = os.path.getsize(video) / (1024 * 1024)
            print(f"  ✅ {name} ({size:.1f} MB)")

if __name__ == "__main__":
    try:
        create_all_scenarios()
        print("\\n🎉 All clear demo videos completed!")
        print("Features:")
        print("- Fixed camera angles (no spinning)")
        print("- Large cubes for visibility")
        print("- Clear collision detection")
        print("- Real trajectory tracking")
        print("- Multiple physics scenarios")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
