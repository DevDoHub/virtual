#!/usr/bin/env python3
"""
完整更新的X-Y地面平面演示 - 使用核心系统
=============================================

使用核心物理引擎、渲染系统和AI预测系统
确保所有组件都使用正确的坐标系统：
- X-Y平面作为水平地面
- Z轴作为垂直方向（高度）
- 重力沿Z轴负方向
"""

import matplotlib
matplotlib.use('Agg')
import sys
import os
import numpy as np
from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor

def create_updated_demo():
    """创建使用正确坐标系统的完整演示"""
    
    print("🎯 启动更新的X-Y地面演示...")
    print("📐 坐标系统：X-Y地面平面，Z轴垂直")
    
    # 1. 创建物理引擎 - 确保使用正确的坐标系统
    bounds = [(-8, 8), (-8, 8), (0, 16)]  # X, Y, Z（Z为高度）
    engine = PhysicsEngine(
        gravity=9.81,
        air_resistance=0.01,
        bounds=bounds
    )
    
    print(f"✅ 物理引擎已创建，边界: {bounds}")
    print(f"   - X轴: {bounds[0]} (东西方向)")
    print(f"   - Y轴: {bounds[1]} (南北方向)")
    print(f"   - Z轴: {bounds[2]} (高度)")
    
    # 2. 创建立方体 - Z轴为高度起始位置
    cube = Cube(
        position=[0, 0, 12],      # X=0, Y=0, Z=12（高度12米）
        velocity=[2, 1.5, 0],     # X-Y平面初始速度，Z轴初始为0
        size=2.0,
        mass=1.0,
        color=(1.0, 0.3, 0.3)
    )
    
    # 设置物理属性
    cube.restitution = 0.75  # 弹性系数
    cube.friction = 0.3      # 摩擦系数
    
    print(f"✅ 立方体已创建")
    print(f"   - 初始位置: {cube.position} (X, Y, Z)")
    print(f"   - 初始速度: {cube.velocity} (vX, vY, vZ)")
    print(f"   - 尺寸: {cube.size}m")
    
    # 3. 创建3D场景 - 使用正确的坐标系统
    scene = Scene3D(figsize=(14, 10), bounds=bounds)
    
    # 设置合适的视角观察X-Y地面
    scene.ax.view_init(elev=25, azim=45)  # 俯视角度看X-Y地面
    
    print("✅ 3D场景已创建，视角设置为俯视X-Y地面")
    
    # 4. 创建视频生成器
    output_dir = "output/videos"
    os.makedirs(output_dir, exist_ok=True)
    video_gen = VideoGenerator(scene, fps=30, output_dir=output_dir)
    
    print(f"✅ 视频生成器已创建，输出目录: {output_dir}")
    
    # 5. 创建AI预测器
    ai_predictor = AIPredictor()
    print("✅ AI预测器已创建")
    
    # 6. 运行模拟
    duration = 10.0  # 10秒模拟
    cubes = [cube]
    
    print(f"\n🚀 开始物理模拟...")
    print(f"   - 模拟时长: {duration}秒")
    print(f"   - 重力: {engine.gravity} m/s² (Z轴负方向)")
    print(f"   - 地面: Z=0 (X-Y平面)")
    
    # 运行模拟并记录
    video_gen.simulate_and_record(
        engine=engine,
        cubes=cubes,
        duration=duration,
        ai_predictor=ai_predictor,
        prediction_steps=15
    )
    
    print("✅ 物理模拟完成")
    
    # 7. 生成视频
    video_filename = "updated_xy_ground_demo.mp4"
    video_path = os.path.join(output_dir, video_filename)
    
    print(f"\n🎬 开始生成视频: {video_filename}")
    
    success = video_gen.save_video(
        filename=video_filename,
        title=f"正确X-Y地面演示\\n{len(video_gen.frame_data)}帧",
        show_energy=True,
        show_prediction=True
    )
    
    if success:
        print(f"✅ 视频已保存: {video_path}")
        
        # 显示文件信息
        if os.path.exists(video_path):
            size_mb = os.path.getsize(video_path) / (1024*1024)
            print(f"   - 文件大小: {size_mb:.2f} MB")
            print(f"   - 帧数: {len(video_gen.frame_data)}")
            print(f"   - 帧率: {video_gen.fps} FPS")
    else:
        print("❌ 视频生成失败")
        return False
    
    # 8. 显示最终状态
    final_pos = cube.position
    print(f"\n📊 最终状态:")
    print(f"   - 最终位置: [{final_pos[0]:.2f}, {final_pos[1]:.2f}, {final_pos[2]:.2f}]")
    print(f"   - 最终速度: [{cube.velocity[0]:.2f}, {cube.velocity[1]:.2f}, {cube.velocity[2]:.2f}]")
    
    # 验证立方体确实落在地面上
    cube_bottom = final_pos[2] - cube.size/2
    print(f"   - 立方体底部高度: {cube_bottom:.3f}m")
    
    if abs(cube_bottom) < 0.1:  # 应该接近0（地面）
        print("   ✅ 立方体正确落在X-Y地面上 (Z=0)")
    else:
        print("   ⚠️  立方体位置可能不正确")
    
    print(f"\n🎯 演示完成！")
    print(f"📁 视频文件: {video_path}")
    
    return True

def show_coordinate_system_info():
    """显示坐标系统信息"""
    print("\n" + "="*60)
    print("📐 坐标系统说明")
    print("="*60)
    print("✅ 正确的坐标系统:")
    print("   - X轴: 东西方向（水平）")
    print("   - Y轴: 南北方向（水平）")
    print("   - Z轴: 上下方向（垂直，高度）")
    print("   - 地面: X-Y平面 (Z=0)")
    print("   - 重力: 沿Z轴负方向 (0, 0, -9.8)")
    print("   - 立方体从高Z值下落到Z=0地面")
    print("="*60)

if __name__ == "__main__":
    show_coordinate_system_info()
    
    try:
        success = create_updated_demo()
        if success:
            print("\n🎉 所有组件都已使用正确的X-Y地面坐标系统！")
        else:
            print("\n❌ 演示过程中出现错误")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 演示失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
