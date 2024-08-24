import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 生成麦克风阵列
def generate_array(N, radius):
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    z = np.zeros(N)
    return np.array([x, y, z]).T

# 生成模拟信号
def generate_signal(theta, phi, freq, num_snapshots, mic_positions):
    wavelength = 343.0 / freq  # 假设声音速度为343 m/s
    k = (2 * np.pi / wavelength) * np.array([np.cos(phi) * np.cos(theta), np.cos(phi) * np.sin(theta), np.sin(phi)])
    
    snapshots = []
    for _ in range(num_snapshots):
        signal = np.exp(1j * np.dot(mic_positions, k))  # 基于位置的相位变化
        snapshots.append(signal)
    
    return np.array(snapshots).T

# MUSIC算法
def music_algorithm(R, mic_positions, search_grid):
    eigvals, eigvecs = np.linalg.eigh(R)
    eigvals_sorted_indices = np.argsort(eigvals)
    noise_subspace = eigvecs[:, eigvals_sorted_indices[:-1]]  # 选择噪声子空间
    
    P_music = []
    for theta, phi in search_grid:
        wavelength = 343.0 / 1000.0  # 假设频率为1000 Hz
        k = (2 * np.pi / wavelength) * np.array([np.cos(phi) * np.cos(theta), np.cos(phi) * np.sin(theta), np.sin(phi)])
        a = np.exp(1j * np.dot(mic_positions, k))
        P_music.append(1.0 / np.abs(np.dot(np.conj(a), np.dot(noise_subspace, np.dot(np.conj(noise_subspace).T, a)))) ** 2)
    
    return np.array(P_music)

# 估计角度
def estimate_angles(P_music, search_grid):
    max_index = np.argmax(P_music)
    return search_grid[max_index]

# 绘制单个角度和麦克风位置
def plot_single_angle_with_mics_degrees(ax, theta_phi, label, color, mic_positions):
    # 将极坐标转换为三维直角坐标系的点
    def sph2cart_deg(theta, phi):
        x = np.cos(np.radians(phi)) * np.cos(np.radians(theta))
        y = np.cos(np.radians(phi)) * np.sin(np.radians(theta))
        z = np.sin(np.radians(phi))
        return x, y, z
    
    # 角度对应的点
    x, y, z = sph2cart_deg(np.degrees(theta_phi[0]), np.degrees(theta_phi[1]))
    ax.scatter(x, y, z, color=color, s=100, label=f'{label} ({np.degrees(theta_phi[0]):.1f}°, {np.degrees(theta_phi[1]):.1f}°)')

    # 连线从原点到该点
    ax.plot([0, x], [0, y], [0, z], color=color)
    
    # 绘制麦克风的位置
    ax.scatter(mic_positions[:, 0], mic_positions[:, 1], mic_positions[:, 2], c='b', marker='o', s=100, label='Mic positions')
    
    # 设置坐标轴范围和标签
    ax.set_xlim([-0.1, 0.1])
    ax.set_ylim([-0.1, 0.1])
    ax.set_zlim([-0.1, 0.1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # 设置图例
    ax.legend()
    
    # 设置图形标题
    ax.set_title(f'{label} (in Degrees) with Mic Positions')

# 主函数
def main_custom():
    # 圆形麦克风阵列参数
    N = 6  # 麦克风的数量
    radius = 0.035  # 半径，单位：米
    
    # 生成麦克风阵列位置
    mic_positions = generate_array(N, radius)
    
    # 模拟的音源角度 (方位角 theta, 俯仰角 phi)
    true_theta = np.random.uniform(0, 2 * np.pi)
    true_phi = np.random.uniform(-np.pi / 2, np.pi / 2)
    
    # 生成接收信号
    freq = 1000  # 频率，单位：Hz
    num_snapshots = 100  # 快照数
    snapshots = generate_signal(true_theta, true_phi, freq, num_snapshots, mic_positions)
    
    # 计算空间相关矩阵
    R = np.dot(snapshots, np.conj(snapshots).T) / num_snapshots
    
    # 定义搜索网格
    theta_grid = np.linspace(0, 2 * np.pi, 180)
    phi_grid = np.linspace(-np.pi / 2, np.pi / 2, 90)
    search_grid = [(theta, phi) for theta in theta_grid for phi in phi_grid]
    
    # 执行MUSIC算法
    P_music = music_algorithm(R, mic_positions, search_grid)
    
    # 估计角度
    estimated_theta, estimated_phi = estimate_angles(P_music, search_grid)
    
    # 反转估计的俯仰角符号
    estimated_phi = estimated_phi
    
    # 将弧度转换为角度
    true_theta_deg = np.degrees(true_theta)
    true_phi_deg = np.degrees(true_phi)
    estimated_theta_deg = np.degrees(estimated_theta)
    estimated_phi_deg = np.degrees(estimated_phi)
    
    # 创建图形窗口并创建两个子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': '3d'})
    
    # 绘制真实角度图像
    plot_single_angle_with_mics_degrees(ax1, (true_theta, true_phi), "True Angle", "g", mic_positions)
    
    # 绘制估计角度图像
    plot_single_angle_with_mics_degrees(ax2, (estimated_theta, estimated_phi), "Estimated Angle", "r", mic_positions)
    
    # 显示图形
    plt.show()
    
    # 返回角度结果
    return (true_theta_deg, true_phi_deg), (estimated_theta_deg, estimated_phi_deg)

# 运行主函数
results = main_custom()
print("True angles (theta, phi):", results[0])
print("Estimated angles (theta, phi):", results[1])
