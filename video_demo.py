#!/usr/bin/env python3
"""
视频生成演示 - 展示如何生成高质量的物理模拟视频
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor

def generate_demo_video():
    """生成演示视频"""
    print("🎬 开始生成演示视频...")
    
    # 创建物理环境
    bounds = [(-8, 8), (0, 16), (-8, 8)]
    engine = PhysicsEngine(gravity=9.81, bounds=bounds)
    
    # 创建立方体 - 高弹性场景
    cube = Cube(
        position=[0, 12, 0],
        velocity=[3, 0, 2],
        size=1.5
    )
    cube.restitution = 0.8  # 高弹性
    
    # 创建3D场景
    scene = Scene3D(bounds=bounds)
    video_gen = VideoGenerator(scene, fps=30, output_dir='videos')
    
    # 加载AI预测器（如果可用）
    predictor = None
    model_path = 'output/models/quick_physics_predictor.pth'
    if os.path.exists(model_path):
        try:
            predictor = AIPredictor()
            predictor.load_model(model_path)
            print("✅ AI预测器已加载")
        except Exception as e:
            print(f"⚠️  AI预测器加载失败: {e}")
            predictor = None
    
    # 运行模拟并记录
    duration = 12.0  # 12秒视频
    print(f"🎥 开始记录 {duration}秒 的物理模拟...")
    
    video_gen.simulate_and_record(
        engine, [cube], 
        duration=duration, 
        ai_predictor=predictor,
        prediction_steps=15
    )
    
    # 生成视频
    video_filename = "physics_simulation_demo.mp4"
    print(f"🎬 正在生成视频: {video_filename}")
    
    try:
        video_gen.render_animation(
            filename=video_filename,
            show_trajectory=True,
            show_prediction=predictor is not None,
            camera_rotation=True
        )
        
        print(f"✅ 视频生成成功: videos/{video_filename}")
        
        # 显示统计信息
        stats = video_gen.get_statistics()
        if stats:
            print(f"\n📊 视频统计:")
            print(f"   总帧数: {stats['total_frames']}")
            print(f"   时长: {stats['duration']:.1f}秒")
            print(f"   帧率: {stats['fps']} FPS")
            print(f"   能量损失: {stats['energy_loss_percent']:.1f}%")
            
    except Exception as e:
        print(f"❌ 视频生成失败: {e}")
        print("💡 尝试安装 ffmpeg: sudo apt install ffmpeg")

if __name__ == "__main__":
    try:
        generate_demo_video()
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
