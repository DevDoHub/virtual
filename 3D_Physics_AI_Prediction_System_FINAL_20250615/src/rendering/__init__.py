"""
渲染模块

包含：
- Scene3D: 3D场景管理和渲染
- VideoGenerator: 视频生成器
"""

from .scene3d import Scene3D
from .video_generator import VideoGenerator

__all__ = ['Scene3D', 'VideoGenerator']
