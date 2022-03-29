import audiolab, scipy
a, fs, enc = audiolab.wavread('b.wav')
b, fs, enc = audiolab.wavread('uw.wav')
c = scipy.vstack((a,b))
audiolab.wavwrite(c, 'file3.wav', fs, enc)