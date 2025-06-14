#!/usr/bin/env python3
"""
简单的坐标系统验证测试
确保X-Y平面为地面，Z轴为垂直方向
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from src.physics import Cube, PhysicsEngine

def test_coordinate_system():
    """测试坐标系统是否正确"""
    print("🧪 坐标系统验证测试")
    print("=" * 40)
    
    # 创建立方体 - Z轴高度15米，X-Y平面初始速度
    cube = Cube(position=[0, 0, 15], velocity=[1, 0, 0], size=2.0)
    engine = PhysicsEngine(gravity=9.81)
    
    print(f"📍 初始位置: {cube.position} (X-Y地面，Z轴高度)")
    print(f"🏃 初始速度: {cube.velocity} (X-Y平面水平运动)")
    print(f"⚡ 重力设置: Z轴负方向 -9.81 m/s²")
    print()
    
    # 模拟几个时间步
    print("📊 模拟过程:")
    for step in range(5):
        engine.step([cube])
        z_height = cube.position[2]
        z_velocity = cube.velocity[2] 
        print(f"步骤 {step+1}: Z高度={z_height:.2f}m, Z速度={z_velocity:.2f}m/s")
    
    print()
    # 验证结果
    if cube.position[2] < 15:  # Z坐标应该减少（下落）
        print("✅ 重力正确：立方体沿Z轴下落")
    else:
        print("❌ 重力错误：立方体没有下落")
        
    if cube.velocity[2] < 0:  # Z方向速度应该为负（向下）
        print("✅ 速度方向正确：Z轴负向速度")
    else:
        print("❌ 速度方向错误")
        
    # 测试势能计算
    pe = cube.get_potential_energy(engine.gravity)
    expected_pe = cube.mass * engine.gravity * cube.position[2]
    if abs(pe - expected_pe) < 1e-10:
        print("✅ 势能计算正确：使用Z轴高度")
    else:
        print("❌ 势能计算错误")
        
    print(f"📏 当前势能: {pe:.2f} J (基于Z轴高度)")
    print()
    print("🎯 坐标系统验证完成!")

if __name__ == "__main__":
    test_coordinate_system()
