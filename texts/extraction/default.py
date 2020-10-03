from core.processing.lemmatization.base import Stemmer
from core.processing.lemmatization.mystem import MystemWrapper
from core.source.frames.complete import FramesCollection
from core.source.frames.variants import FrameVariantsCollection
from core.source.synonyms import SynonymsCollection


class Default:

    @staticmethod
    def create_default_stemmer():
        return MystemWrapper(entire_input=True)

    @staticmethod
    def create_default_frames_collection(frames_collection_filepath):
        assert(isinstance(frames_collection_filepath, str))
        return FramesCollection.from_json(frames_collection_filepath)

    @staticmethod
    def create_default_synonyms_collection(filepath, stemmer):
        return SynonymsCollection.from_file(
            filepath=filepath,
            stemmer=stemmer,
            is_read_only=True)

    @staticmethod
    def create_default_frame_variants_collection(frames, stemmer):
        assert(isinstance(frames, FramesCollection))
        assert(isinstance(stemmer, Stemmer))
        return FrameVariantsCollection.from_iterable(variants_with_id=frames.iter_frame_id_and_variants(),
                                                     stemmer=stemmer)
