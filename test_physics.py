#!/usr/bin/env python3
"""
简单的物理引擎测试和可视化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D
import matplotlib.pyplot as plt
import numpy as np

def test_basic_physics():
    """测试基础物理功能"""
    print("🧪 测试基础物理功能...")
    
    # 创建物理引擎
    engine = PhysicsEngine(gravity=9.81)
    
    # 创建立方体
    cube = Cube([0, 10, 0], [2, 0, 1], size=1.0)
    
    # 运行50步物理模拟
    positions = []
    energies = []
    
    for step in range(50):
        positions.append(cube.position.copy())
        energy = cube.get_kinetic_energy() + cube.get_potential_energy(engine.gravity)
        energies.append(energy)
        
        engine.step([cube])
        
        if step % 10 == 0:
            print(f"步骤 {step}: 位置={cube.position}, 能量={energy:.2f}J")
    
    print(f"✅ 物理测试完成! 最终位置: {cube.position}")
    
    # 绘制轨迹
    positions = np.array(positions)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 轨迹图
    ax1.plot(positions[:, 0], positions[:, 1], 'b-', linewidth=2, label='Trajectory')
    ax1.scatter(positions[0, 0], positions[0, 1], color='green', s=100, label='Start')
    ax1.scatter(positions[-1, 0], positions[-1, 1], color='red', s=100, label='End')
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position') 
    ax1.set_title('2D Trajectory Projection')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 能量图
    ax2.plot(energies, 'r-', linewidth=2)
    ax2.set_xlabel('Time Steps')
    ax2.set_ylabel('Total Energy (J)')
    ax2.set_title('Energy vs Time')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_physics.png', dpi=150, bbox_inches='tight')
    plt.show()

def test_3d_rendering():
    """测试3D渲染"""
    print("🎨 测试3D渲染...")
    
    # 创建场景
    scene = Scene3D()
    
    # 创建立方体
    cube = Cube([0, 5, 0], [1, 0, 0.5], size=2.0)
    
    # 添加一些历史轨迹
    for i in range(20):
        cube.history.append(cube.get_state_vector())
        cube.position += cube.velocity * 0.1
        cube.velocity[1] -= 0.98  # 模拟重力
    
    # 渲染
    scene.render_cube(cube, show_trajectory=True)
    scene.add_text("Test 3D Rendering\nCube Falling")
    
    print("✅ 3D渲染测试完成!")
    scene.show()

def test_collision_detection():
    """测试碰撞检测"""
    print("💥 测试碰撞检测...")
    
    engine = PhysicsEngine(bounds=[(-5, 5), (0, 10), (-5, 5)])
    cube = Cube([0, 8, 0], [3, -2, 2], size=1.0)
    
    print(f"初始状态: 位置={cube.position}, 速度={cube.velocity}")
    
    # 运行直到发生碰撞
    for step in range(100):
        old_pos = cube.position.copy()
        old_vel = cube.velocity.copy()
        
        engine.step([cube])
        
        # 检查是否发生了碰撞（速度方向改变）
        vel_change = np.linalg.norm(cube.velocity - old_vel)
        if vel_change > 1.0:  # 显著的速度变化
            print(f"碰撞发生在步骤 {step}!")
            print(f"  碰撞前: 位置={old_pos}, 速度={old_vel}")
            print(f"  碰撞后: 位置={cube.position}, 速度={cube.velocity}")
            break
    
    print("✅ 碰撞检测测试完成!")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...\n")
    
    try:
        test_basic_physics()
        print()
        test_collision_detection()
        print()
        test_3d_rendering()
        
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
