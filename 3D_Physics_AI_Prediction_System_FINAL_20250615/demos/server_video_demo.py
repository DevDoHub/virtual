#!/usr/bin/env python3
"""
服务器环境视频生成演示
专门为SSH远程连接设计，无需图形界面
"""

import matplotlib
matplotlib.use('Agg')  # 必须在最开始设置

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor
import numpy as np

def generate_server_video():
    """在服务器环境下生成视频"""
    print("🎬 服务器环境视频生成演示")
    print("=" * 50)
    
    # 确保输出目录存在
    os.makedirs('output/videos', exist_ok=True)
    
    # 创建物理环境
    print("🔧 创建物理环境...")
    bounds = [(-8, 8), (0, 16), (-8, 8)]
    engine = PhysicsEngine(gravity=9.81, bounds=bounds)
    
    # 创建立方体 - 使用有趣的初始条件
    cube = Cube(
        position=[-2, 14, 3],
        velocity=[4, -1, -2],
        size=1.5
    )
    cube.restitution = 0.75  # 中等弹性
    
    print(f"📦 立方体初始状态:")
    print(f"   位置: {cube.position}")
    print(f"   速度: {cube.velocity}")
    print(f"   弹性系数: {cube.restitution}")
    
    # 创建3D场景
    print("🎨 创建3D场景...")
    scene = Scene3D(bounds=bounds)
    video_gen = VideoGenerator(scene, fps=30, output_dir='output/videos')
    
    # 尝试加载AI预测器
    predictor = None
    model_path = 'output/models/quick_physics_predictor.pth'
    if os.path.exists(model_path):
        try:
            print("🤖 加载AI预测器...")
            predictor = AIPredictor()
            predictor.load_model(model_path)
            print("✅ AI预测器已加载")
        except Exception as e:
            print(f"⚠️  AI预测器加载失败: {e}")
            predictor = None
    else:
        print("⚠️  未找到预训练模型，将禁用AI预测")
    
    # 运行模拟并记录
    duration = 10.0  # 10秒视频
    print(f"🎥 开始记录 {duration}秒 的物理模拟...")
    
    # 显示进度
    total_frames = int(duration * 30)
    print(f"📊 预计生成 {total_frames} 帧")
    
    video_gen.simulate_and_record(
        engine, [cube], 
        duration=duration, 
        ai_predictor=predictor,
        prediction_steps=10
    )
    
    # 显示模拟统计
    stats = video_gen.get_statistics()
    if stats:
        print(f"\n📈 模拟完成统计:")
        print(f"   总帧数: {stats['total_frames']}")
        print(f"   模拟时长: {stats['duration']:.1f}秒")
        print(f"   初始能量: {stats['energy_initial']:.2f}J")
        print(f"   最终能量: {stats['energy_final']:.2f}J")
        print(f"   能量损失: {stats['energy_loss_percent']:.1f}%")
    
    # 生成视频
    print(f"\n🎬 开始生成视频...")
    video_filename = "server_physics_demo.mp4"
    
    try:
        output_path = video_gen.render_animation(
            filename=video_filename,
            show_trajectory=True,
            show_prediction=predictor is not None,
            camera_rotation=True
        )
        
        if output_path:
            # 检查文件大小
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"✅ 视频生成成功!")
            print(f"📁 文件路径: {output_path}")
            print(f"📦 文件大小: {file_size:.2f} MB")
            
            # 提供下载建议
            print(f"\n💡 下载建议:")
            print(f"   scp命令: scp user@server:{os.path.abspath(output_path)} ./")
            print(f"   或使用FileZilla等工具下载")
        else:
            print("❌ 视频生成失败，但应该有帧序列可用")
            
    except Exception as e:
        print(f"❌ 视频生成失败: {e}")
        import traceback
        traceback.print_exc()

def generate_multiple_scenarios():
    """生成多个场景的视频"""
    print("🎬 生成多场景视频集合")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'basic_fall',
            'position': [0, 12, 0],
            'velocity': [1, 0, 0.5],
            'restitution': 0.7,
            'duration': 8.0
        },
        {
            'name': 'high_energy',
            'position': [-3, 15, 2],
            'velocity': [5, -1, -3],
            'restitution': 0.8,
            'duration': 10.0
        },
        {
            'name': 'bouncy_cube',
            'position': [0, 10, 0],
            'velocity': [0, 0, 0],
            'restitution': 0.9,
            'duration': 12.0
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎬 生成场景 {i}/{len(scenarios)}: {scenario['name']}")
        print("-" * 30)
        
        # 创建物理环境
        bounds = [(-8, 8), (0, 16), (-8, 8)]
        engine = PhysicsEngine(gravity=9.81, bounds=bounds)
        
        # 创建立方体
        cube = Cube(
            position=scenario['position'],
            velocity=scenario['velocity'],
            size=1.5
        )
        cube.restitution = scenario['restitution']
        
        # 创建场景和视频生成器
        scene = Scene3D(bounds=bounds)
        video_gen = VideoGenerator(scene, fps=30, output_dir='output/videos')
        
        # 模拟和录制
        video_gen.simulate_and_record(engine, [cube], duration=scenario['duration'])
        
        # 生成视频
        video_filename = f"{scenario['name']}_demo.mp4"
        try:
            output_path = video_gen.render_animation(
                filename=video_filename,
                show_trajectory=True,
                camera_rotation=True
            )
            if output_path:
                print(f"✅ {scenario['name']} 视频已生成: {output_path}")
            else:
                print(f"⚠️  {scenario['name']} 视频生成失败")
        except Exception as e:
            print(f"❌ {scenario['name']} 生成错误: {e}")
    
    print(f"\n🎉 多场景视频生成完成!")
    print(f"📁 查看 output/videos/ 目录")

def main():
    """主函数"""
    print("请选择模式:")
    print("1. 生成单个演示视频")
    print("2. 生成多场景视频集合")
    print("3. 仅测试视频生成功能")
    
    try:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1' or choice == '':
            generate_server_video()
        elif choice == '2':
            generate_multiple_scenarios()
        elif choice == '3':
            # 快速测试
            print("🧪 快速测试视频生成...")
            bounds = [(-5, 5), (0, 10), (-5, 5)]
            engine = PhysicsEngine(bounds=bounds)
            cube = Cube([0, 8, 0], [1, 0, 0], size=1.0)
            scene = Scene3D(bounds=bounds)
            video_gen = VideoGenerator(scene, fps=30, output_dir='output/videos')
            video_gen.simulate_and_record(engine, [cube], duration=3.0)
            video_gen.render_animation("test_video.mp4", camera_rotation=False)
        else:
            print("无效选择，运行默认演示")
            generate_server_video()
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
