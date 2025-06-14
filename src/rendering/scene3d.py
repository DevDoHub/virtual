import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from typing import List
from ..physics import Cube

class Scene3D:
    """3D场景管理和渲染"""
    
    def __init__(self, figsize=(12, 9), bounds=None):
        """
        初始化3D场景
        
        Args:
            figsize: 图像尺寸
            bounds: 场景边界 [(xmin,xmax), (ymin,ymax), (zmin,zmax)]
        """
        self.fig = plt.figure(figsize=figsize, facecolor='black')
        self.ax = self.fig.add_subplot(111, projection='3d', facecolor='black')
        
        # 场景边界
        if bounds is None:
            self.bounds = [(-10, 10), (0, 20), (-10, 10)]
        else:
            self.bounds = bounds
            
        # 渲染设置
        self.setup_scene()
        
        # 存储渲染对象
        self.cube_artists = []
        self.trajectory_lines = []
        
        # 摄像机设置
        self.camera_angle = 0
        self.camera_elevation = 20
        self.camera_distance = 25
        
    def setup_scene(self):
        """设置场景环境"""
        # 设置坐标轴范围
        self.ax.set_xlim(self.bounds[0])
        self.ax.set_ylim(self.bounds[1])
        self.ax.set_zlim(self.bounds[2])
        
        # 坐标轴标签
        self.ax.set_xlabel('X', color='white', fontsize=12)
        self.ax.set_ylabel('Y', color='white', fontsize=12)
        self.ax.set_zlabel('Z', color='white', fontsize=12)
        
        # 设置背景色
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
        # 设置网格
        self.ax.grid(True, alpha=0.3)
        
        # 绘制地面网格
        self.draw_ground()
        
        # 设置标题
        self.ax.set_title('3D立方体下落模拟', color='white', fontsize=16, pad=20)
        
        # 设置刻度颜色
        self.ax.tick_params(colors='white')
        
    def draw_ground(self):
        """绘制地面网格"""
        x_range = np.linspace(self.bounds[0][0], self.bounds[0][1], 11)
        z_range = np.linspace(self.bounds[2][0], self.bounds[2][1], 11)
        
        # 绘制网格线
        for x in x_range:
            self.ax.plot([x, x], [self.bounds[1][0], self.bounds[1][0]], 
                        [self.bounds[2][0], self.bounds[2][1]], 
                        'w-', alpha=0.2, linewidth=0.5)
        
        for z in z_range:
            self.ax.plot([self.bounds[0][0], self.bounds[0][1]], 
                        [self.bounds[1][0], self.bounds[1][0]], 
                        [z, z], 'w-', alpha=0.2, linewidth=0.5)
    
    def render_cube(self, cube: Cube, show_trajectory=True, trajectory_length=50):
        """渲染单个立方体"""
        # 获取立方体顶点
        corners = cube.get_corners()
        
        # 定义立方体的6个面
        faces = [
            [corners[0], corners[1], corners[2], corners[3]],  # bottom
            [corners[4], corners[5], corners[6], corners[7]],  # top
            [corners[0], corners[1], corners[5], corners[4]],  # front
            [corners[2], corners[3], corners[7], corners[6]],  # back
            [corners[1], corners[2], corners[6], corners[5]],  # right
            [corners[4], corners[7], corners[3], corners[0]]   # left
        ]
        
        # 面的颜色（6个面不同颜色）
        face_colors = [
            [0.8, 0.2, 0.2, 0.8],  # 红色 - 底面
            [0.2, 0.8, 0.2, 0.8],  # 绿色 - 顶面
            [0.2, 0.2, 0.8, 0.8],  # 蓝色 - 前面
            [0.8, 0.8, 0.2, 0.8],  # 黄色 - 后面
            [0.8, 0.2, 0.8, 0.8],  # 品红 - 右面
            [0.2, 0.8, 0.8, 0.8]   # 青色 - 左面
        ]
        
        # 创建3D多边形集合
        cube_collection = Poly3DCollection(faces, alpha=0.8)
        cube_collection.set_facecolors(face_colors)
        cube_collection.set_edgecolor('white')
        cube_collection.set_linewidth(1)
        
        # 添加到场景
        self.ax.add_collection3d(cube_collection)
        self.cube_artists.append(cube_collection)
        
        # 绘制轨迹
        if show_trajectory and len(cube.history) > 1:
            positions = np.array([state[:3] for state in cube.history])
            if len(positions) > trajectory_length:
                positions = positions[-trajectory_length:]
            
            # 轨迹线条，颜色从暗到亮
            for i in range(len(positions) - 1):
                alpha = (i + 1) / len(positions)
                line = self.ax.plot([positions[i][0], positions[i+1][0]],
                                  [positions[i][1], positions[i+1][1]],
                                  [positions[i][2], positions[i+1][2]],
                                  'r-', alpha=alpha * 0.6, linewidth=2)[0]
                self.trajectory_lines.append(line)
    
    def render_prediction(self, predicted_positions, actual_positions=None):
        """渲染AI预测轨迹"""
        if len(predicted_positions) > 1:
            positions = np.array(predicted_positions)
            
            # 预测轨迹用虚线表示
            line = self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                               'g--', alpha=0.8, linewidth=3, label='AI预测')[0]
            self.trajectory_lines.append(line)
            
        # 如果有实际轨迹，也绘制出来进行对比
        if actual_positions is not None and len(actual_positions) > 1:
            positions = np.array(actual_positions)
            line = self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                               'b-', alpha=0.8, linewidth=3, label='实际轨迹')[0]
            self.trajectory_lines.append(line)
    
    def clear_artists(self):
        """清除所有渲染对象"""
        # 移除立方体
        for artist in self.cube_artists:
            artist.remove()
        self.cube_artists.clear()
        
        # 移除轨迹线
        for line in self.trajectory_lines:
            line.remove()
        self.trajectory_lines.clear()
    
    def update_camera(self, angle_increment=1):
        """更新摄像机角度"""
        self.camera_angle += angle_increment
        self.ax.view_init(elev=self.camera_elevation, azim=self.camera_angle)
    
    def set_camera(self, elevation=None, azimuth=None):
        """设置摄像机角度"""
        if elevation is not None:
            self.camera_elevation = elevation
        if azimuth is not None:
            self.camera_angle = azimuth
        self.ax.view_init(elev=self.camera_elevation, azim=self.camera_angle)
    
    def add_text(self, text, position=(0.02, 0.98)):
        """添加文本信息"""
        self.ax.text2D(position[0], position[1], text, 
                      transform=self.ax.transAxes, 
                      fontsize=12, color='white',
                      verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
    
    def save_frame(self, filename):
        """保存当前帧"""
        self.fig.savefig(filename, facecolor='black', dpi=100, bbox_inches='tight')
    
    def show(self):
        """显示场景"""
        plt.show()
    
    def close(self):
        """关闭场景"""
        plt.close(self.fig)
