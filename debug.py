import sounddevice as sd
import soundfile as sf
import config
import resampy


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
    sd.wait()  # Wait until the audio has finished playing

print(sd.query_devices())
