from texts.extraction.text_parser.terms_utils import to_input_terms
from texts.frames import TextFrameVariantsCollection
from texts.objects.collection import TextObjectsCollection
from texts.readers.utils import NewsInfo
from texts.text_info import NewsSentenceInfo


def process_sentence_core_static(news_info, s_ind, stemmer, ner,
                                 ner_extractor, frames_cache, frames_helper,
                                 parse_frames,
                                 using_frames_cache,
                                 need_whole_text_lemmatization):
    """
    The main sentence processor, where sentence considered to be a news title or
    a part of its contents.
    By default, it is assumed to parse news title.
    """
    assert(isinstance(news_info, NewsInfo))
    assert(isinstance(s_ind, int))

    news_sentence_info = NewsSentenceInfo(news_id=news_info.FileName,
                                          sent_id=s_ind)

    # parse text
    terms, parsed = to_input_terms(
        text=news_info.Title if news_sentence_info.IsTitle else news_info.get_sentence(s_ind),
        stemmer=stemmer,
        lemmatized_terms=need_whole_text_lemmatization,
        ner=ner)

    # parse ner
    auth_text_objects = ner_extractor.extract(
        terms_list=terms,
        text_info=news_sentence_info,
        iter_lemmas_in_range=lambda terms_range: parsed.iter_lemmas(
            terms_range=terms_range,
            need_cache=False),
        is_term_func=lambda t_ind: parsed.is_term(t_ind))
    objects = TextObjectsCollection(auth_text_objects)

    # parse frames
    if parse_frames:
        frames = __get_sentence_frames(lemmas=terms,
                                       using_frames_cache=using_frames_cache,
                                       news_sentence_info=news_sentence_info,
                                       frames_cache=frames_cache,
                                       frames_helper=frames_helper)
    else:
        frames = TextFrameVariantsCollection.create_empty()

    return terms, parsed, objects, frames


def __get_sentence_frames(lemmas, news_sentence_info, frames_cache, frames_helper, using_frames_cache):
    assert(isinstance(news_sentence_info, NewsSentenceInfo))

    if using_frames_cache and frames_cache is not None:
        # Reading information from cache.
        return TextFrameVariantsCollection.from_cache(
            cache=frames_cache,
            filename=news_sentence_info.NewsIndex,
            s_ind=news_sentence_info.SentenceIndex)

    # Running frames extraction on flight.
    return TextFrameVariantsCollection.from_parsed_text(
        lemmas=lemmas,
        frames_helper=frames_helper)

