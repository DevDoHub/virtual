#!/bin/bash
# 视频下载脚本
# 使用方法: ./download_videos.sh user@server

if [ -z "$1" ]; then
    echo "使用方法: $0 user@server"
    exit 1
fi

SERVER=$1
LOCAL_DIR="physics_videos"

echo "📁 创建本地目录..."
mkdir -p $LOCAL_DIR

echo "📥 开始下载视频..."
scp $SERVER:/root/virtual/output/videos/01_basic_fall.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/02_high_energy.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/03_low_gravity.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/04_bouncy_cube.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/05_ai_prediction.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/06_complex_motion.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/basic_fall.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/high_energy_bounce.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/server_physics_demo.mp4 $LOCAL_DIR/
scp $SERVER:/root/virtual/output/videos/spinning_cube.mp4 $LOCAL_DIR/

echo "📊 下载其他文件..."
scp $SERVER:/root/virtual/ai_physics_comparison.png $LOCAL_DIR/
scp $SERVER:/root/virtual/output/models/quick_physics_predictor.pth $LOCAL_DIR/
scp $SERVER:/root/virtual/PROJECT_SUMMARY.md $LOCAL_DIR/
scp $SERVER:/root/virtual/COMPLETION_REPORT.md $LOCAL_DIR/

echo "✅ 所有视频下载完成!"
echo "📁 视频保存在: $LOCAL_DIR/"
echo "🎬 可以使用VLC等播放器查看"
