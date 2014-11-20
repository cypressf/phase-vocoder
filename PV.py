# This implements a phase vocoder for time-stretching/compression# Put the file name of the input file in "infile"#     the file to be created is "outfile"# The amount of time-stretch is determined by the ratio of the hopin# and hopout variables. For example, hopin=242 and hopout=161.3333# (integers are not required) increases the tempo by # hopin/hopout = 1.5. To slow down a comparable amount,# choose hopin = 161.3333, hopout = 242.# 5/2005 Bill Setharesfrom __future__ import divisionimport mathimport numpyimport thinkdspfrom findPeaks4 import find_peaks4infile='yoursong.wav'outfile='yoursongchanged'time=0                                    # total time to processhopin=121                                 # hop length for inputhopout=242                                # hop length for outputall2pi=2*math.pi*numpy.arange(0, 101)                       # all multiples of 2 pi (used in PV-style freq search)max_peak=50                               # parameters for peak finding: number of peakseps_peak=0.005                            # height of peaksnfft=2**12nfft2=nfft/2                               # fft lengthwin=numpy.conj(numpy.hanning(nfft))        # windows and windowing variableswave = thinkdsp.read_wave(infile)          # read song filesr = wave.frameratey = wave.yssiz = len(wave)                            # length of song in samplesleny = sizif time==0:    time = 100000tt=numpy.zeros(numpy.ceil(hopout/hopin) * min(leny, time * sr)) # place for outputlenseg=numpy.floor((min(leny,time*sr)-nfft)/hopin) # number of nfft segments to processssf = sr * numpy.arange(0, nfft2+1) / nfft                     # frequency vectorphold=numpy.zeros(nfft2+1)phadvance=numpy.zeros(nfft2+1)outbeat=numpy.zeros(nfft)pold1=[]pold2=[]dtin=hopin/sr                             # time advances dt per hop for inputdtout=hopout/sr                           # time advances dt per hop for outputfor k in range(1,lenseg):                           # main loop - process each beat separately    indin=round[((k-1)*hopin+1):((k-1)*hopin+nfft)]    s=win*y(indin)                # get this frame and take FFT    ffts=fft(s)    mag=abs(ffts[1:nfft2+1])    ph=angle(ffts[1:nfft2+1])    # find peaks to define spectral mapping    peaks = find_peaks4(mag, max_peak, eps_peak)    [dummy,inds]=numpy.sort(mag(peaks[:,2]))    peaksort=peaks[inds,:]    pc=peaksort[:,2]    bestf=numpy.zeros(pc.shape)    for tk in range(1, len(pc)+1):              # estimate frequency using PV strategy        dtheta=(ph(pc(tk))-phold[pc(tk)])+all2pi        fest=dtheta/(2*math.pi*dtin)      # see pvanalysis.m for same idea        [er,indf]=min(abs(ssf(pc(tk))-fest))        bestf(tk)=fest(indf)          # find best freq estimate for each row    # generate output mag and phase    magout=mag    phout=ph    for tk in range(1, len(pc)+1):        fdes=bestf(tk)                           # reconstruct with original frequency        freqind=numpy.arange(peaksort(tk,1),peaksort(tk,3)+1)  # indices of the surrounding bins        # specify magnitude and phase of each partial        magout[freqind] = mag[freqind]        phadvance[peaksort(tk,2)]=phadvance(peaksort(tk,2))+2*math.pi*fdes*dtout        pizero=math.pi*numpy.ones(len(freqind))        pcent=peaksort(tk,2)-peaksort(tk,1)+1        indpc=(2-mod(pcent,2)):2:len(freqind)        pizero[indpc]=numpy.zeros(1,len(indpc))        phout[freqind]=phadvance(peaksort(tk,2))+pizero    # reconstruct time signal (stretched or compressed)    compl=magout*numpy.exp(numpy.sqrt(-1)*phout)    compl[nfft2+1]=ffts[nfft2+1]    compl=[compl,fliplr(numpy.conj(compl[2:nfft2]))]    wave=numpy.real(ifft(compl))    outbeat[:] = wave    phold[:] = ph    indout=round(((k-1)*hopout+1) : ((k-1)*hopout+nfft))    tt[:,indout]=tt[:,indout]+outbeattt=0.8*tt/max(max(abs(tt)))[rtt,ctt]=size(tt) if rtt==2, tt=tt' endwavwrite(tt,sr,16,outfile)fclose('all')