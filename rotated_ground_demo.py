#!/usr/bin/env python3
"""
旋转视角演示 - X-Z平面作为地面
==============================

将整个场景旋转90度，使X-Z平面作为水平地面
这是更常见的3D场景布局方式
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cv2
import os

class RotatedCube:
    """旋转坐标系的立方体类 - X-Z平面为地面"""
    
    def __init__(self, size=2.0, position=None, velocity=None):
        self.size = size
        # 现在Y轴是垂直方向，X-Z是水平面
        self.position = position if position is not None else np.array([0.0, 8.0, 0.0])
        self.velocity = velocity if velocity is not None else np.array([1.5, 0.0, 0.8])
        self.restitution = 0.7
        
    def get_corners(self):
        """获取立方体的8个顶点 - Y轴垂直"""
        s = self.size / 2
        x, y, z = self.position
        
        corners = np.array([
            [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y-s, z+s], [x-s, y-s, z+s],  # 底面 (Y-s)
            [x-s, y+s, z-s], [x+s, y+s, z-s], [x+s, y+s, z+s], [x-s, y+s, z+s]   # 顶面 (Y+s)
        ])
        return corners

def rotated_physics_step(cube, dt=0.05):
    """物理步骤 - Y轴作为垂直方向"""
    
    # 重力沿Y轴负方向
    gravity = np.array([0, -9.8, 0])
    cube.velocity += gravity * dt
    
    # 更新位置
    cube.position += cube.velocity * dt
    
    # 地面碰撞检测 (Y=0为地面)
    ground_level = 0.0
    cube_bottom = cube.position[1] - cube.size/2
    
    if cube_bottom <= ground_level:
        # 位置修正
        cube.position[1] = ground_level + cube.size/2
        
        # 反弹
        if cube.velocity[1] < 0:
            cube.velocity[1] = -cube.velocity[1] * cube.restitution
            
            # 摩擦力 (X-Z平面)
            cube.velocity[0] *= 0.9
            cube.velocity[2] *= 0.9
            
            return True
    
    return False

def create_rotated_frame(cube, time, trajectory, frame_count):
    """创建旋转视角的视频帧 - X-Z平面为地面"""
    
    fig = plt.figure(figsize=(12, 9), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    
    # 关键改变：设置视角让X-Z平面看起来像地面
    # elev=20: 较低的仰角，从上往下俯视X-Z平面
    # azim=45: 45度方位角，看起来平衡
    ax.view_init(elev=20, azim=45)
    
    # 场景边界 - Y轴仍是高度，但视角让X-Z看起来是地面
    bounds = [(-4, 4), (0, 10), (-4, 4)]  # X, Y, Z
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])  # Y轴：高度 (0-10m)
    ax.set_zlim(bounds[2])
    
    # 坐标轴标签 - 强调Y是高度，X-Z是水平面
    ax.set_xlabel('X (East-West)', color='white', fontsize=12)
    ax.set_ylabel('Y (UP-DOWN)', color='yellow', fontsize=12, weight='bold')
    ax.set_zlabel('Z (North-South)', color='white', fontsize=12)
    
    # 设置坐标轴颜色
    ax.tick_params(colors='white')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False  
    ax.zaxis.pane.fill = False
    
    # 绘制地面 (X-Z平面，Y=0)
    x_ground = np.linspace(bounds[0][0], bounds[0][1], 8)
    z_ground = np.linspace(bounds[2][0], bounds[2][1], 8)
    X, Z = np.meshgrid(x_ground, z_ground)
    Y_ground = np.zeros_like(X)  # Y=0 地面
    
    # 棋盘格地面效果
    colors = np.zeros(X.shape + (4,))
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            if (i + j) % 2 == 0:
                colors[i, j] = [0.2, 0.6, 0.2, 0.7]  # 深绿色
            else:
                colors[i, j] = [0.4, 0.8, 0.4, 0.7]  # 浅绿色
    
    ax.plot_surface(X, Y_ground, Z, facecolors=colors, alpha=0.8)
    
    # 地面网格线
    for i in range(len(x_ground)):
        ax.plot([x_ground[i], x_ground[i]], [0, 0], [bounds[2][0], bounds[2][1]], 
               color='darkgreen', alpha=0.5, linewidth=0.5)
    for j in range(len(z_ground)):
        ax.plot([bounds[0][0], bounds[0][1]], [0, 0], [z_ground[j], z_ground[j]], 
               color='darkgreen', alpha=0.5, linewidth=0.5)
    
    # 地面标识
    ax.text(0, 0.5, 0, 'GROUND\n(X-Z Plane)', color='lightgreen', 
           fontsize=11, weight='bold', ha='center')
    
    # 重力指示器 (Y轴负方向)
    ax.quiver(-3, 8, 3, 0, -2, 0, color='red', arrow_length_ratio=0.2, linewidth=3)
    ax.text(-3, 6.5, 3, 'GRAVITY\n↓', color='red', fontsize=10, weight='bold', ha='center')
    
    # 坐标轴指示器
    # X轴 (东西方向)
    ax.quiver(0, 0.5, -3, 2, 0, 0, color='cyan', arrow_length_ratio=0.2, linewidth=2)
    ax.text(1.5, 0.5, -3, 'X→', color='cyan', fontsize=10, weight='bold')
    
    # Z轴 (南北方向)
    ax.quiver(-3, 0.5, 0, 0, 0, 2, color='magenta', arrow_length_ratio=0.2, linewidth=2)
    ax.text(-3, 0.5, 1.5, 'Z→', color='magenta', fontsize=10, weight='bold')
    
    # Y轴 (上下方向)
    ax.quiver(3, 0, -3, 0, 3, 0, color='yellow', arrow_length_ratio=0.2, linewidth=2)
    ax.text(3, 2, -3, 'Y↑', color='yellow', fontsize=10, weight='bold')
    
    # 轨迹线
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               color='cyan', linewidth=3, alpha=0.8, label='Trajectory')
    
    # 立方体
    corners = cube.get_corners()
    
    # 检查状态
    height = cube.position[1]
    speed = np.linalg.norm(cube.velocity)
    target_height = cube.size / 2
    
    if abs(height - target_height) < 0.2 and speed < 1.0:
        cube_color = 'lightgreen'
        status = "✅ LANDED ON GROUND"
        edge_color = 'darkgreen'
    elif height < 3.0:
        cube_color = 'orange'  
        status = "⬇️ APPROACHING GROUND"
        edge_color = 'darkorange'
    else:
        cube_color = 'lightblue'
        status = "⬇️ FALLING FROM HEIGHT"
        edge_color = 'darkblue'
    
    # 绘制立方体面
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
        # 不同面用稍微不同的颜色
        alpha = 0.9 if i < 2 else 0.7  # 顶底面更明显
        ax.add_collection3d(Poly3DCollection(poly, alpha=alpha, facecolor=cube_color, 
                                           edgecolor=edge_color, linewidth=2))
    
    # 立方体中心点
    ax.scatter(*cube.position, color='red', s=80, alpha=0.8)
    
    # 速度矢量
    if speed > 0.5:
        scale = 1.0
        ax.quiver(cube.position[0], cube.position[1], cube.position[2],
                 cube.velocity[0]*scale, cube.velocity[1]*scale, cube.velocity[2]*scale,
                 color='purple', arrow_length_ratio=0.15, linewidth=3, alpha=0.8)
        
        # 速度标签
        vel_end = cube.position + cube.velocity * scale
        ax.text(vel_end[0], vel_end[1], vel_end[2], 'Velocity', 
               color='purple', fontsize=9, weight='bold')
    
    # 从立方体到地面的投影线（帮助判断位置）
    ground_proj = [cube.position[0], 0, cube.position[2]]
    ax.plot([cube.position[0], ground_proj[0]], 
           [cube.position[1], ground_proj[1]], 
           [cube.position[2], ground_proj[2]], 
           'white', linestyle='--', alpha=0.5, linewidth=1)
    
    # 地面投影点
    ax.scatter(*ground_proj, color='white', s=30, alpha=0.7, marker='x')
    
    # 信息显示
    info_text = f"""🎯 ROTATED VIEW PHYSICS DEMO
    
⏱️ Time: {time:.1f}s
📏 Height (Y): {height:.2f}m
🎯 Target: {target_height:.1f}m  
🚀 Speed: {speed:.1f}m/s
📍 Position: ({cube.position[0]:.1f}, {height:.1f}, {cube.position[2]:.1f})
📊 Status: {status}

🌍 X-Z Plane = GROUND
📐 Y-axis = VERTICAL (Height)
👁️ Viewing from above-front
⚡ Gravity points DOWN (Y-)"""
    
    # 背景色根据状态变化
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
             fontsize=11, color='white', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=alpha))
    
    # 标题
    title = "3D Physics Simulation - Ground Plane View (X-Z)"
    ax.text2D(0.5, 0.95, title, transform=ax.transAxes, 
             color='white', fontsize=15, horizontalalignment='center', weight='bold')
    
    # 图例
    legend_elements = [
        plt.Line2D([0], [0], color='cyan', linewidth=3, label='Trajectory'),
        plt.Line2D([0], [0], color='purple', linewidth=3, label='Velocity'),
        plt.Line2D([0], [0], color='red', linewidth=3, label='Gravity'),
        plt.Line2D([0], [0], color='white', linestyle='--', label='Height Line')
    ]
    ax.legend(handles=legend_elements, loc='upper right', 
             bbox_to_anchor=(0.98, 0.88), facecolor='black', 
             edgecolor='white', fontsize=10)
    
    plt.tight_layout()
    
    # 转换为图像
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    frame = buf[:, :, :3]  # 去掉alpha通道
    
    plt.close(fig)
    return frame

def create_rotated_demo():
    """创建旋转视角演示"""
    
    print("🔄 Rotated View Physics Demo - X-Z Ground Plane")
    print("=" * 50)
    
    # 初始化
    cube = RotatedCube(size=2.0, position=np.array([0.0, 8.0, 0.0]), 
                       velocity=np.array([2.0, 0.0, 1.5]))
    
    # 仿真参数
    dt = 0.05
    duration = 6.0
    steps = int(duration / dt)
    fps = 24
    
    print(f"Duration: {duration}s, Steps: {steps}, FPS: {fps}")
    print(f"Initial position: {cube.position}")
    print(f"Initial velocity: {cube.velocity}")
    print(f"Ground level: Y = 0")
    print(f"Expected final Y: {cube.size/2:.1f}m")
    
    # 运行仿真
    positions = []
    collisions = 0
    
    for step in range(steps):
        time = step * dt
        positions.append(cube.position.copy())
        
        # 物理步骤
        collision = rotated_physics_step(cube, dt)
        if collision:
            collisions += 1
            print(f"  🎾 Bounce #{collisions} at t={time:.1f}s")
            print(f"     Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
            print(f"     Velocity: ({cube.velocity[0]:.1f}, {cube.velocity[1]:.1f}, {cube.velocity[2]:.1f})")
        
        # 检查停止条件
        if np.linalg.norm(cube.velocity) < 0.4 and abs(cube.position[1] - 1.0) < 0.3:
            print(f"  ✅ Cube settled at t={time:.1f}s")
            # 延长显示最终状态
            for _ in range(30):
                positions.append(cube.position.copy())
            break
    
    print(f"\n📊 Simulation Results:")
    print(f"   Total bounces: {collisions}")
    print(f"   Final height: {cube.position[1]:.2f}m (expected: ~1.0m)")
    print(f"   Final position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
    print(f"   Final speed: {np.linalg.norm(cube.velocity):.2f}m/s")
    
    # 生成视频帧
    print("\n🎬 Generating video frames...")
    frames = []
    
    frame_interval = max(1, len(positions) // (duration * fps))
    print(f"   Frame interval: {frame_interval}")
    
    for i in range(0, len(positions), frame_interval):
        time = i * dt
        cube.position = positions[i]
        
        # 简单的速度估算
        if i > 0 and i < len(positions) - 1:
            cube.velocity = (positions[i+1] - positions[i-1]) / (2 * dt)
        elif i > 0:
            cube.velocity = (positions[i] - positions[i-1]) / dt
        
        frame = create_rotated_frame(cube, time, positions[:i+1], i)
        frames.append(frame)
        
        if i % (len(positions) // 10) == 0:
            progress = (i / len(positions)) * 100
            print(f"   Progress: {progress:.0f}% ({len(frames)} frames)")
    
    print(f"✅ Generated {len(frames)} frames")
    
    # 保存视频
    output_path = "/root/virtual/output/videos/rotated_ground_plane_demo.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if save_rotated_video(frames, output_path, fps):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"🎉 Video saved: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video save failed")
        return None

def save_rotated_video(frames, output_path, fps):
    """保存旋转视角视频"""
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
        result = create_rotated_demo()
        
        if result:
            print("\n" + "=" * 60)
            print("🎉 ROTATED VIEW DEMO SUCCESSFUL!")
            print(f"📹 Video: {result}")
            print("\n🔑 Key Features:")
            print("✅ X-Z plane as ground (horizontal surface)")
            print("✅ Y-axis as vertical height direction")
            print("✅ Viewing from above-front angle (elev=20)")
            print("✅ Checkerboard ground pattern for depth perception")
            print("✅ Clear coordinate axis indicators")
            print("✅ Height projection lines to ground")
            print("✅ Proper physics with ground collision")
            print("✅ Status tracking and trajectory visualization")
            print("=" * 60)
        else:
            print("\n❌ Demo failed")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
