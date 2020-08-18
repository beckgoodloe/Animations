import os

# Name of audio files in output/temp folder
recording_name = "test.wav"
recording_name_mp3 = f"{recording_name.split('.')[0]}.mp3"

# Name of rendered video in output folder
VIDEO_NAME = "TEST_VIDEO.mp4"

# Directory information
GENTLE_ENDPOINT = "http://localhost:8765/transcriptions"
DIR_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(DIR_PATH)
ANIMATIONS_PATH = os.path.dirname(BASE_DIR)
OUTPUT_PATH = os.path.join(ANIMATIONS_PATH, 'output')
TEMP_OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'temp')
TEMP_RECORDING_WAV = os.path.join(TEMP_OUTPUT_PATH, recording_name)
TEMP_RECORDING_MP3 = os.path.join(TEMP_OUTPUT_PATH, recording_name_mp3)
DATA_PATH = os.path.join(ANIMATIONS_PATH, "data")
VIDEO_PATH = os.path.join(OUTPUT_PATH, VIDEO_NAME)

# Frame rate given in frames per second
ANIMATION_FRAME_RATE = 24

# Library that ties phonemes to mouth shapes.
# Each key in the library needs a corresponding mouth shape
# in the data folder
mouth_library = {
    "a": ["aa", "ae", "aw", "eh", "ey"],
    "e": ["iy"],
    "i": ["ay", "ih"],
    "o": ["ao", "ow", "oy"],
    "u": ["ah", "er", "uh", "uw", "w", "oov"],
    "f": ["f", "v"],
    "m": ["b", "m", "p"],
    "lu": ["dh", "l", "n", "th"],
    "s": ["ch", "d", "g", "hh", "jh", "k", "ng",
          "r", "s", "sh", "t", "y", "z", "zh"],
}
