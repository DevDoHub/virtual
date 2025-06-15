#!/usr/bin/env python3
"""
测试AI预测可视化效果
"""

import numpy as np
import os
from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor

def test_ai_prediction_visualization():
    """测试AI预测的可视化效果"""
    print("🤖 测试AI预测可视化...")
    
    # 创建物理环境
    cube = Cube(position=[0, 0, 10], velocity=[0, 0, 0], size=1.5)
    cube.restitution = 0.9  # bouncy场景
    engine = PhysicsEngine(gravity=9.81)
    
    # 添加障碍物
    engine.add_obstacles('bouncy_obstacles')
    
    # 创建AI预测器
    predictor = AIPredictor()
    
    # 尝试加载模型
    model_paths = [
        'output/models/compatible_physics_predictor.pth',
        'output/models/quick_physics_predictor.pth',
        'output/models/physics_predictor.pth'
    ]
    
    model_loaded = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            try:
                predictor.load_model(model_path)
                print(f"✅ AI模型已加载: {model_path}")
                model_loaded = True
                break
            except Exception as e:
                print(f"⚠️ 模型加载失败 {model_path}: {e}")
    
    if not model_loaded:
        print("❌ 没有可用的AI模型，请先训练模型")
        return None
    
    # 创建渲染器
    scene = Scene3D(bounds=[(-5, 5), (-5, 5), (0, 12)])
    video_gen = VideoGenerator(scene, fps=30, output_dir='.')
    
    print("🎬 生成带AI预测的演示视频...")
    
    # 运行模拟并记录，启用AI预测
    video_gen.simulate_and_record(
        engine, [cube], 
        duration=4.0,  # 4秒测试
        ai_predictor=predictor,
        prediction_steps=5
    )
    
    # 生成高质量视频，显示AI预测
    output_path = video_gen.render_high_quality_animation(
        filename="ai_prediction_test.mp4",
        show_prediction=True,
        figsize=(12, 9),
        engine=engine
    )
    
    if output_path:
        print(f"✅ AI预测测试视频已生成: {output_path}")
        
        # 检查预测数据
        prediction_frames = sum(1 for frame in video_gen.frame_data if frame.get('prediction') is not None)
        total_frames = len(video_gen.frame_data)
        print(f"📊 预测统计: {prediction_frames}/{total_frames} 帧包含AI预测 ({prediction_frames/total_frames*100:.1f}%)")
        
        return output_path
    else:
        print("❌ 视频生成失败")
        return None

if __name__ == "__main__":
    test_ai_prediction_visualization()
