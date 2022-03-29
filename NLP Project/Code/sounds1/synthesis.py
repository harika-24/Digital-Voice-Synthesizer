import re
import wave
import pyaudio
import _thread
import time

import struct

import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

class TextToSpeech:

    CHUNK = 1024

    def __init__(self, words_pron_dict:str = 'cmudict-0.7b.txt'):
        self._l = {}
        self._load_words(words_pron_dict)

    def _load_words(self, words_pron_dict:str):
        with open(words_pron_dict, 'r') as file:
            for line in file:
                if not line.startswith(';;;'):
                    key, val = line.split('  ',2)
                    self._l[key] = re.findall(r"[A-Z]+",val)

    def get_pronunciation(self, str_input):
        list_pron = []
        for word in re.findall(r"[\w']+",str_input.upper()):
            if word in self._l:
                list_pron += self._l[word]
        print(list_pron)
        delay=0
        for pron in list_pron:
            _thread.start_new_thread( TextToSpeech._play_audio, (pron,delay,))
            delay += 0.145

        return list_pron
    def _play_audio(sound, delay):
        try:
            time.sleep(delay)
            wf = wave.open("sounds/"+sound+".wav", 'rb')
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


class AudioRecording:
    
    CHUNK = 1024*2
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RECORD_SECONDS = 3
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "output.wav"
    
    def record():
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format = AudioRecording.FORMAT,
            channels = AudioRecording.CHANNELS,
            rate = AudioRecording.RATE,
            input = True,
            output = True,
            frames_per_buffer = AudioRecording.CHUNK
        )
        
        print("* recording")
        
        frames = []
        data_int=()
        for i in range(0, int(AudioRecording.RATE / AudioRecording.CHUNK * AudioRecording.RECORD_SECONDS)):
            data = stream.read(AudioRecording.CHUNK)
            data_int = data_int+(struct.unpack(str(2 * AudioRecording.CHUNK) + 'B', data),)
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
        
        file = open("output2.txt","w") 
        for t in data_int:
          file.write(str(t))
        print(type(data_int))
        print(len(data_int[0]))
    
        file.close()

class AudioProcess:
    def get_duration_wav(wav_filename):
        f = wave.open(wav_filename, 'r')
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        f.close()
        return duration


    def audio_split(list_pron,f):
        num_phonemes=len(list_pron)
        partition=f/num_phonemes
        
        list_of_timestamps=[]
        print(partition)
        for i in range(1,num_phonemes+1):
            list_of_timestamps.append(partition*i)
           
        print(list_of_timestamps)
        audio_file= "welcome.wav"
        audio = AudioSegment.from_wav(audio_file)
        #list_of_timestamps = [ 10, 20, 30, 40, 50 ,60, 70, 80, 90 ] #and so on in *seconds*
    
        start = 0
        for  idx,t in enumerate(list_of_timestamps):
        #break loop if at last element of list
            if idx == len(list_of_timestamps):
                break
        
            end = t *1000 #pydub works in millisec
            print("split at [ {}:{}] ms".format(start, end))
            audio_chunk=audio[start:end]
            audio_chunk.export( "audio_chunk_{}.wav".format(end), format="wav")
    
            start = end*1000 #pydub works in millisec
        print(f)

if __name__ == '__main__':
    tts = TextToSpeech()
    ar = AudioRecording()
    
    list_pron=tts.get_pronunciation(input('Enter a word or phrase: '))
    #ar.record()
    f= AudioProcess.get_duration_wav("welcome.wav")
    print("Duration of the audio:",f)
    
    print(list_pron)
    AudioProcess.audio_split(list_pron,f)
