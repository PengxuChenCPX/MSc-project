import numpy as np
import wave

def read_wav_file(filename):
    wav_file = wave.open(filename, 'rb')
    n_channels = wav_file.getnchannels()
    sampwidth = wav_file.getsampwidth()
    framerate = wav_file.getframerate()
    n_frames = wav_file.getnframes()
    data = wav_file.readframes(n_frames)
    data = np.frombuffer(data, dtype=np.int16)
    data = np.reshape(data, (n_frames, n_channels))
    wav_file.close()
    return data, framerate

def gcc_phat(sig, refsig, fs=1, max_tau=None, interp=16):
    n = sig.shape[0] + refsig.shape[0]
    n = 1 << (n - 1).bit_length()
    SIG = np.fft.rfft(sig, n=n)
    REFSIG = np.fft.rfft(refsig, n=n)
    R = SIG * np.conj(REFSIG)
    cc = np.fft.irfft(R / np.abs(R), n=(interp * n))
    max_shift = int(interp * n / 2)
    if max_tau:
        max_shift = np.minimum(int(interp * fs * max_tau), max_shift)
    cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))
    shift = np.argmax(np.abs(cc)) - max_shift
    tau = shift / float(interp * fs)
    return tau

def doa_estimation(data, fs):
    num_channels = data.shape[1]
    if num_channels != 2:
        raise ValueError("The input data must have 2 channels.")
    mic_distance = 0.042  # distance between microphones in meters
    speed_of_sound = 343  # speed of sound in m/s
    tau = gcc_phat(data[:, 0], data[:, 1], fs)
    print("calculated delay: {:.2f} seconds".format(tau))
    angle = (180/np.pi)*((speed_of_sound * tau) / mic_distance)+(((speed_of_sound * tau) / mic_distance)**3)/6
    #angle = np.arcsin(tau * speed_of_sound / mic_distance) * 180 / np.pi
    return angle

def main():
    filename = 'gcc.wav'  # replace with your file name
    data, fs = read_wav_file(filename)
    angle = doa_estimation(data, fs)
    #print("Estimated DOA angle: {:.2f} degrees".format(angle))
    

if __name__ == "__main__":
    main()
