from core.processing.lemmatization.base import Stemmer
from core.processing.lemmatization.mystem import MystemWrapper
from core.source.frames.complete import FramesCollection
from core.source.frames.variants import FrameVariantsCollection
from core.source.synonyms import SynonymsCollection
from texts.extraction.frame_based.obj_auth import TextObjectAuthorizer
from texts.ner_wraps import supported
from texts.ner_wraps.deep_ner import LocalDeepNERWrap
from texts.ner_wraps.deepavlov_bert_ner import DeepPavlovBertNERWrap
from texts.objects.extraction.extractor import NerExtractor


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

    @staticmethod
    def create_ner_extractor(ner, ner_cache, default_auth_check):
        return NerExtractor(
            ner=ner,
            ner_cache=ner_cache,
            fix_obj_value=True,
            auth_objs_check_func=default_auth_check)

    @staticmethod
    def create_obj_authorizer(ner_class_type):
        return TextObjectAuthorizer(ner_type=ner_class_type)

    @staticmethod
    def get_class_by_ner_name(ner_name):
        assert(isinstance(ner_name, str))
        if ner_name == supported.ONTONOTES_BERT_MULT_NAME:
            return DeepPavlovBertNERWrap
        elif ner_name == supported.DEEP_NER_NAME:
            return LocalDeepNERWrap
        else:
            raise Exception("NER type '{}' is not supported".format(ner_name))
