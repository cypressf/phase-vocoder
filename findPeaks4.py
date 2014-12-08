import numpy


def find_peaks4(amps, max_peak, eps_peak):
    spectrum_size = len(amps)
    peak_amplitude = numpy.greater(amps[3:spectrum_size - 1], amps[2:spectrum_size - 2]) * \
                     numpy.greater(amps[3:spectrum_size - 1], amps[4:spectrum_size]) * \
                     amps[3:spectrum_size - 1]

    peak_pos = numpy.transpose(numpy.zeros(max_peak))
    max_amp = max(peak_amplitude)
    n_peaks = 0
    for p in range(max_peak):
        b = numpy.argmax(peak_amplitude)
        m = peak_amplitude[b]
        if m <= (eps_peak * max_amp):
            break
        peak_pos[p] = b + 2
        peak_amplitude[b] = 0
        n_peaks = p

    peak_pos = numpy.sort(peak_pos)
    peaks = numpy.zeros([n_peaks, 3])

    last_b = 1
    for p in range(n_peaks):
        b = peak_pos[max_peak - n_peaks + p]
        first_b = last_b + 1
        if p == n_peaks:
            last_b = spectrum_size
        else:
            next_b = peak_pos[max_peak - n_peaks + p + 1]
            rel_min = numpy.argmin(amps[b:next_b])
            last_b = b + rel_min - 1

        peaks[p, 0] = first_b
        peaks[p, 1] = b
        peaks[p, 2] = last_b
        return peaks