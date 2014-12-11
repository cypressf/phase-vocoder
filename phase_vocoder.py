# This implements a phase vocoder for time-stretching/compression# Put the file name of the input file in "infile"# the file to be created is "outfile"# The amount of time-stretch is determined by the ratio of the hopin# and hopout variables. For example, hopin=242 and hopout=161.3333# (integers are not required) increases the tempo by # hopin/hopout = 1.5. To slow down a comparable amount,# choose hopin = 161.3333, hopout = 242.from __future__ import divisionimport mathimport numpyimport thinkdspfrom find_peaks import find_peaksdef main():    infile = 'yoursound.wav'    outfile = 'yoursongchanged.wav'    hopin = 121  # hop length for input    hopout = 242  # hop length for output    all2pi = 2 * math.pi * numpy.arange(0, 101)  # all multiples of 2 pi (used in PV-style freq search)    max_peak = 50  # parameters for peak finding: number of peaks    eps_peak = 0.005  # height of peaks    nfft = 2 ** 12    nfft2 = nfft / 2  # fft length    win = numpy.hanning(nfft)  # windows and windowing variables    wave = thinkdsp.read_wave(infile)  # read song file    wave.normalize()    sr = wave.framerate    y = wave.ys    tt = numpy.zeros(numpy.ceil(hopout / hopin) * len(wave))  # place for output    lenseg = int(numpy.floor((len(wave) - nfft) / hopin))  # number of nfft segments to process    ssf = sr * numpy.arange(0, nfft2 + 1) / nfft  # frequency vector    phold = numpy.zeros(nfft2 + 1)    phadvance = numpy.zeros(nfft2 + 1)    outbeat = numpy.zeros(nfft)    dtin = hopin / sr  # time advances dt per hop for input    dtout = hopout / sr  # time advances dt per hop for output    for k in range(lenseg):  # main loop - process each beat separately        indin = numpy.round(numpy.arange(k * hopin, k * hopin + nfft))        s = win * y[indin]  # get this frame and take FFT        ffts = numpy.fft.fft(s)        spectrum = numpy.abs(ffts[:nfft2+1])        ph = numpy.angle(ffts[:nfft2+1])        # find peaks to define spectral mapping        peak_positions = find_peaks(spectrum, max_peak, eps_peak)        peak_values = spectrum[peak_positions[:, 1]]        inds = numpy.argsort(peak_values)        peaksort = peak_positions[inds, :]        pc = peaksort[:, 1]        best_frequency = numpy.zeros(pc.shape)        for tk, peak_index in enumerate(pc):  # estimate frequency using PV strategy            dtheta = (ph[peak_index] - phold[peak_index]) + all2pi            fest = dtheta / (2 * math.pi * dtin)  # see pvanalysis.m for same idea            indf = numpy.argmin(numpy.abs(ssf[peak_index] - fest))            best_frequency[tk] = fest[indf]  # find best freq estimate for each row        # generate output spectrum and phase        spectrum_out = spectrum        phout = ph        for tk in range(len(pc)):            fdes = best_frequency[tk]  # reconstruct with original frequency            freqind = numpy.arange(peaksort[tk, 0], peaksort[tk, 2])  # indices of the surrounding bins            # specify magnitude and phase of each partial            spectrum_out[freqind] = spectrum[freqind]            phadvance[peaksort[tk, 1]] += 2 * math.pi * fdes * dtout            pizero = math.pi * numpy.ones(len(freqind))            pcent = peaksort[tk, 1] - peaksort[tk, 0] + 1            indpc = numpy.arange((1 - numpy.mod(pcent, 2)), len(freqind), 2)            pizero[indpc] = numpy.zeros([1, len(indpc)])            phout[freqind] = phadvance[peaksort[tk, 1]] + pizero        # reconstruct time signal (stretched or compressed)        compl = spectrum_out * numpy.exp(1j * phout)        compl[nfft2] = ffts[nfft2]        compl = numpy.concatenate([compl, numpy.conj(compl[1:nfft2])[::-1]]) #TODO: make compl match MATLAB        wave = numpy.real(numpy.fft.ifft(compl))        outbeat[:] = wave        phold[:] = ph        indout = numpy.round(numpy.arange(k * hopout, k * hopout + nfft)).astype(int)        tt[indout] = tt[indout] + outbeat    tt = 0.8 * tt / numpy.max(numpy.abs(tt))    rtt = tt.shape[0]    if rtt == 2:        tt = numpy.transpose(tt)  # TODO: complex conjugate transpose    modified_wave = thinkdsp.Wave(tt, sr)    modified_wave.write(outfile)if __name__ == "__main__":    main()