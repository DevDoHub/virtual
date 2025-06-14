#!/usr/bin/env python3
"""
改进的视频生成器 - 清晰展示立方体下落过程
============================================

主要改进:
1. 固定摄像机视角，不旋转
2. 增大立方体尺寸，提高可见性
3. 清晰的碰撞效果
4. 真实的物理参数
5. 对比鲜明的颜色

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

class ImprovedVideoGenerator:
    """改进的视频生成器，专注于清晰展示物理过程"""
    
    def __init__(self, fps=60):
        """
        初始化视频生成器
        
        Args:
            fps: 帧率，建议60fps获得流畅效果
        """
        self.fps = fps
        self.frames = []
        
    def create_clear_physics_demo(self, scenario_name, description, 
                                 initial_pos, initial_vel, duration=8.0,
                                 gravity=9.81, restitution=0.8, cube_size=2.0):
        """
        创建清晰的物理演示视频
        
        Args:
            scenario_name: 场景名称
            description: 场景描述
            initial_pos: 初始位置 [x, y, z]
            initial_vel: 初始速度 [vx, vy, vz]
            duration: 持续时间(秒)
            gravity: 重力加速度
            restitution: 弹性系数
            cube_size: 立方体大小
        """
        
        print(f"🎬 创建视频: {scenario_name}")
        print(f"📝 描述: {description}")
        print("-" * 50)
        
        # 创建物理环境
        bounds = [(-8, 8), (0, 20), (-8, 8)]  # 稍小的空间，更容易看清
        engine = PhysicsEngine(gravity=gravity, bounds=bounds)
        
        # 创建立方体 - 更大更明显
        cube = Cube(
            position=initial_pos,
            velocity=initial_vel,
            size=cube_size,  # 更大的立方体
            mass=1.0
        )
        cube.restitution = restitution
        
        print(f"📦 立方体参数:")
        print(f"   位置: {cube.position}")
        print(f"   速度: {cube.velocity}")
        print(f"   大小: {cube_size}m")
        print(f"   重力: {gravity} m/s²")
        print(f"   弹性: {restitution}")
        
        # 计算总步数
        dt = 1.0 / self.fps
        total_steps = int(duration / dt)
        
        print(f"⚙️  仿真参数:")
        print(f"   帧率: {self.fps} fps")
        print(f"   时间步长: {dt:.4f}s")
        print(f"   总步数: {total_steps}")
        print(f"   持续时间: {duration}s")
        
        # 仿真并收集数据
        print("🔄 执行物理仿真...")
        positions = []
        velocities = []
        collision_events = []
        
        for step in range(total_steps):
            current_time = step * dt
            
            # 记录碰撞前的状态
            pre_velocity = cube.velocity.copy()
            pre_position = cube.position.copy()
            
            # 执行物理步进
            engine.step([cube])
            
            # 检测碰撞
            post_velocity = cube.velocity.copy()
            velocity_change = np.linalg.norm(post_velocity - pre_velocity)
            
            if velocity_change > 0.5:  # 检测到显著速度变化（碰撞）
                collision_events.append({
                    'step': step,
                    'time': current_time,
                    'position': cube.position.copy(),
                    'velocity_before': pre_velocity,
                    'velocity_after': post_velocity
                })
                print(f"💥 碰撞检测! t={current_time:.2f}s, 位置=({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})")
            
            # 存储状态
            positions.append(cube.position.copy())
            velocities.append(cube.velocity.copy())
            
            # 进度显示
            if step % (total_steps // 10) == 0:
                progress = (step / total_steps) * 100
                print(f"  ⏱️  仿真进度: {progress:.0f}% (t={current_time:.1f}s)")
        
        print(f"✅ 仿真完成! 检测到 {len(collision_events)} 次碰撞")
        
        # 生成视频帧
        print("🎥 生成视频帧...")
        self.frames = []
        
        for step in range(0, total_steps, 2):  # 每2帧取1帧，减少文件大小
            current_time = step * dt
            cube.position = positions[step]
            cube.velocity = velocities[step]
            
            # 检查是否为碰撞时刻
            is_collision = any(abs(event['step'] - step) <= 2 for event in collision_events)
            
            # 创建帧
            frame = self._create_frame(cube, current_time, bounds, 
                                     positions[:step+1], is_collision,
                                     scenario_name, description)
            self.frames.append(frame)
            
            if step % (total_steps // 5) == 0:
                progress = (step / total_steps) * 100
                print(f"  📹 视频进度: {progress:.0f}%")
        
        # 保存视频
        output_path = f"/root/virtual/output/videos/{scenario_name}_improved.mp4"
        success = self._save_video(output_path)
        
        if success:
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ 视频生成成功!")
            print(f"📁 文件路径: {output_path}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            print(f"🎬 帧数: {len(self.frames)}")
            print(f"⏱️  时长: {len(self.frames)/30:.1f}秒")
            return output_path
        else:
            print("❌ 视频生成失败")
            return None
    
    def _create_frame(self, cube, current_time, bounds, trajectory, 
                     is_collision, title, description):
        """创建单个视频帧"""
        
        # 创建图形 - 更大的尺寸
        fig = plt.figure(figsize=(16, 12), facecolor='black')
        
        # 主要3D视图 - 占据大部分空间
        ax_main = fig.add_subplot(111, projection='3d', facecolor='black')
        
        # 固定摄像机视角 - Y轴垂直向上，更直观的视角
        ax_main.view_init(elev=30, azim=45)
        
        # 设置场景
        ax_main.set_xlim(bounds[0])
        ax_main.set_ylim(bounds[1]) 
        ax_main.set_zlim(bounds[2])
        
        # 坐标轴设置 - 黑色背景下的白色坐标轴，Y轴为高度
        ax_main.set_xlabel('X (Left-Right)', color='white', fontsize=14)
        ax_main.set_ylabel('Y (Height)', color='white', fontsize=14, weight='bold')
        ax_main.set_zlabel('Z (Forward-Back)', color='white', fontsize=14)
        
        # 设置坐标轴颜色
        ax_main.tick_params(colors='white')
        ax_main.xaxis.pane.fill = False
        ax_main.yaxis.pane.fill = False
        ax_main.zaxis.pane.fill = False
        
        # 网格线
        ax_main.grid(True, alpha=0.3, color='gray')
        
        # 绘制地面 - 更明显的地面
        ground_x, ground_z = np.meshgrid(
            np.linspace(bounds[0][0], bounds[0][1], 10),
            np.linspace(bounds[2][0], bounds[2][1], 10)
        )
        ground_y = np.zeros_like(ground_x)
        ax_main.plot_surface(ground_x, ground_y, ground_z, 
                           alpha=0.2, color='gray', linewidth=0)
        
        # 绘制立方体 - 根据是否碰撞改变颜色
        if is_collision:
            cube_color = 'red'      # 碰撞时红色
            alpha = 0.9
        else:
            cube_color = 'cyan'     # 正常时青色
            alpha = 0.8
            
        self._draw_enhanced_cube(ax_main, cube, cube_color, alpha)
        
        # 绘制轨迹 - 更明显的轨迹线
        if len(trajectory) > 1:
            traj_array = np.array(trajectory)
            ax_main.plot(traj_array[:, 0], traj_array[:, 1], traj_array[:, 2],
                        'yellow', linewidth=3, alpha=0.7, label='轨迹')
        
        # 标题和信息 - 更大更清晰，使用英文
        info_text = f"""{title}
{description}
Time: {current_time:.2f}s
Position: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})m
Velocity: {np.linalg.norm(cube.velocity):.1f} m/s"""
        
        if is_collision:
            info_text += "\nCOLLISION!"
            
        ax_main.text2D(0.02, 0.98, info_text, transform=ax_main.transAxes,
                      fontsize=16, verticalalignment='top', color='white',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.8))
        
        # 速度矢量 - 显示运动方向
        if np.linalg.norm(cube.velocity) > 0.1:
            vel_scale = 2.0  # 速度矢量缩放
            vel_end = cube.position + cube.velocity * vel_scale
            ax_main.quiver(cube.position[0], cube.position[1], cube.position[2],
                          cube.velocity[0], cube.velocity[1], cube.velocity[2],
                          color='yellow', arrow_length_ratio=0.1, linewidth=3)
        
        plt.tight_layout()
        
        # 转换为numpy数组
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        buf = buf.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        buf = buf[:, :, :3]  # 只取RGB，不要Alpha通道
        
        plt.close(fig)
        return buf
    
    def _draw_enhanced_cube(self, ax, cube, color='cyan', alpha=0.8):
        """绘制增强的立方体"""
        
        # 获取立方体的8个顶点
        corners = cube.get_corners()
        
        # 定义立方体的12条边
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # 底面
            [4, 5], [5, 6], [6, 7], [7, 4],  # 顶面  
            [0, 4], [1, 5], [2, 6], [3, 7]   # 竖直边
        ]
        
        # 绘制边框 - 黑色粗线
        for edge in edges:
            points = corners[edge]
            ax.plot3D(points[:, 0], points[:, 1], points[:, 2], 
                     'black', linewidth=4, alpha=1.0)
        
        # 定义立方体的6个面
        faces = [
            [corners[0], corners[1], corners[2], corners[3]],  # 底面
            [corners[4], corners[5], corners[6], corners[7]],  # 顶面
            [corners[0], corners[1], corners[5], corners[4]],  # 前面
            [corners[2], corners[3], corners[7], corners[6]],  # 后面
            [corners[1], corners[2], corners[6], corners[5]],  # 右面
            [corners[0], corners[3], corners[7], corners[4]]   # 左面
        ]
        
        # 添加面 - 半透明彩色
        face_collection = Poly3DCollection(faces, alpha=alpha, 
                                         facecolor=color, edgecolor='black', linewidth=2)
        ax.add_collection3d(face_collection)
    
    def _save_video(self, output_path):
        """保存视频到文件"""
        try:
            if len(self.frames) == 0:
                print("❌ 没有帧数据")
                return False
            
            # 获取帧尺寸
            height, width, _ = self.frames[0].shape
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))
            
            if not out.isOpened():
                print("❌ 无法创建视频文件")
                return False
            
            # 写入帧
            for frame in self.frames:
                # OpenCV使用BGR格式
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
            
            out.release()
            return True
            
        except Exception as e:
            print(f"❌ 视频保存失败: {e}")
            return False

def create_improved_demos():
    """创建改进的演示视频"""
    
    print("🎬 创建改进的物理演示视频")
    print("重点：清晰展示立方体下落和碰撞过程")
    print("=" * 60)
    
    # 确保输出目录
    os.makedirs('/root/virtual/output/videos', exist_ok=True)
    
    generator = ImprovedVideoGenerator(fps=60)
    
    # 定义改进的场景 - 更容易观察的参数
    scenarios = [
        {
            'name': 'clear_basic_fall',
            'description': '清晰基础下落 - 静态视角',
            'initial_pos': [0, 15, 0],
            'initial_vel': [0, 0, 0],  # 纯下落
            'duration': 6.0,
            'gravity': 9.81,
            'restitution': 0.7,
            'cube_size': 2.5
        },
        {
            'name': 'clear_bouncing_cube',
            'description': '清晰弹跳效果 - 多次碰撞',
            'initial_pos': [0, 12, 0],
            'initial_vel': [0, 0, 0],
            'duration': 8.0,
            'gravity': 9.81,
            'restitution': 0.85,  # 高弹性
            'cube_size': 2.5
        },
        {
            'name': 'clear_angled_fall',
            'description': '倾斜下落 - 多面碰撞',
            'initial_pos': [-3, 15, 2],
            'initial_vel': [2, 0, -1],
            'duration': 10.0,
            'gravity': 9.81,
            'restitution': 0.6,
            'cube_size': 2.0
        },
        {
            'name': 'clear_high_energy',
            'description': '高能碰撞 - 复杂轨迹',
            'initial_pos': [-4, 18, 3],
            'initial_vel': [3, -1, -2],
            'duration': 12.0,
            'gravity': 9.81,
            'restitution': 0.75,
            'cube_size': 2.0
        }
    ]
    
    successful_videos = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 生成视频 {i}/{len(scenarios)}")
        
        try:
            output_path = generator.create_clear_physics_demo(
                scenario['name'],
                scenario['description'],
                scenario['initial_pos'],
                scenario['initial_vel'],
                scenario['duration'],
                scenario['gravity'],
                scenario['restitution'],
                scenario['cube_size']
            )
            
            if output_path:
                successful_videos.append(output_path)
                
        except Exception as e:
            print(f"❌ 视频生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成总结
    print("\n" + "=" * 60)
    print("📊 改进视频生成总结")
    print("=" * 60)
    print(f"✅ 成功生成: {len(successful_videos)} 个视频")
    
    if successful_videos:
        total_size = sum(os.path.getsize(path)/(1024*1024) for path in successful_videos)
        print(f"📦 总文件大小: {total_size:.1f} MB")
        print(f"📁 视频位置: /root/virtual/output/videos/")
        
        print(f"\n📋 生成的视频:")
        for path in successful_videos:
            filename = os.path.basename(path)
            size = os.path.getsize(path) / (1024 * 1024)
            print(f"   ✅ {filename} ({size:.1f} MB)")

if __name__ == "__main__":
    try:
        create_improved_demos()
        print("\n🎉 所有改进视频生成完成!")
        print("💡 特点:")
        print("   - 固定摄像机视角，无旋转")
        print("   - 大尺寸立方体，易于观察")
        print("   - 碰撞时变色提示")
        print("   - 清晰的轨迹线")
        print("   - 实时状态信息显示")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
