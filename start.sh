#!/bin/bash
# 3D立方体下落与AI预测系统 - 启动脚本

echo "🎯 3D立方体下落与AI预测系统"
echo "================================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 检查依赖
echo "检查依赖包..."
if python3 -c "import torch, numpy, matplotlib" 2>/dev/null; then
    echo "✅ 主要依赖已安装"
else
    echo "❌ 缺少依赖包，正在安装..."
    pip install -r requirements.txt
fi

# 检查CUDA
if python3 -c "import torch; print('✅ CUDA可用' if torch.cuda.is_available() else '⚠️  仅CPU模式')" 2>/dev/null; then
    :
else
    echo "⚠️  PyTorch未正确安装"
fi

echo ""
echo "🚀 选择运行模式:"
echo "1. 完整演示 (推荐新用户)"
echo "2. 快速AI演示"
echo "3. 生成演示视频"
echo "4. 性能基准测试"
echo "5. 基础物理测试"
echo "6. AI预测对比"
echo "7. 自定义演示"
echo ""

read -p "请选择 (1-7): " choice

case $choice in
    1)
        echo "🎬 启动完整演示..."
        python3 complete_demo.py
        ;;
    2)
        echo "🤖 启动快速AI演示..."
        python3 quick_ai_demo.py
        ;;
    3)
        echo "🎥 生成演示视频..."
        python3 video_demo.py
        ;;
    4)
        echo "⚡ 运行性能测试..."
        python3 benchmark.py
        ;;
    5)
        echo "🧪 基础物理测试..."
        python3 test_physics.py
        ;;
    6)
        echo "🔍 AI预测对比..."
        python3 ai_comparison_demo.py
        ;;
    7)
        echo "⚙️  自定义演示模式..."
        echo "可用场景: basic, high_energy, low_gravity, bouncy"
        read -p "选择场景: " scenario
        read -p "时长(秒): " duration
        read -p "启用AI预测? (y/n): " ai_flag
        read -p "保存视频? (y/n): " video_flag
        
        cmd="python3 main.py --scenario $scenario --duration $duration"
        if [[ $ai_flag == "y" ]]; then
            cmd="$cmd --ai-predict"
        fi
        if [[ $video_flag == "y" ]]; then
            cmd="$cmd --save-video"
        fi
        
        echo "执行: $cmd"
        eval $cmd
        ;;
    *)
        echo "💡 默认运行交互式演示..."
        python3 main.py
        ;;
esac

echo ""
echo "🎉 演示完成！查看生成的文件:"
echo "📁 输出目录: output/"
echo "📊 图表文件: *.png"
echo "🎬 视频文件: videos/"
echo ""
echo "💡 更多选项:"
echo "   ./start.sh  - 重新运行此脚本"
echo "   python3 -h  - 查看帮助"
