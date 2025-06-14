#!/usr/bin/env python3
"""
修复AI模型兼容性的训练脚本
使用与预测器相同的默认参数
"""

import numpy as np
import os
from src.physics import Cube, PhysicsEngine
from src.ai import AIPredictor
from src.utils import ensure_dir

def train_compatible_ai():
    """训练兼容的AI模型"""
    print("🤖 训练兼容的AI模型...")
    
    # 确保模型目录存在
    ensure_dir("output/models")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    
    # 创建AI预测器 - 使用默认参数确保兼容性
    predictor = AIPredictor(sequence_length=5)  # 使用默认参数
    
    print("📊 收集训练数据...")
    
    # 收集多样化的训练数据
    all_sequences = []
    all_targets = []
    
    # 不同的初始条件 - 包含bouncy场景
    scenarios = [
        {'pos': [0, 0, 15], 'vel': [1, 0.5, 0], 'restitution': 0.7},     # 基础场景
        {'pos': [-3, 2, 18], 'vel': [4, -1, -2], 'restitution': 0.7},    # 高能量
        {'pos': [0, 0, 10], 'vel': [0, 0, 0], 'restitution': 0.9},       # bouncy场景
        {'pos': [2, -1, 12], 'vel': [-2, 3, 1], 'restitution': 0.8},     # 不同角度
        {'pos': [0, 0, 20], 'vel': [0, 0, 0], 'restitution': 0.6},       # 自由落体
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"  场景 {i+1}/{len(scenarios)}: {scenario}")
        
        # 创建立方体
        cube = Cube(scenario['pos'], scenario['vel'], size=1.5)
        cube.restitution = scenario['restitution']
        
        # 模拟多个回合
        for episode in range(30):  # 每个场景30回合
            # 重置立方体
            cube.position = np.array(scenario['pos']) + np.random.normal(0, 0.5, 3)
            cube.velocity = np.array(scenario['vel']) + np.random.normal(0, 0.3, 3)
            cube.rotation = np.array([1.0, 0.0, 0.0, 0.0])
            cube.angular_velocity = np.random.normal(0, 0.1, 3)
            cube.history.clear()
            
            # 运行模拟
            for step in range(100):  # 每回合100步
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
    predictor.train(sequences, targets, epochs=80, batch_size=32)
    
    # 保存兼容模型
    model_path = "output/models/compatible_physics_predictor.pth"
    predictor.save_model(model_path)
    print(f"✅ 兼容AI模型已保存: {model_path}")
    
    # 快速测试
    print("🧪 快速测试模型...")
    test_cube = Cube([0, 0, 10], [0, 0, 0], size=1.5)
    test_cube.restitution = 0.9  # bouncy测试
    test_engine = PhysicsEngine(gravity=9.81)
    
    # 运行几步收集历史
    for _ in range(predictor.sequence_length):
        test_engine.step([test_cube])
        test_cube.add_to_history()
    
    # 测试预测
    try:
        prediction = predictor.predict_next_states([test_cube], steps=3)
        if prediction is not None:
            print("✅ AI预测测试成功")
            print(f"   当前位置: [{test_cube.position[0]:.2f}, {test_cube.position[1]:.2f}, {test_cube.position[2]:.2f}]")
            print(f"   预测位置: [{prediction[0][0]:.2f}, {prediction[0][1]:.2f}, {prediction[0][2]:.2f}]")
        else:
            print("❌ AI预测测试失败")
    except Exception as e:
        print(f"❌ AI预测错误: {e}")
    
    return model_path

if __name__ == "__main__":
    train_compatible_ai()
