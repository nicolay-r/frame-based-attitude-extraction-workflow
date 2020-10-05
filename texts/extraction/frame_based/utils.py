from core.source.frames.complete import FramesCollection


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def get_frames_polarities(text_frame_variants, frames):
    assert (isinstance(text_frame_variants, list))
    assert (isinstance(frames, FramesCollection))

    polarities = []
    is_inverted = []
    for text_frame_variant in text_frame_variants:

        frame_id = text_frame_variant.Variant.FrameID
        polarity = frames.try_get_frame_polarity(frame_id, "a0", "a1")

        if polarity is None:
            continue

        polarities.append(polarity)
        is_inverted.append(text_frame_variant.IsInverted)

    return polarities, is_inverted

