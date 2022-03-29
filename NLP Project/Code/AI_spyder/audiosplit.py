import re
import wave
import pyaudio
import _thread
import time

import struct

import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

from scipy.fftpack import fft
from scipy.io import wavfile


class A:
    word = input('Enter a word: ')


class TextToSpeech:
    CHUNK = 1024

    def __init__(self, words_pron_dict: str = 'cmudict-0.7b.txt'):
        self._l = {}
        self._load_words(words_pron_dict)

    def _load_words(self, words_pron_dict: str):
        with open(words_pron_dict, 'r') as file:
            for line in file:
                if not line.startswith(';;;'):
                    key, val = line.split('  ', 2)
                    self._l[key] = re.findall(r"[A-Z]+", val)

    def get_pronunciation(self, str_input):
        list_pron = []
        for word in re.findall(r"[\w']+", str_input.upper()):
            if word in self._l:
                list_pron += self._l[word]
        print(list_pron)
        delay = 0
        for pron in list_pron:
            _thread.start_new_thread(TextToSpeech._play_audio, (pron, delay,))
            delay += 0.145

        return list_pron

    def _play_audio(sound, delay):
        try:
            time.sleep(delay)
            wf = wave.open("sounds/" + sound + ".wav", 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(TextToSpeech.CHUNK)

            while data:
                stream.write(data)
                data = wf.readframes(TextToSpeech.CHUNK)

            stream.stop_stream()
            stream.close()

            p.terminate()
            return
        except:
            pass


class AudioRecording(A):
    word = A.word
    CHUNK = 1024 * 2
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RECORD_SECONDS = 3
    RATE = 44100
    WAVE_OUTPUT_FILENAME = word + ".wav"

    def record():
        p = pyaudio.PyAudio()

        stream = p.open(
            format=AudioRecording.FORMAT,
            channels=AudioRecording.CHANNELS,
            rate=AudioRecording.RATE,
            input=True,
            output=True,
            frames_per_buffer=AudioRecording.CHUNK
        )

        print("* recording")

        frames = []
        data_int = ()
        for i in range(0, int(AudioRecording.RATE / AudioRecording.CHUNK * AudioRecording.RECORD_SECONDS)):
            data = stream.read(AudioRecording.CHUNK)
            data_int = data_int + (struct.unpack(str(2 * AudioRecording.CHUNK) + 'B', data),)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(AudioRecording.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(AudioRecording.CHANNELS)
        wf.setsampwidth(p.get_sample_size(AudioRecording.FORMAT))
        wf.setframerate(AudioRecording.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        file = open(word + ".txt", "w")
        for t in data_int:
            file.write(str(t))
        print(type(data_int))
        print(len(data_int[0]))

        file.close()


class FT(A):
    def fast_fourier(self):
        fs, data = wavfile.read("audio_samples/" + A.word + '.wav')
        a = data
        print()
        print("Waveform beore FFT:")
        print()
        plt.plot(a, 'g')
        plt.show()
        b = [(ele / 2 ** 8.) * 2 - 1 for ele in a]
        c = fft(b)

        d = len(c)
        print("Frequency in Hz: ", d)
        print()
        print("Waveform after FFT:")
        plt.plot(abs(c[:(d - 1)]), 'r')
        plt.show()

        print()
        print("The list of breakpoints")
        break_point = []
        ctr = 1
        print(ctr)
        break_point.append(1)
        print(break_point)
        bool1 = False

        condition = False
        for i in range(d):

            if (bool1):
                condition = (abs(c[i][0]) < 300)


            else:
                condition = (abs(c[i][0]) > 300)

            if (condition):

                ctr = ctr + 1
                print(ctr)
                break_point.append(i)
                print(break_point)
                bool1 = (ctr % 2 == 1)


            else:
                pass


class AudioProcess(A):
    def get_duration_wav(wav_filename):
        f = wave.open(wav_filename, 'r')
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        f.close()
        return duration

    def audio_split(list_pron, f):
        num_phonemes = len(list_pron)
        partition = f / num_phonemes

        list_of_timestamps = []

        for i in range(1, num_phonemes + 1):
            list_of_timestamps.append(partition * i)

        audio_file = "audio_samples/" + word + ".wav"
        audio = AudioSegment.from_wav(audio_file)
        # list_of_timestamps = [ 10, 20, 30, 40, 50 ,60, 70, 80, 90 ] #and so on in *seconds*
        print(list(audio.get_array_of_samples()))
        start = 0
        for idx, t in enumerate(list_of_timestamps):
            # break loop if at last element of list
            if idx == len(list_of_timestamps):
                break

            end = t * 1000  # pydub works in millisec
            print(list_pron[idx] + " Phoneme split at [ {}:{}] ms".format(round(start), round(end, 2)))
            audio_chunk = audio[start:end]
            audio_chunk.export("sounds/" + list_pron[idx].lower() + ".wav".format(end), format="wav")
            # audio_chunk.export(list_pron[idx].lower()+".wav".format(end), format="wav")

            start = end  # pydub works in millisec


if __name__ == '__main__':
    tts = TextToSpeech()
    ar = AudioRecording()
    transform = FT()

    word = A.word
    print("Audio sample taken or analysis: " + word + ".wav")
    # ar.record()
    print("")

    list_pron = tts.get_pronunciation(word)
    print("")
    f = AudioProcess.get_duration_wav("audio_samples/" + word + ".wav")
    print("Duration of the audio:", f)

    print("")

    # print(list_pron)
    AudioProcess.audio_split(list_pron, f)

    print()
    transform.fast_fourier()

    for i in range(len(list_pron)):
        fs, data = wavfile.read("sounds/" + list_pron[i] + '.wav')
        a = data
        print()
        print(list_pron[i] + " Phoneme Waveform beore FFT:")
        print()
        plt.plot(a, 'g')
        plt.show()
        b = [(ele / 2 ** 8.) * 2 - 1 for ele in a]
        c = fft(b)

        d = len(c)
        print("Frequency in Hz: ", d)
        print()
        print(list_pron[i] + " Phoneme Waveform after FFT:")
        plt.plot(abs(c[:(d - 1)]), 'r')
        plt.show()
