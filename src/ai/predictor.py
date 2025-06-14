import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Tuple
from ..physics import Cube

class PhysicsLSTM(nn.Module):
    """LSTM神经网络用于预测物理状态"""
    
    def __init__(self, input_size=13, hidden_size=128, num_layers=2, output_size=13):
        """
        初始化LSTM网络
        
        Args:
            input_size: 输入特征维度 [x,y,z,vx,vy,vz,qw,qx,qy,qz,wx,wy,wz]
            hidden_size: 隐藏层维度
            num_layers: LSTM层数
            output_size: 输出维度（与输入相同）
        """
        super(PhysicsLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        # 全连接层
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, output_size)
        )
        
        # 初始化权重
        self.init_weights()
    
    def init_weights(self):
        """初始化网络权重"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                if 'lstm' in name:
                    nn.init.xavier_uniform_(param)
                else:
                    nn.init.kaiming_normal_(param)
            elif 'bias' in name:
                nn.init.constant_(param, 0)
    
    def forward(self, x, hidden=None):
        """
        前向传播
        
        Args:
            x: 输入序列 [batch_size, sequence_length, input_size]
            hidden: 隐藏状态（可选）
            
        Returns:
            output: 预测输出 [batch_size, output_size]
            hidden: 新的隐藏状态
        """
        # LSTM前向传播
        lstm_out, hidden = self.lstm(x, hidden)
        
        # 取最后一个时间步的输出
        last_output = lstm_out[:, -1, :]
        
        # 全连接层
        output = self.fc_layers(last_output)
        
        return output, hidden
    
    def predict_sequence(self, x, steps=10):
        """
        预测未来多个时间步
        
        Args:
            x: 输入序列 [batch_size, sequence_length, input_size]
            steps: 预测步数
            
        Returns:
            predictions: 预测序列 [batch_size, steps, input_size]
        """
        self.eval()
        predictions = []
        
        with torch.no_grad():
            current_input = x.clone()
            hidden = None
            
            for _ in range(steps):
                # 预测下一步
                next_state, hidden = self.forward(current_input, hidden)
                predictions.append(next_state.unsqueeze(1))
                
                # 更新输入序列（滑动窗口）
                next_state_expanded = next_state.unsqueeze(1)
                current_input = torch.cat([current_input[:, 1:, :], next_state_expanded], dim=1)
        
        return torch.cat(predictions, dim=1)

class AIPredictor:
    """AI预测器，管理训练和预测"""
    
    def __init__(self, sequence_length=10, device=None):
        """
        初始化AI预测器
        
        Args:
            sequence_length: 输入序列长度
            device: 计算设备
        """
        self.sequence_length = sequence_length
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 创建网络
        self.model = PhysicsLSTM().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-5)
        self.criterion = nn.MSELoss()
        
        # 训练历史
        self.train_losses = []
        self.val_losses = []
        
        # 数据标准化参数
        self.data_mean = None
        self.data_std = None
        
    def collect_training_data(self, engine, cubes: List[Cube], num_episodes=100, 
                            episode_length=300):
        """
        收集训练数据
        
        Args:
            engine: 物理引擎
            cubes: 立方体列表
            num_episodes: 收集的轮次数
            episode_length: 每轮的帧数
            
        Returns:
            sequences: 训练序列数据
            targets: 目标数据
        """
        print(f"开始收集训练数据: {num_episodes} 轮次")
        
        all_sequences = []
        all_targets = []
        
        for episode in range(num_episodes):
            # 随机初始化立方体
            for cube in cubes:
                # 随机位置
                x = np.random.uniform(-5, 5)
                y = np.random.uniform(10, 18)
                z = np.random.uniform(-5, 5)
                
                # 随机初始速度
                vx = np.random.uniform(-3, 3)
                vy = np.random.uniform(-2, 2)
                vz = np.random.uniform(-3, 3)
                
                engine.reset_cube(cube, [x, y, z], [vx, vy, vz])
            
            # 运行模拟
            episode_data = []
            for step in range(episode_length):
                # 记录当前状态
                states = [cube.get_state_vector().copy() for cube in cubes]
                episode_data.append(states[0])  # 只使用第一个立方体
                
                # 物理步进
                engine.step(cubes)
            
            # 生成训练序列
            episode_data = np.array(episode_data)
            for i in range(len(episode_data) - self.sequence_length):
                sequence = episode_data[i:i+self.sequence_length]
                target = episode_data[i+self.sequence_length]
                
                all_sequences.append(sequence)
                all_targets.append(target)
            
            if episode % 10 == 0:
                print(f"已完成 {episode}/{num_episodes} 轮次")
        
        sequences = np.array(all_sequences)
        targets = np.array(all_targets)
        
        print(f"收集完成: {len(sequences)} 个训练样本")
        return sequences, targets
    
    def normalize_data(self, data):
        """数据标准化"""
        if self.data_mean is None:
            self.data_mean = np.mean(data, axis=(0, 1))
            self.data_std = np.std(data, axis=(0, 1)) + 1e-8
        
        return (data - self.data_mean) / self.data_std
    
    def denormalize_data(self, data):
        """数据反标准化"""
        return data * self.data_std + self.data_mean
    
    def train(self, sequences, targets, epochs=100, batch_size=32, val_split=0.2):
        """
        训练模型
        
        Args:
            sequences: 输入序列 [num_samples, sequence_length, features]
            targets: 目标输出 [num_samples, features]
            epochs: 训练轮数
            batch_size: 批大小
            val_split: 验证集比例
        """
        print("开始训练AI模型...")
        
        # 数据标准化
        sequences_norm = self.normalize_data(sequences)
        targets_norm = (targets - self.data_mean) / self.data_std
        
        # 划分训练集和验证集
        num_samples = len(sequences_norm)
        num_val = int(num_samples * val_split)
        indices = np.random.permutation(num_samples)
        
        train_indices = indices[num_val:]
        val_indices = indices[:num_val]
        
        train_sequences = sequences_norm[train_indices]
        train_targets = targets_norm[train_indices]
        val_sequences = sequences_norm[val_indices]
        val_targets = targets_norm[val_indices]
        
        # 转换为PyTorch张量
        train_sequences = torch.FloatTensor(train_sequences).to(self.device)
        train_targets = torch.FloatTensor(train_targets).to(self.device)
        val_sequences = torch.FloatTensor(val_sequences).to(self.device)
        val_targets = torch.FloatTensor(val_targets).to(self.device)
        
        # 训练循环
        for epoch in range(epochs):
            self.model.train()
            total_train_loss = 0
            num_batches = 0
            
            # 批量训练
            for i in range(0, len(train_sequences), batch_size):
                batch_sequences = train_sequences[i:i+batch_size]
                batch_targets = train_targets[i:i+batch_size]
                
                # 前向传播
                self.optimizer.zero_grad()
                predictions, _ = self.model(batch_sequences)
                
                # 计算损失
                loss = self.criterion(predictions, batch_targets)
                
                # 反向传播
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                total_train_loss += loss.item()
                num_batches += 1
            
            # 验证
            self.model.eval()
            with torch.no_grad():
                val_predictions, _ = self.model(val_sequences)
                val_loss = self.criterion(val_predictions, val_targets).item()
            
            # 记录损失
            avg_train_loss = total_train_loss / num_batches
            self.train_losses.append(avg_train_loss)
            self.val_losses.append(val_loss)
            
            # 打印进度
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs}, "
                      f"Train Loss: {avg_train_loss:.6f}, "
                      f"Val Loss: {val_loss:.6f}")
        
        print("训练完成!")
    
    def predict_next_states(self, cubes: List[Cube], steps=10):
        """
        预测立方体的未来状态
        
        Args:
            cubes: 立方体列表
            steps: 预测步数
            
        Returns:
            predictions: 预测的状态序列
        """
        if len(cubes[0].history) < self.sequence_length:
            return None
        
        self.model.eval()
        
        # 准备输入序列
        sequence = np.array(cubes[0].history[-self.sequence_length:])
        sequence_norm = self.normalize_data(sequence.reshape(1, self.sequence_length, -1))
        
        # 转换为张量
        input_tensor = torch.FloatTensor(sequence_norm).to(self.device)
        
        # 预测
        with torch.no_grad():
            predictions = self.model.predict_sequence(input_tensor, steps)
            predictions = predictions.cpu().numpy()[0]  # [steps, features]
        
        # 反标准化
        predictions = self.denormalize_data(predictions)
        
        return predictions
    
    def save_model(self, filepath):
        """保存模型"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'data_mean': self.data_mean,
            'data_std': self.data_std,
            'sequence_length': self.sequence_length,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }, filepath)
        print(f"模型已保存: {filepath}")
    
    def load_model(self, filepath):
        """加载模型"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.data_mean = checkpoint['data_mean']
        self.data_std = checkpoint['data_std']
        self.sequence_length = checkpoint['sequence_length']
        self.train_losses = checkpoint.get('train_losses', [])
        self.val_losses = checkpoint.get('val_losses', [])
        
        print(f"模型已加载: {filepath}")
    
    def evaluate(self, sequences, targets):
        """评估模型性能"""
        # 标准化数据
        sequences_norm = self.normalize_data(sequences)
        targets_norm = (targets - self.data_mean) / self.data_std
        
        # 转换为张量
        sequences_tensor = torch.FloatTensor(sequences_norm).to(self.device)
        targets_tensor = torch.FloatTensor(targets_norm).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            predictions, _ = self.model(sequences_tensor)
            mse_loss = self.criterion(predictions, targets_tensor).item()
            
            # 反标准化进行实际误差计算
            predictions_denorm = self.denormalize_data(predictions.cpu().numpy())
            targets_denorm = targets
            
            # 计算各个分量的误差
            position_error = np.mean(np.sqrt(np.sum((predictions_denorm[:, :3] - targets_denorm[:, :3])**2, axis=1)))
            velocity_error = np.mean(np.sqrt(np.sum((predictions_denorm[:, 3:6] - targets_denorm[:, 3:6])**2, axis=1)))
        
        return {
            'mse_loss': mse_loss,
            'position_error': position_error,
            'velocity_error': velocity_error
        }
