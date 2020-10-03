import importlib
from core.processing.ner.base import NamedEntityRecognition
from texts.ner_wraps import supported


class DeepPavlovBertNERWrap(NamedEntityRecognition):

    def __init__(self):

        # Dynamic libraries import.
        deeppavlov = importlib.import_module("deeppavlov")
        build_model = deeppavlov.build_model
        configs = deeppavlov.configs

        self.__ner_model = build_model(configs.ner.ner_ontonotes_bert_mult,
                                       download=True)

    @property
    def InputLimitation(self):
        gap = 296
        return 512 - gap

    @property
    def NeedLemmatization(self):
        return False

    @property
    def NeedLowercase(self):
        return False

    @staticmethod
    def get_location_type_str():
        return "LOC"

    @staticmethod
    def get_geo_political_type_str():
        return "GPE"

    @staticmethod
    def get_person_type_str():
        return "PERSON"

    @staticmethod
    def get_organization_type_str():
        return "ORG"

    def _extract_tags(self, sequences):
        tokens, labels = self.__ner_model(sequences)

        gathered_labels_seq = []

        for i, sequence in enumerate(sequences):
            _, labels = self.tokens_to_terms(terms=sequence,
                                             tokens=tokens[i],
                                             labels=labels[i])

            gathered_labels_seq.append(self.gather(labels))

        return gathered_labels_seq

    @staticmethod
    def tokens_to_terms(terms, tokens, labels):
        def __cur_term():
            return len(joined_tokens) - 1

        assert (len(labels) == len(tokens))

        terms_lengths = [len(term) for term in terms]
        current_lengths = [0] * len(terms)
        joined_tokens = [[]]
        joined_labels = [[]]
        for i, token in enumerate(tokens):
            if current_lengths[__cur_term()] == terms_lengths[__cur_term()]:
                joined_tokens.append([])
                joined_labels.append([])
            joined_tokens[-1].append(token)
            joined_labels[-1].append(labels[i])
            current_lengths[__cur_term()] += len(token)

        return joined_tokens, joined_labels

    @staticmethod
    def gather(labels_in_lists):
        return [labels[0] if len(labels) == 1 else DeepPavlovBertNERWrap.gather_many(labels)
                for labels in labels_in_lists]

    @staticmethod
    def gather_many(labels):
        return 'O'

    def __str__(self):
        return supported.ONTONOTES_BERT_MULT_NAME
