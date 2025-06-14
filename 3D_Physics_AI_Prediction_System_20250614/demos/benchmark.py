#!/usr/bin/env python3
"""
性能基准测试 - 测试系统各组件的性能
"""

import sys
import os
import time
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.ai import AIPredictor
import torch

def benchmark_physics_engine():
    """测试物理引擎性能"""
    print("⚡ 物理引擎性能测试")
    print("-" * 40)
    
    engine = PhysicsEngine()
    cubes = [Cube([i, 10, j], [0, 0, 0]) for i in range(-2, 3) for j in range(-2, 3)]
    
    # 预热
    for _ in range(10):
        engine.step(cubes)
    
    # 性能测试
    num_steps = 1000
    start_time = time.time()
    
    for _ in range(num_steps):
        engine.step(cubes)
    
    end_time = time.time()
    duration = end_time - start_time
    fps = num_steps / duration
    
    print(f"立方体数量: {len(cubes)}")
    print(f"模拟步数: {num_steps}")
    print(f"总耗时: {duration:.3f}秒")
    print(f"物理FPS: {fps:.1f}")
    print(f"每个立方体: {fps/len(cubes):.1f} FPS")

def benchmark_ai_prediction():
    """测试AI预测性能"""
    print("\n🧠 AI预测性能测试")
    print("-" * 40)
    
    # 检查是否有训练好的模型
    model_path = 'output/models/quick_physics_predictor.pth'
    if not os.path.exists(model_path):
        print("❌ 未找到训练好的模型")
        return
    
    predictor = AIPredictor()
    predictor.load_model(model_path)
    
    # 创建测试数据
    engine = PhysicsEngine()
    cube = Cube([0, 10, 0], [1, 0, 0])
    
    # 建立历史数据
    for _ in range(predictor.sequence_length):
        engine.step([cube])
    
    # 预热
    for _ in range(5):
        predictor.predict_next_states([cube], steps=5)
    
    # 性能测试
    num_predictions = 100
    prediction_steps = 10
    
    start_time = time.time()
    
    for _ in range(num_predictions):
        prediction = predictor.predict_next_states([cube], steps=prediction_steps)
        engine.step([cube])  # 更新历史
    
    end_time = time.time()
    duration = end_time - start_time
    fps = num_predictions / duration
    
    print(f"预测次数: {num_predictions}")
    print(f"每次预测步数: {prediction_steps}")
    print(f"总耗时: {duration:.3f}秒")
    print(f"预测FPS: {fps:.1f}")
    print(f"设备: {predictor.device}")

def benchmark_memory_usage():
    """测试内存使用情况"""
    print("\n💾 内存使用测试")
    print("-" * 40)
    
    import psutil
    process = psutil.Process(os.getpid())
    
    # 基线内存
    baseline_memory = process.memory_info().rss / 1024 / 1024
    print(f"基线内存: {baseline_memory:.1f} MB")
    
    # 创建物理系统
    engine = PhysicsEngine()
    cubes = [Cube([i, 10, j], [0, 0, 0]) for i in range(-5, 6) for j in range(-5, 6)]
    
    physics_memory = process.memory_info().rss / 1024 / 1024
    print(f"物理系统内存: {physics_memory:.1f} MB (+{physics_memory-baseline_memory:.1f} MB)")
    
    # 加载AI模型
    model_path = 'output/models/quick_physics_predictor.pth'
    if os.path.exists(model_path):
        predictor = AIPredictor()
        predictor.load_model(model_path)
        
        ai_memory = process.memory_info().rss / 1024 / 1024
        print(f"AI系统内存: {ai_memory:.1f} MB (+{ai_memory-physics_memory:.1f} MB)")
    
    # 运行一段时间模拟
    for _ in range(1000):
        engine.step(cubes)
    
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"运行后内存: {final_memory:.1f} MB")

def benchmark_gpu_vs_cpu():
    """比较GPU和CPU性能"""
    print("\n🚀 GPU vs CPU 性能对比")
    print("-" * 40)
    
    if not torch.cuda.is_available():
        print("❌ CUDA不可用，跳过GPU测试")
        return
    
    model_path = 'output/models/quick_physics_predictor.pth'
    if not os.path.exists(model_path):
        print("❌ 未找到训练好的模型")
        return
    
    # CPU测试
    print("测试CPU性能...")
    predictor_cpu = AIPredictor(device=torch.device('cpu'))
    predictor_cpu.load_model(model_path)
    
    # 创建测试数据
    test_sequences = torch.randn(32, 10, 13)  # batch_size=32
    
    start_time = time.time()
    for _ in range(50):
        with torch.no_grad():
            output, _ = predictor_cpu.model(test_sequences)
    cpu_time = time.time() - start_time
    
    # GPU测试
    print("测试GPU性能...")
    predictor_gpu = AIPredictor(device=torch.device('cuda'))
    predictor_gpu.load_model(model_path)
    test_sequences_gpu = test_sequences.cuda()
    
    # GPU预热
    for _ in range(10):
        with torch.no_grad():
            output, _ = predictor_gpu.model(test_sequences_gpu)
    torch.cuda.synchronize()
    
    start_time = time.time()
    for _ in range(50):
        with torch.no_grad():
            output, _ = predictor_gpu.model(test_sequences_gpu)
    torch.cuda.synchronize()
    gpu_time = time.time() - start_time
    
    print(f"CPU时间: {cpu_time:.3f}秒")
    print(f"GPU时间: {gpu_time:.3f}秒")
    print(f"加速比: {cpu_time/gpu_time:.1f}x")

def run_all_benchmarks():
    """运行所有基准测试"""
    print("🏁 系统性能基准测试")
    print("=" * 50)
    
    benchmark_physics_engine()
    benchmark_ai_prediction()
    benchmark_memory_usage()
    benchmark_gpu_vs_cpu()
    
    print("\n" + "=" * 50)
    print("✅ 所有基准测试完成！")

if __name__ == "__main__":
    try:
        run_all_benchmarks()
    except Exception as e:
        print(f"❌ 基准测试失败: {e}")
        import traceback
        traceback.print_exc()
