import pyaudio
import wave

def record_audio(filename, duration=5, rate=48000, channels=1, format=pyaudio.paInt16):
    p = pyaudio.PyAudio()
    
    # Open stream
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=1024)

    print("Recording...")
    frames = []
    
    for _ in range(0, int(rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    
    print("Recording finished.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

record_audio('test6.wav')
