#!/usr/bin/env python3
"""
3D立方体下落与AI预测系统 - 主程序

这是一个展示物理模拟与AI预测结合的研究生项目
"""

import numpy as np
import argparse
import os
from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator
from src.ai import AIPredictor
from src.utils import Logger, ensure_dir

def create_demo_scenario(scenario='basic'):
    """创建演示场景"""
    scenarios = {
        'basic': {
            'position': [0, 15, 0],
            'velocity': [1, 0, 0.5],
            'gravity': 9.81,
            'duration': 8.0
        },
        'high_energy': {
            'position': [-3, 18, 2],
            'velocity': [4, -1, -2],
            'gravity': 9.81,
            'duration': 10.0
        },
        'low_gravity': {
            'position': [0, 12, 0],
            'velocity': [2, 1, 1],
            'gravity': 3.71,  # 火星重力
            'duration': 15.0
        },
        'bouncy': {
            'position': [0, 10, 0],
            'velocity': [0, 0, 0],
            'gravity': 9.81,
            'duration': 12.0,
            'restitution': 0.9
        }
    }
    
    return scenarios.get(scenario, scenarios['basic'])

def main():
    parser = argparse.ArgumentParser(description='3D立方体下落与AI预测系统')
    parser.add_argument('--mode', choices=['train', 'simulate', 'demo'], 
                       default='demo', help='运行模式')
    parser.add_argument('--scenario', choices=['basic', 'high_energy', 'low_gravity', 'bouncy'],
                       default='basic', help='演示场景')
    parser.add_argument('--duration', type=float, default=8.0, help='模拟时长（秒）')
    parser.add_argument('--ai-predict', action='store_true', help='启用AI预测')
    parser.add_argument('--save-video', action='store_true', help='保存视频')
    parser.add_argument('--output-dir', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    ensure_dir(args.output_dir)
    ensure_dir(os.path.join(args.output_dir, 'videos'))
    ensure_dir(os.path.join(args.output_dir, 'models'))
    ensure_dir(os.path.join(args.output_dir, 'logs'))
    
    # 设置日志
    logger = Logger(os.path.join(args.output_dir, 'logs', 'simulation.log'))
    logger.info(f"开始运行，模式: {args.mode}, 场景: {args.scenario}")
    
    if args.mode == 'train':
        run_training(args, logger)
    elif args.mode == 'simulate':
        run_simulation(args, logger)
    else:
        run_demo(args, logger)

def run_training(args, logger):
    """运行AI训练模式"""
    logger.info("开始AI训练模式")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    cube = Cube([0, 15, 0], [0, 0, 0], size=1.0)
    
    # 创建AI预测器
    predictor = AIPredictor(sequence_length=10)
    
    # 收集训练数据
    logger.info("收集训练数据...")
    sequences, targets = predictor.collect_training_data(
        engine, [cube], num_episodes=200, episode_length=250
    )
    
    # 训练模型
    logger.info("开始训练模型...")
    predictor.train(sequences, targets, epochs=150, batch_size=64)
    
    # 保存模型
    model_path = os.path.join(args.output_dir, 'models', 'physics_predictor.pth')
    predictor.save_model(model_path)
    logger.info(f"模型已保存到: {model_path}")
    
    # 评估模型
    eval_results = predictor.evaluate(sequences[-1000:], targets[-1000:])
    logger.info(f"模型评估结果: {eval_results}")

def run_simulation(args, logger):
    """运行物理模拟模式"""
    logger.info("开始物理模拟模式")
    
    # 获取场景参数
    scenario_config = create_demo_scenario(args.scenario)
    
    # 创建物理环境
    bounds = [(-10, 10), (0, 20), (-10, 10)]
    engine = PhysicsEngine(gravity=scenario_config['gravity'], bounds=bounds)
    
    # 创建立方体
    cube = Cube(
        position=scenario_config['position'],
        velocity=scenario_config['velocity'],
        size=1.5
    )
    
    if 'restitution' in scenario_config:
        cube.restitution = scenario_config['restitution']
    
    # 创建3D场景
    scene = Scene3D(bounds=bounds)
    video_gen = VideoGenerator(scene, fps=30, output_dir=os.path.join(args.output_dir, 'videos'))
    
    # AI预测器（可选）
    predictor = None
    if args.ai_predict:
        predictor = AIPredictor()
        model_paths = [
            os.path.join(args.output_dir, 'models', 'physics_predictor.pth'),
            os.path.join(args.output_dir, 'models', 'quick_physics_predictor.pth'),
            'output/models/quick_physics_predictor.pth'
        ]
        
        model_loaded = False
        for model_path in model_paths:
            if os.path.exists(model_path):
                try:
                    predictor.load_model(model_path)
                    logger.info(f"AI预测器已加载: {model_path}")
                    model_loaded = True
                    break
                except Exception as e:
                    logger.warning(f"加载模型失败 {model_path}: {e}")
        
        if not model_loaded:
            logger.warning("未找到可用的预训练模型，将禁用AI预测")
            predictor = None
    
    # 运行模拟
    logger.info("开始物理模拟...")
    video_gen.simulate_and_record(
        engine, [cube], 
        duration=args.duration, 
        ai_predictor=predictor
    )
    
    # 生成视频
    if args.save_video:
        video_filename = f"simulation_{args.scenario}_{args.duration}s.mp4"
        logger.info(f"生成视频: {video_filename}")
        video_gen.render_animation(
            filename=video_filename,
            show_prediction=predictor is not None,
            camera_rotation=True
        )
    
    # 显示统计信息
    stats = video_gen.get_statistics()
    if stats:
        logger.info(f"模拟统计: {stats}")

def run_demo(args, logger):
    """运行演示模式"""
    logger.info("开始演示模式")
    
    print("=" * 60)
    print("🎯 3D立方体下落与AI预测系统演示")
    print("=" * 60)
    print(f"📦 场景: {args.scenario}")
    print(f"⏱️  时长: {args.duration}秒")
    print(f"🤖 AI预测: {'启用' if args.ai_predict else '禁用'}")
    print(f"📹 保存视频: {'是' if args.save_video else '否'}")
    print("=" * 60)
    
    # 运行模拟
    run_simulation(args, logger)
    
    print("\n🎉 演示完成！")
    print(f"📁 输出文件保存在: {args.output_dir}")
    
    if args.save_video:
        print("🎬 查看生成的视频文件")
    
    print("\n💡 尝试不同的场景:")
    print("  python main.py --scenario high_energy --ai-predict --save-video")
    print("  python main.py --scenario low_gravity --duration 15")
    print("  python main.py --scenario bouncy --save-video")
    
    print("\n🚀 训练AI模型:")
    print("  python main.py --mode train")

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示模式")
    print("请选择场景:")
    print("1. 基础下落")
    print("2. 高能量碰撞")
    print("3. 低重力环境")
    print("4. 高弹性碰撞")
    
    scenarios = ['basic', 'high_energy', 'low_gravity', 'bouncy']
    choice = input("请输入选择 (1-4): ").strip()
    
    try:
        scenario_idx = int(choice) - 1
        if 0 <= scenario_idx < len(scenarios):
            scenario = scenarios[scenario_idx]
        else:
            scenario = 'basic'
    except:
        scenario = 'basic'
    
    duration = input("模拟时长 (默认8秒): ").strip()
    try:
        duration = float(duration) if duration else 8.0
    except:
        duration = 8.0
    
    ai_predict = input("启用AI预测? (y/n): ").strip().lower() == 'y'
    save_video = input("保存视频? (y/n): ").strip().lower() == 'y'
    
    # 创建参数对象
    class Args:
        mode = 'demo'
        scenario = scenario
        duration = duration
        ai_predict = ai_predict
        save_video = save_video
        output_dir = 'output'
    
    args = Args()
    logger = Logger()
    
    run_demo(args, logger)

if __name__ == "__main__":
    try:
        # 检查是否有命令行参数
        import sys
        if len(sys.argv) == 1:
            interactive_demo()
        else:
            main()
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
