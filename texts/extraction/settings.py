from collections import OrderedDict

from core.helpers.frames import FramesHelper
from core.processing.pos.mystem_wrap import POSMystemWrapper
from texts.ner_wraps import supported
from texts.extraction.default import Default
from texts.objects.authorized.collection import AuthorizedObjectsCollection
from texts.objects.cache.base import BaseObjectCache


class Settings(object):

    DISABLE_LEMMA_FOR_SYNONYMS = True

    def __init__(self,
                 synonyms_collection_filepath,
                 frames_collection_filepath,
                 init_ner=True,
                 init_stemmer=True,
                 init_frames=True,
                 use_ner_cache_only=False,
                 ner_name=supported.ONTONOTES_BERT_MULT_NAME):
        assert(isinstance(init_ner, bool))
        assert(isinstance(init_frames, bool))
        assert(isinstance(init_stemmer, bool))
        assert(isinstance(ner_name, str))

        self.__auth_objects = None
        self.__use_ner_cache_only = use_ner_cache_only
        self.__synonyms = None
        self.__stemmer = None
        self.__frame_variants = None
        self.__frames = None
        self.__pos_tagger = None
        self.__syntax = None
        self.__use_auth_list = False
        self.__frames_cache = None

        # NER
        self.__ner_cache = None
        self.__ner_class_type = Default.get_class_by_ner_name(ner_name)
        self.__ner = None

        if init_stemmer:
            self.__stemmer = Default.create_default_stemmer()

        if self.__stemmer is not None:
            self.__pos_tagger = POSMystemWrapper(self.__stemmer.MystemInstance)

        if init_frames:
            self.__frames = Default.create_default_frames_collection(frames_collection_filepath)

        if self.__stemmer is not None and self.__frames is not None:
            self.__frame_variants = Default.create_default_frame_variants_collection(frames=self.__frames,
                                                                                     stemmer=self.__stemmer)

        if self.__frame_variants is not None:
            self.__frames_helper = FramesHelper(self.__frame_variants)

        if init_ner and not use_ner_cache_only:
            self.__ner = self.__ner_class_type()

        self.__synonyms = Default.create_default_synonyms_collection(
            filepath=synonyms_collection_filepath,
            stemmer=None if self.DISABLE_LEMMA_FOR_SYNONYMS else self.__stemmer)

        self.__auth_objects = AuthorizedObjectsCollection(OrderedDict())

        # self.__auth_objects = AuthorizedObjectsCollection.from_relations_file(
        #     filepath=join(io_utils.get_objects_root(), "relevant_relations.txt"),
        #     synonyms=self.__synonyms)

    # region properties

    @property
    def AuthorizedObjects(self):
        return self.__auth_objects

    @property
    def NER(self):
        return self.__ner

    @property
    def NERClassType(self):
        return self.__ner_class_type

    @property
    def NerCache(self):
        return self.__ner_cache

    @property
    def FramesCache(self):
        return self.__frames_cache

    @property
    def Stemmer(self):
        return self.__stemmer

    @property
    def PosTagger(self):
        return self.__pos_tagger

    @property
    def Frames(self):
        return self.__frames

    @property
    def FrameVariants(self):
        return self.__frame_variants

    @property
    def FramesHelper(self):
        return self.__frames_helper

    @property
    def Syntax(self):
        return self.__syntax

    @property
    def Synonyms(self):
        return self.__synonyms

    # endregion

    # region public methods

    def set_ner_cache(self, ner_cache):
        assert(isinstance(ner_cache, BaseObjectCache))
        self.__ner_cache = ner_cache

    def set_frames_cache(self, frames_cache):
        assert(isinstance(frames_cache, BaseObjectCache))
        self.__frames_cache = frames_cache

    # endregion