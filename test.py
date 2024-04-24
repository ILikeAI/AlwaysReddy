import sounddevice as sd
import soundfile as sf
import config

import resampy

def resample_and_play(filename, target_sample_rate):
    # Read audio file
    data, original_sample_rate = sf.read(filename, dtype='float32')
    print(original_sample_rate)


    # Resample the audio to the target sample rate
    resampled_data = resampy.resample(data, original_sample_rate, target_sample_rate)
    
    # Play the resampled audio
    sd.play(resampled_data, target_sample_rate, device=config.OUT_DEVICE)
    sd.wait()  # Wait until the audio has finished playing


# Specify the path to your audio file
# Execute: echo "Im ready to assist." | ./piper2/piper/piper --model piper_voices/en_US-amy-medium.onnx -c --sample-rate 48000 piper_voices/en_en_US_amy_medium_en_US-amy-medium.onnx.json --output_file /home/atomwalk12/development/github/AlwaysReddy/razvan.wav
audio_file_path = '/home/atomwalk12/development/github/AlwaysReddy/razvan.wav'

# Call the function to play the audio
target_sample_rate = config.FS  # Specify the target sample rate in Hz
resample_and_play(audio_file_path, target_sample_rate)