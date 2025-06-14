#!/usr/bin/env python3
"""
优化的X-Z地面视角演示 - 模仿用户提供的理想视角
=============================================

基于用户提供的第二张图片，优化视角参数：
- 更低的仰角，接近平视
- X-Z平面完全水平
- 立方体清晰地在地面上方
- 更好的深度感知
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cv2
import os

class OptimizedCube:
    """优化视角的立方体类"""
    
    def __init__(self, size=2.0, position=None, velocity=None):
        self.size = size
        self.position = position if position is not None else np.array([0.0, 6.0, 0.0])
        self.velocity = velocity if velocity is not None else np.array([1.0, 0.0, 0.5])
        self.restitution = 0.75
        
    def get_corners(self):
        """获取立方体的8个顶点"""
        s = self.size / 2
        x, y, z = self.position
        
        corners = np.array([
            [x-s, y-s, z-s], [x+s, y-s, z-s], [x+s, y-s, z+s], [x-s, y-s, z+s],  # 底面
            [x-s, y+s, z-s], [x+s, y+s, z-s], [x+s, y+s, z+s], [x-s, y+s, z+s]   # 顶面
        ])
        return corners

def optimized_physics_step(cube, dt=0.04):
    """优化的物理步骤"""
    
    # 重力沿Y轴负方向
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
            cube.velocity[0] *= 0.92
            cube.velocity[2] *= 0.92
            
            return True
    
    return False

def create_optimized_frame(cube, time, trajectory, frame_count):
    """创建优化视角的视频帧 - 模仿第二张图的视角"""
    
    fig = plt.figure(figsize=(12, 8), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')
    
    # 关键优化：使用更低的仰角，模仿第二张图的视角
    # elev=15: 非常低的仰角，接近平视
    # azim=35: 稍微调整方位角，获得更好的视觉效果
    ax.view_init(elev=15, azim=35)
    
    # 场景边界
    bounds = [(-3, 5), (0, 8), (-2, 4)]
    ax.set_xlim(bounds[0])
    ax.set_ylim(bounds[1])
    ax.set_zlim(bounds[2])
    
    # 坐标轴标签 - 与第二张图保持一致
    ax.set_xlabel('X (East-West)', color='white', fontsize=11, labelpad=10)
    ax.set_ylabel('Y (UP-DOWN)', color='yellow', fontsize=11, weight='bold', labelpad=10)
    ax.set_zlabel('Z (North-South)', color='white', fontsize=11, labelpad=10)
    
    # 设置坐标轴颜色和样式
    ax.tick_params(colors='white', labelsize=9)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False  
    ax.zaxis.pane.fill = False
    
    # 设置网格线颜色
    ax.xaxis.pane.set_edgecolor('gray')
    ax.yaxis.pane.set_edgecolor('gray')
    ax.zaxis.pane.set_edgecolor('gray')
    ax.xaxis.pane.set_alpha(0.3)
    ax.yaxis.pane.set_alpha(0.3)
    ax.zaxis.pane.set_alpha(0.3)
    
    # 绘制X-Z地面平面（模仿第二张图的绿色棋盘格）
    x_ground = np.linspace(bounds[0][0], bounds[0][1], 10)
    z_ground = np.linspace(bounds[2][0], bounds[2][1], 8)
    X, Z = np.meshgrid(x_ground, z_ground)
    Y_ground = np.zeros_like(X)
    
    # 创建棋盘格效果
    colors = np.zeros(X.shape + (4,))
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            if (i + j) % 2 == 0:
                colors[i, j] = [0.1, 0.5, 0.1, 0.8]  # 深绿色
            else:
                colors[i, j] = [0.2, 0.7, 0.2, 0.8]  # 浅绿色
    
    ax.plot_surface(X, Y_ground, Z, facecolors=colors, alpha=0.9)
    
    # 添加地面网格线（更清晰）
    for i in range(len(x_ground)):
        ax.plot([x_ground[i], x_ground[i]], [0, 0], [bounds[2][0], bounds[2][1]], 
               color='darkgreen', alpha=0.6, linewidth=0.8)
    for j in range(len(z_ground)):
        ax.plot([bounds[0][0], bounds[0][1]], [0, 0], [z_ground[j], z_ground[j]], 
               color='darkgreen', alpha=0.6, linewidth=0.8)
    
    # 地面标识
    ax.text(1, 0.3, 1, 'GROUND\n(X-Z Plane)', color='lightgreen', 
           fontsize=10, weight='bold', ha='center')
    
    # 重力指示器
    gravity_x, gravity_z = bounds[0][1] - 1, bounds[2][1] - 0.5
    ax.quiver(gravity_x, 6, gravity_z, 0, -1.8, 0, 
             color='red', arrow_length_ratio=0.15, linewidth=3)
    ax.text(gravity_x + 0.3, 5, gravity_z, 'GRAVITY\n↓', 
           color='red', fontsize=9, weight='bold', ha='center')
    
    # 坐标轴指示器（模仿第二张图的样式）
    # X轴指示器
    ax.quiver(0, 0.3, bounds[2][0] + 0.5, 1.5, 0, 0, 
             color='cyan', arrow_length_ratio=0.2, linewidth=2)
    ax.text(1, 0.3, bounds[2][0] + 0.5, 'X→', color='cyan', fontsize=10, weight='bold')
    
    # Z轴指示器
    ax.quiver(bounds[0][0] + 0.5, 0.3, 0, 0, 0, 1.5, 
             color='magenta', arrow_length_ratio=0.2, linewidth=2)
    ax.text(bounds[0][0] + 0.5, 0.3, 1, 'Z→', color='magenta', fontsize=10, weight='bold')
    
    # Y轴指示器
    ax.quiver(bounds[0][1] - 0.5, 0, bounds[2][0] + 0.5, 0, 2, 0, 
             color='yellow', arrow_length_ratio=0.2, linewidth=2)
    ax.text(bounds[0][1] - 0.5, 1.5, bounds[2][0] + 0.5, 'Y↑', 
           color='yellow', fontsize=10, weight='bold')
    
    # 轨迹线
    if len(trajectory) > 1:
        traj = np.array(trajectory)
        ax.plot(traj[:, 0], traj[:, 1], traj[:, 2], 
               color='cyan', linewidth=2, alpha=0.7)
    
    # 立方体
    corners = cube.get_corners()
    
    # 检查状态
    height = cube.position[1]
    speed = np.linalg.norm(cube.velocity)
    target_height = cube.size / 2
    
    if abs(height - target_height) < 0.15 and speed < 0.8:
        cube_color = 'lightgreen'
        status = "✅ LANDED"
        edge_color = 'darkgreen'
    elif height < 2.5:
        cube_color = 'orange'  
        status = "⬇️ LANDING"
        edge_color = 'darkorange'
    else:
        cube_color = 'lightblue'
        status = "⬇️ FALLING"
        edge_color = 'darkblue'
    
    # 绘制立方体（增强的视觉效果）
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
        # 不同面使用稍微不同的透明度
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
    ground_proj = [cube.position[0], 0, cube.position[2]]
    ax.plot([cube.position[0], ground_proj[0]], 
           [cube.position[1], ground_proj[1]], 
           [cube.position[2], ground_proj[2]], 
           'white', linestyle='--', alpha=0.6, linewidth=1.5)
    
    # 地面投影点
    ax.scatter(*ground_proj, color='yellow', s=40, alpha=0.8, marker='o')
    
    # 信息显示（简化，模仿第二张图的简洁风格）
    info_text = f"""🎯 OPTIMIZED X-Z GROUND VIEW
    
⏱️ Time: {time:.1f}s
📏 Height: {height:.2f}m  
🚀 Speed: {speed:.1f}m/s
📍 Position: ({cube.position[0]:.1f}, {height:.1f}, {cube.position[2]:.1f})
📊 Status: {status}

🌍 X-Z = GROUND PLANE
📐 Y = VERTICAL HEIGHT
👁️ Low angle view (elev=15°)"""
    
    # 状态颜色
    if "LANDED" in status:
        bg_color = 'darkgreen'
        alpha = 0.9
    elif "LANDING" in status:
        bg_color = 'darkorange'
        alpha = 0.8
    else:
        bg_color = 'darkblue'
        alpha = 0.8
    
    ax.text2D(0.02, 0.98, info_text, transform=ax.transAxes,
             fontsize=10, color='white', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor=bg_color, alpha=alpha))
    
    # 标题（模仿第二张图）
    title = "3D Physics Simulation - Optimized Ground Plane View (X-Z)"
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

def create_optimized_demo():
    """创建优化视角演示"""
    
    print("🎯 Creating Optimized X-Z Ground Plane View Demo")
    print("Based on user's ideal viewing angle reference")
    print("=" * 55)
    
    # 初始化
    cube = OptimizedCube(size=2.0, position=np.array([0.0, 6.0, 0.0]), 
                        velocity=np.array([1.2, 0.0, 0.8]))
    
    # 仿真参数
    dt = 0.04
    duration = 5.0
    steps = int(duration / dt)
    fps = 25
    
    print(f"Duration: {duration}s, Steps: {steps}, FPS: {fps}")
    print(f"View angle: elev=15° (low angle), azim=35°")
    print(f"Initial position: {cube.position}")
    print(f"Ground: X-Z plane at Y=0")
    
    # 运行仿真
    positions = []
    collisions = 0
    
    for step in range(steps):
        time = step * dt
        positions.append(cube.position.copy())
        
        # 物理步骤
        collision = optimized_physics_step(cube, dt)
        if collision:
            collisions += 1
            print(f"  🎾 Bounce #{collisions} at t={time:.1f}s")
            print(f"     Height: {cube.position[1]:.2f}m, Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
        
        # 检查停止条件
        if np.linalg.norm(cube.velocity) < 0.3 and abs(cube.position[1] - 1.0) < 0.2:
            print(f"  ✅ Cube settled at t={time:.1f}s")
            # 延长显示
            for _ in range(25):
                positions.append(cube.position.copy())
            break
    
    print(f"\n📊 Simulation Results:")
    print(f"   Total bounces: {collisions}")
    print(f"   Final height: {cube.position[1]:.2f}m")
    print(f"   Final position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
    
    # 生成视频帧
    print("\n🎬 Generating optimized video frames...")
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
        
        frame = create_optimized_frame(cube, time, positions[:i+1], i)
        frames.append(frame)
        
        if i % (len(positions) // 8) == 0:
            progress = (i / len(positions)) * 100
            print(f"   Progress: {progress:.0f}% ({len(frames)} frames)")
    
    print(f"✅ Generated {len(frames)} frames")
    
    # 保存视频
    output_path = "/root/virtual/output/videos/optimized_ground_view_demo.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if save_optimized_video(frames, output_path, fps):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"🎉 Video saved: {output_path} ({size_mb:.1f}MB)")
        return output_path
    else:
        print("❌ Video save failed")
        return None

def save_optimized_video(frames, output_path, fps):
    """保存优化视角视频"""
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
            
            if i % 15 == 0:
                print(f"   Writing frame {i+1}/{len(frames)}")
        
        out.release()
        return True
        
    except Exception as e:
        print(f"Video save error: {e}")
        return False

if __name__ == "__main__":
    try:
        result = create_optimized_demo()
        
        if result:
            print("\n" + "=" * 60)
            print("🎉 OPTIMIZED VIEW DEMO SUCCESSFUL!")
            print(f"📹 Video: {result}")
            print("\n🔑 Key Optimizations Based on Reference Image:")
            print("✅ Lower viewing angle (elev=15°) for better X-Z plane view")
            print("✅ Optimized azimuth angle (35°) for ideal perspective")
            print("✅ Enhanced checkerboard ground pattern")
            print("✅ Clearer coordinate axis indicators")
            print("✅ Better depth perception with projection lines")
            print("✅ Simplified information display")
            print("✅ Professional color scheme matching reference")
            print("=" * 60)
        else:
            print("\n❌ Demo failed")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
