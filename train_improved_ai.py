#!/usr/bin/env python3
"""
快速AI训练脚本
改善AI预测效果
"""

import numpy as np
import os
import sys
sys.path.append('.')

from src.physics import Cube, PhysicsEngine
from src.ai import AIPredictor

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def quick_train_ai():
    """快速训练AI模型"""
    print("🚀 开始快速AI训练...")
    
    # 确保模型目录存在
    ensure_dir("output/models")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    
    # 创建AI预测器 - 使用默认参数
    predictor = AIPredictor(sequence_length=8)
    
    # 手动调整网络参数以获得更好的性能
    predictor.model = predictor.model.__class__(
        input_size=13,
        hidden_size=64,     # 较小的隐藏层
        num_layers=2,       # 2层LSTM
        output_size=13
    ).to(predictor.device)
    
    print("📊 收集训练数据...")
    
    # 收集多样化的训练数据
    all_sequences = []
    all_targets = []
    
    # 不同的初始条件
    scenarios = [
        {'pos': [0, 0, 15], 'vel': [1, 0.5, 0]},    # 基础场景
        {'pos': [-3, 2, 18], 'vel': [4, -1, -2]},   # 高能量
        {'pos': [2, -1, 12], 'vel': [-2, 3, 1]},    # 不同角度
        {'pos': [0, 0, 20], 'vel': [0, 0, 0]},      # 自由落体
        {'pos': [1, 1, 10], 'vel': [2, -1, 0.5]},   # 斜抛
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"  场景 {i+1}/{len(scenarios)}: {scenario}")
        
        # 创建立方体
        cube = Cube(scenario['pos'], scenario['vel'], size=1.5)
        
        # 模拟多个回合
        for episode in range(40):  # 每个场景40回合
            # 重置立方体
            cube.position = np.array(scenario['pos']) + np.random.normal(0, 1, 3)
            cube.velocity = np.array(scenario['vel']) + np.random.normal(0, 0.5, 3)
            cube.rotation = np.array([1.0, 0.0, 0.0, 0.0])
            cube.angular_velocity = np.random.normal(0, 0.2, 3)
            cube.history.clear()
            
            # 运行模拟
            for step in range(120):  # 每回合120步
                engine.step([cube])
                cube.add_to_history()
                
                # 收集序列数据
                if len(cube.history) >= predictor.sequence_length + 1:
                    sequence = cube.history[-predictor.sequence_length-1:-1]
                    target = cube.history[-1]
                    all_sequences.append(sequence)
                    all_targets.append(target)
    
    print(f"✅ 收集完成，总序列数: {len(all_sequences)}")
    
    # 转换为训练格式
    sequences = np.array(all_sequences)
    targets = np.array(all_targets)
    
    print("🧠 开始训练模型...")
    predictor.train(
        sequences, targets,
        epochs=100,         # 更多训练轮次
        batch_size=32      # 较小的批次大小
    )
    
    # 保存模型
    model_path = "output/models/improved_physics_predictor.pth"
    predictor.save_model(model_path)
    print(f"✅ 改进的AI模型已保存: {model_path}")
    
    # 快速测试
    print("🧪 快速测试模型...")
    test_cube = Cube([0, 0, 15], [2, 1, 0], size=1.5)
    test_engine = PhysicsEngine(gravity=9.81)
    
    # 运行几步收集历史
    for _ in range(predictor.sequence_length):
        test_engine.step([test_cube])
        test_cube.add_to_history()
    
    # 测试预测
    try:
        prediction = predictor.predict_next_states([test_cube], steps=5)
        if prediction is not None:
            print("✅ AI预测测试成功")
            print(f"   预测步数: {len(prediction)}")
            print(f"   当前位置: {test_cube.position}")
            print(f"   预测位置: {prediction[0][:3]}")
        else:
            print("❌ AI预测测试失败")
    except Exception as e:
        print(f"❌ AI预测错误: {e}")
    
    return model_path

if __name__ == "__main__":
    quick_train_ai()
