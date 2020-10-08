from core.processing.lemmatization.base import Stemmer
from core.processing.ner.base import NamedEntityRecognition
from core.runtime.parser import ParsedText, TextParser


def to_input_terms(text, ner, stemmer, return_parsed_text=True, lemmatized_terms=False):
    assert(isinstance(ner, NamedEntityRecognition) or ner is None)
    assert (isinstance(stemmer, Stemmer) or stemmer is None)

    parsed_text = TextParser.parse(text=text, stemmer=stemmer, lemmatize_on_init=lemmatized_terms)
    input_terms = __get_terms_from_parsed_text(parsed_text=parsed_text,
                                               ner=ner,
                                               lemmatized_terms=lemmatized_terms)

    if return_parsed_text:
        return input_terms, parsed_text
    else:
        return input_terms


def __get_terms_from_parsed_text(parsed_text, ner, lemmatized_terms=False):
    assert(isinstance(parsed_text, ParsedText))
    assert(isinstance(ner, NamedEntityRecognition) or ner is None)

    ner_input_terms = None

    # Transforming terms into list of strings
    if ner is not None:
        # Optional lemmatization.
        if ner.NeedLemmatization or lemmatized_terms:
            ner_input_terms = parsed_text.iter_lemmas(need_cache=True)
        # Optional lowercase.
        if ner.NeedLowercase:
            ner_input_terms = [t.lower() for t in ner_input_terms]
    else:
        if lemmatized_terms:
            ner_input_terms = list(parsed_text.iter_lemmas(return_raw=True))
        else:
            ner_input_terms = list(parsed_text.iter_original_terms())

    return ner_input_terms

