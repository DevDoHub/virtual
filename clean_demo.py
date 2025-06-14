#!/usr/bin/env python3
"""
简洁的3D立方体下落演示
使用正确的X-Y地面平面，Z轴垂直坐标系统
"""

import matplotlib
matplotlib.use('Agg')  # 无头环境

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D
import cv2

def create_demo():
    """创建简洁的演示"""
    print("🎬 创建3D立方体下落演示")
    print("📐 坐标系统：X-Y地面平面，Z轴垂直")
    print()
    
    # 创建物理组件
    cube = Cube(position=[0, 0, 10], velocity=[2, 1, 0], size=2.0)
    engine = PhysicsEngine(gravity=9.81)
    scene = Scene3D()
    
    # 创建视频帧
    frames = []
    duration = 5.0  # 5秒
    fps = 30
    total_frames = int(duration * fps)
    
    print(f"🎥 生成 {total_frames} 帧 (5秒 @ 30fps)")
    
    for frame_idx in range(total_frames):
        # 物理模拟
        engine.step([cube])
        
        # 渲染帧
        fig = plt.figure(figsize=(10, 8), facecolor='black')
        ax = fig.add_subplot(111, projection='3d', facecolor='black')
        
        # 设置正确的视角 - 能看到X-Y地面和Z轴垂直
        ax.view_init(elev=20, azim=45)
        
        # 设置场景边界 - X-Y为地面，Z为高度
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.set_zlim([0, 12])
        
        # 标签
        ax.set_xlabel('X (East-West)', color='white')
        ax.set_ylabel('Y (North-South)', color='white') 
        ax.set_zlabel('Z (HEIGHT)', color='yellow', weight='bold')
        
        # 绘制X-Y地面网格 (Z=0)
        x_grid = np.linspace(-5, 5, 11)
        y_grid = np.linspace(-5, 5, 11)
        X, Y = np.meshgrid(x_grid, y_grid)
        Z = np.zeros_like(X)
        ax.plot_wireframe(X, Y, Z, color='gray', alpha=0.3, linewidth=0.5)
        
        # 绘制立方体
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
        for i, face in enumerate(faces):
            poly = [[list(vertex) for vertex in face]]
            ax.add_collection3d(Poly3DCollection(poly, alpha=0.7, 
                                               facecolors=colors[i], 
                                               edgecolors='white'))
        
        # 信息显示
        ax.text2D(0.02, 0.98, f"Time: {frame_idx/fps:.1f}s", 
                 transform=ax.transAxes, color='white', fontsize=12,
                 verticalalignment='top')
        ax.text2D(0.02, 0.93, f"Pos: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})", 
                 transform=ax.transAxes, color='white', fontsize=10,
                 verticalalignment='top')
        ax.text2D(0.02, 0.88, f"Vel: ({cube.velocity[0]:.1f}, {cube.velocity[1]:.1f}, {cube.velocity[2]:.1f})", 
                 transform=ax.transAxes, color='white', fontsize=10,
                 verticalalignment='top')
        
        # 样式设置
        ax.tick_params(colors='white', labelsize=8)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        # 转换为视频帧
        fig.canvas.draw()
        # 修复matplotlib API兼容性
        buf = fig.canvas.buffer_rgba()
        img = np.asarray(buf)[:,:,:3]  # 只取RGB通道
        frames.append(img)
        
        plt.close(fig)
        
        if frame_idx % 30 == 0:
            print(f"  帧 {frame_idx}/{total_frames} - Z高度: {cube.position[2]:.1f}m")
    
    # 保存视频
    output_path = 'clean_demo.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, 
                         (frames[0].shape[1], frames[0].shape[0]))
    
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    
    out.release()
    print(f"✅ 视频已保存: {output_path}")
    print(f"📊 立方体最终位置: {cube.position}")
    
    return output_path

if __name__ == "__main__":
    create_demo()
