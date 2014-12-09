import numpy


def find_peaks4(spectrum, max_peaks, eps_peak):

    # find the peaks in the spectrum
    greater_than_previous = numpy.greater(spectrum[3:-1], spectrum[2:-2])
    greater_than_next = numpy.greater(spectrum[3:-1], spectrum[4:])
    peak_amplitudes = greater_than_previous * greater_than_next * spectrum[3:-1]

    # identify the 50 biggest peaks, and save their indices in peak_positions
    peak_positions = numpy.transpose(numpy.zeros(max_peaks))
    max_amp = max(peak_amplitudes)
    n_peaks = 0
    for i in range(max_peaks):
        b = numpy.argmax(peak_amplitudes)
        m = peak_amplitudes[b]
        if m <= (eps_peak * max_amp):
            break
        peak_positions[i] = b + 2
        peak_amplitudes[b] = 0
        n_peaks = i
    peak_positions = numpy.sort(peak_positions)

    # get the peaks???
    peaks = numpy.zeros([n_peaks, 3], dtype="uint32")

    last_b = 1
    for i in range(n_peaks):
        b = peak_positions[max_peaks - n_peaks + i]
        first_b = last_b + 1
        if i == n_peaks:
            last_b = len(spectrum)
        else:
            next_b = peak_positions[max_peaks - n_peaks + i]
            rel_min = numpy.argmin(spectrum[b:next_b])
            last_b = b + rel_min - 1

        peaks[i, 0] = first_b
        peaks[i, 1] = b
        peaks[i, 2] = last_b
    return peaks