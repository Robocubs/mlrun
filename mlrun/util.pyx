# cython: language_level=3, boundscheck=False, wraparound=False, embedsignature=True, cdivision=True
"""Utility functions for the pipeline of MLRun."""

cpdef list filter_confidence(list unfiltered, float min_score):
    """
    Filter inference results by confidence.
    Args:
        unfiltered: The unfiltered results.
        min_score: The minimum score that is required for an item to pass.

    Returns:
        A list of inference results which have the required confidence.

    Notes:
        Roughly equivalent to the original lambda used, which was:
            lambda unfiltered: [
                unfiltered[i] for i in range(len(unfiltered))
                if unfiltered[i][0] > engine_config["min_score"]
            ]
    """
    cdef list output = []
    cdef int length = len(unfiltered)
    cdef int i = 0
    if length > 1:
        for i in range(length):
            score = unfiltered[i][0]
            if score > min_score:
                output.append(unfiltered[i])
    return output

cpdef list normalize(list filtered, int camera_width, int camera_height, int inference_width, int inference_height):
    """
    Normalize the floating point coordinates into pixel values, and convert the inference results into
    a human-understandable format.
    Args:
        filtered: Filtered results from earlier in the pipeline.
        camera_width: The width of the input image for normalization.
        camera_height: The height of the input image for normalization.
        inference_width: The width of the output image from the inference process.
        inference_height: The height of the output image from the inference process.

    Returns:
        The normalized values.
    """
    cdef list output = []
    cdef int one = 0
    cdef int two = 0
    cdef int three = 0
    cdef int four = 0
    cdef float confidence = 0.0
    for i in filtered:
        # This stuff is complicated. Long story short, the inference process returns values relative to
        # its expected input size, which need to be changed to the values relative to the size of the camera's
        # input.
        one = int(((max(1, i[1][0] * inference_height)) / inference_height) * camera_height)
        two = int(((max(1, i[1][1] * inference_width)) / inference_width) * camera_width)
        three = int((min(inference_height, (i[1][2] * inference_height)) / inference_height) * camera_height)
        four = int((min(inference_width, (i[1][3] * inference_width)) / inference_width) * camera_width)
        confidence = round(100 * i[0], 1)
        output.append([
            four, three, two, one, confidence
        ])
    return output

cpdef dict humanize(list normalized, double t1, double t2, float freq):
    """
    Convert processed values to readable output.
    Args:
        normalized: Normalized values.
        t1: Tick count at start.
        t2: Tick count at end.
        freq: Tick frequency.

    Returns:
        Readable dictionary.
    """
    cdef int length = len(normalized)
    cdef double tick_count = t2 - t1
    cdef float inv_fps = tick_count / freq
    cdef double fps_u = 1 / inv_fps
    return {
        "fps": round(fps_u, 1),
        "numDetections": length,
        "detections": normalized
    }