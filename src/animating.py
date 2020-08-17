import os
import numpy as np

from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from PIL import Image
from pydub import AudioSegment
from recording import *
from setup import *


def get_mouth_shape(shape):
    append = f"{shape}.PNG"
    path = os.path.join(DATA_PATH, append)
    return path


def normalize_images_in_library():
    images = os.listdir(DATA_PATH)
    images = [name for name in images if name.endswith(".png")]
    first_image = Image.open(os.path.join(DATA_PATH, images[0]))
    WIDTH, HEIGHT = first_image.size
    for item in images:
        path = os.path.join(DATA_PATH, item)
        im = Image.open(path)
        im = im.resize((WIDTH, HEIGHT))
        im.save(path)
    print("Normalizing complete.")


def write_video(images):
    normalize_images_in_library()
    convert_to_mp3()

    # Write video clip without audio
    print("Beginning video render.")
    clip = ImageSequenceClip(images, fps=ANIMATION_FRAME_RATE)
    audio_clip = AudioFileClip(TEMP_RECORDING_MP3)
    audio_clip = audio_clip.subclip(0, clip.duration)
    clip = clip.set_audio(audio_clip)
    clip.write_videofile(VIDEO_PATH, fps=ANIMATION_FRAME_RATE, codec='libx264',
                         audio_codec="aac")

    print("Video rendered and saved with audio.")
    exit_program()


def convert_to_mp3():
    sound = AudioSegment.from_wav(TEMP_RECORDING_WAV)
    sound.export(TEMP_RECORDING_MP3, format="mp3")
    print("Audio converted to mp3.")


def main():
    pass
    # a_path = os.path.join(DATA_PATH, "a.PNG")
    # im = Image.open(a_path)
    # im = get_mouth_shape("m")
    # im.save(os.path.join(DATA_PATH, "TEST.PNG"))


if __name__ == '__main__':
    main()
