# -*- coding: utf-8 -*-
from tqdm import tqdm

from core.evaluation.labels import PositiveLabel, NegativeLabel
from core.source.opinion import Opinion
from core.source.synonyms import SynonymsCollection
from texts.printing.statistics.element import StatisticSentimentElement
from texts.printing.statistics.sort_utils import order_by_sentiment_and_amount


class OpinionStatisticBasePrinter:

    TEXT_LEVEL_EXTRACTED_KEY = '[OpinionStatPrinter]: Зарегистрировано отношений (на уровне текста)'

    def __init__(self, synonyms, display_pn_stat=False):
        assert(isinstance(synonyms, SynonymsCollection))
        self.__synonyms = synonyms
        self.__stat = {}
        self.__extra_parameters = []
        self.__display_pn_stat = display_pn_stat

    @classmethod
    def from_file(cls, filepath, synonyms):
        assert(isinstance(filepath, str))
        assert(isinstance(synonyms, SynonymsCollection))

        instance = cls(synonyms=synonyms)

        with open(filepath, 'r') as f:
            it = cls.iter_line_params(f)
            for args in tqdm(it, desc="Init BasePrinter from file"):

                pos_count, neg_count, source_id, target_id, _ = args

                value_left = synonyms.get_group_by_index(int(source_id))[0]
                value_right = synonyms.get_group_by_index(int(target_id))[0]

                pos_opinion = Opinion(value_left=value_left,
                                      value_right=value_right,
                                      sentiment=PositiveLabel())

                neg_opinion = Opinion(value_left=value_left,
                                      value_right=value_right,
                                      sentiment=NegativeLabel())

                if pos_count > 0:
                    instance.register_extracted_opinion(pos_opinion, count=pos_count)
                if neg_count > 0:
                    instance.register_extracted_opinion(neg_opinion, count=neg_count)

        return instance

    # region public methods

    @staticmethod
    def iter_opinion_end_values(f, read_sentiment=False):
        assert(isinstance(read_sentiment, bool))

        for line in f:

            if not '->' in line:
                continue

            start_index = line.index(']') + 1
            end_index = line.index('(', start_index)
            args = line[start_index:end_index].split('->')
            obj, subj = [a.strip() for a in args]

            sentiment = 0

            if read_sentiment:

                args_begin = line.find('[') + 1
                args_end = line.find(']')

                _, pos_count, neg_count = line[args_begin:args_end].split(',')
                diff = int(pos_count) - int(neg_count)

                if diff != 0:
                    sentiment = 1 if diff > 0 else -1

            value_left = obj[1:-1]
            value_right = subj[1:-1]

            yield value_left, value_right, sentiment

    @staticmethod
    def iter_line_params(f):
        for line in f:
            if '[' in line:
                # [a_b, p, n]

                args = line[1:line.index(']', 1)].split(',')

                if len(args) != 3:
                    continue

                opinion_id, pos_count, neg_count = args
                source_id, target_id = opinion_id.split('_')
                yield int(pos_count), int(neg_count), source_id, target_id, line

    def register_extracted_opinion(self, opinion, count=1):
        assert(isinstance(opinion, Opinion))
        assert(isinstance(count, int) and count > 0)

        if not self.__synonyms.IsReadOnly:
            if not self.__synonyms.has_synonym(opinion.value_left):
                self.__synonyms.add_synonym(s=opinion.value_left)
            if not self.__synonyms.has_synonym(opinion.value_right):
                self.__synonyms.add_synonym(s=opinion.value_right)

        key = opinion.create_synonym_id(self.__synonyms)

        if key not in self.__stat:
            self.__stat[key] = StatisticSentimentElement(opinion)

        self.__stat[key].inc(label=opinion.sentiment,
                             count=count)

    def add_extra_separator(self):
        self.__extra_parameters.append(("--------------------", ""))

    def add_extra_parameter(self, description, value):
        assert(isinstance(description, str))
        assert(isinstance(description, str))
        self.__extra_parameters.append((description, value))

    def clear_extra_parameters(self):
        self.__extra_parameters = []

    def __pn_stat(self, element):
        assert(isinstance(element, StatisticSentimentElement))

        pos = element.PositiveCount
        neg = element.NegativeCount
        pos_p = round((100.0 * element.PositiveCount) / element.Count, 1)
        neg_p = round((100.0 * element.NegativeCount) / element.Count, 1)

        return pos, neg, pos_p, neg_p

    def __calculate_total(self):
        return sum([v.Count for v in self.__stat.values()])

    def save(self,
             filepath,
             sort_stat_elem_func=None,
             is_save_elem=None,
             write_header=True):
        assert(callable(sort_stat_elem_func) or sort_stat_elem_func is None)
        assert(callable(is_save_elem) or is_save_elem is None)
        assert(isinstance(filepath, str))

        total = self.__calculate_total()

        with open(filepath, "w") as out:
            out.writelines("{key}: {total}\n".format(key=self.TEXT_LEVEL_EXTRACTED_KEY,
                                                     total=str(total)))

            for desc, value in self.__extra_parameters:
                out.writelines("{key}: {value}\n".format(key=desc,
                                                         value=value))

            sort_func = sort_stat_elem_func \
                if sort_stat_elem_func is not None \
                else lambda elem: order_by_sentiment_and_amount(elem, total)

            it = reversed(sorted(iter(self.__stat.values()), key=sort_func))

            for value in tqdm(iterable=it, desc="Printing statistics"):
                assert(isinstance(value, StatisticSentimentElement))

                if is_save_elem is not None and not is_save_elem(value):
                    continue

                opin_line = "{source}->{target}: {count}".format(
                    source=value.Opinion.value_left,
                    target=value.Opinion.value_right,
                    count=value.Count)

                result_line = opin_line
                if self.__display_pn_stat:
                    pos, neg, pos_p, neg_p = self.__pn_stat(value)
                    source = value.Opinion.value_left
                    target = value.Opinion.value_right

                    header = "[{o_syn_ids},{pos},{neg}] ".format(
                        o_syn_ids=value.Opinion.create_synonym_id(self.__synonyms),
                        pos=pos,
                        neg=neg)

                    result_line = "{header}'{source}'->'{target}' (p:{pos} ({pos_p}%), n:{neg} ({neg_p}%))".format(
                        header=header if write_header else "",
                        source=source, target=target,
                        pos=pos, neg=neg,
                        pos_p=pos_p, neg_p=neg_p)

                out.writelines("{l}\n".format(l=result_line))

    # endregion