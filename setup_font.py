#!/usr/bin/env python3
"""
设置matplotlib中文字体支持
"""

import matplotlib.pyplot as plt
import matplotlib
import platform

def setup_chinese_font():
    """设置中文字体支持"""
    try:
        # 对于Linux系统，尝试使用DejaVu Sans或其他字体
        if platform.system() == 'Linux':
            # 设置使用内置字体，避免中文字符问题
            plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 或者直接禁用字体警告并使用英文
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            
        elif platform.system() == 'Windows':
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            
        elif platform.system() == 'Darwin':  # macOS
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC']
            plt.rcParams['axes.unicode_minus'] = False
            
    except Exception as e:
        print(f"字体设置失败: {e}")

if __name__ == "__main__":
    setup_chinese_font()
    print("字体设置完成")
