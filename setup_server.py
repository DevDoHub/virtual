#!/usr/bin/env python3
"""
服务器环境配置 - 修复SSH远程运行的问题
"""

import matplotlib
# 设置无头模式，不需要图形界面
matplotlib.use('Agg')  # 必须在import pyplot之前设置

import matplotlib.pyplot as plt
import os
import subprocess

def setup_server_environment():
    """配置服务器环境"""
    print("🔧 配置服务器环境...")
    
    # 1. 设置matplotlib后端
    print("✅ 设置matplotlib无头模式")
    
    # 2. 检查ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg已安装")
        else:
            print("❌ ffmpeg未正确安装")
    except FileNotFoundError:
        print("❌ ffmpeg未安装，正在尝试安装...")
        try:
            # 尝试安装ffmpeg
            subprocess.run(['apt', 'update'], check=True)
            subprocess.run(['apt', 'install', '-y', 'ffmpeg'], check=True)
            print("✅ ffmpeg安装成功")
        except Exception as e:
            print(f"⚠️  自动安装失败: {e}")
            print("请手动安装: sudo apt install ffmpeg")
    
    # 3. 设置字体和显示
    plt.rcParams['font.family'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 4. 创建输出目录
    os.makedirs('output/videos', exist_ok=True)
    os.makedirs('output/images', exist_ok=True)
    
    print("🎯 服务器环境配置完成!")

if __name__ == "__main__":
    setup_server_environment()
