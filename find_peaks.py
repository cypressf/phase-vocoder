import numpy


def find_peaks(spectrum_magnitude, max_peaks, eps_peak):

    # find the peaks in the spectrum
    greater_than_previous = numpy.greater(spectrum_magnitude[3:-1], spectrum_magnitude[2:-2])
    greater_than_next = numpy.greater(spectrum_magnitude[3:-1], spectrum_magnitude[4:])
    peak_amplitudes = greater_than_previous * greater_than_next * spectrum_magnitude[3:-1]

    # identify the 50 biggest peaks, and save their indices in peak_positions
    peak_positions = []
    max_amp = max(peak_amplitudes)
    for i in range(max_peaks):
        peak_position = numpy.argmax(peak_amplitudes)
        m = peak_amplitudes[peak_position]
        if m <= (eps_peak * max_amp):
            break
        peak_positions.append(peak_position + 3)
        peak_amplitudes[peak_position] = 0
    peak_positions = numpy.sort(peak_positions)

    # get the valleys in between the peaks or something?
    peaks = numpy.zeros([len(peak_positions), 3], dtype="uint32")

    previous_peak_position = 0  # TODO: verify that this index is correct
    for i, peak_position in enumerate(peak_positions):
        first_peak_position = previous_peak_position + 1
        if i == len(peak_positions) - 1:
            previous_peak_position = len(spectrum_magnitude) - 1  # TODO: verify that this index is correct
        else:
            next_peak_position = peak_positions[i+1]
            rel_min = numpy.argmin(spectrum_magnitude[peak_position:next_peak_position])
            previous_peak_position = peak_position + rel_min - 1

        peaks[i, 0] = first_peak_position
        peaks[i, 1] = peak_position
        peaks[i, 2] = previous_peak_position

    peak_values = spectrum_magnitude[peaks[:, 1]]
    return peaks[numpy.argsort(peak_values), :]