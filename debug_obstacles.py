#!/usr/bin/env python3
"""
调试障碍物交互问题
"""

import numpy as np
from src.physics import Cube, PhysicsEngine
from src.rendering import Scene3D, VideoGenerator

def debug_obstacle_interaction():
    """调试障碍物交互"""
    print("🔍 调试障碍物交互...")
    
    # 创建物理环境
    engine = PhysicsEngine(gravity=9.81)
    engine.add_obstacles('bouncy_obstacles')
    
    # 打印障碍物信息
    print(f"\n📦 场景中有 {len(engine.obstacle_manager.obstacles)} 个障碍物:")
    for i, obs in enumerate(engine.obstacle_manager.obstacles):
        print(f"  {i+1}. {obs.obstacle_type.upper()}: 位置{obs.position}, 尺寸{obs.size}")
    
    # 创建立方体 - 从更高位置开始
    cube = Cube([0, 0, 15], [0, 0, 0], size=1.5)
    cube.restitution = 0.8  # 高弹性
    
    print(f"\n🎯 立方体初始状态:")
    print(f"  位置: {cube.position}")
    print(f"  速度: {cube.velocity}")
    print(f"  尺寸: {cube.size}")
    print(f"  弹性系数: {cube.restitution}")
    
    # 模拟前几步，检查碰撞
    print(f"\n⚡ 模拟前10步:")
    collision_count = 0
    
    for step in range(150):  # 5秒
        engine.step([cube])
        
        # 检查是否发生碰撞
        collided = False
        for j, obs in enumerate(engine.obstacle_manager.obstacles):
            if obs.check_collision(cube.position, cube.size):
                if step % 10 == 0:  # 每10步输出一次
                    print(f"  步骤 {step}: 碰撞障碍物 {j+1} ({obs.obstacle_type})")
                    print(f"    立方体位置: {cube.position}")
                    print(f"    立方体速度: {cube.velocity}")
                collided = True
                collision_count += 1
                break
        
        # 如果立方体停下来了就退出
        if np.linalg.norm(cube.velocity) < 0.1 and cube.position[2] < 5:
            print(f"  步骤 {step}: 立方体基本静止")
            break
            
        if step % 30 == 0:  # 每1秒输出位置
            print(f"  步骤 {step}: 位置{cube.position[:2]}, 高度{cube.position[2]:.1f}, 速度{np.linalg.norm(cube.velocity):.1f}")
    
    print(f"\n📊 统计结果:")
    print(f"  总碰撞次数: {collision_count}")
    print(f"  最终位置: {cube.position}")
    print(f"  最终速度: {cube.velocity}")
    
    return collision_count > 0

if __name__ == "__main__":
    debug_obstacle_interaction()
