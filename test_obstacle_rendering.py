#!/usr/bin/env python3
"""
测试障碍物渲染功能
"""

import matplotlib
matplotlib.use('Agg')  # 无头模式

from src.physics import PhysicsEngine
from src.rendering import VideoGenerator, Scene3D

def test_obstacle_rendering():
    """测试障碍物渲染"""
    print("🧱 测试障碍物渲染功能...")
    
    # 创建物理引擎和障碍物
    engine = PhysicsEngine()
    engine.add_obstacles('bouncy_obstacles')
    
    print(f"✅ 已添加 {len(engine.obstacle_manager.obstacles)} 个障碍物")
    
    # 测试获取渲染数据
    obstacle_data = engine.get_obstacles_render_data()
    print(f"✅ 获取到 {len(obstacle_data)} 个障碍物的渲染数据")
    
    for i, data in enumerate(obstacle_data):
        print(f"  障碍物 {i+1}: 类型={data.get('type', 'unknown')}")
    
    # 创建场景和视频生成器
    scene = Scene3D()
    video_gen = VideoGenerator(scene)
    
    # 测试_render_simple_obstacle方法
    print("🎨 测试障碍物渲染方法...")
    
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    try:
        for data in obstacle_data:
            video_gen._render_simple_obstacle(ax, data)
        print("✅ 障碍物渲染方法正常工作")
    except Exception as e:
        print(f"❌ 障碍物渲染错误: {e}")
        return False
    
    plt.close(fig)
    
    print("🎉 障碍物渲染功能测试通过！")
    return True

if __name__ == "__main__":
    test_obstacle_rendering()
