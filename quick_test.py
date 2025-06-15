#!/usr/bin/env python3
"""
测试改进后的障碍物系统
"""

import sys
import os
sys.path.append('/root/virtual')

try:
    from src.physics import PhysicsEngine, Cube
    print("✅ 模块导入成功")
    
    # 测试新的障碍物配置
    engine = PhysicsEngine()
    engine.add_obstacles('bouncy_obstacles')
    
    print(f"📦 障碍物数量: {len(engine.obstacle_manager.obstacles)}")
    for i, obs in enumerate(engine.obstacle_manager.obstacles):
        print(f"  {i+1}. {obs.obstacle_type.upper()}: 位置{obs.position}")
    
    # 测试新的立方体配置
    cube = Cube([-1, -2, 14], [1.5, 1.0, 0], size=1.5)
    cube.restitution = 0.85
    print(f"\n🎯 立方体: 位置{cube.position}, 速度{cube.velocity}, 弹性{cube.restitution}")
    
    # 快速模拟测试
    collision_count = 0
    for step in range(50):
        engine.step([cube])
        
        # 检查碰撞
        for obs in engine.obstacle_manager.obstacles:
            if obs.check_collision(cube.position, cube.size):
                collision_count += 1
                break
    
    print(f"\n📊 50步模拟结果:")
    print(f"  碰撞次数: {collision_count}")
    print(f"  最终位置: {cube.position}")
    print(f"  最终速度: {cube.velocity}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
