import tkinter as tk
import os
import threading
import pyaudio
import wave

from tkinter import *
from tkinter import filedialog, messagebox
from setup import *
from recording import playback, transcribe

HEIGHT = 500
WIDTH = 700

BUTTON_PAD_X = 10
BUTTON_PAD_Y = 5
BUTTON_HEIGHT = 2

ANCHOR_X = 10
ANCHOR_Y = 10
VERTICAL_SPACING = 50
HORIZONTAL_SPACING = 160

# Create root
root = tk.Tk()
root.title("Animate!")

# Updateable variables
which_audio = IntVar()

upload_audio_path = StringVar()
upload_audio_path.set("NOTHING UPLOADED")

record_audio_path = StringVar()
record_audio_path.set("NOTHING RECORDED")

currently_recording = StringVar()
currently_recording.set("Not Recording")

transcript = ""
live_record = False


# This class is for recording with multithreading
class Recorder():
    def __init__(self, root):
        self.isrecording = False
        self.record_audio_button = tk.Button(root, text="Hold to record audio",
                                             padx=BUTTON_PAD_X,
                                             pady=BUTTON_PAD_Y,
                                             height=BUTTON_HEIGHT,
                                             fg='black', bg='black')
        self.record_audio_button.place(x=ANCHOR_X, y=ANCHOR_Y + 1 *
                                       (BUTTON_HEIGHT + VERTICAL_SPACING))
        self.record_audio_button.bind("<Button-1>", self.startrecording)
        self.record_audio_button.bind("<ButtonRelease-1>", self.stoprecording)

    def startrecording(self, event):
        self.isrecording = True
        t = threading.Thread(target=self._record)
        t.start()

    def stoprecording(self, event):
        self.isrecording = False

    def _record(self):
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

        # Start the recording loop
        while self.isrecording:
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

        record_audio_path.set(TEMP_RECORDING_WAV)


def upload_audio():
    upload_audio_path.set(filedialog.askopenfilename(initialdir="/",
                                                     title="Select \
                                                     Audio File"))
    if(not upload_audio_path.get().endswith(".mp3") and
       not upload_audio_path.get().endswith(".wav")):
        messagebox.showerror("Error", "File must be and MP3 or WAV format.")
        upload_audio_path.set("NOTHING UPLOADED")


def play():
    # Get path of selected audio
    if(which_audio.get()):
        path = record_audio_path.get()
    else:
        path = upload_audio_path.get()

    # Check if audio is valid
    if(path.startswith("NOTHING")):
        messagebox.showerror("Error", "There is no audio currently queued.")
    elif(not (path.endswith(".wav"))):
        messagebox.showerror("Error", "File must be WAV format.")
    else:
        playback(path)


def scribe():
    # Get path of selected audio
    if(which_audio.get()):
        path = record_audio_path.get()
    else:
        path = upload_audio_path.get()

    # Check if audio is valid
    if(path.startswith("NOTHING")):
        messagebox.showerror("Error", "There is no audio currently queued.")
    elif(not (path.endswith(".wav") or path.endswith(".mp3"))):
        messagebox.showerror("Error", "File must be and MP3 or WAV format.")
    else:
        global transcript
        transcript = transcribe(path)

    # Create a text widget with this transcript
    text = tk.Text(root)
    text.insert(END, transcript)
    text.place(x=ANCHOR_X + HORIZONTAL_SPACING + 18, y=ANCHOR_Y + 5 *
               (BUTTON_HEIGHT + VERTICAL_SPACING))


def setup_layout():
    # Create canvas and pack
    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg="#AB82FF")
    canvas.pack()

    # Create upload audio button
    upload_audio_button = tk.Button(root, text="Upload an audio file",
                                    padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y,
                                    height=BUTTON_HEIGHT,
                                    fg='black', bg='black',
                                    command=upload_audio)
    upload_audio_button.place(x=ANCHOR_X, y=ANCHOR_Y)

    # Create associated button
    upload_audio_label = tk.Label(root, textvariable=upload_audio_path)
    upload_audio_label.place(x=ANCHOR_X + HORIZONTAL_SPACING, y=ANCHOR_Y,
                             height=40)

    # Create associated button
    record_audio_label = tk.Label(root, textvariable=record_audio_path)
    record_audio_label.place(x=ANCHOR_X + HORIZONTAL_SPACING, y=ANCHOR_Y + 1 *
                             (BUTTON_HEIGHT + VERTICAL_SPACING), height=40)

    # Create radio button to choose recorded or uploaded audio
    audio_selector_upload = Radiobutton(root, text="Use Uploaded Audio",
                                        variable=which_audio, value=0,
                                        padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y,
                                        indicatoron='true',)
    audio_selector_record = Radiobutton(root, text="Use Recorded Audio",
                                        variable=which_audio, value=1,
                                        padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y,
                                        indicatoron='true',)
    audio_selector_upload.place(x=ANCHOR_X, y=ANCHOR_Y + 2 *
                                (BUTTON_HEIGHT + VERTICAL_SPACING))
    audio_selector_record.place(x=ANCHOR_X + HORIZONTAL_SPACING + 2 *
                                BUTTON_PAD_X, y=ANCHOR_Y +
                                2 * (BUTTON_HEIGHT + VERTICAL_SPACING))

    # Create playback button
    playback_button = tk.Button(root,
                                text="Playback audio that's currently queued",
                                padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y,
                                height=BUTTON_HEIGHT,
                                fg='black', bg='black',
                                command=play)
    playback_button.place(x=ANCHOR_X, y=ANCHOR_Y + 3 *
                          (BUTTON_HEIGHT + VERTICAL_SPACING) - 13)

    # Create transcribe button
    transcribe_button = tk.Button(root,
                                  text="Transcribe queued text",
                                  padx=BUTTON_PAD_X, pady=BUTTON_PAD_Y,
                                  height=BUTTON_HEIGHT,
                                  fg='black', bg='black',
                                  command=scribe)
    transcribe_button.place(x=ANCHOR_X, y=ANCHOR_Y + 5 *
                            (BUTTON_HEIGHT + VERTICAL_SPACING))


def main():
    # Setup the layout of the app
    setup_layout()

    # Create the record app
    recorder = Recorder(root)

    # Run applet
    root.mainloop()


if __name__ == '__main__':
    main()
