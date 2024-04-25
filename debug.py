import sounddevice as sd
import soundfile as sf
import config
import resampy
import keyboard
import threading
import time

stopping = False
def resample_and_play(id):
    target_sample_rate = config.FS
    filename = '/home/atomwalk12/development/github/AlwaysReddy/atom.wav'

    # Read audio file
    data, original_sample_rate = sf.read(filename, dtype='float32')
    print(original_sample_rate)


    # Resample the audio to the target sample rate
    resampled_data = resampy.resample(data, original_sample_rate, target_sample_rate)
    
    # Play the resampled audio
    sd.play(resampled_data, target_sample_rate, device=id)
    while sd.get_stream().active and not sd.get_stream().stopped:
        print("Playing...")
        # time.sleeep(0.1)  # Adjust sleep time if necessary
        if stopping:
            break

    print("Stopped playing")

print(sd.query_devices())

def seg_fault():
    global stopping
    input("Press anything to seg fault.")
    print("Segfault follows")
    stopping = True
    print("No seg fault, a miracle!")


# Create a new thread
thread = threading.Thread(target=seg_fault)

# Start the thread
thread.start()

#keyboard.add_hotkey(config.CANCEL_HOTKEY, seg_fault)

resample_and_play(config.OUT_DEVICE)

thread.join()
