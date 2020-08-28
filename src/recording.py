import wave
import pyaudio
import re
import sys
import speech_recognition as sr
import requests
import json
import gentle
import inflect

from pydub import AudioSegment
from pynput import keyboard
from termios import tcflush, TCIOFLUSH
from setup import *

currently_recording = False
recording_finished = False


def print_pretty(object):
    print(json.dumps(object, indent=2, sort_keys=True))


def transcribe(filename):
    print("Starting transcription.")
    # Create a transcriber object
    r = sr.Recognizer()
    # Convert .wav into AudioFile type
    audio = sr.AudioFile(filename)
    # Convert AudioFile into AudioData
    with audio as source:
        data = r.record(source)

    # Choose output method
    try:
        script = r.recognize_google(data)
        # return r.recognize_sphinx(data)
    except Exception as e:
        return "ERROR: COULD NOT TRANSCRIBE"
    script = convert_numbers(script)
    return script


def playback(filename):

    # Set chunk size of 1024 samples per data frame
    chunk = 1024

    # check audio file type
    if(not filename.endswith('.wav')):
        AudioSegment.from_mp3(
            filename).export("test_wav", format="wav")

    # Open the sound file
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather
    # than recorded
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while (data != b'') and (data != ''):
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()


# takes in name of output file
def record(output_file):
    # set parameters for stream
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    filename = TEMP_RECORDING_WAV

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    listener = keyboard.Listener(
        on_press=on_press, on_release=on_release)
    listener.start()
    while(currently_recording):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Move on to prompts about keeping recording
    keep_recording()


def clear_input_queue():
    sys.stdout.flush()
    tcflush(sys.stdin, TCIOFLUSH)


def re_record():
    clear_input_queue()
    response = input("Do you want to re-record? (y/n)")
    if(response == "y" or response == "Y"):
        main()
    elif(response == "n" or response == "N"):
        # print("Program Terminated")
        global recording_finished
        recording_finished = True
        clear_input_queue()
        sys.exit(0)
    else:
        re_record()


def keep_recording():
    clear_input_queue()
    response = input("Do you want to keep the recording? (y/n)")
    if(response == "y" or response == "Y"):
        main(True)
    elif(response == "n" or response == "N"):
        re_record()
    else:
        # print("Invalid input")
        keep_recording()


def on_press(key):
    global currently_recording

    # Check if this key press is to start or end the recording
    # Execute appropriately
    if(currently_recording):
        currently_recording = False
    else:
        currently_recording = True
        print("Recording has started.")
        record(recording_name)
    return False


def on_release(key):
    pass


def force_align(transcript, recording_name, disfluency=True):
    if(disfluency):
        params = (('async', 'false'), ('disfluency', 'false'),
                  ('conservative', 'true'),)
    else:
        params = (('async', 'false'), ('conservative', 'true'),)
    files = {
        'audio': (recording_name, open(recording_name, 'rb')),
        'transcript': ('words.txt', transcript),
    }

    response = requests.post(
        GENTLE_ENDPOINT, params=params, files=files)
    return response.text


def process_alignment_data(data):
    data = json.loads(data)

    cases = []
    phones = []
    starts = []
    ends = []
    words = []

    # Extract data from json into dicts
    for item in data["words"]:
        if(item["case"] != "not-found-in-audio"):
            cases.append(item["case"])
            phones.append(item["phones"])
            starts.append(item["start"])
            ends.append(item["end"])
            words.append(item["alignedWord"])

    # Remove failed alignments
    to_remove = []
    for i in range(0, len(cases)):
        if(cases[i] != 'success' and cases[i] != 'not-found-in-transcript'):
            to_remove.append(i)
    to_remove = to_remove[::-1]
    for i in range(0, len(to_remove)):
        phones.pop(to_remove[i])
        starts.pop(to_remove[i])
        ends.pop(to_remove[i])
        cases.pop(to_remove[i])
        words.pop(to_remove[i])

    # Prints all of data in a readable format
    # for i in range(0, len(cases)):
    #     print(f"We are at word indexed {i}")
    #     print_pretty(phones[i])
    #     print_pretty(starts[i])
    #     print_pretty(ends[i])
    # print_pretty(data)

    # Open wave file and find length, calculate number of frames for animation
    wf = wave.open(TEMP_RECORDING_WAV, 'rb')
    rate = wf.getframerate()
    num_audio_frames = wf.getnframes()
    duration = num_audio_frames / float(rate)
    num_animation_frames = int(duration * ANIMATION_FRAME_RATE)
    phoneme_map = ["sl"] * num_animation_frames

    # Iterate through detected phonemes and assign them in the map
    for i, word in enumerate(phones):
        word_start = starts[i]
        for phoneme in word:
            phone = phoneme['phone'].split('_')[0]
            word_end = word_start + phoneme['duration']
            for index in range(int(word_start * ANIMATION_FRAME_RATE),
                               int(word_end * ANIMATION_FRAME_RATE)):
                phoneme_map[index] = which_mouth_shape(phone)
                word_start = word_end

    # replace all the silences with the correct path
    for i in range(0, len(phoneme_map)):
        phoneme_map[i] = get_mouth_shape(phoneme_map[i])

    write_video(phoneme_map)
    sys.exit(0)


# Takes in the phoneme and returns which mouthshape to use
def which_mouth_shape(phone):
    for key, value in mouth_library.items():
        if(phone in value):
            return key
    print(f"ERROR {phone}")
    return "sl"


def exit_program():
    sys.exit()
    sys.exit(0)
    sys.exit(1)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def convert_numbers(transcript):
    print(f"Transcript is {transcript}")
    # Using inflect engine to NUM_TO_WORD
    engine = inflect.engine()
    # Split text and iterate, sorting by words that are all nums v partial nums
    split_text = transcript.split(" ")
    for i, word in enumerate(split_text):
        if (hasNumbers(word)):
            if(word.isdecimal()):
                split_text[i] = engine.number_to_words(split_text[i])
            else:
                res = list(re.findall(r'(\w+?)(\d+)', word)[0])
                for j, item in enumerate(res):
                    if(item.isdecimal()):
                        res[j] = engine.number_to_words(res[j])
                split_text[i] = " ".join(res)
    return " ".join(split_text)


def main(processing=False):
    if(processing):
        print("Processing beginning.")
        transcript = transcribe(TEMP_RECORDING_WAV)
        # transcript = convert_numbers(transcript)
        print("Transcipt is : {}".format(transcript))

        '''RUNNING WITH gentle AS A PYTHON MODULE'''
        '''
        print("Force alignment beginning.")
        disfluencies = set(['uh', 'um', 'err'])
        resources = gentle.Resources()

        with gentle.resampled(recording_name) as wavfile:
            aligner = gentle.ForcedAligner(resources, transcript,
                                           disfluency=True, conservative=True,
                                           disfluencies=disfluencies)
            result = aligner.transcribe(wavfile)
        print(result)
        '''

        '''RUNNING WITH THE SERVER LIVE'''
        data = force_align(transcript, TEMP_RECORDING_WAV, disfluency=False)
        print("Force alignment complete. Starting processing.")
        process_alignment_data(data)

    else:
        global recording_finished
        listener = keyboard.Listener(
            on_press=on_press, on_release=on_release)
        listener.start()
        print("Press spacebar to record. Press again to stop.")
        while not recording_finished:
            pass


if __name__ == '__main__':
    main()
