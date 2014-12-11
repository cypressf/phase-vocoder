# This implements a phase vocoder for time-stretching/compression# Put the file name of the input file in "infile"# the file to be created is "outfile"# The amount of time-stretch is determined by the ratio of the hopin# and hopout variables. For example, hopin=242 and hopout=161.3333# (integers are not required) increases the tempo by # hopin/hopout = 1.5. To slow down a comparable amount,# choose hopin = 161.3333, hopout = 242.from __future__ import divisionimport mathimport numpyimport thinkdspimport copyfrom find_peaks import find_peaksdef phase_vocoder(input_wave, hop_in=121, hop_out=242, max_peak=20):    input_wave.normalize()    all_2_pi = 2 * math.pi * numpy.arange(0, 101)  # all multiples of 2 pi (used in PV-style freq search)    eps_peak = 0.005  # height of peaks    segment_length = 2 ** 12    fft_length = segment_length / 2  # fft length (divide by 2 to eliminate redundant negative frequencies)    window = numpy.hanning(segment_length)    tt = numpy.zeros(numpy.ceil(hop_out / hop_in) * len(input_wave))  # place for output    number_of_segments = int(numpy.floor((len(input_wave) - segment_length) / hop_in))    ssf = input_wave.framerate * numpy.arange(0, fft_length + 1) / segment_length  # frequency vector    old_spectrum_phase = numpy.zeros(fft_length + 1)    phadvance = numpy.zeros(fft_length + 1)    outbeat = numpy.zeros(segment_length)    dt_in = hop_in / input_wave.framerate  # time advances dt per hop for input    dt_out = hop_out / input_wave.framerate  # time advances dt per hop for output    for segment_number in range(number_of_segments):  # main loop - process each segment        segment = window * input_wave.ys[segment_number * hop_in:segment_number * hop_in + segment_length]        segment_spectrum = numpy.fft.fft(segment)        spectrum_magnitude = numpy.abs(segment_spectrum[:fft_length+1])        spectrum_phase = numpy.angle(segment_spectrum[:fft_length+1])        # find peaks to define spectral mapping        peaks = find_peaks(spectrum_magnitude, max_peak, eps_peak)        peak_indices = peaks[:, 1]        # estimate frequency using PV strategy        best_frequency = []        for peak_index in peak_indices:            dthetas = spectrum_phase[peak_index] - old_spectrum_phase[peak_index] + all_2_pi            frequency_estimates = dthetas / (2 * math.pi * dt_in)            indf = numpy.argmin(numpy.abs(ssf[peak_index] - frequency_estimates))            best_frequency.append(frequency_estimates[indf])  # find best freq estimate for each row        # generate output spectrum and phase        spectrum_magnitude_output = spectrum_magnitude        phout = spectrum_phase        for tk in range(len(peak_indices)):            fdes = best_frequency[tk]  # reconstruct with original frequency            freqind = numpy.arange(peaks[tk, 0], peaks[tk, 2])  # indices of the surrounding bins            # specify magnitude and phase of each partial            spectrum_magnitude_output[freqind] = spectrum_magnitude[freqind]            phadvance[peaks[tk, 1]] += 2 * math.pi * fdes * dt_out            pizero = math.pi * numpy.ones(len(freqind))            pcent = peaks[tk, 1] - peaks[tk, 0] + 1            indpc = numpy.arange((1 - numpy.mod(pcent, 2)), len(freqind), 2)            pizero[indpc] = numpy.zeros([1, len(indpc)])            phout[freqind] = phadvance[peaks[tk, 1]] + pizero        # reconstruct time signal (stretched or compressed)        compl = spectrum_magnitude_output * numpy.exp(1j * phout)        compl[fft_length] = segment_spectrum[fft_length]        compl = numpy.concatenate([compl, numpy.conj(compl[1:fft_length])[::-1]])        wave = numpy.real(numpy.fft.ifft(compl))        outbeat = copy.copy(wave)        old_spectrum_phase = copy.copy(spectrum_phase)        indout = numpy.round(numpy.arange(segment_number * hop_out, segment_number * hop_out + segment_length)).astype(int)        tt[indout] = tt[indout] + outbeat    output_wave = thinkdsp.Wave(tt, input_wave.framerate)    output_wave.normalize()    return output_waveif __name__ == "__main__":    input_file = "yoursound.wav"    output_file = "yoursoundchanged.wav"    input_wave = thinkdsp.read_wave(input_file)    output_wave = phase_vocoder(input_wave)    output_wave.write(output_file)