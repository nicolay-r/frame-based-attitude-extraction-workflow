# -*- coding: utf-8 -*-


class StatisticObjectsPrinter(object):
    """
    Statistics of ignored entities.
    """

    def __init__(self, filepath):
        """
        stat: dict
            dictionary of pairs <value, count>
        """
        assert(isinstance(filepath, str))
        self.__filepath = filepath
        self.__stat = {}

    def register_missed_entity(self, value):
        assert(isinstance(value, str))
        if value in self.__stat:
            self.__stat[value] += 1
        else:
            self.__stat[value] = 1

    def save(self):
        total = sum(self.__stat.values())
        with open(self.__filepath, "w") as out:
            out.writelines("Число уникальных, не найденых объектов: {}\n".format(str(len(self.__stat))))
            out.writelines("Oбъектов не найденых в коллекции синонимов: {}\n".format(str(total)))

            for value, count in reversed(sorted(iter(self.__stat.items()), key=lambda pair: pair[1])):
                out.writelines("{v}: {c}\n".format(v=value, c=str(count)))
