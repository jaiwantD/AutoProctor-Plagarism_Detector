import pyaudio
import numpy as np
import time

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Sampling rate
CHUNK = 1024  # Buffer size
SILENT_THRESHOLD_DB = 10  # dB above baseline noise level

def get_rms(data):
    """Calculate RMS value of audio data"""
    return np.sqrt(np.mean(np.square(np.frombuffer(data, dtype=np.int16))))

def rms_to_db(rms):
    """Convert RMS to dB"""
    return 20 * np.log10(rms + 1e-6)  # Avoid log(0)

# Initialize PyAudio
pa = pyaudio.PyAudio()
stream = pa.open(format=FORMAT, channels=CHANNELS,
                 rate=RATE, input=True,
                 frames_per_buffer=CHUNK)

# Get baseline noise level
print("Calibrating noise level...")
baseline_rms = np.mean([get_rms(stream.read(CHUNK, exception_on_overflow=False)) for _ in range(30)])
baseline_db = rms_to_db(baseline_rms)
print(f"Baseline noise level: {baseline_db:.2f} dB")

time.sleep(1)
print("Listening for noise...")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        rms = get_rms(data)
        current_db = rms_to_db(rms)

        if current_db > baseline_db + SILENT_THRESHOLD_DB:
            print("Noise detected!")

except KeyboardInterrupt:
    print("Stopping...")
    
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()