from core.processing.ner.base import NamedEntityRecognition
from core.processing.ner.obj_decs import NerObjectDescriptor
from texts.objects.authorized.collection import AuthorizedObjectsCollection
from texts.objects.authorized.object import AuthTextObject
from texts.objects.cache.base import BaseObjectCache
from texts.text_info import NewsSentenceInfo
from texts.objects.helper import TextObjectHelper


class NerExtractor:

    def __init__(self, ner, ner_cache,
                 auth_objs_check_func,
                 objs_to_restore=None,
                 fix_obj_value=True):
        assert(isinstance(ner, NamedEntityRecognition) or ner is None)
        assert(isinstance(ner_cache, BaseObjectCache))
        assert(isinstance(objs_to_restore, AuthorizedObjectsCollection) or objs_to_restore is None)
        assert(isinstance(fix_obj_value, bool))
        assert(callable(auth_objs_check_func))
        self.__ner = ner
        self.__ner_cache = ner_cache
        self.__objs_to_restore = objs_to_restore
        self.__auth_objs_check_func = auth_objs_check_func
        self.__fixing_obj_values = fix_obj_value

    # region private methods

    @staticmethod
    def __is_able_to_get_objects(terms_list, ner, ner_cache, news_id):
        """ NOTE: We use 3 in order to increase performance, due to the specifics of the task.
        """
        if ner is not None:
            return ner.InputLimitation >= len(terms_list) >= 3
        else:
            return ner_cache.is_news_registered(news_id)

    @staticmethod
    def __get_object_from_parsed_text(ner_input_terms, ner, ner_cache, text_info):
        """ ner_input_terms: list
            ner: NamedEntityRecognition
            ner_cache: BaseNERCache
            text_info: NewsSentenceInfo
            returns: list[]
                list of the following elements: (positions, lengths, types)
        """
        assert(isinstance(text_info, NewsSentenceInfo))

        if ner is None:
            # from cache.
            return ner_cache.try_get(filename=text_info.NewsIndex,
                                     s_ind=text_info.SentenceIndex)

        return ner.extract([ner_input_terms])

    def __iter_missed_objects(self, founded_objects, lemmas_list):
        """
        added: already founded elements
        """

        it_missed = TextObjectHelper.iter_missed_objects(
            lemmas_list=lemmas_list,
            existed_objects=founded_objects,
            auth_objects=self.__objs_to_restore,
            get_collection_ind_func=lambda: len(founded_objects))

        for missed_obj in it_missed:
            yield missed_obj

    # endregion

    def extract(self, terms_list, iter_lemmas_in_range, text_info, is_term_func):
        assert(isinstance(terms_list, list))
        assert(isinstance(text_info, NewsSentenceInfo))
        assert(callable(iter_lemmas_in_range))
        assert(callable(is_term_func))

        extracted_text_objs = []

        is_able_to_get_objects = NerExtractor.__is_able_to_get_objects(terms_list=terms_list,
                                                                       ner=self.__ner,
                                                                       ner_cache=self.__ner_cache,
                                                                       news_id=text_info.NewsIndex)

        if not is_able_to_get_objects:
            return extracted_text_objs

        extracted_objs = NerExtractor.__get_object_from_parsed_text(ner_input_terms=terms_list,
                                                                    ner=self.__ner,
                                                                    ner_cache=self.__ner_cache,
                                                                    text_info=text_info)

        # TODO. TEMPORARY
        if extracted_objs is None:
            return extracted_text_objs

        for i, obj_desc in enumerate(extracted_objs):
            assert(isinstance(obj_desc, NerObjectDescriptor))

            fixed_obj_desc = obj_desc
            if self.__fixing_obj_values:

                # Fix borders.
                fixed_obj_desc = TextObjectHelper.try_fix_object_value(obj_desc=obj_desc,
                                                                       input_terms=terms_list,
                                                                       is_term_func=is_term_func)

                if fixed_obj_desc is None:
                    continue

            lemmas = list(iter_lemmas_in_range(fixed_obj_desc.get_range()))
            TextObjectHelper.fix_terms_inplace(lemmas)

            text_object = AuthTextObject.create(
                lemmas=lemmas,
                position=fixed_obj_desc.Position,
                obj_type=obj_desc.ObjectType,
                is_object_auth=self.__auth_objs_check_func,
                description="ner",
                collection_ind=len(extracted_text_objs))

            extracted_text_objs.append(text_object)

        if self.__objs_to_restore is not None:

            lemmas_list = list(iter_lemmas_in_range(None))
            assert(len(lemmas_list) == len(terms_list))

            missed_objs_it = self.__iter_missed_objects(founded_objects=extracted_text_objs,
                                                        lemmas_list=lemmas_list)

            for missed_obj in missed_objs_it:
                extracted_text_objs.append(missed_obj)

        return extracted_text_objs

