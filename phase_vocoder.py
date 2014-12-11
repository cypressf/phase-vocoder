# This implements a phase vocoder for time-stretching/compression# Put the file name of the input file in "infile"# the file to be created is "outfile"# The amount of time-stretch is determined by the ratio of the hopin# and hopout variables. For example, hopin=242 and hopout=161.3333# (integers are not required) increases the tempo by # hopin/hopout = 1.5. To slow down a comparable amount,# choose hopin = 161.3333, hopout = 242.from __future__ import divisionimport mathimport numpyimport thinkdspfrom find_peaks import find_peaksdef phase_vocoder(input_wave, hop_in=121, hop_out=242, max_peak=20):    ALL_2_PI = 2 * math.pi * numpy.arange(0, 101)  # all multiples of 2 pi (used in PV-style freq search)    EPS_PEAK = 0.005  # height of peaks    NFFT = 2 ** 12    NFFT2 = NFFT / 2  # fft length    win = numpy.hanning(NFFT)  # windows and windowing variables    input_wave.normalize()    frame_rate = input_wave.framerate    y = input_wave.ys    tt = numpy.zeros(numpy.ceil(hop_out / hop_in) * len(input_wave))  # place for output    lenseg = int(numpy.floor((len(input_wave) - NFFT) / hop_in))  # number of fft segments to process    ssf = frame_rate * numpy.arange(0, NFFT2 + 1) / NFFT  # frequency vector    phold = numpy.zeros(NFFT2 + 1)    phadvance = numpy.zeros(NFFT2 + 1)    outbeat = numpy.zeros(NFFT)    dtin = hop_in / frame_rate  # time advances dt per hop for input    dtout = hop_out / frame_rate  # time advances dt per hop for output    for k in range(lenseg):  # main loop - process each beat separately        indin = numpy.round(numpy.arange(k * hop_in, k * hop_in + NFFT))        s = win * y[indin]  # get this frame and take FFT        ffts = numpy.fft.fft(s)        spectrum = numpy.abs(ffts[:NFFT2+1])        ph = numpy.angle(ffts[:NFFT2+1])        # find peaks to define spectral mapping        peak_positions = find_peaks(spectrum, max_peak, EPS_PEAK)        peak_values = spectrum[peak_positions[:, 1]]        inds = numpy.argsort(peak_values)        peaksort = peak_positions[inds, :]        pc = peaksort[:, 1]        best_frequency = numpy.zeros(pc.shape)        for tk, peak_index in enumerate(pc):  # estimate frequency using PV strategy            dtheta = (ph[peak_index] - phold[peak_index]) + ALL_2_PI            fest = dtheta / (2 * math.pi * dtin)  # see pvanalysis.m for same idea            indf = numpy.argmin(numpy.abs(ssf[peak_index] - fest))            best_frequency[tk] = fest[indf]  # find best freq estimate for each row        # generate output spectrum and phase        spectrum_out = spectrum        phout = ph        for tk in range(len(pc)):            fdes = best_frequency[tk]  # reconstruct with original frequency            freqind = numpy.arange(peaksort[tk, 0], peaksort[tk, 2])  # indices of the surrounding bins            # specify magnitude and phase of each partial            spectrum_out[freqind] = spectrum[freqind]            phadvance[peaksort[tk, 1]] += 2 * math.pi * fdes * dtout            pizero = math.pi * numpy.ones(len(freqind))            pcent = peaksort[tk, 1] - peaksort[tk, 0] + 1            indpc = numpy.arange((1 - numpy.mod(pcent, 2)), len(freqind), 2)            pizero[indpc] = numpy.zeros([1, len(indpc)])            phout[freqind] = phadvance[peaksort[tk, 1]] + pizero        # reconstruct time signal (stretched or compressed)        compl = spectrum_out * numpy.exp(1j * phout)        compl[NFFT2] = ffts[NFFT2]        compl = numpy.concatenate([compl, numpy.conj(compl[1:NFFT2])[::-1]]) #TODO: make compl match MATLAB        wave = numpy.real(numpy.fft.ifft(compl))        outbeat[:] = wave        phold[:] = ph        indout = numpy.round(numpy.arange(k * hop_out, k * hop_out + NFFT)).astype(int)        tt[indout] = tt[indout] + outbeat    output_wave = thinkdsp.Wave(tt, frame_rate)    output_wave.normalize()    return output_waveif __name__ == "__main__":    input_file = "yoursound.wav"    output_file = "yoursoundchanged.wav"    input_wave = thinkdsp.read_wave(input_file)    output_wave = phase_vocoder(input_wave)    output_wave.write(output_file)