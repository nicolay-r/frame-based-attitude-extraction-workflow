import json
import os
from glob import glob
import importlib
from os.path import dirname
from core.processing.ner.base import NamedEntityRecognition
from texts.ner_wraps import supported


class LocalDeepNERWrap(NamedEntityRecognition):
    """
    Deep Pavlov NER wrapper
    """

    separator = '-'
    gpu_memory_fraction = 0.2

    def __init__(self):
        self.__corpus = None
        self.__network = None
        self.__initialize()

    @property
    def InputLimitation(self):
        return 10000

    @property
    def NeedLemmatization(self):
        return True

    @property
    def NeedLowercase(self):
        return True

    @property
    def LocationTypeStr(self):
        return "LOC"

    @staticmethod
    def get_geo_political_type_str():
        # Does not exists.
        return "-"

    @staticmethod
    def get_person_type_str():
        return "PER"

    @staticmethod
    def get_organization_type_str():
        return "ORG"

    def __model_root(self):
        return os.path.join(dirname(__file__), './model/')

    def __initialize(self):

        # Dynamic lybraries import.
        nn = importlib.import_module('ner.network')
        ner_corpus = importlib.import_module('ner.corpus')
        md5_hashsum = importlib.import_module('ner.corpus.md5_hashsum')
        download_untar = importlib.import_module('ner.corpus.download_untar')

        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

        # Check existence of the model by hashsum
        if md5_hashsum(sorted(glob(self.__model_root() + '*'))) != 'fd50a27b96b24cdabdda13795a3baae7':
            # Download and extract model
            download_url = 'http://lnsigo.mipt.ru/export/models/ner/ner_model_total_rus.tar.gz'
            download_path = self.__model_root()
            download_untar(download_url, download_path)

        # Load network params
        with open(os.path.join(self.__model_root(), 'params.json')) as f:
            network_params = json.load(f)

        self.__corpus = ner_corpus.Corpus(dicts_filepath=os.path.join(self.__model_root(), 'dict.txt'))
        self.__network = nn.NER(self.__corpus,
                                mem_fraction=self.gpu_memory_fraction,
                                verbouse=False,
                                pretrained_model_filepath=os.path.join(self.__model_root(), 'ner_model'),
                                **network_params)

    def _extract_tags(self, sequences):
        assert(isinstance(sequences, list))
        return self.__network.predict_for_token_batch(sequences)

    def __str__(self):
        return supported.DEEP_NER_NAME
