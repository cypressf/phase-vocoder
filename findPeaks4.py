import numpy


def find_peaks4(spectrum, max_peaks, eps_peak):

    # find the peaks in the spectrum
    greater_than_previous = numpy.greater(spectrum[3:-1], spectrum[2:-2])
    greater_than_next = numpy.greater(spectrum[3:-1], spectrum[4:])
    peak_amplitudes = greater_than_previous * greater_than_next * spectrum[3:-1]

    # identify the 50 biggest peaks, and save their indices in peak_positions
    peak_positions = []
    max_amp = max(peak_amplitudes)
    for i in range(max_peaks):
        peak_position = numpy.argmax(peak_amplitudes)
        m = peak_amplitudes[peak_position]
        if m <= (eps_peak * max_amp):
            break
        peak_positions.append(peak_position + 2)
        peak_amplitudes[peak_position] = 0
    peak_positions = numpy.sort(peak_positions)

    # get the peaks???
    peaks = numpy.zeros([len(peak_positions), 3], dtype="uint32")

    previous_peak_position = 1
    for i, peak_position in enumerate(peak_positions):
        first_peak_position = previous_peak_position + 1
        if i == len(peak_positions) - 1:
            previous_peak_position = len(spectrum)
        else:
            next_peak_position = peak_positions[i+1]
            rel_min = numpy.argmin(spectrum[peak_position:next_peak_position])
            previous_peak_position = peak_position + rel_min - 1

        peaks[i, 0] = first_peak_position
        peaks[i, 1] = peak_position
        peaks[i, 2] = previous_peak_position
    return peaks