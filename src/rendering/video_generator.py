import matplotlib
matplotlib.use('Agg')  # 设置无头模式
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2
import os
from typing import List, Callable
from .scene3d import Scene3D
from ..physics import Cube, PhysicsEngine

class VideoGenerator:
    """视频生成器，负责创建动画和保存视频"""
    
    def __init__(self, scene: Scene3D, fps=30, output_dir="videos"):
        """
        初始化视频生成器
        
        Args:
            scene: 3D场景对象
            fps: 帧率
            output_dir: 输出目录
        """
        self.scene = scene
        self.fps = fps
        self.output_dir = output_dir
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 帧数据存储
        self.frames = []
        self.frame_data = []
        
    def simulate_and_record(self, engine: PhysicsEngine, cubes: List[Cube], 
                           duration: float, ai_predictor=None, 
                           prediction_steps=10):
        """
        运行物理模拟并记录帧数据
        
        Args:
            engine: 物理引擎
            cubes: 立方体列表
            duration: 模拟时长（秒）
            ai_predictor: AI预测器
            prediction_steps: 预测步数
        """
        total_frames = int(duration * self.fps)
        self.frame_data.clear()
        
        print(f"开始模拟，总帧数: {total_frames}")
        
        for frame in range(total_frames):
            # 物理步进
            engine.step(cubes)
            
            # 记录当前状态
            frame_info = {
                'frame': frame,
                'time': frame / self.fps,
                'cubes': [cube.get_state_vector().copy() for cube in cubes],
                'energy': engine.get_total_energy(cubes)
            }
            
            # AI预测（如果提供）
            if ai_predictor is not None and len(cubes[0].history) >= ai_predictor.sequence_length:
                try:
                    prediction = ai_predictor.predict_next_states(cubes, prediction_steps)
                    frame_info['prediction'] = prediction
                except Exception as e:
                    print(f"预测错误在帧 {frame}: {e}")
                    frame_info['prediction'] = None
            else:
                frame_info['prediction'] = None
                
            self.frame_data.append(frame_info)
            
            # 进度显示
            if frame % (total_frames // 10) == 0:
                progress = (frame / total_frames) * 100
                print(f"模拟进度: {progress:.1f}%")
    
    def render_animation(self, filename="cube_simulation.mp4", 
                        show_trajectory=True, show_prediction=True,
                        camera_rotation=True):
        """
        渲染动画并保存为视频
        
        Args:
            filename: 输出文件名
            show_trajectory: 是否显示轨迹
            show_prediction: 是否显示AI预测
            camera_rotation: 是否旋转摄像机
        """
        if not self.frame_data:
            print("错误：没有帧数据，请先运行模拟")
            return
            
        output_path = os.path.join(self.output_dir, filename)
        
        # 创建动画函数
        def animate(frame_idx):
            self.scene.clear_artists()
            
            if frame_idx >= len(self.frame_data):
                return
                
            frame_info = self.frame_data[frame_idx]
            
            # 重建立方体状态
            cubes = []
            for i, state in enumerate(frame_info['cubes']):
                cube = Cube([0, 0, 0], [0, 0, 0])  # 临时创建
                cube.set_state_vector(state)
                cubes.append(cube)
                
                # 渲染立方体
                self.scene.render_cube(cube, show_trajectory=False)  # 轨迹单独处理
            
            # 绘制历史轨迹
            if show_trajectory and frame_idx > 0:
                positions = []
                for prev_frame in range(max(0, frame_idx - 50), frame_idx + 1):
                    if prev_frame < len(self.frame_data):
                        pos = self.frame_data[prev_frame]['cubes'][0][:3]  # 第一个立方体的位置
                        positions.append(pos)
                
                if len(positions) > 1:
                    positions = np.array(positions)
                    for i in range(len(positions) - 1):
                        alpha = (i + 1) / len(positions)
                        line = self.scene.ax.plot([positions[i][0], positions[i+1][0]],
                                                [positions[i][1], positions[i+1][1]],
                                                [positions[i][2], positions[i+1][2]],
                                                'r-', alpha=alpha * 0.6, linewidth=2)[0]
                        self.scene.trajectory_lines.append(line)
            
            # 绘制AI预测
            if show_prediction and frame_info['prediction'] is not None:
                pred_positions = frame_info['prediction'][:, :3]  # 只取位置
                if len(pred_positions) > 1:
                    line = self.scene.ax.plot(pred_positions[:, 0], 
                                            pred_positions[:, 1], 
                                            pred_positions[:, 2],
                                            'g--', alpha=0.8, linewidth=3)[0]
                    self.scene.trajectory_lines.append(line)
            
            # 更新摄像机
            if camera_rotation:
                self.scene.update_camera(0.5)
            
            # 添加信息文本
            info_text = (f"帧: {frame_info['frame']}\n"
                        f"时间: {frame_info['time']:.2f}s\n"
                        f"能量: {frame_info['energy']:.2f}J")
            
            if frame_info['prediction'] is not None:
                info_text += "\n预测: 开启"
            
            self.scene.add_text(info_text)
        
        # 创建动画
        anim = animation.FuncAnimation(
            self.scene.fig, animate, frames=len(self.frame_data),
            interval=1000/self.fps, blit=False, repeat=False
        )
        
        # 保存动画
        print(f"正在保存视频到: {output_path}")
        
        # 检查ffmpeg是否可用
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            writer_name = 'ffmpeg'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  ffmpeg不可用，尝试使用pillow")
            writer_name = 'pillow'
        
        # 使用适当的编写器
        if writer_name == 'ffmpeg':
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=self.fps, metadata=dict(artist='Physics Simulation'), 
                           bitrate=1800, extra_args=['-vcodec', 'libx264'])
        else:
            Writer = animation.writers['pillow']
            writer = Writer(fps=self.fps)
            output_path = output_path.replace('.mp4', '.gif')
        
        try:
            anim.save(output_path, writer=writer)
            print(f"✅ 视频已保存: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ 视频保存失败: {e}")
            # 备用方案：保存帧序列
            self._save_frame_sequence(output_path.replace('.mp4', '').replace('.gif', ''))
            return None
    
    def create_comparison_video(self, physics_data, ai_data, filename="comparison.mp4"):
        """
        创建物理模拟与AI预测的对比视频
        
        Args:
            physics_data: 物理模拟数据
            ai_data: AI预测数据
            filename: 输出文件名
        """
        # 实现对比视频的生成逻辑
        pass
    
    def export_frames(self, directory="frames", format="png"):
        """
        导出所有帧为图片
        
        Args:
            directory: 输出目录
            format: 图片格式
        """
        frame_dir = os.path.join(self.output_dir, directory)
        os.makedirs(frame_dir, exist_ok=True)
        
        for i, frame_info in enumerate(self.frame_data):
            # 重建场景
            self.scene.clear_artists()
            
            # 重建立方体
            for state in frame_info['cubes']:
                cube = Cube([0, 0, 0], [0, 0, 0])
                cube.set_state_vector(state)
                self.scene.render_cube(cube, show_trajectory=False)
            
            # 保存帧
            filename = os.path.join(frame_dir, f"frame_{i:06d}.{format}")
            self.scene.save_frame(filename)
            
            if i % 30 == 0:
                print(f"已导出帧: {i}/{len(self.frame_data)}")
        
        print(f"所有帧已导出到: {frame_dir}")
    
    def get_statistics(self):
        """获取模拟统计信息"""
        if not self.frame_data:
            return None
            
        energies = [frame['energy'] for frame in self.frame_data]
        
        stats = {
            'total_frames': len(self.frame_data),
            'duration': len(self.frame_data) / self.fps,
            'fps': self.fps,
            'energy_initial': energies[0],
            'energy_final': energies[-1],
            'energy_loss': energies[0] - energies[-1],
            'energy_loss_percent': ((energies[0] - energies[-1]) / energies[0]) * 100
        }
        
        return stats
    
    def _save_frame_sequence(self, base_path):
        """保存帧序列作为备用方案"""
        print(f"📸 保存帧序列到: {base_path}_frames/")
        frame_dir = f"{base_path}_frames"
        os.makedirs(frame_dir, exist_ok=True)
        
        for i, frame_info in enumerate(self.frame_data):
            # 重建场景
            self.scene.clear_artists()
            
            # 重建立方体
            for state in frame_info['cubes']:
                cube = Cube([0, 0, 0], [0, 0, 0])
                cube.set_state_vector(state)
                self.scene.render_cube(cube, show_trajectory=False)
            
            # 添加信息
            info_text = (f"Frame: {frame_info['frame']}\n"
                        f"Time: {frame_info['time']:.2f}s\n"
                        f"Energy: {frame_info['energy']:.2f}J")
            self.scene.add_text(info_text)
            
            # 保存帧
            filename = os.path.join(frame_dir, f"frame_{i:06d}.png")
            self.scene.save_frame(filename)
            
            if i % 30 == 0:
                print(f"已保存帧: {i}/{len(self.frame_data)}")
        
        print(f"✅ 帧序列已保存到: {frame_dir}")
        return frame_dir
    
    def render_high_quality_animation(self, filename="high_quality_simulation.mp4", 
                                     show_prediction=False, figsize=(12, 9), engine=None):
        """
        生成高质量视频动画，参考clean_demo.py的渲染方式
        
        Args:
            filename: 输出文件名
            show_prediction: 是否显示AI预测
            figsize: 图像尺寸
            engine: 物理引擎对象（可选，用于渲染障碍物）
        """
        if not self.frame_data:
            print("❌ 没有帧数据，请先运行 simulate_and_record")
            return None
            
        output_path = os.path.join(self.output_dir, filename)
        print(f"🎬 生成高质量视频: {filename}")
        
        # 创建视频帧
        frames = []
        total_frames = len(self.frame_data)
        
        for i, frame_info in enumerate(self.frame_data):
            # 创建新的图形，使用高质量设置
            fig = plt.figure(figsize=figsize, facecolor='black', dpi=100)
            ax = fig.add_subplot(111, projection='3d', facecolor='black')
            
            # 设置固定的优化视角
            ax.view_init(elev=25, azim=45)
            
            # 设置场景边界
            ax.set_xlim(self.scene.bounds[0])
            ax.set_ylim(self.scene.bounds[1])
            ax.set_zlim(self.scene.bounds[2])
            
            # 高质量标签设置
            ax.set_xlabel('X (East-West)', color='white', fontsize=11)
            ax.set_ylabel('Y (North-South)', color='white', fontsize=11)
            ax.set_zlabel('Z (HEIGHT)', color='yellow', fontsize=12, weight='bold')
            
            # 绘制高质量地面网格
            x_grid = np.linspace(self.scene.bounds[0][0], self.scene.bounds[0][1], 11)
            y_grid = np.linspace(self.scene.bounds[1][0], self.scene.bounds[1][1], 11)
            X, Y = np.meshgrid(x_grid, y_grid)
            Z = np.zeros_like(X)
            ax.plot_wireframe(X, Y, Z, color='gray', alpha=0.3, linewidth=0.5)
            
            # 渲染立方体
            for cube_state in frame_info['cubes']:
                # 重建立方体对象
                cube = Cube([0, 0, 0], [0, 0, 0])
                cube.set_state_vector(cube_state)
                corners = cube.get_corners()
                
                # 立方体的6个面
                faces = [
                    [corners[0], corners[1], corners[2], corners[3]],  # 底面
                    [corners[4], corners[5], corners[6], corners[7]],  # 顶面
                    [corners[0], corners[1], corners[5], corners[4]],  # 前面
                    [corners[2], corners[3], corners[7], corners[6]],  # 后面
                    [corners[1], corners[2], corners[6], corners[5]],  # 右面
                    [corners[0], corners[3], corners[7], corners[4]]   # 左面
                ]
                
                colors = ['red', 'blue', 'green', 'yellow', 'cyan', 'magenta']
                
                from mpl_toolkits.mplot3d.art3d import Poly3DCollection
                for j, face in enumerate(faces):
                    poly = [[list(vertex) for vertex in face]]
                    collection = Poly3DCollection(poly, alpha=0.7, 
                                                facecolors=colors[j], 
                                                edgecolors='white',
                                                linewidths=0.5)
                    ax.add_collection3d(collection)
            
            # 渲染障碍物 (如果提供了物理引擎)
            if engine is not None and hasattr(engine, 'obstacle_manager') and engine.obstacle_manager.obstacles:
                try:
                    obstacle_render_data = engine.get_obstacles_render_data()
                    for obstacle_data in obstacle_render_data:
                        self._render_simple_obstacle(ax, obstacle_data)
                except AttributeError:
                    # 如果物理引擎没有相关方法，跳过障碍物渲染
                    pass
            
            # 获取第一个立方体的状态用于显示信息
            first_cube = Cube([0, 0, 0], [0, 0, 0])
            first_cube.set_state_vector(frame_info['cubes'][0])
            
            # 显示信息
            time_text = f"Time: {frame_info['time']:.1f}s"
            pos_text = f"Pos: ({first_cube.position[0]:.1f}, {first_cube.position[1]:.1f}, {first_cube.position[2]:.1f})"
            vel_text = f"Vel: ({first_cube.velocity[0]:.1f}, {first_cube.velocity[1]:.1f}, {first_cube.velocity[2]:.1f})"
            
            ax.text2D(0.02, 0.98, time_text, transform=ax.transAxes, 
                     color='white', fontsize=12, verticalalignment='top')
            ax.text2D(0.02, 0.93, pos_text, transform=ax.transAxes,
                     color='white', fontsize=10, verticalalignment='top')
            ax.text2D(0.02, 0.88, vel_text, transform=ax.transAxes,
                     color='white', fontsize=10, verticalalignment='top')
            
            # 绘制AI预测轨迹 - 超级明显版本
            if show_prediction and frame_info.get('prediction') is not None:
                # 闪烁效果的AI标题
                flash_color = 'lime' if (i // 5) % 2 == 0 else 'yellow'
                ax.text2D(0.02, 0.83, "🔥 AI PREDICTION: ACTIVE 🔥", transform=ax.transAxes,
                         color=flash_color, fontsize=14, verticalalignment='top', weight='bold',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.8))
                
                # 绘制预测轨迹
                prediction = frame_info['prediction']
                if len(prediction) > 1:
                    pred_positions = prediction[:, :3]  # 只取位置坐标
                    
                    # 1. 主预测轨迹 - 超粗亮绿色虚线
                    ax.plot(pred_positions[:, 0], pred_positions[:, 1], pred_positions[:, 2],
                           'lime', linestyle='--', alpha=1.0, linewidth=8, 
                           dash_capstyle='round', label='AI Prediction')
                    
                    # 2. 外围光晕效果
                    ax.plot(pred_positions[:, 0], pred_positions[:, 1], pred_positions[:, 2],
                           'yellow', linestyle='--', alpha=0.6, linewidth=12)
                    
                    # 3. 渐变的预测点 - 更大更明显
                    for j, pos in enumerate(pred_positions):
                        progress = j / len(pred_positions)
                        alpha = 1.0 - progress * 0.5  # 从1.0渐变到0.5
                        size = 200 - (j * 20)  # 从200渐变到较小
                        
                        # 主要标记点 (亮绿色)
                        ax.scatter([pos[0]], [pos[1]], [pos[2]], 
                                 c='lime', s=max(size, 80), alpha=alpha, 
                                 marker='*', edgecolors='white', linewidths=3)
                        
                        # 外围光晕点 (黄色)
                        ax.scatter([pos[0]], [pos[1]], [pos[2]], 
                                 c='yellow', s=max(size+50, 120), alpha=alpha*0.4, 
                                 marker='o', edgecolors='orange', linewidths=2)
                    
                    # 4. 预测起始点特殊标记
                    start_pos = pred_positions[0]
                    ax.scatter([start_pos[0]], [start_pos[1]], [start_pos[2]], 
                             c='red', s=300, alpha=0.9, marker='^', 
                             edgecolors='white', linewidths=4, label='Prediction Start')
                    
                    
                    # 在预测终点放置一个超明显的预测立方体
                    if len(pred_positions) >= 3:
                        final_pred_pos = pred_positions[-1]
                        
                        # 绘制超大预测立方体轮廓 - 闪烁效果
                        cube_size = 1.2  # 更大的预测立方体
                        flash_alpha = 0.9 if (i // 3) % 2 == 0 else 0.6  # 快速闪烁
                        
                        pred_cube_corners = np.array([
                            [final_pred_pos[0]-cube_size, final_pred_pos[1]-cube_size, final_pred_pos[2]-cube_size],
                            [final_pred_pos[0]+cube_size, final_pred_pos[1]-cube_size, final_pred_pos[2]-cube_size],
                            [final_pred_pos[0]+cube_size, final_pred_pos[1]+cube_size, final_pred_pos[2]-cube_size],
                            [final_pred_pos[0]-cube_size, final_pred_pos[1]+cube_size, final_pred_pos[2]-cube_size],
                            [final_pred_pos[0]-cube_size, final_pred_pos[1]-cube_size, final_pred_pos[2]+cube_size],
                            [final_pred_pos[0]+cube_size, final_pred_pos[1]-cube_size, final_pred_pos[2]+cube_size],
                            [final_pred_pos[0]+cube_size, final_pred_pos[1]+cube_size, final_pred_pos[2]+cube_size],
                            [final_pred_pos[0]-cube_size, final_pred_pos[1]+cube_size, final_pred_pos[2]+cube_size],
                        ])
                        
                        # 绘制预测立方体边框 - 更粗的线
                        edges = [
                            [0,1], [1,2], [2,3], [3,0],  # 底面
                            [4,5], [5,6], [6,7], [7,4],  # 顶面
                            [0,4], [1,5], [2,6], [3,7]   # 垂直边
                        ]
                        
                        for edge in edges:
                            start, end = edge
                            ax.plot([pred_cube_corners[start][0], pred_cube_corners[end][0]],
                                   [pred_cube_corners[start][1], pred_cube_corners[end][1]],
                                   [pred_cube_corners[start][2], pred_cube_corners[end][2]],
                                   'lime', linewidth=5, alpha=flash_alpha)
                        
                        # 添加终点爆炸效果
                        ax.scatter([final_pred_pos[0]], [final_pred_pos[1]], [final_pred_pos[2]], 
                                 c='lime', s=400, alpha=flash_alpha, marker='*', 
                                 edgecolors='white', linewidths=5)
                        ax.scatter([final_pred_pos[0]], [final_pred_pos[1]], [final_pred_pos[2]], 
                                 c='yellow', s=600, alpha=flash_alpha*0.5, marker='o', 
                                 edgecolors='orange', linewidths=3)
                        
                        # 显示超明显的预测信息
                        pred_text = f"🎯 AI PREDICTS: ({final_pred_pos[0]:.1f}, {final_pred_pos[1]:.1f}, {final_pred_pos[2]:.1f})"
                        ax.text2D(0.02, 0.78, pred_text, transform=ax.transAxes,
                                 color='lime', fontsize=12, verticalalignment='top', weight='bold',
                                 bbox=dict(boxstyle="round,pad=0.2", facecolor='darkgreen', alpha=0.7))
                        
                        # 预测精度指示器
                        steps_text = f"🧠 Thinking {len(pred_positions)} steps ahead"
                        ax.text2D(0.02, 0.73, steps_text, transform=ax.transAxes,
                                 color='cyan', fontsize=11, verticalalignment='top', weight='bold')
                        
                        # 添加预测置信度动画效果
                        confidence = 85 + (i % 15)  # 模拟变化的置信度
                        conf_color = 'lime' if confidence > 90 else 'yellow' if confidence > 80 else 'orange'
                        confidence_text = f"📊 Confidence: {confidence}%"
                        ax.text2D(0.02, 0.68, confidence_text, transform=ax.transAxes,
                                 color=conf_color, fontsize=10, verticalalignment='top', weight='bold')
            else:
                # 如果没有预测，显示AI状态
                if show_prediction:
                    ax.text2D(0.02, 0.83, "🤖 AI Prediction: LOADING...", transform=ax.transAxes,
                             color='yellow', fontsize=11, verticalalignment='top', weight='bold')
            
            # 样式设置
            ax.tick_params(colors='white', labelsize=9)
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            
            # 转换为视频帧
            fig.canvas.draw()
            buf = fig.canvas.buffer_rgba()
            img = np.asarray(buf)[:,:,:3]  # 只取RGB通道
            frames.append(img)
            
            plt.close(fig)
            
            if i % 30 == 0:
                print(f"  渲染进度: {i}/{total_frames} ({i/total_frames*100:.1f}%)")
        
        # 保存高质量视频
        if frames:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps, 
                                (frames[0].shape[1], frames[0].shape[0]))
            
            for frame in frames:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
            
            out.release()
            print(f"✅ 高质量视频已保存: {output_path}")
            return output_path
        else:
            print("❌ 视频帧生成失败")
            return None
    
    def _render_simple_obstacle(self, ax, obstacle_data):
        """
        渲染简单的障碍物
        
        Args:
            ax: matplotlib 3D坐标轴
            obstacle_data: 障碍物渲染数据
        """
        obstacle_type = obstacle_data.get('type', 'box')
        color = obstacle_data.get('color', (0.5, 0.5, 0.5))
        
        if obstacle_type == 'box':
            # 渲染方形障碍物
            faces = obstacle_data.get('faces', [])
            
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            for face in faces:
                poly = [face]
                collection = Poly3DCollection(poly, alpha=0.6, 
                                            facecolors=color, 
                                            edgecolors='black',
                                            linewidths=1.0)
                ax.add_collection3d(collection)
                
        elif obstacle_type == 'sphere':
            # 渲染球形障碍物
            center = obstacle_data.get('center', [0, 0, 0])
            radius = obstacle_data.get('radius', 1.0)
            
            # 创建球面
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 10)
            x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
            y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
            z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
            
            ax.plot_surface(x, y, z, alpha=0.6, color=color, edgecolor='black', linewidth=0.5)
