"""
工具函数模块
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def plot_training_curves(train_losses, val_losses, save_path=None):
    """绘制训练曲线"""
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='训练损失', color='blue')
    plt.plot(val_losses, label='验证损失', color='red')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('训练损失曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_energy_conservation(frame_data, save_path=None):
    """绘制能量守恒图"""
    times = [frame['time'] for frame in frame_data]
    energies = [frame['energy'] for frame in frame_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(times, energies, 'b-', linewidth=2)
    plt.xlabel('时间 (s)')
    plt.ylabel('总能量 (J)')
    plt.title('系统能量随时间变化')
    plt.grid(True, alpha=0.3)
    
    # 显示能量损失百分比
    energy_loss = ((energies[0] - energies[-1]) / energies[0]) * 100
    plt.text(0.7, 0.9, f'能量损失: {energy_loss:.2f}%', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def plot_trajectory_3d(positions, save_path=None):
    """绘制3D轨迹"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    positions = np.array(positions)
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'b-', linewidth=2)
    ax.scatter(positions[0, 0], positions[0, 1], positions[0, 2], 
               color='green', s=100, label='起点')
    ax.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2], 
               color='red', s=100, label='终点')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('立方体运动轨迹')
    ax.legend()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

def calculate_prediction_accuracy(predictions, actual, components=['position', 'velocity']):
    """计算预测精度"""
    results = {}
    
    predictions = np.array(predictions)
    actual = np.array(actual)
    
    if 'position' in components:
        pos_pred = predictions[:, :3]
        pos_actual = actual[:, :3]
        pos_error = np.sqrt(np.sum((pos_pred - pos_actual)**2, axis=1))
        results['position_rmse'] = np.sqrt(np.mean(pos_error**2))
        results['position_mae'] = np.mean(pos_error)
    
    if 'velocity' in components:
        vel_pred = predictions[:, 3:6]
        vel_actual = actual[:, 3:6]
        vel_error = np.sqrt(np.sum((vel_pred - vel_actual)**2, axis=1))
        results['velocity_rmse'] = np.sqrt(np.mean(vel_error**2))
        results['velocity_mae'] = np.mean(vel_error)
    
    return results

def create_config_file(config_dict, filepath):
    """创建配置文件"""
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4, ensure_ascii=False)

def load_config_file(filepath):
    """加载配置文件"""
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_video_info(video_path):
    """获取视频信息"""
    import cv2
    
    if not os.path.exists(video_path):
        return None
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        'fps': fps,
        'frame_count': frame_count,
        'width': width,
        'height': height,
        'duration': duration
    }

class Logger:
    """简单的日志记录器"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        
    def log(self, message, level='INFO'):
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {level}: {message}"
        
        print(log_message)
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
    
    def info(self, message):
        self.log(message, 'INFO')
    
    def warning(self, message):
        self.log(message, 'WARNING')
    
    def error(self, message):
        self.log(message, 'ERROR')
