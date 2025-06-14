#!/usr/bin/env python3
"""
快速AI训练演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.ai import AIPredictor
from src.utils import Logger
import torch

def quick_ai_demo():
    """快速AI演示"""
    print("🤖 开始快速AI训练演示...")
    
    # 检查是否有GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🔧 使用设备: {device}")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    cube = Cube([0, 15, 0], [0, 0, 0], size=1.0)
    
    # 创建AI预测器
    predictor = AIPredictor(sequence_length=5, device=device)
    
    print("📊 收集训练数据...")
    # 快速训练版本 - 较少的数据
    sequences, targets = predictor.collect_training_data(
        engine, [cube], num_episodes=20, episode_length=100
    )
    
    print("🧠 开始训练模型...")
    # 快速训练
    predictor.train(sequences, targets, epochs=30, batch_size=32)
    
    # 保存模型
    os.makedirs('output/models', exist_ok=True)
    model_path = 'output/models/quick_physics_predictor.pth'
    predictor.save_model(model_path)
    
    # 评估模型
    print("📈 评估模型性能...")
    eval_results = predictor.evaluate(sequences[-200:], targets[-200:])
    print(f"评估结果: {eval_results}")
    
    # 测试预测
    print("🔮 测试预测功能...")
    engine.reset_cube(cube, [2, 12, -1], [1, 0, 0.5])
    
    # 运行几步建立历史
    for _ in range(10):
        engine.step([cube])
    
    # 进行预测
    prediction = predictor.predict_next_states([cube], steps=5)
    if prediction is not None:
        print("✅ 预测成功!")
        print(f"预测的前3步位置:")
        for i, pred in enumerate(prediction[:3]):
            print(f"  步骤 {i+1}: 位置 [{pred[0]:.2f}, {pred[1]:.2f}, {pred[2]:.2f}]")
    else:
        print("❌ 预测失败")
    
    print("\n🎉 快速AI演示完成！")
    return model_path

if __name__ == "__main__":
    try:
        model_path = quick_ai_demo()
        print(f"🎯 模型已保存到: {model_path}")
        print("💡 现在可以运行: python main.py --scenario basic --ai-predict --save-video")
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
