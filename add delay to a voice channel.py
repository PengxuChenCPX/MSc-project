import wave
import numpy as np
from pydub import AudioSegment

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
    return data, framerate, sampwidth

def add_delayed_channel(data, delay, framerate):
    delay_samples = int(delay * framerate)
    delayed_channel = np.roll(data[:, 0], delay_samples)
    new_data = np.column_stack((data, delayed_channel))
    return new_data

def save_wave(filename, data, sample_rate, sampwidth):
    n_channels = data.shape[1]
    n_frames = data.shape[0]
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(n_channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(sample_rate)
    wf.writeframes((data * 32767).astype(np.int16).tobytes())
    wf.close()

def main():
    filename = "St John's Hill 2.m4a"
    wav_filename = "St John's Hill 2.wav"
    audio = AudioSegment.from_file(filename, format='m4a')
    audio.export(wav_filename, format='wav')

    data, framerate, sampwidth = read_wav_file(wav_filename)
    
    delay = 0.1
    print("expected delay: -{:.2f} seconds".format(delay))
    new_data = add_delayed_channel(data, delay, framerate)
    
    new_wav_filename = "gcc.wav"
    save_wave(new_wav_filename, new_data, framerate, sampwidth)
    
if __name__ == "__main__":
    main()
