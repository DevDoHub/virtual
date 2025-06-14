#!/usr/bin/env python3
"""
正确的X-Y地面平面演示 - Z轴垂直向上
=====================================

修正坐标系统：
- X-Y平面作为水平地面
- Z轴作为垂直方向（高度）
- 重力沿Z轴负方向
- 立方体从高处沿Z轴下落到X-Y地面
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cv2
import os

class CorrectCube:
    """正确坐标系的立方体类 - Z轴垂直"""
    
    def __init__(self, size=2.0, position=None, velocity=None):
        self.size = size
        # Z轴是垂直方向，X-Y是水平面
        self.position = position if position is not None else np.array([0.0, 0.0, 8.0])  # 高Z值开始
        self.velocity = velocity if velocity is not None else np.array([1.0, 0.8, 0.0])   # X-Y平面初始速度
        self.restitution = 0.75
        
    def get_corners(self):
        """获取立方体的8个顶点 - Z轴垂直"""
        s = self.size / 2
        x, y, z = self.position
        
        corners = np.array([
            [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y+s, z-s], [x-s, y+s, z-s],  # 底面 (Z-s)
            [x-s, y-s, z+s], [x+s, y-s, z+s], [x+s, y+s, z+s], [x-s, y+s, z+s]   # 顶面 (Z+s)
        ])
        return corners

def correct_physics_step(cube, dt=0.04):
    """正确的物理步骤 - Z轴重力"""
    
    # 重力沿Z轴负方向（向下）
    gravity = np.array([0, 0, -9.8])  # Z轴负方向
    cube.velocity += gravity * dt
    
    # 更新位置
    cube.position += cube.velocity * dt
    
    # 地面碰撞检测 (Z=0为地面，X-Y平面)
    ground_level = 0.0
    cube_bottom = cube.position[2] - cube.size/2  # Z坐标
    
    if cube_bottom <= ground_level:
        # 位置修正
        cube.position[2] = ground_level + cube.size/2
        
        # 反弹
        if cube.velocity[2] < 0:  # Z方向速度
            cube.velocity[2] = -cube.velocity[2] * cube.restitution
            
            # 摩擦力 (X-Y平面)
            cube.velocity[0] *= 0.92
            cube.velocity[1] *= 0.92
            
            return True
    
    return False

def create_correct_frame(cube, time, trajectory, frame_count):
    """创建正确坐标系的视频帧 - X-Y地面，Z轴垂直"""
    
    fig = plt.figure(figsize=(12, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    
    # 正确的视角设置 - 俯视X-Y平面，Z轴向上
    # elev=25: 稍微俯视，可以看到X-Y地面
    # azim=45: 45度角，平衡的视角
    ax.view_init(elev=25, azim=45)
    
    # 场景边界 - X-Y为地面，Z为高度
    bounds = [(-4, 4), (-4, 4), (0, 10)]  # X, Y, Z
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])  # Z轴：高度 (0-10m)
    
    # 坐标轴标签 - 明确Z是高度，X-Y是地面
    ax.set_xlabel('X (East-West)', color='white', fontsize=11)
    ax.set_ylabel('Y (North-South)', color='white', fontsize=11)
    ax.set_zlabel('Z (UP-DOWN)', color='yellow', fontsize=11, weight='bold')  # Z轴是高度
    
    # 设置坐标轴颜色
    ax.tick_params(colors='white', labelsize=9)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False  
    ax.zaxis.pane.fill = False
    
    # 绘制X-Y地面平面（Z=0）
    x_ground = np.linspace(bounds[0][0], bounds[0][1], 10)
    y_ground = np.linspace(bounds[1][0], bounds[1][1], 10)
    X, Y = np.meshgrid(x_ground, y_ground)
    Z_ground = np.zeros_like(X)  # Z=0 地面
    
    # 棋盘格地面效果
    colors = np.zeros(X.shape + (4,))
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            if (i + j) % 2 == 0:
                colors[i, j] = [0.1, 0.5, 0.1, 0.8]  # 深绿色
            else:
                colors[i, j] = [0.2, 0.7, 0.2, 0.8]  # 浅绿色
    
    ax.plot_surface(X, Y, Z_ground, facecolors=colors, alpha=0.9)
    
    # 地面网格线
    for i in range(len(x_ground)):
        ax.plot([x_ground[i], x_ground[i]], [bounds[1][0], bounds[1][1]], [0, 0], 
               color='darkgreen', alpha=0.6, linewidth=0.8)
    for j in range(len(y_ground)):
        ax.plot([bounds[0][0], bounds[0][1]], [y_ground[j], y_ground[j]], [0, 0], 
               color='darkgreen', alpha=0.6, linewidth=0.8)
    
    # 地面标识
    ax.text(0, 0, 0.3, 'GROUND\n(X-Y Plane)', color='lightgreen', 
           fontsize=10, weight='bold', ha='center')
    
    # 重力指示器 (Z轴负方向)
    gravity_x, gravity_y = 3, 3
    ax.quiver(gravity_x, gravity_y, 8, 0, 0, -2, 
             color='red', arrow_length_ratio=0.15, linewidth=3)
    ax.text(gravity_x + 0.3, gravity_y, 6.5, 'GRAVITY\n↓(Z-)', 
           color='red', fontsize=9, weight='bold', ha='center')
    
    # 坐标轴指示器
    # X轴指示器
    ax.quiver(0, -3, 0.5, 2, 0, 0, 
             color='cyan', arrow_length_ratio=0.2, linewidth=2)
    ax.text(1.5, -3, 0.5, 'X→', color='cyan', fontsize=10, weight='bold')
    
    # Y轴指示器
    ax.quiver(-3, 0, 0.5, 0, 2, 0, 
             color='magenta', arrow_length_ratio=0.2, linewidth=2)
    ax.text(-3, 1.5, 0.5, 'Y→', color='magenta', fontsize=10, weight='bold')
    
    # Z轴指示器（高度）
    ax.quiver(-3, -3, 0, 0, 0, 3, 
             color='yellow', arrow_length_ratio=0.2, linewidth=2)
    ax.text(-3, -3, 2, 'Z↑', color='yellow', fontsize=10, weight='bold')
    
    # 轨迹线
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               color='cyan', linewidth=2, alpha=0.7)
    
    # 立方体
    corners = cube.get_corners()
    
    # 检查状态
    height = cube.position[2]  # Z坐标是高度
    speed = np.linalg.norm(cube.velocity)
    target_height = cube.size / 2
    
    if abs(height - target_height) < 0.15 and speed < 0.8:
        cube_color = 'lightgreen'
        status = "✅ LANDED ON X-Y PLANE"
        edge_color = 'darkgreen'
    elif height < 2.5:
        cube_color = 'orange'  
        status = "⬇️ APPROACHING X-Y GROUND"
        edge_color = 'darkorange'
    else:
        cube_color = 'lightblue'
        status = "⬇️ FALLING DOWN Z-AXIS"
        edge_color = 'darkblue'
    
    # 绘制立方体
    faces = [
        [corners[0], corners[1], corners[2], corners[3]],  # 底面
        [corners[4], corners[5], corners[6], corners[7]],  # 顶面
        [corners[0], corners[1], corners[5], corners[4]],  # 前面
        [corners[2], corners[3], corners[7], corners[6]],  # 后面
        [corners[1], corners[2], corners[6], corners[5]],  # 右面
        [corners[0], corners[3], corners[7], corners[4]]   # 左面
    ]
    
    for i, face in enumerate(faces):
        poly = [face]
        alpha = 0.9 if i < 2 else 0.7
        ax.add_collection3d(Poly3DCollection(poly, alpha=alpha, facecolor=cube_color, 
                                           edgecolor=edge_color, linewidth=1.5))
    
    # 立方体中心点
    ax.scatter(*cube.position, color='red', s=60, alpha=0.9)
    
    # 速度矢量
    if speed > 0.3:
        scale = 0.8
        ax.quiver(cube.position[0], cube.position[1], cube.position[2],
                 cube.velocity[0]*scale, cube.velocity[1]*scale, cube.velocity[2]*scale,
                 color='purple', arrow_length_ratio=0.12, linewidth=2, alpha=0.8)
    
    # 从立方体到地面的投影线
    ground_proj = [cube.position[0], cube.position[1], 0]  # Z=0地面投影
    ax.plot([cube.position[0], ground_proj[0]], 
           [cube.position[1], ground_proj[1]], 
           [cube.position[2], ground_proj[2]], 
           'white', linestyle='--', alpha=0.6, linewidth=1.5)
    
    # 地面投影点
    ax.scatter(*ground_proj, color='yellow', s=40, alpha=0.8, marker='o')
    
    # 信息显示
    info_text = f"""🎯 CORRECT X-Y GROUND PLANE VIEW
    
⏱️ Time: {time:.1f}s
📏 Height (Z): {height:.2f}m  
🚀 Speed: {speed:.1f}m/s
📍 Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {height:.1f})
📊 Status: {status}

🌍 X-Y = GROUND PLANE
📐 Z = VERTICAL HEIGHT
⬇️ Gravity along Z-axis
👁️ View: elev=25°, azim=45°"""
    
    # 状态颜色
    if "LANDED" in status:
        bg_color = 'darkgreen'
        alpha = 0.9
    elif "APPROACHING" in status:
        bg_color = 'darkorange'
        alpha = 0.8
    else:
        bg_color = 'darkblue'
        alpha = 0.8
    
    ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
             fontsize=10, color='white', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=alpha))
    
    # 标题
    title = "3D Physics Simulation - Correct X-Y Ground Plane (Z-axis UP)"
    ax.text2D(0.5, 0.95, title, transform=ax.transAxes, 
             color='white', fontsize=14, horizontalalignment='center', weight='bold')
    
    plt.tight_layout()
    
    # 转换为图像
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    frame = buf[:, :, :3]
    
    plt.close(fig)
    return frame

def create_correct_demo():
    """创建正确坐标系演示"""
    
    print("🎯 Creating CORRECT X-Y Ground Plane Demo")
    print("Z-axis as vertical direction (height)")
    print("=" * 50)
    
    # 初始化
    cube = CorrectCube(size=2.0, position=np.array([0.0, 0.0, 8.0]),  # 高Z值开始
                       velocity=np.array([1.2, 0.8, 0.0]))           # X-Y平面初始速度
    
    # 仿真参数
    dt = 0.04
    duration = 6.0
    steps = int(duration / dt)
    fps = 25
    
    print(f"Duration: {duration}s, Steps: {steps}, FPS: {fps}")
    print(f"Coordinate system: X-Y ground plane, Z-axis vertical")
    print(f"Initial position: {cube.position}")
    print(f"Ground: X-Y plane at Z=0")
    print(f"Gravity: along Z-axis (negative direction)")
    
    # 运行仿真
    positions = []
    collisions = 0
    
    for step in range(steps):
        time = step * dt
        positions.append(cube.position.copy())
        
        # 物理步骤
        collision = correct_physics_step(cube, dt)
        if collision:
            collisions += 1
            print(f"  🎾 Bounce #{collisions} at t={time:.1f}s")
            print(f"     Height (Z): {cube.position[2]:.2f}m")
            print(f"     Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
        
        # 检查停止条件
        if np.linalg.norm(cube.velocity) < 0.3 and abs(cube.position[2] - 1.0) < 0.2:
            print(f"  ✅ Cube settled at t={time:.1f}s")
            # 延长显示
            for _ in range(30):
                positions.append(cube.position.copy())
            break
    
    print(f"\n📊 Simulation Results:")
    print(f"   Total bounces: {collisions}")
    print(f"   Final height (Z): {cube.position[2]:.2f}m (expected: ~1.0m)")
    print(f"   Final position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
    print(f"   Final speed: {np.linalg.norm(cube.velocity):.2f}m/s")
    
    # 生成视频帧
    print("\n🎬 Generating correct coordinate system video...")
    frames = []
    
    frame_interval = max(1, len(positions) // (duration * fps))
    
    for i in range(0, len(positions), frame_interval):
        time = i * dt
        cube.position = positions[i]
        
        # 速度估算
        if i > 0 and i < len(positions) - 1:
            cube.velocity = (positions[i+1] - positions[i-1]) / (2 * dt)
        elif i > 0:
            cube.velocity = (positions[i] - positions[i-1]) / dt
        
        frame = create_correct_frame(cube, time, positions[:i+1], i)
        frames.append(frame)
        
        if i % (len(positions) // 8) == 0:
            progress = (i / len(positions)) * 100
            print(f"   Progress: {progress:.0f}% ({len(frames)} frames)")
    
    print(f"✅ Generated {len(frames)} frames")
    
    # 保存视频
    output_path = "/root/virtual/output/videos/correct_xy_ground_demo.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if save_correct_video(frames, output_path, fps):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"🎉 Video saved: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video save failed")
        return None

def save_correct_video(frames, output_path, fps):
    """保存正确坐标系视频"""
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
            
            if i % 20 == 0:
                print(f"   Writing frame {i+1}/{len(frames)}")
        
        out.release()
        return True
        
    except Exception as e:
        print(f"Video save error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = create_correct_demo()
        
        if result:
            print("\n" + "=" * 60)
            print("🎉 CORRECT COORDINATE SYSTEM DEMO SUCCESSFUL!")
            print(f"📹 Video: {result}")
            print("\n🔑 Corrected Coordinate System:")
            print("✅ X-Y plane as horizontal ground surface")
            print("✅ Z-axis as vertical height direction")
            print("✅ Gravity along Z-axis (downward)")
            print("✅ Cube falls from high Z to X-Y plane")
            print("✅ Proper physics with ground collision at Z=0")
            print("✅ Clear visualization of 3D coordinate system")
            print("=" * 60)
        else:
            print("\n❌ Demo failed")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
