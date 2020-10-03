# -*- coding: utf-8 -*-
from core.source.news import News, Sentence
from core.runtime.parser import TextParser


class NewsTermsCollection:

    def __init__(self):
        self.by_id = {}

    def get_by_news_id(self, news_ID):
        assert(isinstance(news_ID, int))
        return self.by_id[news_ID]

    def add_news_terms(self, news_terms):
        assert(isinstance(news_terms, NewsTerms))
        assert(news_terms.RelatedNewsID not in self.by_id)
        self.by_id[news_terms.RelatedNewsID] = news_terms

    def iter_news_terms(self, news_ID):
        assert(isinstance(news_ID, int))
        for term in self.by_id[news_ID].iter_terms():
            yield term

    def calculate_min_terms_per_context(self):
        if len(self.by_id) == 0:
            return None

        return min([len(news_terms) for news_terms in self.by_id.values()])


class NewsTerms:
    """
    Extracted News lexemes, such as:
        - news words
        - tokens
        - entities (positions).
    """

    def __init__(self, news_ID, terms, entity_positions, sentences_count, sentence_begin_inds):
        assert(isinstance(news_ID, int))
        assert(isinstance(terms, list))
        assert(isinstance(entity_positions, dict))
        assert(isinstance(sentences_count, int))
        assert(isinstance(sentence_begin_inds, list))
        self.__news_ID = news_ID
        self.__terms = terms
        self.__entity_positions = entity_positions
        self.__sentences_count = sentences_count
        self.__sentence_begin_inds = sentence_begin_inds

    @property
    def SentencesCount(self):
        return self.__sentences_count

    @classmethod
    def create_from_news(cls, news_ID, news, keep_tokens):
        assert(isinstance(keep_tokens, bool))
        terms, entity_positions, sentence_begin_inds = cls._extract_terms_and_entity_positions(news)
        return cls(news_ID, terms, entity_positions, news.sentences_count(), sentence_begin_inds)

    def iter_terms(self):
        for term in self.__terms:
            yield term

    def iter_sentence_terms(self, sentence_index):
        assert(isinstance(sentence_index, int))
        begin = self.__sentence_begin_inds[sentence_index]
        end = len(self.__terms) if sentence_index == self.__sentences_count - 1 \
            else self.__sentence_begin_inds[sentence_index + 1]
        for i in range(begin, end):
            yield self.__terms[i]

    @property
    def RelatedNewsID(self):
        return self.__news_ID

    def get_entity_position(self, entity_ID):
        assert(type(entity_ID) == str)      # ID which is a part of *.ann files.
        return self.__entity_positions[entity_ID]

    def get_term_index_in_sentence(self, term_index):
        assert(isinstance(term_index, int))
        begin = 0
        for i, begin_index in enumerate(self.__sentence_begin_inds):
            if begin_index > term_index:
                break
            begin = begin_index

        return term_index - begin

    @staticmethod
    def _extract_terms_and_entity_positions(news):
        assert(isinstance(news, News))

        sentence_begin = []
        terms = []
        entity_positions = {}
        for s_index, sentence in enumerate(news.iter_sentences()):
            assert(isinstance(sentence, Sentence))
            sentence_begin.append(len(terms))
            s_pos = 0
            # TODO: guarantee that entities ordered by e_begin.
            for e_ID, e_begin, e_end in sentence.iter_entities_info():
                # add terms before entity
                if e_begin > s_pos:
                    parsed_text_before = TextParser.parse(sentence.Text[s_pos:e_begin])
                    terms.extend(parsed_text_before.iter_raw_terms())
                # add entity position
                entity_positions[e_ID] = EntityPosition(term_index=len(terms), sentence_index=s_index)
                # add entity_text
                terms.append(news.Entities.get_entity_by_id(e_ID))
                s_pos = e_end

            # add text part after last entity of sentence.
            parsed_text_last = TextParser.parse((sentence.Text[s_pos:len(sentence.Text)]))
            terms.extend(parsed_text_last.iter_raw_terms())

        return terms, entity_positions, sentence_begin

    def __len__(self):
        return len(self.__terms)


class EntityPosition:

    def __init__(self, term_index, sentence_index):
        self.__term_index = term_index
        self.__sentence_index = sentence_index

    @property
    def TermIndex(self):
        return self.__term_index

    @property
    def SentenceIndex(self):
        return self.__sentence_index

