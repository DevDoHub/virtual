#!/usr/bin/env python3
"""
完整的项目演示脚本
展示所有功能：物理模拟、AI预测、3D渲染、视频生成
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_complete_demo():
    """运行完整演示"""
    print("🎬 3D立方体下落与AI预测系统 - 完整演示")
    print("=" * 60)
    
    demos = [
        ("🧪 基础物理测试", "python test_physics.py"),
        ("🤖 AI训练演示", "python quick_ai_demo.py"),
        ("🔍 AI预测对比", "python ai_comparison_demo.py"),
        ("🎯 基础场景演示", "python main.py --scenario basic --duration 6"),
        ("⚡ 高能量场景", "python main.py --scenario high_energy --duration 8"),
        ("🌙 低重力场景", "python main.py --scenario low_gravity --duration 10"),
        ("🏀 高弹性场景", "python main.py --scenario bouncy --duration 8"),
        ("🤖 AI预测演示", "python main.py --scenario basic --ai-predict --duration 6"),
    ]
    
    for i, (name, command) in enumerate(demos, 1):
        print(f"\n{i}. {name}")
        print("-" * 40)
        
        # 询问用户是否运行此演示
        response = input(f"运行此演示? (y/n/q): ").strip().lower()
        
        if response == 'q':
            print("演示已终止")
            break
        elif response == 'y' or response == '':
            print(f"正在运行: {command}")
            print("=" * 40)
            
            os.system(command)
            
            print("=" * 40)
            print("演示完成!")
            
            if i < len(demos):
                input("按回车键继续下一个演示...")
        else:
            print("跳过此演示")
    
    print("\n🎉 所有演示完成!")
    show_summary()

def show_summary():
    """显示项目总结"""
    print("\n" + "=" * 60)
    print("📋 项目功能总结")
    print("=" * 60)
    
    features = [
        "✅ 完整的3D物理引擎（重力、碰撞检测、旋转动力学）",
        "✅ LSTM神经网络预测未来运动状态",
        "✅ 高质量3D渲染与可视化",
        "✅ 多种演示场景（基础、高能量、低重力、高弹性）",
        "✅ AI预测与物理模拟对比分析",
        "✅ 视频生成和导出功能",
        "✅ 能量守恒监测",
        "✅ 预测精度评估"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n📁 生成的文件:")
    files_to_check = [
        "test_physics.png",
        "ai_physics_comparison.png",
        "output/models/quick_physics_predictor.pth",
        "output/logs/simulation.log"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (未生成)")
    
    print(f"\n📊 项目统计:")
    print(f"  📂 Python文件: {count_python_files()}")
    print(f"  📝 代码行数: ~{estimate_code_lines()}")
    print(f"  🧠 AI模型参数: ~{estimate_model_parameters()}")

def count_python_files():
    """统计Python文件数量"""
    count = 0
    for root, dirs, files in os.walk('.'):
        if 'output' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                count += 1
    return count

def estimate_code_lines():
    """估算代码行数"""
    total_lines = 0
    for root, dirs, files in os.walk('.'):
        if 'output' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
    return total_lines

def estimate_model_parameters():
    """估算模型参数数量"""
    # 基于LSTM架构估算
    input_size = 13
    hidden_size = 128
    num_layers = 2
    
    # LSTM参数估算
    lstm_params = num_layers * (4 * (input_size * hidden_size + hidden_size * hidden_size + hidden_size))
    
    # 全连接层参数
    fc_params = hidden_size * hidden_size + hidden_size * 64 + 64 * 13
    
    total_params = lstm_params + fc_params
    return f"{total_params:,}"

def quick_start_guide():
    """快速开始指南"""
    print("\n🚀 快速开始指南")
    print("=" * 40)
    
    print("1. 基础演示:")
    print("   python main.py")
    
    print("\n2. 训练AI模型:")
    print("   python quick_ai_demo.py")
    
    print("\n3. AI预测演示:")
    print("   python main.py --ai-predict")
    
    print("\n4. 生成视频:")
    print("   python main.py --save-video")
    
    print("\n5. 完整训练:")
    print("   python main.py --mode train")
    
    print("\n6. 自定义场景:")
    print("   python main.py --scenario high_energy --duration 10 --ai-predict --save-video")

if __name__ == "__main__":
    try:
        print("欢迎使用3D立方体下落与AI预测系统!")
        print("请选择模式:")
        print("1. 完整演示 (推荐)")
        print("2. 快速开始指南")
        print("3. 项目总结")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1" or choice == "":
            run_complete_demo()
        elif choice == "2":
            quick_start_guide()
        elif choice == "3":
            show_summary()
        else:
            print("无效选择，显示快速开始指南")
            quick_start_guide()
            
    except KeyboardInterrupt:
        print("\n⏹️  演示已中断")
    except Exception as e:
        print(f"❌ 演示错误: {e}")
        import traceback
        traceback.print_exc()
