#!/usr/bin/env python3
"""
创建最终项目包 - 包含所有视角优化和改进
===========================================

这个脚本创建最终的项目交付包，包括：
- 所有源代码文件
- 所有演示视频（包括新的视角优化）
- 完整的文档
- 下载脚本和工具
"""

import os
import shutil
import json
from datetime import datetime

def create_final_package():
    """创建最终项目包"""
    
    print("🎯 Creating Final Project Package with View Optimizations")
    print("=" * 60)
    
    # 包目录
    package_name = "3D_Physics_AI_Prediction_System_FINAL_20250615"
    package_path = f"/root/virtual/{package_name}"
    
    # 清理旧包
    if os.path.exists(package_path):
        shutil.rmtree(package_path)
    
    os.makedirs(package_path, exist_ok=True)
    
    print(f"📦 Package path: {package_path}")
    
    # 1. 复制核心源代码
    print("📄 Copying source code...")
    
    source_dirs = [
        ("/root/virtual/src", f"{package_path}/src"),
    ]
    
    for src, dst in source_dirs:
        if os.path.exists(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✅ {src} -> {dst}")
    
    # 2. 复制主要脚本
    print("🔧 Copying main scripts...")
    
    main_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "PROJECT_SUMMARY.md", 
        "COMPLETION_REPORT.md",
        "FINAL_PROJECT_REPORT.md"
    ]
    
    for file in main_files:
        src_file = f"/root/virtual/{file}"
        dst_file = f"{package_path}/{file}"
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"  ✅ {file}")
    
    # 3. 复制演示脚本（包括新的视角优化）
    print("🎬 Copying demonstration scripts...")
    
    demos_dir = f"{package_path}/demos"
    os.makedirs(demos_dir, exist_ok=True)
    
    demo_files = [
        "quick_ai_demo.py",
        "benchmark.py", 
        "test_physics.py",
        "server_video_demo.py",
        "quick_videos.py",
        "simple_fixed_demo.py",
        "intuitive_physics_demo.py",
        "quick_intuitive_demo.py",
        "rotated_ground_demo.py",
        "create_improved_videos.py",
        "fixed_physics_demo.py",
        "simple_clear_demo.py"
    ]
    
    for demo in demo_files:
        src_file = f"/root/virtual/{demo}"
        dst_file = f"{demos_dir}/{demo}"
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"  ✅ {demo}")
    
    # 4. 复制所有视频（包括新的视角优化视频）
    print("📹 Copying all demonstration videos...")
    
    videos_src = "/root/virtual/output/videos"
    videos_dst = f"{package_path}/output/videos"
    
    if os.path.exists(videos_src):
        os.makedirs(videos_dst, exist_ok=True)
        video_count = 0
        total_size = 0
        
        for video_file in os.listdir(videos_src):
            if video_file.endswith('.mp4'):
                src_path = os.path.join(videos_src, video_file)
                dst_path = os.path.join(videos_dst, video_file)
                shutil.copy2(src_path, dst_path)
                
                size = os.path.getsize(src_path)
                total_size += size
                video_count += 1
                
                print(f"  ✅ {video_file} ({size/1024/1024:.1f}MB)")
        
        print(f"  📊 Total: {video_count} videos, {total_size/1024/1024:.1f}MB")
    
    # 5. 复制AI模型文件
    print("🤖 Copying AI models...")
    
    models_src = "/root/virtual/output/models"
    models_dst = f"{package_path}/output/models"
    
    if os.path.exists(models_src):
        shutil.copytree(models_src, models_dst, dirs_exist_ok=True)
        for model_file in os.listdir(models_dst):
            print(f"  ✅ {model_file}")
    
    # 6. 复制文档和图片
    print("📚 Copying documentation...")
    
    docs_dst = f"{package_path}/docs"
    os.makedirs(docs_dst, exist_ok=True)
    
    doc_files = [
        "ai_physics_comparison.png",
        "test_physics.png"
    ]
    
    for doc_file in doc_files:
        src_file = f"/root/virtual/{doc_file}"
        dst_file = f"{docs_dst}/{doc_file}"
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"  ✅ {doc_file}")
    
    # 7. 创建脚本目录
    print("📜 Creating scripts...")
    
    scripts_dst = f"{package_path}/scripts"
    os.makedirs(scripts_dst, exist_ok=True)
    
    # 复制下载脚本
    download_scripts = [
        "download_videos.sh",
        "download_all_videos.sh"
    ]
    
    for script in download_scripts:
        src_file = f"/root/virtual/{script}"
        dst_file = f"{scripts_dst}/{script}"
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            os.chmod(dst_file, 0o755)  # 设置可执行权限
            print(f"  ✅ {script}")
    
    # 8. 创建项目配置文件
    print("⚙️ Creating project configuration...")
    
    config = {
        "project_name": "3D Physics AI Prediction System",
        "version": "1.0.0-final",
        "created_date": datetime.now().isoformat(),
        "description": "Graduate AI Course Project - 3D Physics Simulation with LSTM Prediction",
        "features": [
            "3D Physics Engine with RK4 Integration",
            "LSTM Neural Network for Motion Prediction", 
            "High-Quality 3D Rendering and Visualization",
            "Multiple Viewing Angle Optimizations",
            "Video Generation and Export",
            "Server Environment Compatibility",
            "X-Z Ground Plane View Implementation",
            "Y-Axis Vertical Orientation Support",
            "Advanced Collision Detection",
            "Energy Conservation Monitoring"
        ],
        "viewing_optimizations": [
            "Y-axis vertical view (intuitive_physics_demo.mp4)",
            "Quick Y-up demonstration (quick_intuitive_y_up_demo.mp4)", 
            "X-Z ground plane view (rotated_ground_plane_demo.mp4)"
        ],
        "video_count": video_count if 'video_count' in locals() else 0,
        "total_size_mb": round(total_size/1024/1024, 1) if 'total_size' in locals() else 0,
        "python_version": "3.11+",
        "dependencies": [
            "numpy", "matplotlib", "torch", "opencv-python", "scipy"
        ]
    }
    
    config_file = f"{package_path}/project_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, indent=2, fp=f)
    print(f"  ✅ project_config.json")
    
    # 9. 创建README文件
    print("📖 Creating final README...")
    
    readme_content = f"""# 3D Physics AI Prediction System - Final Version

## Graduate AI Course Project

**Version:** 1.0.0-final  
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Status:** ✅ COMPLETE WITH VIEW OPTIMIZATIONS

## 🎯 Project Overview

This is a comprehensive 3D physics simulation system with AI prediction capabilities, featuring multiple viewing angle optimizations based on user feedback.

## 🔑 Key Features

### Core Capabilities
- **3D Physics Engine**: RK4 numerical integration, collision detection
- **AI Prediction**: LSTM neural network for motion forecasting  
- **3D Visualization**: High-quality rendering and animation
- **Video Generation**: Multiple demonstration scenarios
- **Server Compatibility**: Headless operation for SSH environments

### New: Viewing Angle Optimizations
- **Y-Axis Vertical View**: Natural height orientation (elev=30, azim=45)
- **X-Z Ground Plane View**: Rotated coordinate system with horizontal ground
- **Quick Demonstrations**: Streamlined physics for rapid visualization

## 📹 Video Demonstrations

### Viewing Angle Optimizations ({len([f for f in os.listdir(videos_dst) if 'intuitive' in f or 'rotated' in f])} videos)
- `intuitive_physics_demo.mp4` - Y-axis vertical orientation
- `quick_intuitive_y_up_demo.mp4` - Quick Y-up demo  
- `rotated_ground_plane_demo.mp4` - X-Z ground plane view

### Main Demonstrations ({len([f for f in os.listdir(videos_dst) if f.startswith(('basic_', 'high_', 'spinning_', 'server_', 'simple_'))])} videos)
- Basic physics, high-energy collisions, rotation dynamics
- Server environment validation, collision verification

### AI Predictions ({len([f for f in os.listdir(videos_dst) if f.startswith('0')])} videos)
- LSTM motion prediction, complex trajectory forecasting

**Total: {len([f for f in os.listdir(videos_dst) if f.endswith('.mp4')])} demonstration videos**

## 🚀 Quick Start

### 1. Setup Environment
```bash
pip install -r requirements.txt
```

### 2. Run Basic Demonstration
```bash
python main.py
```

### 3. View Angle Optimizations
```bash
# Y-axis vertical view
python demos/intuitive_physics_demo.py

# X-Z ground plane view  
python demos/rotated_ground_demo.py

# Quick demonstration
python demos/quick_intuitive_demo.py
```

### 4. AI Training and Prediction
```bash
python demos/quick_ai_demo.py
```

## 📁 Project Structure

```
{package_name}/
├── src/                     # Core source code
│   ├── physics/            # Physics engine
│   ├── ai/                 # LSTM prediction system
│   ├── rendering/          # 3D visualization  
│   └── utils/              # Utilities
├── demos/                   # Demonstration scripts
├── output/
│   ├── videos/             # All demonstration videos
│   └── models/             # Trained AI models
├── docs/                   # Documentation and images
├── scripts/                # Download and utility scripts
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🎓 Educational Value

This project demonstrates:
- Advanced 3D physics simulation techniques
- LSTM neural network implementation  
- Real-time 3D graphics and visualization
- Software engineering best practices
- User feedback integration and iteration

## 📊 Technical Specifications

- **Physics Engine**: RK4 integration, quaternion rotation
- **AI System**: Multi-layer LSTM with 13D state vectors
- **Rendering**: Matplotlib 3D with multiple viewing angles
- **Video Export**: OpenCV MP4 encoding
- **Compatibility**: Linux server environments, SSH access

## 🔄 Recent Improvements

Based on user feedback, we implemented:
1. **Multiple Viewing Angles**: Y-vertical and X-Z ground plane views
2. **Enhanced Physics**: Improved collision detection and ground landing
3. **Visual Clarity**: Better trajectory tracking and status indicators
4. **Performance**: Optimized rendering and video generation

## 📞 Support

For questions about this project:
- Check the documentation in `/docs/`
- Review demonstration videos in `/output/videos/`
- Examine source code with detailed comments

## 🎉 Completion Status

✅ **PROJECT COMPLETE** - Ready for graduate course submission

---

*3D Physics AI Prediction System - Graduate AI Course Project*
"""
    
    readme_file = f"{package_path}/README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"  ✅ Final README.md")
    
    # 10. 生成包统计信息
    print("📊 Generating package statistics...")
    
    def get_dir_size(path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += os.path.getsize(filepath)
        return total
    
    stats = {
        "package_name": package_name,
        "creation_date": datetime.now().isoformat(),
        "total_size_mb": round(get_dir_size(package_path) / 1024 / 1024, 1),
        "directories": {
            "src": len(os.listdir(f"{package_path}/src")) if os.path.exists(f"{package_path}/src") else 0,
            "demos": len(os.listdir(f"{package_path}/demos")) if os.path.exists(f"{package_path}/demos") else 0,
            "videos": len([f for f in os.listdir(f"{package_path}/output/videos") if f.endswith('.mp4')]) if os.path.exists(f"{package_path}/output/videos") else 0,
            "docs": len(os.listdir(f"{package_path}/docs")) if os.path.exists(f"{package_path}/docs") else 0
        },
        "key_improvements": [
            "X-Z ground plane viewing angle",
            "Y-axis vertical orientation", 
            "Enhanced physics collision detection",
            "Multiple demonstration scenarios",
            "Comprehensive documentation"
        ]
    }
    
    stats_file = f"{package_path}/package_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, indent=2, fp=f)
    print(f"  ✅ package_stats.json")
    
    # 最终报告
    print("\n" + "=" * 60)
    print("🎉 FINAL PROJECT PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📦 Package: {package_name}")
    print(f"📁 Location: {package_path}")
    print(f"💾 Total Size: {stats['total_size_mb']}MB")
    print(f"🎬 Videos: {stats['directories']['videos']}")
    print(f"🔧 Demos: {stats['directories']['demos']}")
    print("")
    print("🔑 Key Improvements in Final Version:")
    for improvement in stats['key_improvements']:
        print(f"  ✅ {improvement}")
    print("")
    print("📚 Ready for Graduate Course Submission!")
    print("=" * 60)
    
    return package_path

if __name__ == "__main__":
    try:
        package_path = create_final_package()
        print(f"\n✅ Final package ready at: {package_path}")
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        import traceback
        traceback.print_exc()
