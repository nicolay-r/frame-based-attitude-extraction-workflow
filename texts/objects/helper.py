from collections import Iterable

from core.processing.ner.obj_decs import NerObjectDescriptor
from texts.objects.authorized.collection import AuthorizedObjectsCollection
from texts.objects.authorized.object import AuthTextObject


class TextObjectHelper:

    QUOTE = '&quote'

    def __init__(self):
        pass

    @staticmethod
    def fix_terms_inplace(input_terms):
        """
        Fix remove extra garbage, that was not captured by text reader.
        """

        for i, term in enumerate(input_terms):

            if TextObjectHelper.QUOTE not in term:
                continue

            # Removing quote
            from_ind = term.index(TextObjectHelper.QUOTE)
            if from_ind > 0:
                input_terms[i] = term[:from_ind]

    @staticmethod
    def try_fix_object_value(obj_desc, input_terms, is_term_func, check_obj_includes_non_term=True):
        assert(isinstance(obj_desc, NerObjectDescriptor))
        assert(isinstance(input_terms, list))
        assert(callable(is_term_func))

        r_len = obj_desc.Length

        i, j = obj_desc.get_range()
        j -= 1

        # Crop from non-terms at left and right object bounds.
        changed = False
        while not is_term_func(i) or not is_term_func(j):

            if not is_term_func(i):
                i += 1
                r_len -= 1
                changed = True

            if not is_term_func(j):
                j -= 1
                r_len -= 1
                changed = True

            if i >= len(input_terms):
                break
            if j == 0:
                break
            if i > j:
                break

        if i > j:
            return None

        if check_obj_includes_non_term:
            for index in range(i, j+1):
                if not is_term_func(index):
                    return None

        if not changed:
            return obj_desc

        return NerObjectDescriptor(pos=i,
                                   length=r_len,
                                   obj_type=obj_desc.ObjectType)

    @staticmethod
    def iter_missed_objects(lemmas_list, existed_objects, auth_objects, get_collection_ind_func):
        assert(isinstance(lemmas_list, list))
        assert(isinstance(existed_objects, Iterable))
        assert(isinstance(auth_objects, AuthorizedObjectsCollection))
        assert(callable(get_collection_ind_func))

        used = [False] * len(lemmas_list)

        for obj in existed_objects:
            bound = obj.get_bound()
            i = bound.TermIndex
            while i < bound.TermIndex + bound.Length:
                used[i] = True
                i += 1

        position = 0
        while position < len(used):

            if used[position]:
                position += 1
                continue

            max_term_length = 1
            while max_term_length < auth_objects.MaxTermLength:
                index = position + max_term_length
                if index >= len(used):
                    break
                if used[index]:
                    break
                max_term_length += 1

            next_position = position + 1
            for r_offset in reversed(list(range(max_term_length))):

                last_term_index = position + r_offset

                if not (last_term_index < len(used)):
                    position = next_position
                    break

                terms = lemmas_list[position:last_term_index+1]
                lemma_value = ' '.join(terms)

                if not auth_objects.has_value(lemma_value):
                    if r_offset == 0:
                        position = next_position
                        break
                    else:
                        continue

                yield AuthTextObject(terms=terms,
                                     position=position,
                                     is_auth=True,
                                     obj_type="UNKN",
                                     description="restored",
                                     collection_ind=get_collection_ind_func())

                position = last_term_index + 1

                break
