#!/usr/bin/env python3

import numpy as np
import glob, plotxvg
from scipy.io import wavfile
from scipy.fft import rfft, rfftfreq

def analyze_owl_call(file_path):
    # 1. Load the audio file
    sample_rate, data = wavfile.read(file_path)
    
    # 2. Convert to mono if it's stereo
    if len(data.shape) > 1:
        data = data[:, 0]
    
    # 3. Perform Fast Fourier Transform (FFT)
    n = len(data)
    yf = rfft(data)
    xf = rfftfreq(n, 1 / sample_rate)
    
    # 4. Find the peak frequency
    idx = np.argmax(np.abs(yf))
    peak_freq = xf[idx]
    
    # 5. Classify sex based on frequency
    if 200 <= peak_freq <= 450:
        result = "MALE"
    elif 450 < peak_freq <= 850:
        result = "FEMALE"
    else:
        result = "Unknown"
        
    return peak_freq, result

def sexit():
    outcsv = "eagle-owls.csv"
    count = { "MALE": 0, "FEMALE": 0, "Unknown": 0 }
    spec  = { "MALE": [], "FEMALE": [], "Unknown": [] }
    with open(outcsv, "w") as outf:
        input_files = glob.glob("*wav") + glob.glob("*mp3")
        for input_file in input_files:
            freq, sex = analyze_owl_call(input_file)
            count[sex] += 1
            www = input_file.split("_")
            mydate = www[3]
            mytime = www[4]
        
            outf.write(f"{mydate},{mytime},{input_file},{freq},{sex}\n")
            spec[sex].append(freq)
    # Done reading wav files
    print("Please check %s\n" % outcsv)
    # Make frequency plots
    cxvgs = []
    dsleg = []
    for c in [ "MALE", "FEMALE" ]:
        print(f"{c} {count[c]}")
        if count[c] == 0:
            continue
        cxvg = f"freq-{c}.xvg"
        cxvgs.append(cxvg)
        dsleg.append(c)
        with open(cxvg, "w") as outf:
            index = 0
            outf.write("@title \"xeno-canto sex %s\"\n" % c)
            outf.write("@xaxis label \"Index\"\n")
            outf.write("@yaxis label \"Peak frequency (Hz)\"\n")
            for f in spec[c]:
                outf.write("%5d  %10g\n" % ( index, f ) )
                index += 1
    cpdf = "eagle-owl-sexes.pdf"
    plotxvg.plot(cxvgs, dslegends=dsleg, save=cpdf, noshow=True, legend_x=0.7)
    print("Please check %s" % cpdf)

if __name__ == "__main__":
    sexit()
