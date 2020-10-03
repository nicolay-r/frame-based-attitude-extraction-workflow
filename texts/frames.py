from core.helpers.frames import FramesHelper
from texts.objects.cache.base import BaseObjectCache


class TextFrameVariantsCollection(object):

    def __init__(self, text_frame_variant):
        assert(isinstance(text_frame_variant, list) or text_frame_variant is None)
        self.__text_frame_variants = text_frame_variant if text_frame_variant is not None else []

    @classmethod
    def create_empty(cls):
        return cls.__create_empty()

    @classmethod
    def from_parsed_text(cls, lemmas, frames_helper):
        assert(isinstance(frames_helper, FramesHelper))
        return cls(frames_helper.find_frames(lemmas))

    @classmethod
    def from_cache(cls, cache, filename, s_ind):
        assert(isinstance(cache, BaseObjectCache))

        founded_frames = cache.try_get(filename=filename, s_ind=s_ind)

        if founded_frames is None:
            return cls.__create_empty()

        return cls(founded_frames)

    @classmethod
    def __create_empty(cls):
        return cls(text_frame_variant=None)

    def __len__(self):
        return len(self.__text_frame_variants)

    def __iter__(self):
        for frame_variant in self.__text_frame_variants:
            yield frame_variant
