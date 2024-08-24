import numpy as np

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
        # 引入固定的误差
        freq_with_error = 1000 * 1.05
        wavelength = 343.0 / freq_with_error  # 使用带有误差的频率计算波长
        k = (2 * np.pi / wavelength) * np.array([np.cos(phi) * np.cos(theta), np.cos(phi) * np.sin(theta), np.sin(phi)])
        a = np.exp(1j * np.dot(mic_positions, k))
        P_music.append(1.0 / np.abs(np.dot(np.conj(a), np.dot(noise_subspace, np.dot(np.conj(noise_subspace).T, a)))) ** 2)
    
    return np.array(P_music)

# 估计角度
def estimate_angles(P_music, search_grid):
    max_index = np.argmax(P_music)
    return search_grid[max_index]

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
    
    # 返回结果
    return (true_theta, true_phi), (estimated_theta, estimated_phi)

# 运行100次并计算平均误差
num_runs = 10
total_theta_error = 0
total_phi_error = 0

for _ in range(num_runs):
    (true_theta, true_phi), (estimated_theta, estimated_phi) = main_custom()
    
    # 计算误差并累积
    theta_error = (np.abs(np.abs(np.degrees(estimated_theta)) - np.abs(np.degrees(true_theta))) / np.abs(np.degrees(true_theta))) * 100
    phi_error = (np.abs(np.abs(np.degrees(estimated_phi)) - np.abs(np.degrees(true_phi))) / np.abs(np.degrees(true_phi))) * 100
    
    total_theta_error += theta_error
    total_phi_error += phi_error

# 计算平均误差
average_theta_error = total_theta_error / num_runs
average_phi_error = total_phi_error / num_runs

# 输出平均误差
print(f"Average Theta Error: {average_theta_error:.2f}%")
print(f"Average Phi Error: {average_phi_error:.2f}%")
