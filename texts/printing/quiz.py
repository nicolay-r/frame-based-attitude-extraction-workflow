# -*- coding: utf-8 -*-
from texts.printing.utils import ContextDescriptor, TitleDescriptor
import texts.printing.utils as utils


class QuizPrinter:

    def __init__(self, filepath, limit=1000):
        assert(isinstance(filepath, str))
        assert(isinstance(limit, int) and limit > 0)

        self.__filepath = filepath
        self.__out = open(filepath, "w")
        self.__written = 0
        self.__limit = limit

    def __open_file(self):
        return

    @property
    def IsLimitReached(self):
        return not self.__written < self.__limit

    def print_extracted_opinion(self,
                                title_descriptor,
                                context_descriptor,
                                print_title):
        assert(isinstance(title_descriptor, TitleDescriptor))
        assert(isinstance(context_descriptor, ContextDescriptor))
        assert(isinstance(print_title, bool))

        self.__written += 1

        td = title_descriptor
        cd = context_descriptor

        if print_title:
            s = "-----------\n"
            self.__out.writelines(s)

            s = "File: {}\n".format(td.news_info.FileName)
            self.__out.writelines(s)

            s = "Title: {}\n".format(td.parsed_title.to_string())
            self.__out.writelines(s)

        s = "Sentence: {}\n".format(cd.sentence_index)
        self.__out.writelines(s)

        utils.print_objects(f=self.__out,
                            objects_collection=cd.objects_collection)

        utils.print_opinions(f=self.__out,
                             opinion_refs=cd.opinion_refs,
                             objects_collection=cd.objects_collection)

        s = "TermsInText: {}\n".format(len(cd.parsed_text))
        self.__out.writelines(s)

        s = "Text: {}\n".format(cd.parsed_text.to_string())
        self.__out.writelines(s)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__out.close()
