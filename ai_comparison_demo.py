#!/usr/bin/env python3
"""
AI预测对比可视化演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from src.physics import Cube, PhysicsEngine
from src.ai import AIPredictor
import torch

def compare_ai_vs_physics():
    """对比AI预测与实际物理模拟"""
    print("🔍 AI预测 vs 物理模拟对比演示")
    
    # 加载训练好的模型
    predictor = AIPredictor()
    model_path = 'output/models/quick_physics_predictor.pth'
    
    if not os.path.exists(model_path):
        print("❌ 未找到训练好的模型，请先运行 quick_ai_demo.py")
        return
    
    predictor.load_model(model_path)
    print(f"✅ 模型已加载: {model_path}")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    
    # 测试场景1: 基础下落
    print("\n📊 测试场景: 基础下落")
    cube = Cube([0, 10, 0], [2, 0, 1], size=1.0)
    
    # 运行初始步骤建立历史
    for _ in range(predictor.sequence_length):
        engine.step([cube])
    
    # 记录实际物理模拟轨迹
    physics_positions = []
    ai_predictions = []
    
    prediction_steps = 20
    
    for step in range(prediction_steps):
        # 记录当前位置
        physics_positions.append(cube.position.copy())
        
        # AI预测接下来5步
        if len(cube.history) >= predictor.sequence_length:
            try:
                prediction = predictor.predict_next_states([cube], steps=5)
                if prediction is not None:
                    ai_predictions.append(prediction)
                else:
                    ai_predictions.append(None)
            except Exception as e:
                print(f"预测错误: {e}")
                ai_predictions.append(None)
        else:
            ai_predictions.append(None)
        
        # 物理步进
        engine.step([cube])
    
    # 可视化结果
    visualize_comparison(physics_positions, ai_predictions)

def visualize_comparison(physics_positions, ai_predictions):
    """可视化AI预测与物理模拟的对比"""
    physics_positions = np.array(physics_positions)
    
    fig = plt.figure(figsize=(15, 10))
    
    # 2D轨迹对比 (X-Y平面)
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(physics_positions[:, 0], physics_positions[:, 1], 'b-', 
             linewidth=3, label='Actual Physics', alpha=0.8)
    
    # 绘制AI预测轨迹
    for i, prediction in enumerate(ai_predictions):
        if prediction is not None and i < len(physics_positions) - 1:
            # 只显示第一步预测，避免混乱
            next_pos = prediction[0][:3]
            current_pos = physics_positions[i]
            ax1.arrow(current_pos[0], current_pos[1], 
                     next_pos[0] - current_pos[0], 
                     next_pos[1] - current_pos[1],
                     head_width=0.1, head_length=0.1, 
                     fc='red', ec='red', alpha=0.6)
    
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position')
    ax1.set_title('2D Trajectory Comparison (XY Plane)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 3D轨迹
    ax2 = plt.subplot(2, 2, 2, projection='3d')
    ax2.plot(physics_positions[:, 0], physics_positions[:, 1], physics_positions[:, 2], 
             'b-', linewidth=3, label='Actual Physics')
    ax2.scatter(physics_positions[0, 0], physics_positions[0, 1], physics_positions[0, 2],
                color='green', s=100, label='Start')
    ax2.scatter(physics_positions[-1, 0], physics_positions[-1, 1], physics_positions[-1, 2],
                color='red', s=100, label='End')
    
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.set_title('3D Trajectory')
    ax2.legend()
    
    # 预测精度分析
    ax3 = plt.subplot(2, 2, 3)
    prediction_errors = []
    
    for i, prediction in enumerate(ai_predictions):
        if prediction is not None and i < len(physics_positions) - 1:
            actual_next = physics_positions[i + 1]
            predicted_next = prediction[0][:3]
            error = np.linalg.norm(actual_next - predicted_next)
            prediction_errors.append(error)
        else:
            prediction_errors.append(np.nan)
    
    valid_errors = [e for e in prediction_errors if not np.isnan(e)]
    ax3.plot(range(len(prediction_errors)), prediction_errors, 'ro-', alpha=0.7)
    ax3.set_xlabel('Time Step')
    ax3.set_ylabel('Prediction Error')
    ax3.set_title('AI Prediction Error Over Time')
    ax3.grid(True, alpha=0.3)
    
    if valid_errors:
        avg_error = np.mean(valid_errors)
        ax3.axhline(y=avg_error, color='orange', linestyle='--', 
                   label=f'Avg Error: {avg_error:.3f}')
        ax3.legend()
    
    # 统计信息
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    # 计算统计信息
    total_distance = np.sum(np.linalg.norm(np.diff(physics_positions, axis=0), axis=1))
    max_height = np.max(physics_positions[:, 1])
    min_height = np.min(physics_positions[:, 1])
    
    avg_error = np.mean(valid_errors) if valid_errors else 0
    max_error = np.max(valid_errors) if valid_errors else 0
    min_error = np.min(valid_errors) if valid_errors else 0
    
    avg_error_str = f"{avg_error:.3f}" if valid_errors else "N/A"
    max_error_str = f"{max_error:.3f}" if valid_errors else "N/A"
    min_error_str = f"{min_error:.3f}" if valid_errors else "N/A"
    
    stats_text = f"""
    Physics Simulation Statistics:
    
    Total Distance Traveled: {total_distance:.2f}
    Max Height: {max_height:.2f}
    Min Height: {min_height:.2f}
    
    AI Prediction Statistics:
    
    Valid Predictions: {len(valid_errors)}/{len(ai_predictions)}
    Average Error: {avg_error_str}
    Max Error: {max_error_str}
    Min Error: {min_error_str}
    """
    
    ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
             fontsize=11, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('ai_physics_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n📈 对比图表已保存: ai_physics_comparison.png")
    
    if valid_errors:
        print(f"📊 AI预测性能:")
        print(f"   平均误差: {np.mean(valid_errors):.3f}")
        print(f"   标准差: {np.std(valid_errors):.3f}")
        print(f"   成功预测率: {len(valid_errors)}/{len(ai_predictions)} ({len(valid_errors)/len(ai_predictions)*100:.1f}%)")

if __name__ == "__main__":
    try:
        compare_ai_vs_physics()
    except Exception as e:
        print(f"❌ 对比演示失败: {e}")
        import traceback
        traceback.print_exc()
