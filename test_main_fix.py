#!/usr/bin/env python3
"""
快速测试修复的main.py
"""

import matplotlib
matplotlib.use('Agg')

import numpy as np
import os
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 直接导入模块
import sys
sys.path.append('.')

from src.physics import Cube, PhysicsEngine

def test_high_quality_video():
    """生成高质量视频，模仿clean_demo.py的方式"""
    print("🎬 测试高质量视频生成")
    
    # 创建物理组件
    cube = Cube(position=[-3, 2, 18], velocity=[4, -1, -2], size=1.5)  # high_energy场景
    engine = PhysicsEngine(gravity=9.81)
    
    # 创建视频帧
    frames = []
    duration = 3.0  # 3秒测试
    fps = 30
    total_frames = int(duration * fps)
    
    print(f"🎥 生成 {total_frames} 帧")
    
    for frame_idx in range(total_frames):
        # 物理模拟
        engine.step([cube])
        
        # 渲染帧 - 使用与clean_demo.py相同的方式
        fig = plt.figure(figsize=(12, 9), facecolor='black')
        ax = fig.add_subplot(111, projection='3d', facecolor='black')
        
        # 固定视角 - 不旋转！
        ax.view_init(elev=25, azim=45)
        
        # 设置场景边界
        ax.set_xlim([-10, 10])
        ax.set_ylim([-10, 10])
        ax.set_zlim([0, 20])
        
        # 标签
        ax.set_xlabel('X (East-West)', color='white', fontsize=11)
        ax.set_ylabel('Y (North-South)', color='white', fontsize=11)
        ax.set_zlabel('Z (HEIGHT)', color='yellow', fontsize=12, weight='bold')
        
        # 绘制地面网格
        x_grid = np.linspace(-10, 10, 11)
        y_grid = np.linspace(-10, 10, 11)
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
        
        for i, face in enumerate(faces):
            poly = [[list(vertex) for vertex in face]]
            ax.add_collection3d(Poly3DCollection(poly, alpha=0.7, 
                                               facecolors=colors[i], 
                                               edgecolors='white',
                                               linewidths=0.5))
        
        # 信息显示
        time_text = f"Time: {frame_idx/fps:.1f}s"
        pos_text = f"Pos: ({cube.position[0]:.1f}, {cube.position[1]:.1f}, {cube.position[2]:.1f})"
        vel_text = f"Vel: ({cube.velocity[0]:.1f}, {cube.velocity[1]:.1f}, {cube.velocity[2]:.1f})"
        
        ax.text2D(0.02, 0.98, time_text, transform=ax.transAxes,
                 color='white', fontsize=12, verticalalignment='top')
        ax.text2D(0.02, 0.93, pos_text, transform=ax.transAxes,
                 color='white', fontsize=10, verticalalignment='top')
        ax.text2D(0.02, 0.88, vel_text, transform=ax.transAxes,
                 color='white', fontsize=10, verticalalignment='top')
        
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
        
        if frame_idx % 15 == 0:
            print(f"  帧 {frame_idx}/{total_frames} - Z高度: {cube.position[2]:.1f}m")
    
    # 保存视频
    output_path = 'test_main_fixed.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, 
                         (frames[0].shape[1], frames[0].shape[0]))
    
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    
    out.release()
    print(f"✅ 测试视频已保存: {output_path}")
    print(f"📊 立方体最终位置: {cube.position}")
    
    return output_path

if __name__ == "__main__":
    test_high_quality_video()
