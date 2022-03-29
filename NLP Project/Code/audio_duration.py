import wave
def get_duration_wav(wav_filename):
    f = wave.open(wav_filename, 'r')
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)
    f.close()
    return duration


f= get_duration_wav("hi.wav")

from pydub import AudioSegment

def audio_split(breakpoint_list,num_phoneme,f):
    t1 = 0 * 1000 #Works in milliseconds
    audio_phoneme=0
    for e in breakpoint_list:
        t2 = e
        newAudio = AudioSegment.from_wav("how.wav")
        newAudio = newAudio[t1:t2]
        newAudio.export('newSong.wav', format="wav")
        audio_phoneme=audio_phoneme+1
        if(num_phoneme>num_phoneme):
            t1=t2
        else:
            t1=f
    print(f)