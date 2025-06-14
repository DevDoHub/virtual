#!/bin/bash

echo "================================================"
echo "3D Physics AI Prediction System - Video Downloads"
echo "Graduate AI Course Project"
echo "================================================"

VIDEO_DIR="/root/virtual/output/videos"
TOTAL_SIZE=0

if [ ! -d "$VIDEO_DIR" ]; then
    echo "❌ Video directory not found: $VIDEO_DIR"
    exit 1
fi

echo "📹 Available demonstration videos:"
echo ""

# 主要演示视频
echo "🎯 MAIN DEMONSTRATIONS:"
echo "1. basic_fall.mp4                    - Basic cube falling physics"
echo "2. high_energy_bounce.mp4            - High energy collision demo"  
echo "3. spinning_cube.mp4                 - Rotating cube with physics"
echo "4. server_physics_demo.mp4           - Server environment demo"
echo "5. simple_fixed_demo.mp4             - Fixed physics collision"
echo ""

# 改进的清晰演示
echo "🔧 IMPROVED CLEAR DEMONSTRATIONS:"
echo "6. simple_clear_demo.mp4             - Clear simple physics"
echo "7. clear_basic_fall.mp4              - Clear basic falling"
echo "8. clear_basic_fall_improved.mp4     - Enhanced basic fall"
echo "9. clear_angled_fall.mp4             - Angled trajectory fall"
echo "10. clear_angled_fall_improved.mp4   - Enhanced angled fall"
echo "11. clear_bouncing_cube_improved.mp4 - Enhanced bouncing cube"
echo "12. clear_bouncy_ball.mp4            - Bouncy ball physics"
echo "13. clear_high_energy_improved.mp4   - Enhanced high energy"
echo "14. clear_low_gravity.mp4            - Low gravity simulation"
echo ""

# 视角优化演示
echo "👁️ VIEWING ANGLE OPTIMIZATIONS:"
echo "15. intuitive_physics_demo.mp4       - Y-axis vertical view"
echo "16. quick_intuitive_y_up_demo.mp4    - Quick Y-up demonstration"
echo "17. rotated_ground_plane_demo.mp4    - X-Z ground plane view"
echo ""

# AI预测演示
echo "🤖 AI PREDICTION DEMONSTRATIONS:"
echo "18. 05_ai_prediction.mp4             - LSTM motion prediction"
echo "19. 06_complex_motion.mp4            - Complex trajectory AI"
echo ""

# 物理变量演示
echo "⚗️ PHYSICS VARIATIONS:"
echo "20. 01_basic_fall.mp4                - Standard physics"
echo "21. 02_high_energy.mp4               - High impact energy"
echo "22. 03_low_gravity.mp4               - Reduced gravity"
echo "23. 04_bouncy_cube.mp4               - High elasticity"
echo ""

echo "📊 Video file details:"
echo "----------------------------------------"

cd "$VIDEO_DIR"
for video in *.mp4; do
    if [ -f "$video" ]; then
        size=$(du -h "$video" | cut -f1)
        size_bytes=$(du -b "$video" | cut -f1)
        TOTAL_SIZE=$((TOTAL_SIZE + size_bytes))
        duration=$(ffprobe -v quiet -show_entries format=duration -of csv="p=0" "$video" 2>/dev/null | cut -d'.' -f1)
        if [ -z "$duration" ]; then
            duration="N/A"
        else
            duration="${duration}s"
        fi
        printf "%-35s %8s %8s\n" "$video" "$size" "$duration"
    fi
done

echo "----------------------------------------"
total_mb=$((TOTAL_SIZE / 1024 / 1024))
echo "📁 Total size: ${total_mb}MB"
echo "🎬 Total videos: $(find . -name "*.mp4" | wc -l)"

echo ""
echo "🔗 Download commands for individual videos:"
echo "----------------------------------------"
echo "# Basic physics demonstrations"
echo "scp user@server:/root/virtual/output/videos/basic_fall.mp4 ."
echo "scp user@server:/root/virtual/output/videos/high_energy_bounce.mp4 ."
echo "scp user@server:/root/virtual/output/videos/spinning_cube.mp4 ."
echo ""
echo "# Viewing angle optimizations"  
echo "scp user@server:/root/virtual/output/videos/intuitive_physics_demo.mp4 ."
echo "scp user@server:/root/virtual/output/videos/quick_intuitive_y_up_demo.mp4 ."
echo "scp user@server:/root/virtual/output/videos/rotated_ground_plane_demo.mp4 ."
echo ""
echo "# AI prediction demonstrations"
echo "scp user@server:/root/virtual/output/videos/05_ai_prediction.mp4 ."
echo "scp user@server:/root/virtual/output/videos/06_complex_motion.mp4 ."
echo ""
echo "# Download all videos"
echo "scp user@server:/root/virtual/output/videos/*.mp4 ./videos/"
echo ""

echo "================================================"
echo "🎓 3D Physics AI Prediction System Complete"
echo "📚 Ready for Graduate AI Course Submission"
echo "================================================"
