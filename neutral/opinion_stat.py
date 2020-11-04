from core.source.synonyms import SynonymsCollection


class OpinionStatisticPrinter(object):

    OpinionsAdded = "Добавлено отношений"

    def __init__(self, synonyms):
        assert(isinstance(synonyms, SynonymsCollection))
        self.__synonyms = synonyms
        self.__d = {}
        self.__opinion_ends = {}

    def register_opinion(self, key, source, target):
        assert(isinstance(key, str))
        assert(isinstance(source, str))
        assert(isinstance(target, str))

        if key not in self.__d:
            self.__d[key] = 0

        self.__d[key] += 1

        if key not in self.__opinion_ends:
            self.__opinion_ends[key] = (source, target)

    def print_statistic(self, filepath):

        with open(filepath, "w") as out:

            out.writelines("{pref}: {count}\n".format(
                pref=self.OpinionsAdded,
                count=sum([c for _, c in self.__d.items()])))

            sorted_opinions = sorted(self.__d.items(), key=lambda pair: pair[1])
            for key, total_count in reversed(sorted_opinions):
                value_left, value_right = self.__opinion_ends[key]
                s = "'{v_l}'->'{v_r}' (total: {t})\n".format(v_l=value_left,
                                                             v_r=value_right,
                                                             t=str(total_count))

                out.writelines(s)
