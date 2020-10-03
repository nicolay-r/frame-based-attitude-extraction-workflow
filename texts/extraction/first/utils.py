from tqdm import tqdm

from core.evaluation.labels import Label
from core.source.opinion import OpinionCollection, Opinion
from core.source.synonyms import SynonymsCollection


def __iter_opinion_end_values(filepath, read_sentiment):
    with open(filepath) as f:
        for line in f.readlines():
            line = line
            line_parts = line.split(':')
            values = line_parts[0].split('->')
            left_value, right_value = values

            sentiment = int(round(float(line_parts[-1][:-2]))) \
                if read_sentiment \
                else 0

            yield left_value, right_value, sentiment


def read_opinions(filepath, synonyms,
                  custom_opin_ends_iter=None,
                  read_sentiment=True,
                  skip_non_added=True):
    assert(isinstance(synonyms, SynonymsCollection))
    assert(callable(custom_opin_ends_iter) or custom_opin_ends_iter is None)
    assert(isinstance(read_sentiment, bool))
    assert(isinstance(skip_non_added, bool))

    opinions = OpinionCollection(opinions=[], synonyms=synonyms)

    it = __iter_opinion_end_values(filepath, read_sentiment) if custom_opin_ends_iter is None \
        else custom_opin_ends_iter(read_sentiment)

    for left_value, right_value, sentiment in tqdm(it, "Reading opinions:"):

            o = Opinion(value_left=left_value,
                        value_right=right_value,
                        sentiment=Label.from_int(sentiment))

            add_result = opinions.try_add_opinion(o)

            msg = "Warning: opinion '{}->{}' was skipped!".format(o.value_left, o.value_right)

            if add_result is False:
                if not skip_non_added:
                    raise Exception(msg)
                else:
                    print(msg)

    return opinions
