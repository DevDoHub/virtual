#!/usr/bin/env python3
"""
快速直观视角演示 - Y轴垂直向上
=============================

快速创建一个展示Y轴作为垂直方向（高度）的物理演示视频
使用简化的物理引擎，专注于视角的改进
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cv2
import os

class QuickCube:
    """简化的立方体类"""
    
    def __init__(self, size=2.0, position=None, velocity=None):
        self.size = size
        self.position = position if position is not None else np.array([0.0, 8.0, 0.0])
        self.velocity = velocity if velocity is not None else np.array([1.0, 0.0, 0.5])
        self.restitution = 0.7
        
    def get_corners(self):
        """获取立方体的8个顶点"""
        s = self.size / 2
        x, y, z = self.position
        
        corners = np.array([
            [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y+s, z-s], [x-s, y+s, z-s],  # 底面
            [x-s, y-s, z+s], [x+s, y-s, z+s], [x+s, y+s, z+s], [x-s, y+s, z+s]   # 顶面
        ])
        return corners

def quick_physics_step(cube, dt=0.05):
    """简化的物理步骤"""
    
    # 重力（Y方向向下）
    gravity = np.array([0, -9.8, 0])
    cube.velocity += gravity * dt
    
    # 更新位置
    cube.position += cube.velocity * dt
    
    # 地面碰撞检测
    ground_level = 0.0
    cube_bottom = cube.position[1] - cube.size/2
    
    if cube_bottom <= ground_level:
        # 位置修正
        cube.position[1] = ground_level + cube.size/2
        
        # 反弹
        if cube.velocity[1] < 0:
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            
            # 摩擦力
            cube.velocity[0] *= 0.9
            cube.velocity[2] *= 0.9
            
            return True
    
    return False

def create_quick_frame(cube, time, trajectory, frame_count):
    """创建单个视频帧 - 直观Y轴向上视角"""
    
    fig = plt.figure(figsize=(10, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    
    # 关键：设置直观的Y轴垂直视角
    # elev=30: 从稍微下方向上看，让Y轴显得垂直
    # azim=45: 45度角侧视，平衡感好
    ax.view_init(elev=30, azim=45)
    
    # 场景边界 - Y轴为高度
    bounds = [(-4, 4), (0, 10), (-4, 4)]
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 坐标轴标签 - 强调Y是高度
    ax.set_xlabel('X (Left-Right)', color='white', fontsize=12)
    ax.set_ylabel('Y (HEIGHT)', color='yellow', fontsize=12, weight='bold')
    ax.set_zlabel('Z (Forward-Back)', color='white', fontsize=12)
    
    # 设置坐标轴颜色
    ax.tick_params(colors='white')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False  
    ax.zaxis.pane.fill = False
    
    # 绘制地面（Y=0平面）
    x_ground = np.linspace(bounds[0][0], bounds[0][1], 5)
    z_ground = np.linspace(bounds[2][0], bounds[2][1], 5)
    X, Z = np.meshgrid(x_ground, z_ground)
    Y = np.zeros_like(X)
    
    ax.plot_surface(X, Y, Z, alpha=0.3, color='darkgreen')
    
    # 地面标识
    ax.text(0, 0.2, 0, 'GROUND LEVEL', color='lightgreen', fontsize=10, weight='bold')
    
    # 重力指示器
    ax.quiver(3, 8, 0, 0, -2, 0, color='red', arrow_length_ratio=0.2, linewidth=3)
    ax.text(3.5, 7, 0, 'GRAVITY\n↓', color='red', fontsize=10, weight='bold')
    
    # Y轴方向指示器
    ax.quiver(0, 0, 3, 0, 3, 0, color='yellow', arrow_length_ratio=0.2, linewidth=3)
    ax.text(0.3, 2, 3, 'HEIGHT\n↑', color='yellow', fontsize=10, weight='bold')
    
    # 轨迹线
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               color='cyan', linewidth=2, alpha=0.8, label='Trajectory')
    
    # 立方体
    corners = cube.get_corners()
    
    # 检查状态
    height = cube.position[1]
    speed = np.linalg.norm(cube.velocity)
    target_height = cube.size / 2
    
    if abs(height - target_height) < 0.2 and speed < 1.0:
        cube_color = 'lightgreen'
        status = "✅ LANDED"
    elif height < 3.0:
        cube_color = 'orange'  
        status = "⬇️ LANDING"
    else:
        cube_color = 'lightblue'
        status = "⬇️ FALLING"
    
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
        ax.add_collection3d(Poly3DCollection(poly, alpha=0.8, facecolor=cube_color, 
                                           edgecolor='white', linewidth=1.5))
    
    # 速度矢量
    if speed > 0.5:
        scale = 0.8
        ax.quiver(cube.position[0], cube.position[1], cube.position[2],
                 cube.velocity[0]*scale, cube.velocity[1]*scale, cube.velocity[2]*scale,
                 color='purple', arrow_length_ratio=0.15, linewidth=2)
    
    # 信息显示
    info_text = f"""⚡ INTUITIVE Y-UP PHYSICS DEMO
    
⏱️ Time: {time:.1f}s
📏 Height (Y): {height:.2f}m
🎯 Target: {target_height:.1f}m  
🚀 Speed: {speed:.1f}m/s
📍 Position: ({cube.position[0]:.1f}, {height:.1f}, {cube.position[2]:.1f})
📊 Status: {status}

🔄 Y-axis = VERTICAL (Height)
📐 Natural viewing angle
🌍 Gravity points DOWN"""
    
    # 背景色根据状态变化
    if "LANDED" in status:
        bg_color = 'darkgreen'
    elif "LANDING" in status:
        bg_color = 'darkorange'
    else:
        bg_color = 'darkblue'
    
    ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
             fontsize=10, color='white', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.8))
    
    # 标题
    title = "3D Physics Simulation - Intuitive Y-Up View"
    ax.text2D(0.5, 0.95, title, transform=ax.transAxes, 
             color='white', fontsize=14, horizontalalignment='center', weight='bold')
    
    plt.tight_layout()
    
    # 转换为图像
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    frame = buf[:, :, :3]  # 去掉alpha通道
    
    plt.close(fig)
    return frame

def create_quick_demo():
    """创建快速演示"""
    
    print("🚀 Quick Intuitive Y-Up Physics Demo")
    print("=" * 40)
    
    # 初始化
    cube = QuickCube(size=2.0, position=np.array([0.0, 8.0, 0.0]), 
                     velocity=np.array([1.5, 0.0, 0.8]))
    
    # 仿真参数
    dt = 0.05
    duration = 5.0
    steps = int(duration / dt)
    fps = 20
    
    print(f"Duration: {duration}s, Steps: {steps}, FPS: {fps}")
    
    # 运行仿真
    positions = []
    collisions = 0
    
    for step in range(steps):
        time = step * dt
        positions.append(cube.position.copy())
        
        # 物理步骤
        collision = quick_physics_step(cube, dt)
        if collision:
            collisions += 1
            print(f"  Bounce {collisions} at t={time:.1f}s, height={cube.position[1]:.1f}m")
        
        # 检查停止条件
        if np.linalg.norm(cube.velocity) < 0.3 and abs(cube.position[1] - 1.0) < 0.2:
            print(f"  Settled at t={time:.1f}s")
            # 延长一点时间显示最终状态
            for _ in range(20):
                positions.append(cube.position.copy())
            break
    
    print(f"Simulation complete. Total bounces: {collisions}")
    print(f"Final height: {cube.position[1]:.2f}m (expected: ~1.0m)")
    
    # 生成视频帧
    print("🎥 Generating video frames...")
    frames = []
    
    frame_interval = max(1, len(positions) // (duration * fps))
    
    for i in range(0, len(positions), frame_interval):
        time = i * dt
        cube.position = positions[i]
        
        # 简单的速度估算用于显示
        if i > 0:
            cube.velocity = (positions[i] - positions[i-1]) / dt
        
        frame = create_quick_frame(cube, time, positions[:i+1], i)
        frames.append(frame)
        
        if i % 20 == 0:
            print(f"  Frame {len(frames)}/{len(positions)//frame_interval}")
    
    print(f"Generated {len(frames)} frames")
    
    # 保存视频
    output_path = "/root/virtual/output/videos/quick_intuitive_y_up_demo.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if save_quick_video(frames, output_path, fps):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Video saved: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video save failed")
        return None

def save_quick_video(frames, output_path, fps):
    """快速保存视频"""
    try:
        if not frames:
            return False
        
        height, width, _ = frames[0].shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print("❌ Cannot open video writer")
            return False
        
        for i, frame in enumerate(frames):
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
            
            if i % 10 == 0:
                print(f"  Writing frame {i+1}/{len(frames)}")
        
        out.release()
        return True
        
    except Exception as e:
        print(f"Video save error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = create_quick_demo()
        
        if result:
            print("\n" + "=" * 50)
            print("🎉 QUICK DEMO SUCCESSFUL!")
            print(f"📹 Video: {result}")
            print("\n🔑 Key Features:")
            print("✅ Y-axis is vertical (natural height)")
            print("✅ Intuitive viewing angle (elev=30, azim=45)")
            print("✅ Clear ground plane at Y=0")
            print("✅ Visual gravity and height indicators")  
            print("✅ Proper physics with ground collision")
            print("✅ Status indicators and trajectory tracking")
            print("=" * 50)
        else:
            print("\n❌ Demo failed")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
