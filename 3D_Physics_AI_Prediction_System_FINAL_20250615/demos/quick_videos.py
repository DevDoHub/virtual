#!/usr/bin/env python3
"""
快速生成几个关键演示视频
"""

import matplotlib
matplotlib.use('Agg')

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator

def quick_video_batch():
    """快速生成几个关键视频"""
    print("🎬 快速生成演示视频集合")
    print("=" * 40)
    
    os.makedirs('output/videos', exist_ok=True)
    
    # 简化的场景列表
    scenarios = [
        {
            'name': 'basic_fall',
            'position': [0, 12, 0],
            'velocity': [1, 0, 0.5],
            'duration': 6.0,
            'description': '基础下落'
        },
        {
            'name': 'high_energy_bounce',
            'position': [-3, 15, 2],
            'velocity': [4, -1, -2],
            'duration': 8.0,
            'description': '高能量弹跳'
        },
        {
            'name': 'spinning_cube',
            'position': [0, 10, 0],
            'velocity': [2, 1, 1],
            'duration': 7.0,
            'description': '旋转立方体'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 生成视频 {i}/{len(scenarios)}: {scenario['name']}")
        print(f"描述: {scenario['description']}")
        
        try:
            # 创建物理环境
            bounds = [(-8, 8), (0, 16), (-8, 8)]
            engine = PhysicsEngine(gravity=9.81, bounds=bounds)
            
            # 创建立方体
            cube = Cube(
                position=scenario['position'],
                velocity=scenario['velocity'],
                size=1.5
            )
            cube.restitution = 0.75
            
            # 创建场景
            scene = Scene3D(bounds=bounds)
            video_gen = VideoGenerator(scene, fps=30, output_dir='output/videos')
            
            print("🎥 模拟中...")
            video_gen.simulate_and_record(engine, [cube], duration=scenario['duration'])
            
            print("🎬 生成视频...")
            video_filename = f"{scenario['name']}.mp4"
            output_path = video_gen.render_animation(
                filename=video_filename,
                show_trajectory=True,
                camera_rotation=True
            )
            
            if output_path and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ 完成! 大小: {file_size:.1f} MB")
            else:
                print("❌ 生成失败")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print(f"\n🎉 批量生成完成!")
    print(f"📁 查看: output/videos/")

if __name__ == "__main__":
    quick_video_batch()
