#!/usr/bin/env python3
"""
一键生成所有演示视频 - 适合服务器环境
"""

import matplotlib
matplotlib.use('Agg')

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor

def generate_all_demos():
    """生成所有演示视频"""
    print("🎬 一键生成所有演示视频")
    print("=" * 60)
    
    # 确保输出目录
    os.makedirs('output/videos', exist_ok=True)
    
    # 检查AI模型
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
    else:
        print("⚠️  未找到AI模型，将先训练一个")
        # 快速训练一个模型
        from quick_ai_demo import quick_ai_demo
        quick_ai_demo()
        try:
            predictor = AIPredictor()
            predictor.load_model(model_path)
            print("✅ AI预测器训练并加载完成")
        except:
            predictor = None
    
    # 定义所有场景
    scenarios = [
        {
            'name': '01_basic_fall',
            'description': '基础下落场景',
            'position': [0, 15, 0],
            'velocity': [1, 0, 0.5],
            'gravity': 9.81,
            'restitution': 0.7,
            'duration': 8.0,
            'use_ai': False
        },
        {
            'name': '02_high_energy',
            'description': '高能量碰撞',
            'position': [-3, 18, 2],
            'velocity': [4, -1, -2],
            'gravity': 9.81,
            'restitution': 0.7,
            'duration': 10.0,
            'use_ai': False
        },
        {
            'name': '03_low_gravity',
            'description': '低重力环境（火星）',
            'position': [0, 12, 0],
            'velocity': [2, 1, 1],
            'gravity': 3.71,  # 火星重力
            'restitution': 0.7,
            'duration': 15.0,
            'use_ai': False
        },
        {
            'name': '04_bouncy_cube',
            'description': '高弹性立方体',
            'position': [0, 10, 0],
            'velocity': [0, 0, 0],
            'gravity': 9.81,
            'restitution': 0.9,
            'duration': 12.0,
            'use_ai': False
        },
        {
            'name': '05_ai_prediction',
            'description': 'AI预测演示',
            'position': [1, 14, -1],
            'velocity': [2, 0, 1],
            'gravity': 9.81,
            'restitution': 0.75,
            'duration': 10.0,
            'use_ai': True
        },
        {
            'name': '06_complex_motion',
            'description': '复杂运动轨迹',
            'position': [-4, 16, 3],
            'velocity': [5, -2, -3],
            'gravity': 9.81,
            'restitution': 0.8,
            'duration': 12.0,
            'use_ai': True
        }
    ]
    
    successful_videos = []
    failed_videos = []
    
    start_time = time.time()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 生成视频 {i}/{len(scenarios)}: {scenario['name']}")
        print(f"📝 描述: {scenario['description']}")
        print("-" * 50)
        
        try:
            # 创建物理环境
            bounds = [(-10, 10), (0, 20), (-10, 10)]
            engine = PhysicsEngine(
                gravity=scenario['gravity'], 
                bounds=bounds
            )
            
            # 创建立方体
            cube = Cube(
                position=scenario['position'],
                velocity=scenario['velocity'],
                size=1.5
            )
            cube.restitution = scenario['restitution']
            
            print(f"📦 立方体设置:")
            print(f"   位置: {cube.position}")
            print(f"   速度: {cube.velocity}")
            print(f"   重力: {scenario['gravity']} m/s²")
            print(f"   弹性: {cube.restitution}")
            print(f"   AI预测: {'启用' if scenario['use_ai'] and predictor else '禁用'}")
            
            # 创建场景
            scene = Scene3D(bounds=bounds)
            video_gen = VideoGenerator(scene, fps=30, output_dir='output/videos')
            
            # 模拟
            print("🎥 开始模拟...")
            video_gen.simulate_and_record(
                engine, [cube], 
                duration=scenario['duration'],
                ai_predictor=predictor if scenario['use_ai'] else None,
                prediction_steps=10
            )
            
            # 生成视频
            video_filename = f"{scenario['name']}.mp4"
            print(f"🎬 生成视频: {video_filename}")
            
            output_path = video_gen.render_animation(
                filename=video_filename,
                show_trajectory=True,
                show_prediction=scenario['use_ai'] and predictor is not None,
                camera_rotation=True
            )
            
            if output_path and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ 视频生成成功! 大小: {file_size:.2f} MB")
                successful_videos.append({
                    'name': scenario['name'],
                    'path': output_path,
                    'size': file_size,
                    'description': scenario['description']
                })
            else:
                print(f"❌ 视频生成失败")
                failed_videos.append(scenario['name'])
                
        except Exception as e:
            print(f"❌ 场景生成失败: {e}")
            failed_videos.append(scenario['name'])
            import traceback
            traceback.print_exc()
    
    # 生成总结报告
    total_time = time.time() - start_time
    generate_summary_report(successful_videos, failed_videos, total_time)

def generate_summary_report(successful_videos, failed_videos, total_time):
    """生成总结报告"""
    print("\n" + "=" * 60)
    print("📊 视频生成总结报告")
    print("=" * 60)
    
    print(f"⏱️  总耗时: {total_time/60:.1f} 分钟")
    print(f"✅ 成功生成: {len(successful_videos)} 个视频")
    print(f"❌ 生成失败: {len(failed_videos)} 个视频")
    
    if successful_videos:
        total_size = sum(video['size'] for video in successful_videos)
        print(f"📦 总文件大小: {total_size:.2f} MB")
        
        print(f"\n📁 成功生成的视频:")
        for video in successful_videos:
            print(f"   ✅ {video['name']}: {video['description']} ({video['size']:.1f} MB)")
    
    if failed_videos:
        print(f"\n❌ 失败的视频:")
        for name in failed_videos:
            print(f"   ❌ {name}")
    
    # 生成下载脚本
    if successful_videos:
        create_download_script(successful_videos)
    
    print(f"\n📁 所有视频保存在: output/videos/")
    print(f"💡 使用 scp 命令下载到本地查看")

def create_download_script(successful_videos):
    """创建下载脚本"""
    script_content = """#!/bin/bash
# 视频下载脚本
# 使用方法: ./download_videos.sh user@server

if [ -z "$1" ]; then
    echo "使用方法: $0 user@server"
    exit 1
fi

SERVER=$1
LOCAL_DIR="physics_videos"

echo "📁 创建本地目录..."
mkdir -p $LOCAL_DIR

echo "📥 开始下载视频..."
"""
    
    for video in successful_videos:
        script_content += f'scp $SERVER:/root/virtual/{video["path"]} $LOCAL_DIR/\n'
    
    script_content += """
echo "✅ 所有视频下载完成!"
echo "📁 视频保存在: $LOCAL_DIR/"
echo "🎬 可以使用VLC等播放器查看"
"""
    
    with open('download_videos.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('download_videos.sh', 0o755)
    print(f"📜 已生成下载脚本: download_videos.sh")

if __name__ == "__main__":
    try:
        generate_all_demos()
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
