# -*- coding: utf-8 -*-
from core.evaluation.labels import NegativeLabel, PositiveLabel
from core.source.opinion import OpinionCollection, Opinion
from core.source.synonyms import SynonymsCollection


class DiffStatisticTitleOpinionsPrinter(object):

    DocumentsParsed = "Разобрано документов"
    OpinionsMatched = "Сопоставлено отношений из заголовков"
    Diff = "Противоречий"
    Same = "Совпадений"

    def __init__(self, filepath, opinions, synonyms):
        assert(isinstance(filepath, str))
        assert(isinstance(opinions, OpinionCollection))
        assert(isinstance(synonyms, SynonymsCollection))
        self.__opinions = opinions
        self.__synonyms = synonyms
        self.__filepath = filepath
        self.__keys_pos = {}
        self.__keys_neg = {}
        self.__text_parsed_count = 0
        self.__same_count = 0
        self.__diff_count = 0
        self.__extra_parameters = []

    # region public methods

    def try_register_title_opinion_from_other_method(self, other_opinion, count=1):
        assert(isinstance(other_opinion, Opinion))

        if not self.__opinions.has_synonymous_opinion(other_opinion):
            return False

        key = other_opinion.create_synonym_id(self.__synonyms)
        d = self.__keys_neg if isinstance(other_opinion.sentiment, NegativeLabel) else self.__keys_pos
        if key not in d:
            d[key] = 0
        d[key] += count

        self.__update_same_or_diff_opinion_stat(other_opinion=other_opinion,
                                                count=count)

        return True

    def update_texts_parsed_count(self, text_parsed_count):
        assert(isinstance(text_parsed_count, int))
        self.__text_parsed_count = text_parsed_count

    def add_extra_parameter(self, description, value):
        assert(isinstance(description, str))
        assert(isinstance(description, str))
        self.__extra_parameters.append((description, value))

    def clear_extra_parameters(self):
        self.__extra_parameters = []

    def print_statistic(self):

        def avg_opin(opinion):
            pos_count, neg_count = times_opin_appears(opinion)
            total_count = pos_count + neg_count
            if total_count > 0:
                avg = 1.0 * (pos_count - neg_count) / total_count
            else:
                avg = 0
            return avg

        def matched_opin(opinion):
            pos_count, neg_count = times_opin_appears(opinion)
            total_count = pos_count + neg_count
            if total_count > 0:
                if isinstance(opinion.sentiment, PositiveLabel):
                    matched = 1.0 - neg_count * 1.0 / total_count
                else:
                    matched = 1.0 - pos_count * 1.0 / total_count
            else:
                matched = 0

            return matched

        def times_opin_appears(opinion):
            key = opinion.create_synonym_id(self.__synonyms)
            pos_count = 0 if key not in self.__keys_pos else self.__keys_pos[key]
            neg_count = 0 if key not in self.__keys_neg else self.__keys_neg[key]
            return pos_count, neg_count

        def calc_opinions_count():
            total_count = 0
            for value in self.__keys_pos.values():
                total_count += value
            for value in self.__keys_neg.values():
                total_count += value
            return total_count

        with open(self.__filepath, "w") as out:

            out.writelines("{pref}: {count}\n".format(pref=self.DocumentsParsed,
                                                      count=str(self.__text_parsed_count)))

            out.writelines("{pref}: {count}\n".format(pref=self.OpinionsMatched,
                                                      count=str(calc_opinions_count())))

            if self.__diff_count + self.__same_count == 0:
                return

            diff_percent = round(100.0 * self.__diff_count / (self.__diff_count + self.__same_count), 4)
            same_percent = round(100.0 * self.__same_count / (self.__diff_count + self.__same_count), 4)

            out.writelines("\t{pref}: {count} ({perc}%)\n".format(pref=self.Diff,
                                                                  count=str(self.__diff_count),
                                                                  perc=str(diff_percent)))
            out.writelines("\t{pref}: {count} ({perc}%)\n".format(pref=self.Same,
                                                                  count=str(self.__same_count),
                                                                  perc=str(same_percent)))

            for d, v in self.__extra_parameters:
                out.writelines("{}: {}\n".format(d, v))

            sorted_opinions = sorted(self.__opinions, key=lambda opinion: sum(times_opin_appears(opinion)))
            sorted_opinions = sorted(sorted_opinions, key=lambda opinion: matched_opin(opinion))

            for o in reversed(sorted_opinions):
                pos_count, neg_count = times_opin_appears(o)
                total_count = pos_count + neg_count

                s = "[{s_id},{sent},{p},{n}]: '{v_l}'->'{v_r}' -- {sent} (matched: {m}%, total: {t} (pos: {p}, neg: {n}), avg: {avg})\n".format(
                    s_id=o.create_synonym_id(self.__synonyms),
                    v_l=o.value_left,
                    v_r=o.value_right,
                    sent=str(o.sentiment.to_int()),
                    m=str(round(100.0 * matched_opin(o), 2)),
                    t=str(total_count),
                    p=str(pos_count),
                    n=str(neg_count),
                    avg=str(round(avg_opin(o), 2)))

                out.writelines(s)

    # endregion

    # region private methods

    def __update_same_or_diff_opinion_stat(self, other_opinion, count=1):
        assert(isinstance(other_opinion, Opinion))
        orig_opinion = self.__opinions.get_synonymous_opinion(other_opinion)
        if orig_opinion.sentiment.to_int() == other_opinion.sentiment.to_int():
            self.__same_count += count
        else:
            self.__diff_count += count

    # endregion