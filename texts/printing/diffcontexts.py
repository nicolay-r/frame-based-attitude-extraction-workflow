# -*- coding: utf-8 -*-
from os import path

import texts.printing.utils as utils
from texts.printing.utils import ContextDescriptor, TitleDescriptor


class DiffContextsPrinter(object):

    TITLE_KEY = 'Title'
    SENTENCE_KEY = 'Sentence'
    TEXT_KEY = 'Text'

    def __init__(self, directory, filename):
        assert(isinstance(directory, str))
        assert(isinstance(filename, str))
        self.__out = open(path.join(directory, filename), "w")

    def print_title(self, title_descriptor):
        self.__print_title(f=self.__out, title_descriptor=title_descriptor)

    def print_context(self, context_descriptor):
        self.__print_sentence(f=self.__out, context_descriptor=context_descriptor)

    @staticmethod
    def __print_title(f, title_descriptor):
        assert(isinstance(title_descriptor, TitleDescriptor))

        td = title_descriptor

        s = "-----------\n"
        f.writelines(s)

        s = "File: {}\n".format(td.news_info.FileName)
        f.writelines(s)

        utils.print_objects(f=f, objects_collection=td.objects_collection)

        utils.print_opinions(f=f,
                             opinion_refs=td.opinion_refs,
                             objects_collection=td.objects_collection)

        utils.print_frame_variants(f=f,
                                   text_frames=td.title_frames,
                                   frames=td.frames)

        s = "{t_key}: {t_value}\n".format(t_key=DiffContextsPrinter.TITLE_KEY,
                                          t_value=td.parsed_title.to_string())
        f.writelines(s)

    @staticmethod
    def __print_sentence(f, context_descriptor):
        assert(isinstance(context_descriptor, ContextDescriptor))

        cd = context_descriptor

        s = "{s_key}: {s_ind}\n".format(s_key=DiffContextsPrinter.SENTENCE_KEY,
                                        s_ind=cd.sentence_index)
        f.writelines(s)

        utils.print_objects(f=f, objects_collection=cd.objects_collection)

        utils.print_opinions(f=f,
                             opinion_refs=cd.opinion_refs,
                             objects_collection=cd.objects_collection)

        utils.print_frame_variants(f=f,
                                   text_frames=cd.text_frames,
                                   frames=cd.frames)

        s = "{text_key}: {text_value}\n".format(text_key=DiffContextsPrinter.TEXT_KEY,
                                                text_value=cd.parsed_text.to_string())
        f.writelines(s)
