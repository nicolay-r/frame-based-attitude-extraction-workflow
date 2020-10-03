from core.source.synonyms import SynonymsCollection
from collections import OrderedDict


class AuthorizedObjectsCollection(object):
    """
    Represents a collection of unicode objects, that could be used
    as a part of extracted relations.
    """

    def __init__(self, object_values):
        assert(isinstance(object_values, OrderedDict))
        self.__auth_rule_func = None
        self.__object_values = object_values
        self.__max_term_length = 0 \
            if len(object_values) == 0 else \
            max([len(item.split(' ')) for item in object_values])

    @property
    def MaxTermLength(self):
        return self.__max_term_length

    @classmethod
    def from_relations_file(cls, filepath, synonyms):
        assert(isinstance(filepath, str))
        assert(isinstance(synonyms, SynonymsCollection))

        object_values = OrderedDict()

        with open(filepath, 'r') as f:
            for line in f.readlines():
                line = line
                relation = line[:line.index(':')]
                left, right = relation.split('->')
                cls.__add_group(object_values=object_values, synonyms=synonyms, value=left)
                cls.__add_group(object_values=object_values, synonyms=synonyms, value=right)

        return cls(object_values)

    @staticmethod
    def __add_group(object_values, synonyms, value):
        if not synonyms.has_synonym(value):
            if value not in object_values:
                object_values[value] = True
            return
        g = synonyms.get_synonym_group_index(value)
        for o in synonyms.iter_group(g):
            if o not in object_values:
                object_values[o] = True

    def has_value(self, object_value):
        return object_value in self.__object_values

    def __iter__(self):
        for object in self.__object_values.keys():
            yield object
